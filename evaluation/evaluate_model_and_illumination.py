"""
evaluation/evaluate_model_and_illumination.py
Rigorous Empirical Evaluation of GreenScan 2.0:
1. Production Model Validation Split Evaluation (1,507 Images)
2. Comparative Evaluation: Baseline vs. Illumination-Normalized Pipeline
3. Confusion Matrices, Metrics Reports, Confidence Distributions, and Error Analysis
"""

import sys
import os
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
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import tensorflow as tf
try:
    from keras.preprocessing.image import ImageDataGenerator
except ImportError:
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Import backend preprocessing pipelines
try:
    from backend.illumination_normalizer import normalize_illumination
    from backend.image_enhancer import enhance_leaf_image
except ImportError:
    from illumination_normalizer import normalize_illumination
    from image_enhancer import enhance_leaf_image

DATASET_PATH = project_root / "dataset"
MODEL_PATH = project_root / "model" / "greenscan_model.keras"
OUTPUT_DIR = project_root / "evaluation"
OUTPUT_DIR.mkdir(exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

def main():
    print("=" * 70)
    print("  GREENSCAN 2.0 MASTER EMPIRICAL ML EVALUATION")
    print("=" * 70)
    
    print(f"\n[1] Loading Trained Model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(str(MODEL_PATH))
    print(f"    Model architecture: {model.name if hasattr(model, 'name') else 'Keras Functional'}")
    print(f"    Total Layers: {len(model.layers)}, Input Shape: {model.input_shape}, Output Shape: {model.output_shape}")
    
    print(f"\n[2] Setting up Deterministic Validation Split (20% of 7,536 images)...")
    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
    val_data = datagen.flow_from_directory(
        str(DATASET_PATH),
        target_size=(224, 224),
        batch_size=1,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=42
    )
    
    filepaths = val_data.filepaths
    true_labels = val_data.classes
    num_samples = len(filepaths)
    print(f"    Total Validation Samples: {num_samples}")
    print(f"    Class Index Mapping: {val_data.class_indices}")
    
    # Store predictions
    baseline_preds = []
    baseline_confs = []
    
    norm_preds = []
    norm_confs = []
    
    records = []
    
    print(f"\n[3] Running Comparative Inference across {num_samples} images...")
    start_eval_time = time.time()
    
    for i, (fpath, true_idx) in enumerate(zip(filepaths, true_labels)):
        if (i + 1) % 150 == 0 or i == num_samples - 1:
            elapsed = time.time() - start_eval_time
            print(f"    Progress: {i+1}/{num_samples} ({(i+1)/num_samples*100:.1f}%) in {elapsed:.1f}s")
            
        img_bgr = cv2.imread(fpath)
        if img_bgr is None:
            continue
            
        true_class = CLASS_LABELS[true_idx]
        
        # ── Pipeline A: Baseline (Standard Resize & Normalize) ──
        img_base_rgb = cv2.cvtColor(cv2.resize(img_bgr, (224, 224)), cv2.COLOR_BGR2RGB)
        arr_base = np.expand_dims(img_base_rgb.astype(np.float32) / 255.0, axis=0)
        p_base = model.predict(arr_base, verbose=0)[0]
        idx_base = int(np.argmax(p_base))
        conf_base = float(p_base[idx_base])
        baseline_preds.append(idx_base)
        baseline_confs.append(conf_base)
        
        # ── Pipeline B: GreenScan Illumination Normalization ──
        enhanced_bgr, q_info = enhance_leaf_image(img_bgr, target_size=(224, 224))
        img_norm_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        arr_norm = np.expand_dims(img_norm_rgb.astype(np.float32) / 255.0, axis=0)
        p_norm = model.predict(arr_norm, verbose=0)[0]
        idx_norm = int(np.argmax(p_norm))
        conf_norm = float(p_norm[idx_norm])
        norm_preds.append(idx_norm)
        norm_confs.append(conf_norm)
        
        records.append({
            "image": Path(fpath).name,
            "filepath": str(fpath),
            "true_idx": true_idx,
            "true_class": true_class,
            "baseline_pred_idx": idx_base,
            "baseline_pred_class": CLASS_LABELS[idx_base],
            "baseline_conf": conf_base,
            "baseline_correct": (idx_base == true_idx),
            "norm_pred_idx": idx_norm,
            "norm_pred_class": CLASS_LABELS[idx_norm],
            "norm_conf": conf_norm,
            "norm_correct": (idx_norm == true_idx),
            "lighting_condition": q_info.get("illumination", {}).get("lighting_condition", "unknown"),
            "color_cast": q_info.get("illumination", {}).get("color_cast", "unknown")
        })
        
    df_results = pd.DataFrame(records)
    df_results.to_csv(OUTPUT_DIR / "test_predictions.csv", index=False)
    print(f"\n[4] Saved test_predictions.csv ({len(df_results)} rows)")
    
    # ─── Compute Metrics ──────────────────────────────────────────────────────────
    true_arr = np.array(true_labels[:len(records)])
    base_arr = np.array(baseline_preds)
    norm_arr = np.array(norm_preds)
    
    # Accuracy
    acc_base = accuracy_score(true_arr, base_arr)
    acc_norm = accuracy_score(true_arr, norm_arr)
    
    # Macro
    mp_base = precision_score(true_arr, base_arr, average='macro')
    mr_base = recall_score(true_arr, base_arr, average='macro')
    mf1_base = f1_score(true_arr, base_arr, average='macro')
    
    mp_norm = precision_score(true_arr, norm_arr, average='macro')
    mr_norm = recall_score(true_arr, norm_arr, average='macro')
    mf1_norm = f1_score(true_arr, norm_arr, average='macro')
    
    # Weighted
    wp_base = precision_score(true_arr, base_arr, average='weighted')
    wr_base = recall_score(true_arr, base_arr, average='weighted')
    wf1_base = f1_score(true_arr, base_arr, average='weighted')
    
    wp_norm = precision_score(true_arr, norm_arr, average='weighted')
    wr_norm = recall_score(true_arr, norm_arr, average='weighted')
    wf1_norm = f1_score(true_arr, norm_arr, average='weighted')
    
    # Per-class metrics
    rep_base_dict = classification_report(true_arr, base_arr, target_names=CLASS_LABELS, output_dict=True)
    rep_norm_dict = classification_report(true_arr, norm_arr, target_names=CLASS_LABELS, output_dict=True)
    
    # Save baseline metrics
    df_base_metrics = pd.DataFrame(rep_base_dict).transpose()
    df_base_metrics.to_csv(OUTPUT_DIR / "baseline_metrics.csv")
    
    # Save normalized metrics
    df_norm_metrics = pd.DataFrame(rep_norm_dict).transpose()
    df_norm_metrics.to_csv(OUTPUT_DIR / "normalized_metrics.csv")
    
    # Save classification report csv and txt (Illumination Normalized)
    df_norm_metrics.to_csv(OUTPUT_DIR / "classification_report.csv")
    with open(OUTPUT_DIR / "classification_report.txt", "w") as f:
        f.write(classification_report(true_arr, norm_arr, target_names=CLASS_LABELS, digits=4))
        
    # Save comparative table
    comp_data = [
        {"Metric": "Accuracy", "Baseline": round(acc_base * 100, 2), "Normalized": round(acc_norm * 100, 2), "Difference (% pts)": round((acc_norm - acc_base) * 100, 2)},
        {"Metric": "Macro Precision", "Baseline": round(mp_base * 100, 2), "Normalized": round(mp_norm * 100, 2), "Difference (% pts)": round((mp_norm - mp_base) * 100, 2)},
        {"Metric": "Macro Recall", "Baseline": round(mr_base * 100, 2), "Normalized": round(mr_norm * 100, 2), "Difference (% pts)": round((mr_norm - mr_base) * 100, 2)},
        {"Metric": "Macro F1-Score", "Baseline": round(mf1_base * 100, 2), "Normalized": round(mf1_norm * 100, 2), "Difference (% pts)": round((mf1_norm - mf1_base) * 100, 2)},
        {"Metric": "Weighted F1-Score", "Baseline": round(wf1_base * 100, 2), "Normalized": round(wf1_norm * 100, 2), "Difference (% pts)": round((wf1_norm - wf1_base) * 100, 2)},
    ]
    for c in CLASS_LABELS:
        f1_b = rep_base_dict[c]["f1-score"] * 100
        f1_n = rep_norm_dict[c]["f1-score"] * 100
        comp_data.append({
            "Metric": f"F1-Score ({c})",
            "Baseline": round(f1_b, 2),
            "Normalized": round(f1_n, 2),
            "Difference (% pts)": round(f1_n - f1_b, 2)
        })
    df_comp = pd.DataFrame(comp_data)
    df_comp.to_csv(OUTPUT_DIR / "illumination_comparison.csv", index=False)
    
    print("\n" + "=" * 70)
    print("  EMPIRICAL METRICS COMPARISON TABLE")
    print("=" * 70)
    print(df_comp.to_string(index=False))
    
    # ─── Confusion Matrices ───────────────────────────────────────────────────────
    cm_base = confusion_matrix(true_arr, base_arr)
    cm_norm = confusion_matrix(true_arr, norm_arr)
    
    # Plot Baseline Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_base, annot=True, fmt='d', cmap='Blues', xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS)
    plt.title(f'Baseline Model Confusion Matrix (Acc: {acc_base*100:.2f}%)', fontsize=12, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=10)
    plt.ylabel('True Label', fontsize=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "baseline_confusion_matrix.png", dpi=200)
    plt.close()
    
    # Plot Normalized Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_norm, annot=True, fmt='d', cmap='Greens', xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS)
    plt.title(f'Illumination-Normalized Confusion Matrix (Acc: {acc_norm*100:.2f}%)', fontsize=12, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=10)
    plt.ylabel('True Label', fontsize=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "normalized_confusion_matrix.png", dpi=200)
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=200) # Standard name
    plt.close()
    
    # ─── Confidence Distribution Analysis ─────────────────────────────────────────
    correct_confs = df_results[df_results["norm_correct"] == True]["norm_conf"]
    incorrect_confs = df_results[df_results["norm_correct"] == False]["norm_conf"]
    
    plt.figure(figsize=(10, 5))
    plt.hist(correct_confs, bins=30, alpha=0.7, label=f'Correct (N={len(correct_confs)}, Mean={correct_confs.mean():.3f})', color='green')
    if len(incorrect_confs) > 0:
        plt.hist(incorrect_confs, bins=30, alpha=0.7, label=f'Incorrect (N={len(incorrect_confs)}, Mean={incorrect_confs.mean():.3f})', color='red')
    plt.title('Prediction Confidence Distribution (Correct vs. Incorrect)', fontsize=12, fontweight='bold')
    plt.xlabel('Model Softmax Confidence', fontsize=10)
    plt.ylabel('Number of Samples', fontsize=10)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confidence_distribution.png", dpi=200)
    plt.close()
    
    # ─── Error Analysis ───────────────────────────────────────────────────────────
    df_errors = df_results[df_results["norm_correct"] == False][[
        "image", "true_class", "norm_pred_class", "norm_conf",
        "baseline_pred_class", "baseline_conf", "lighting_condition", "color_cast"
    ]]
    df_errors.to_csv(OUTPUT_DIR / "error_analysis.csv", index=False)
    print(f"\n[5] Saved error_analysis.csv ({len(df_errors)} errors detected out of {num_samples} samples)")
    print("=" * 70)
    print("  EVALUATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    main()
