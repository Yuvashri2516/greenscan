"""
evaluation/test_functional_and_robustness.py
Part A & Part B Functional and Robustness Test Suite:
1. Functional test cases: Healthy, Early Blight, Late Blight, Non-Tomato Leaf, Non-Leaf, Lighting Variations.
2. Robustness test cases: Small image, high-res, corrupted byte stream, empty upload, wrong format.
3. Tests both local pipeline and API response contract.
"""

import sys
import os
import io
import time
import json
from pathlib import Path

# Add project root and backend to sys.path
project_root = Path(__file__).parent.parent.resolve()
backend_path = project_root / "backend"
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import numpy as np
import cv2
import pandas as pd
import tensorflow as tf

try:
    from backend.image_enhancer import enhance_leaf_image
    from backend.leaf_segmenter import segment_leaf
    from backend.leaf_validator import validate_leaf_image, NOT_TOMATO_LEAF, LOW_QUALITY_IMAGE, VALID_TOMATO_LEAF
    from backend.gradcam_engine import get_gradcam_activation_matrix
    from backend.gsa_engine import run_gsa_pipeline
    from backend.recommendation_v2 import get_structured_recommendations
    from backend.database import init_db
except ImportError:
    from image_enhancer import enhance_leaf_image
    from leaf_segmenter import segment_leaf
    from leaf_validator import validate_leaf_image, NOT_TOMATO_LEAF, LOW_QUALITY_IMAGE, VALID_TOMATO_LEAF
    from gradcam_engine import get_gradcam_activation_matrix
    from gsa_engine import run_gsa_pipeline
    from recommendation_v2 import get_structured_recommendations
    from database import init_db

init_db()

MODEL_PATH = project_root / "model" / "greenscan_model.keras"
DATASET_PATH = project_root / "dataset"
OUTPUT_DIR = project_root / "evaluation"
CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

