import os
import cv2
import numpy as np
import pandas as pd
import random
from pathlib import Path
import tensorflow as tf
import matplotlib.pyplot as plt
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from image_enhancer import enhance_leaf_image
from gradcam_engine import get_gradcam_activation_matrix
from leaf_segmenter import segment_leaf
import gsa_engine
import config

DATASET_PATH = PROJECT_ROOT / "dataset"
MODEL_PATH = PROJECT_ROOT / "model" / "greenscan_model.keras"
CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

TASK_DIR = PROJECT_ROOT / "expert_annotation_task"
IMAGES_DIR = TASK_DIR / "images"
TASK_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

def overlay_heatmap(img_bgr, heatmap, alpha=0.4):
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    return cv2.addWeighted(heatmap_colored, alpha, img_bgr, 1 - alpha, 0)

def main():
    print("Loading Model...", flush=True)
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    test_files = []
    for cls in CLASS_LABELS:
        cls_dir = DATASET_PATH / cls
        all_imgs = list(cls_dir.glob("*.JPG")) + list(cls_dir.glob("*.jpg"))
        random.seed(42)
        if all_imgs:
            sample = random.sample(all_imgs, min(30, len(all_imgs)))
            for img_path in sample:
                test_files.append((img_path, cls))
                
    results = []
    
    for idx, (img_path, true_class) in enumerate(test_files):
        print(f"Preparing Composite {idx+1}/{len(test_files)}...", flush=True)
        
        orig_img = cv2.imread(str(img_path))
        if orig_img is None: continue
        
        enhanced_bgr, _ = enhance_leaf_image(orig_img)
        leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)
        
        rgb_img = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        input_arr = np.expand_dims(rgb_img.astype(np.float32) / 255.0, axis=0)
        
        preds = model.predict(input_arr, verbose=0)
        pred_idx = int(np.argmax(preds[0]))
        conf = float(np.max(preds[0]))
        pred_class = CLASS_LABELS[pred_idx]
        
        gradcam = get_gradcam_activation_matrix(model, input_arr, pred_idx)
        
        gsa_engine.GRADCAM_THRESHOLD = 0.60
        gsa_res = gsa_engine.run_gsa_pipeline(gradcam, leaf_mask, leaf_pixels, conf, pred_class)
        
        # Save composite visualization
        plt.figure(figsize=(15, 3))
        
        plt.subplot(1, 5, 1)
        plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
        plt.title("Original")
        plt.axis('off')
        
        plt.subplot(1, 5, 2)
        plt.imshow(leaf_mask, cmap='gray')
        plt.title("Leaf Mask")
        plt.axis('off')
        
        heatmap_resized = cv2.resize(gradcam, (224, 224))
        overlay = overlay_heatmap(enhanced_bgr, heatmap_resized)
        plt.subplot(1, 5, 3)
        plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        plt.title("Grad-CAM Overlay")
        plt.axis('off')
        
        plt.subplot(1, 5, 4)
        activation_mask = np.where((heatmap_resized >= 0.60) & (leaf_mask == 1), 1, 0)
        plt.imshow(activation_mask, cmap='jet')
        plt.title("Activation Mask (>=0.60)")
        plt.axis('off')
        
        plt.subplot(1, 5, 5)
        plt.axis('off')
        stat_text = (
            f"Image: {img_path.name}\n"
            f"Pred: {pred_class.split('_')[-1]}\n"
            f"Conf: {conf*100:.1f}%\n"
            f"Affected: {gsa_res['attention_affected_region_percent']:.1f}%\n"
            f"W. Activ: {gsa_res['mean_leaf_activation']:.3f}\n"
            f"Health: {gsa_res['plant_health_score']}\n"
            f"Severity: {gsa_res['severity_level']}"
        )
        plt.text(0.1, 0.5, stat_text, fontsize=12, verticalalignment='center')
        
        plt.tight_layout()
        out_filename = f"{idx:03d}_{img_path.name}_composite.png"
        plt.savefig(IMAGES_DIR / out_filename)
        plt.close()

        results.append({
            "image_id": out_filename,
            "predicted_disease": pred_class,
            "model_confidence": round(conf, 4),
            "estimated_attention_affected_region": gsa_res["attention_affected_region_percent"],
            "weighted_activation": gsa_res["mean_leaf_activation"],
            "green_scan_health_score": gsa_res["plant_health_score"],
            "green_scan_severity": gsa_res["severity_level"],
            "expert_disease": "",
            "expert_severity": "",
            "expert_comments": ""
        })

    df = pd.DataFrame(results)
    df.to_csv(TASK_DIR / "gsa_expert_validation.csv", index=False)
    print("Expert Annotation Task Prepared in 'expert_annotation_task/'", flush=True)

if __name__ == "__main__":
    main()
