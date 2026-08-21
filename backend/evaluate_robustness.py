import os
import cv2
import numpy as np
import pandas as pd
import random
from pathlib import Path
import tensorflow as tf
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from image_enhancer import check_image_quality, enhance_leaf_image
from leaf_segmenter import segment_leaf
from gradcam_engine import get_gradcam_activation_matrix
import gsa_engine
import config

DATASET_PATH = PROJECT_ROOT / "dataset"
MODEL_PATH = PROJECT_ROOT / "model" / "greenscan_model.keras"
CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

def apply_transformation(img, condition):
    if condition == "A. Normal":
        return img
    elif condition == "B. Low-Resolution":
        h, w = img.shape[:2]
        small = cv2.resize(img, (64, 64))
        return cv2.resize(small, (w, h))
    elif condition == "C. Slightly Blurred":
        return cv2.GaussianBlur(img, (25, 25), 0)
    elif condition == "D. Dark":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv = np.array(hsv, dtype=np.float64)
        hsv[:,:,2] = hsv[:,:,2] * 0.3
        hsv[:,:,2][hsv[:,:,2]>255]  = 255
        hsv = np.array(hsv, dtype=np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    elif condition == "E. Overexposed":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv = np.array(hsv, dtype=np.float64)
        hsv[:,:,2] = hsv[:,:,2] * 1.8
        hsv[:,:,2][hsv[:,:,2]>255]  = 255
        hsv = np.array(hsv, dtype=np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    elif condition == "F. Uneven Lighting":
        h, w = img.shape[:2]
        gradient = np.tile(np.linspace(0.1, 1.8, w), (h, 1))
        gradient = np.stack([gradient]*3, axis=2)
        out = img * gradient
        return np.clip(out, 0, 255).astype(np.uint8)
    elif condition == "H. Partial Leaf":
        h, w = img.shape[:2]
        out = img.copy()
        out[:, w//2:] = 0
        return out
    elif condition == "I. Rotated":
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif condition == "K. Small Portion":
        h, w = img.shape[:2]
        small = cv2.resize(img, (w//3, h//3))
        out = np.full((h, w, 3), (100, 150, 100), dtype=np.uint8)
        y_offset = (h - h//3) // 2
        x_offset = (w - w//3) // 2
        out[y_offset:y_offset+h//3, x_offset:x_offset+w//3] = small
        return out
    return img

def main():
    print("Loading Model...", flush=True)
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    test_files = []
    for cls in CLASS_LABELS:
        cls_dir = DATASET_PATH / cls
        all_imgs = list(cls_dir.glob("*.JPG")) + list(cls_dir.glob("*.jpg"))
        random.seed(42)
        if all_imgs:
            sample = random.sample(all_imgs, min(10, len(all_imgs)))
            for img_path in sample:
                test_files.append((img_path, cls))
                
    conditions = [
        "A. Normal", "B. Low-Resolution", "C. Slightly Blurred", "D. Dark",
        "E. Overexposed", "F. Uneven Lighting", "H. Partial Leaf", "I. Rotated", "K. Small Portion"
    ]
    
    results = []
    
    for idx, (img_path, true_class) in enumerate(test_files):
        print(f"Processing Image {idx+1}/{len(test_files)}", flush=True)
        orig_img = cv2.imread(str(img_path))
        if orig_img is None: continue
        
        for cond in conditions:
            test_img = apply_transformation(orig_img, cond)
            
            # Quality Detection (before enhancement)
            quality_info = check_image_quality(test_img)
            
            enhanced_bgr, _ = enhance_leaf_image(test_img)
            leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)
            
            rgb_img = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
            input_arr = np.expand_dims(rgb_img.astype(np.float32) / 255.0, axis=0)
            preds = model.predict(input_arr, verbose=0)
            pred_idx = int(np.argmax(preds[0]))
            conf = float(np.max(preds[0]))
            pred_class = CLASS_LABELS[pred_idx]
            
            gradcam = get_gradcam_activation_matrix(model, input_arr, pred_idx)
            
            gsa_engine.GRADCAM_THRESHOLD = config.GRADCAM_THRESHOLD
            gsa_res = gsa_engine.run_gsa_pipeline(gradcam, leaf_mask, leaf_pixels, conf, pred_class)
            
            is_correct = (pred_class == true_class)
            
            failure_type = "None"
            if not is_correct and conf >= config.MIN_CONFIDENCE_THRESHOLD:
                failure_type = "High-confidence error"
            elif not is_correct and conf < config.MIN_CONFIDENCE_THRESHOLD:
                failure_type = "Low-confidence correct rejection"
            elif is_correct and conf < config.MIN_CONFIDENCE_THRESHOLD:
                failure_type = "Low-confidence correct (Warning)"
                
            results.append({
                "Image ID": img_path.name,
                "Test Condition": cond,
                "True Class": true_class,
                "Predicted Class": pred_class,
                "Correct": is_correct,
                "Confidence": round(conf, 4),
                "Leaf Pixels": gsa_res["leaf_pixels"],
                "Activated Pixels": gsa_res["activated_pixels"],
                "Affected Region %": gsa_res["attention_affected_region_percent"],
                "Weighted Activation": gsa_res["mean_leaf_activation"],
                "Health Score": gsa_res["plant_health_score"],
                "Severity": gsa_res["severity_level"],
                "Image Quality Passed": quality_info["passed"],
                "Failure Type": failure_type
            })
            
    df = pd.DataFrame(results)
    df.to_csv(PROJECT_ROOT / "greenscan_robustness_results.csv", index=False)
    print("Robustness Evaluation Saved to greenscan_robustness_results.csv", flush=True)

if __name__ == "__main__":
    main()