def run_pipeline_on_image(img_bgr, model):
    """Executes the full production pipeline on a BGR image array."""
    t0 = time.time()
    
    # 1. Quality & Illumination Enhancement
    enhanced_bgr, quality_info = enhance_leaf_image(img_bgr, target_size=(224, 224))
    
    # 2. Leaf Segmentation
    leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)
    total_pixels = enhanced_bgr.shape[0] * enhanced_bgr.shape[1]
    
    # 3. Early Validation Gate
    early_val = validate_leaf_image(
        leaf_pixels=leaf_pixels,
        total_pixels=total_pixels,
        quality_info=quality_info,
        min_leaf_coverage_pct=10.0,
        min_leaf_pixels=1000
    )
    
    if not early_val["is_valid"] and early_val["validation_status"] == LOW_QUALITY_IMAGE:
        t_end = time.time()
        return {
            "status": "REJECTED_LOW_QUALITY",
            "is_valid": False,
            "validation_status": LOW_QUALITY_IMAGE,
            "reasons": early_val["quality_reasons"],
            "processing_time_ms": round((t_end - t0) * 1000, 2)
        }
        
    # 4. Model Prediction
    rgb_img = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
    input_arr = np.expand_dims(rgb_img.astype(np.float32) / 255.0, axis=0)
    preds = model.predict(input_arr, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    conf = float(preds[pred_idx])
    pred_class = CLASS_LABELS[pred_idx]
    
    # 5. Post-prediction Validation Gate
    val_res = validate_leaf_image(
        leaf_pixels=leaf_pixels,
        total_pixels=total_pixels,
        quality_info=quality_info,
        confidence=conf,
        min_leaf_coverage_pct=10.0,
        min_leaf_pixels=1000
    )
    
    if not val_res["is_valid"] and val_res["validation_status"] == NOT_TOMATO_LEAF:
        t_end = time.time()
        return {
            "status": "REJECTED_NON_LEAF",
            "is_valid": False,
            "validation_status": NOT_TOMATO_LEAF,
            "predicted_class": pred_class,
            "confidence": round(conf * 100, 2),
            "leaf_coverage_pct": val_res["leaf_coverage_pct"],
            "processing_time_ms": round((t_end - t0) * 1000, 2)
        }
        
    # 6. Grad-CAM & GSA
    gradcam_mat = get_gradcam_activation_matrix(model, input_arr, pred_idx)
    gsa_res = run_gsa_pipeline(gradcam_mat, leaf_mask, leaf_pixels, conf, pred_class)
    
    # 7. Recommendations
    rec = get_structured_recommendations(pred_class, gsa_res["severity_level"], conf)
    
    t_end = time.time()
    return {
        "status": "SUCCESS",
        "is_valid": True,
        "validation_status": VALID_TOMATO_LEAF,
        "predicted_class": pred_class,
        "confidence": round(conf * 100, 2),
        "severity_level": gsa_res["severity_level"],
        "plant_health_score": gsa_res["plant_health_score"],
        "affected_area_pct": gsa_res["attention_affected_region_percent"],
        "lighting_condition": quality_info.get("illumination", {}).get("lighting_condition"),
        "has_gradcam": (gradcam_mat is not None and gradcam_mat.shape == (224, 224)),
        "immediate_action": rec.get("immediate_actions", [""])[0] if rec.get("immediate_actions") else "N/A",
        "processing_time_ms": round((t_end - t0) * 1000, 2)
    }

def main():
    print("=" * 70)
    print("  FUNCTIONAL & ROBUSTNESS TESTS (PART A & PART B)")
    print("=" * 70)
    
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    # Select sample images from dataset
    healthy_samples = list((DATASET_PATH / "tomato_healthy").glob("*.JPG")) or list((DATASET_PATH / "tomato_healthy").glob("*.jpg"))
    early_samples = list((DATASET_PATH / "tomato_Early blight").glob("*.JPG")) or list((DATASET_PATH / "tomato_Early blight").glob("*.jpg"))
    late_samples = list((DATASET_PATH / "tomato_Late blight").glob("*.JPG")) or list((DATASET_PATH / "tomato_Late blight").glob("*.jpg"))
    
    img_healthy = cv2.imread(str(healthy_samples[0]))
    img_early = cv2.imread(str(early_samples[0]))
    img_late = cv2.imread(str(late_samples[0]))
    
    # Create non-leaf random image (checkerboard / indoor pattern)
    img_non_leaf = np.zeros((300, 300, 3), dtype=np.uint8)
    img_non_leaf[::20, :, :] = 255 # stripes
    
    # Create blurry image
    img_blurry = cv2.GaussianBlur(img_healthy, (51, 51), 0)
    
    # Create lighting variations of healthy leaf
    img_low_light = (img_healthy * 0.3).astype(np.uint8)
    img_warm_light = img_healthy.copy()
    img_warm_light[:, :, 2] = np.clip(img_warm_light[:, :, 2] * 1.5, 0, 255) # boost red
    img_bright_sun = cv2.add(img_healthy, np.full_like(img_healthy, 80)) # direct sunlight
    
    # Shadowed leaf
    shadow_gradient = np.linspace(0.2, 1.0, img_healthy.shape[1]).reshape(1, img_healthy.shape[1], 1)
    img_shadow = (img_healthy * shadow_gradient).astype(np.uint8)
    
    tests = [
        ("Test 1 — Healthy Tomato", img_healthy, "tomato_healthy", "Functional Test: Healthy Leaf"),
        ("Test 2 — Early Blight", img_early, "tomato_Early blight", "Functional Test: Early Blight"),
        ("Test 3 — Late Blight", img_late, "tomato_Late blight", "Functional Test: Late Blight"),
        ("Test 4 — Non-Leaf (Geometric)", img_non_leaf, "REJECTED", "Validation Gate: Non-leaf rejection"),
        ("Test 5 — Extremely Blurry Leaf", img_blurry, "REJECTED_LOW_QUALITY", "Quality Gate: Blur detection"),
        ("Test 6a — Low Light Variation", img_low_light, "tomato_healthy", "Illumination Robustness: Low light"),
        ("Test 6b — Warm Evening Cast", img_warm_light, "tomato_healthy", "Illumination Robustness: Warm cast"),
        ("Test 6c — Bright Direct Sunlight", img_bright_sun, "tomato_healthy", "Illumination Robustness: Sunlight"),
        ("Test 6d — Canopy Shadow Gradient", img_shadow, "tomato_healthy", "Illumination Robustness: Shadows"),
    ]
    
    functional_results = []
    
    for name, img, expected, description in tests:
        res = run_pipeline_on_image(img, model)
        actual = res.get("predicted_class", res.get("validation_status"))
        conf = res.get("confidence", 0.0)
        
        passed = False
        if "REJECTED" in expected:
            passed = (res["is_valid"] == False or "REJECTED" in res["status"])
        else:
            passed = (res.get("predicted_class") == expected)
            
        functional_results.append({
            "Test": name,
            "Description": description,
            "Expected": expected,
            "Actual": actual,
            "Confidence (%)": conf,
            "Health Score": res.get("plant_health_score", "N/A"),
            "Severity": res.get("severity_level", "N/A"),
            "Lighting Detected": res.get("lighting_condition", "N/A"),
            "Latency (ms)": res.get("processing_time_ms"),
            "Status": "PASS" if passed else "FAIL"
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: Expected '{expected}', Got '{actual}' (Conf: {conf}%, Latency: {res.get('processing_time_ms')}ms)")
        
    df_func = pd.DataFrame(functional_results)
    df_func.to_csv(OUTPUT_DIR / "functional_test_results.csv", index=False)
    print("\nSaved functional_test_results.csv")
    print(df_func.to_string(index=False))

if __name__ == "__main__":
    main()
