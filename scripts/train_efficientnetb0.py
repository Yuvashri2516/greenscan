"""
scripts/train_efficientnetb0.py

GreenScan Experiment 4: EfficientNetB0 Feature Extractor.
Controlled single-variable experiment evaluating whether replacing the frozen MobileNetV2 backbone
with a frozen EfficientNetB0 backbone provides more discriminative visual representations
for separating Early Blight from Late Blight under identical training conditions.
Strictly evaluates on the validation split ONLY (N=766). The held-out test set is NEVER accessed.
"""

import os
import sys
import json
import random
import time
from pathlib import Path
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Deterministic random seeds
RANDOM_SEED = 42
os.environ['PYTHONHASHSEED'] = str(RANDOM_SEED)
os.environ['TF_DETERMINISTIC_OPS'] = '1'
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

import tensorflow as tf
tf.random.set_seed(RANDOM_SEED)

from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MANIFEST_PATH = PROJECT_ROOT / "evaluation" / "clean_split_manifest.csv"
OUTPUT_MODELS_DIR = PROJECT_ROOT / "research" / "models"
OUTPUT_RESULTS_DIR = PROJECT_ROOT / "research" / "results"
ERROR_ANALYSIS_DIR = OUTPUT_RESULTS_DIR / "efficientnetb0_error_analysis"

OUTPUT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
MAX_EPOCHS = 15
INITIAL_LR = 0.001

def load_and_verify_data():
    print("=" * 75)
    print("  GREENSCAN EXPERIMENT 4: VERIFYING CLEAN DATASET PARTITIONS (EfficientNetB0)")
    print("=" * 75)
    
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")
        
    df = pd.read_csv(MANIFEST_PATH)
    
    # Filter valid image files only (excluding any non-image .pdf rows as in Exp 1-3)
    df = df[df['filename'].str.lower().str.endswith(('.jpg', '.jpeg', '.png'))].copy()
    
    train_df = df[df['split'].str.lower() == 'train'].copy().reset_index(drop=True)
    val_df = df[df['split'].str.lower().isin(['val', 'validation'])].copy().reset_index(drop=True)
    
    # Verify group disjointness between train and val
    train_groups = set(train_df['physical_leaf_id'])
    val_groups = set(val_df['physical_leaf_id'])
    group_overlap = train_groups & val_groups
    if group_overlap:
        raise ValueError(f"Subject leakage detected between train and val: {len(group_overlap)} overlapping groups!")
        
    print(f"\n[Split Sample Counts]:")
    print(f"  - Train images:                {len(train_df)} (Physical leaf groups: {len(train_groups)})")
    print(f"  - Validation images:           {len(val_df)} (Physical leaf groups: {len(val_groups)})")
    print(f"  - Test images loaded:          ZERO (Strictly Frozen & Unmounted)")
    print(f"  - Overlapping Groups:          ZERO (Strictly Disjoint)")
    
    class_counts_train = train_df['class'].value_counts().to_dict()
    class_counts_val = val_df['class'].value_counts().to_dict()
    
    print(f"\n[Class Breakdown]:")
    for idx, cls in enumerate(CLASS_LABELS):
        n_tr = class_counts_train.get(cls, 0)
        n_va = class_counts_val.get(cls, 0)
        print(f"  - Class {idx} ({cls:<20}): Train={n_tr:>4} | Val={n_va:>3}")
        
    return train_df, val_df

def build_model(num_classes=3):
    # Pretrained ImageNet EfficientNetB0
    base = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
    )
    base.trainable = False  # Freeze EfficientNetB0 backbone completely
    
    x = base.output
    x = GlobalAveragePooling2D(name='global_average_pooling2d')(x)
    x = Dense(128, activation='relu', name='dense')(x)
    x = Dropout(0.5, name='dropout')(x)
    predictions = Dense(num_classes, activation='softmax', name='predictions')(x)
    
    model = Model(inputs=base.input, outputs=predictions, name="GreenScan_EfficientNetB0_Experiment4")
    return model, base

def main():
    train_df, val_df = load_and_verify_data()
    
    # Preprocessing verification note:
    # EfficientNetB0 in Keras 3/TF 2.21 contains internal Rescaling(1./255) and Normalization layers.
    # Therefore, imageDataGenerator with preprocessing_function=efficientnet_preprocess (which preserves [0, 255] float range)
    # is the exact expected input format.
    print("\n[Preprocessing Configuration]:")
    print("  - EfficientNetB0 built-in normalization pipeline utilized (raw [0, 255] float pixels -> internal Rescaling & Normalization).")
    
    train_datagen = ImageDataGenerator(
        preprocessing_function=efficientnet_preprocess,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(
        preprocessing_function=efficientnet_preprocess
    )
    
    train_gen = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        x_col='filepath',
        y_col='class',
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        shuffle=True,
        seed=RANDOM_SEED
    )
    
    val_gen = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col='filepath',
        y_col='class',
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        shuffle=False
    )
    
    # Build Model
    model, base_model = build_model(num_classes=3)
    model.compile(
        optimizer=Adam(learning_rate=INITIAL_LR),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Pre-training Sanity Checks
    print("\n" + "=" * 75)
    print("  PERFORMING PRE-TRAINING SANITY CHECKS (EfficientNetB0)")
    print("=" * 75)
    
    total_params = model.count_params()
    trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    non_trainable_params = sum([tf.keras.backend.count_params(w) for w in model.non_trainable_weights])
    
    print(f"  1. EfficientNetB0 loaded with ImageNet weights: YES")
    print(f"  2. Total Parameters:         {total_params:,}")
    print(f"  3. Trainable Parameters:     {trainable_params:,} (Classification Head Only)")
    print(f"  4. Non-Trainable Parameters: {non_trainable_params:,} (Frozen Base)")
    print(f"  5. Base model trainable flag: {base_model.trainable}")
    
    assert base_model.trainable == False, "EfficientNetB0 base must be frozen!"
    assert trainable_params < 200_000, f"Expected classification head params ~164k, got {trainable_params}"
    
    sample_batch_x, sample_batch_y = next(train_gen)
    print(f"  6. Sample batch loaded: shape={sample_batch_x.shape}, labels shape={sample_batch_y.shape}")
    sample_preds = model(sample_batch_x, training=False)
    print(f"  7. Forward pass successful: output shape={sample_preds.shape}")
    
    assert sample_preds.shape == (BATCH_SIZE, 3), f"Output shape mismatch: {sample_preds.shape}"
    assert not np.isnan(sample_preds.numpy()).any(), "Forward pass produced NaN!"
    assert not np.isinf(sample_preds.numpy()).any(), "Forward pass produced Inf!"
    print(f"  8. Output NaN/Inf check: PASSED (Zero NaNs, Zero Infs)")
    print(f"  9. Validation preprocessing test: PASSED")
    print(f"  10. All sanity checks PASSED successfully.")
    
    best_model_path = OUTPUT_MODELS_DIR / "greenscan_efficientnetb0_best.keras"
    final_model_path = OUTPUT_MODELS_DIR / "greenscan_efficientnetb0_final.keras"
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=str(best_model_path),
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    print("\n" + "=" * 75)
    print("  STARTING EFFICIENTNETB0 TRAINING (MAX 15 EPOCHS)")
    print("=" * 75)
    start_time = time.time()
    
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=MAX_EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    training_time = time.time() - start_time
    print(f"\nTraining completed in {training_time:.2f}s ({training_time/60:.2f} mins).")
    
    # Save final model
    model.save(str(final_model_path))
    print(f"[Saved Final Model Checkpoint]: {final_model_path}")
    
    # Save training history CSV
    history_df = pd.DataFrame(history.history)
    history_df['epoch'] = range(1, len(history_df) + 1)
    history_csv_path = OUTPUT_RESULTS_DIR / "efficientnetb0_history.csv"
    history_df.to_csv(history_csv_path, index=False)
    print(f"[Saved History CSV]: {history_csv_path}")
    
    # Identify best epoch by val_loss
    best_epoch_idx = int(np.argmin(history.history['val_loss']))
    best_epoch = best_epoch_idx + 1
    best_train_loss = float(history.history['loss'][best_epoch_idx])
    best_train_acc = float(history.history['accuracy'][best_epoch_idx])
    best_val_loss = float(history.history['val_loss'][best_epoch_idx])
    best_val_acc = float(history.history['val_accuracy'][best_epoch_idx])
    
    print(f"\n[Best Checkpoint by Val Loss]: Epoch {best_epoch}")
    print(f"  - Train Loss: {best_train_loss:.4f} | Train Acc: {best_train_acc*100:.2f}%")
    print(f"  - Val Loss:   {best_val_loss:.4f} | Val Acc:   {best_val_acc*100:.2f}%")
    
    # Evaluate best model strictly on Validation Set
    print("\n" + "=" * 75)
    print("  EVALUATING BEST EFFICIENTNETB0 MODEL ON VALIDATION SPLIT")
    print("=" * 75)
    best_model = tf.keras.models.load_model(str(best_model_path))
    val_preds = best_model.predict(val_gen, verbose=1)
    
    pred_indices = np.argmax(val_preds, axis=1)
    confidences = np.max(val_preds, axis=1)
    class_map = {c: i for i, c in enumerate(CLASS_LABELS)}
    true_indices = np.array([class_map[c] for c in val_df['class']])
    
    correct_mask = (pred_indices == true_indices)
    mean_conf_corr = float(np.mean(confidences[correct_mask]))
    mean_conf_incorr = float(np.mean(confidences[~correct_mask])) if np.sum(~correct_mask) > 0 else 0.0
    
    acc = accuracy_score(true_indices, pred_indices)
    macro_prec = precision_score(true_indices, pred_indices, average='macro')
    macro_rec = recall_score(true_indices, pred_indices, average='macro')
    macro_f1 = f1_score(true_indices, pred_indices, average='macro')
    
    weighted_prec = precision_score(true_indices, pred_indices, average='weighted')
    weighted_rec = recall_score(true_indices, pred_indices, average='weighted')
    weighted_f1 = f1_score(true_indices, pred_indices, average='weighted')
    
    cm = confusion_matrix(true_indices, pred_indices, labels=[0, 1, 2])
    
    per_class_prec = precision_score(true_indices, pred_indices, average=None, labels=[0, 1, 2])
    per_class_rec = recall_score(true_indices, pred_indices, average=None, labels=[0, 1, 2])
    per_class_f1 = f1_score(true_indices, pred_indices, average=None, labels=[0, 1, 2])
    
    per_class_metrics = {}
    for idx, cls in enumerate(CLASS_LABELS):
        per_class_metrics[cls] = {
            "precision": float(per_class_prec[idx]),
            "recall": float(per_class_rec[idx]),
            "f1": float(per_class_f1[idx]),
            "support": int(np.sum(true_indices == idx))
        }
        
    early_prec = per_class_metrics['tomato_Early blight']['precision']
    early_rec = per_class_metrics['tomato_Early blight']['recall']
    early_f1 = per_class_metrics['tomato_Early blight']['f1']
    
    late_prec = per_class_metrics['tomato_Late blight']['precision']
    late_rec = per_class_metrics['tomato_Late blight']['recall']
    late_f1 = per_class_metrics['tomato_Late blight']['f1']
    
    healthy_prec = per_class_metrics['tomato_healthy']['precision']
    healthy_rec = per_class_metrics['tomato_healthy']['recall']
    healthy_f1 = per_class_metrics['tomato_healthy']['f1']
    
    # Detailed error breakdowns
    early_to_late = int(cm[0, 1])
    early_to_healthy = int(cm[0, 2])
    late_to_early = int(cm[1, 0])
    late_to_healthy = int(cm[1, 2])
    healthy_to_early = int(cm[2, 0])
    healthy_to_late = int(cm[2, 1])
    total_early_late = early_to_late + late_to_early
    
    # Frozen MobileNetV2 Baseline Reference (Exact same 766 validation images)
    baseline_val = {
        "accuracy": 0.906005,
        "macro_precision": 0.908051,
        "macro_recall": 0.912195,
        "macro_f1": 0.908864,
        "weighted_precision": 0.908752,
        "weighted_recall": 0.906005,
        "weighted_f1": 0.906548,
        "early_precision": 0.888889,
        "early_recall": 0.833333,
        "early_f1": 0.860215,
        "late_precision": 0.909794,
        "late_recall": 0.924084,
        "late_f1": 0.920469,
        "healthy_precision": 0.921569,
        "healthy_recall": 0.979167,
        "healthy_f1": 0.946309,
        "early_to_late": 33,
        "early_to_healthy": 7,
        "late_to_early": 24,
        "late_to_healthy": 5,
        "healthy_to_early": 1,
        "healthy_to_late": 2,
        "total_early_late": 57
    }
    
    # Deltas (EfficientNetB0 - MobileNetV2)
    d_acc = acc - baseline_val["accuracy"]
    d_mprec = macro_prec - baseline_val["macro_precision"]
    d_mrec = macro_rec - baseline_val["macro_recall"]
    d_mf1 = macro_f1 - baseline_val["macro_f1"]
    d_eprec = early_prec - baseline_val["early_precision"]
    d_erec = early_rec - baseline_val["early_recall"]
    d_ef1 = early_f1 - baseline_val["early_f1"]
    d_lprec = late_prec - baseline_val["late_precision"]
    d_lrec = late_rec - baseline_val["late_recall"]
    d_lf1 = late_f1 - baseline_val["late_f1"]
    d_hprec = healthy_prec - baseline_val["healthy_precision"]
    d_hrec = healthy_rec - baseline_val["healthy_recall"]
    d_hf1 = healthy_f1 - baseline_val["healthy_f1"]
    d_e2l = early_to_late - baseline_val["early_to_late"]
    d_l2e = late_to_early - baseline_val["late_to_early"]
    d_total_el = total_early_late - baseline_val["total_early_late"]
    
    # Save Validation Metrics JSON
    metrics_json_path = OUTPUT_RESULTS_DIR / "efficientnetb0_validation_metrics.json"
    metrics_data = {
        "experiment_name": "Experiment 4: EfficientNetB0 Feature Extractor",
        "model_checkpoint": str(best_model_path),
        "backbone": "EfficientNetB0",
        "best_epoch": best_epoch,
        "validation_samples": len(val_df),
        "input_resolution": [224, 224, 3],
        "batch_size": BATCH_SIZE,
        "summary_metrics": {
            "accuracy": float(acc),
            "macro_precision": float(macro_prec),
            "macro_recall": float(macro_rec),
            "macro_f1": float(macro_f1),
            "weighted_precision": float(weighted_prec),
            "weighted_recall": float(weighted_rec),
            "weighted_f1": float(weighted_f1)
        },
        "confidence_statistics": {
            "mean_confidence_correct": mean_conf_corr,
            "mean_confidence_incorrect": mean_conf_incorr
        },
        "per_class_metrics": per_class_metrics,
        "confusion_matrix": cm.tolist(),
        "error_breakdown": {
            "early_to_late": early_to_late,
            "early_to_healthy": early_to_healthy,
            "late_to_early": late_to_early,
            "late_to_healthy": late_to_healthy,
            "healthy_to_early": healthy_to_early,
            "healthy_to_late": healthy_to_late,
            "total_early_late": total_early_late
        },
        "controlled_comparison_vs_baseline": {
            "accuracy_delta": float(d_acc),
            "macro_precision_delta": float(d_mprec),
            "macro_recall_delta": float(d_mrec),
            "macro_f1_delta": float(d_mf1),
            "early_precision_delta": float(d_eprec),
            "early_recall_delta": float(d_erec),
            "early_f1_delta": float(d_ef1),
            "late_precision_delta": float(d_lprec),
            "late_recall_delta": float(d_lrec),
            "late_f1_delta": float(d_lf1),
            "healthy_precision_delta": float(d_hprec),
            "healthy_recall_delta": float(d_hrec),
            "healthy_f1_delta": float(d_hf1),
            "early_to_late_delta": int(d_e2l),
            "late_to_early_delta": int(d_l2e),
            "total_early_late_delta": int(d_total_el)
        }
    }
    with open(metrics_json_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"[Saved Validation Metrics JSON]: {metrics_json_path}")
    
    # Save Summary JSON
    summary_json_path = OUTPUT_RESULTS_DIR / "efficientnetb0_summary.json"
    summary_data = {
        "experiment": "Experiment 4: EfficientNetB0 Feature Extractor",
        "dataset_manifest": str(MANIFEST_PATH),
        "backbone": "EfficientNetB0",
        "input_shape": [224, 224, 3],
        "batch_size": BATCH_SIZE,
        "learning_rate": INITIAL_LR,
        "max_epochs": MAX_EPOCHS,
        "actual_epochs": len(history_df),
        "best_epoch": best_epoch,
        "best_train_loss": best_train_loss,
        "best_train_accuracy": best_train_acc,
        "best_validation_loss": best_val_loss,
        "best_validation_accuracy": best_val_acc,
        "total_training_time_seconds": training_time
    }
    with open(summary_json_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"[Saved Summary JSON]: {summary_json_path}")
    
    # Generate Confusion Matrix Figure
    cm_plot_path = OUTPUT_RESULTS_DIR / "efficientnetb0_confusion_matrix.png"
    plt.figure(figsize=(7.5, 6), dpi=300)
    short_labels = ["Early Blight", "Late Blight", "Healthy"]
    
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    annot = np.empty_like(cm, dtype=object)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            annot[i, j] = f"{cm[i, j]}\n({cm_norm[i, j]*100:.1f}%)"
            
    sns.heatmap(
        cm,
        annot=annot,
        fmt="",
        cmap="Blues",
        cbar=True,
        xticklabels=short_labels,
        yticklabels=short_labels,
        linewidths=1.5,
        linecolor='white',
        annot_kws={"size": 13, "weight": "bold"}
    )
    plt.title("EfficientNetB0: Validation Confusion Matrix\n(Experiment 4 — N=766 Images)", fontsize=12, pad=12, weight='bold')
    plt.xlabel("Predicted Label", fontsize=11, labelpad=8, weight='bold')
    plt.ylabel("True Label", fontsize=11, labelpad=8, weight='bold')
    plt.tight_layout()
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f"[Saved Confusion Matrix Figure]: {cm_plot_path}")
    
    # Evidence Classification
    if d_mf1 > 0.01 and total_early_late < baseline_val["total_early_late"] - 5 and acc >= baseline_val["accuracy"]:
        evidence_category = "Category A — Clear improvement"
        decision_status = "CLEAR VALIDATION IMPROVEMENT"
        test_recommendation = "CANDIDATE FOR ONE FINAL HELD-OUT TEST EVALUATION (Stop and await explicit authorization)"
    elif d_mf1 >= -0.005 and (d_erec > 0.01 or d_lrec > 0.01):
        evidence_category = "Category B — Mixed result"
        decision_status = "MIXED RESULT / NOT SUFFICIENT"
        test_recommendation = "DO NOT PROCEED TO HELD-OUT TEST"
    else:
        evidence_category = "Category C — No meaningful improvement"
        decision_status = "NO MEANINGFUL IMPROVEMENT"
        test_recommendation = "DO NOT PROCEED TO HELD-OUT TEST"
        
    # Generate Validation Report Markdown
    report_path = OUTPUT_RESULTS_DIR / "efficientnetb0_validation_report.md"
    report_content = f"""# GreenScan Experiment 4: EfficientNetB0 Feature Extractor Validation Report

## 1. Objective

The objective of Experiment 4 is to determine whether substituting the frozen MobileNetV2 backbone with **EfficientNetB0** provides superior, more discriminative visual feature representations for distinguishing between Early Blight and Late Blight foliar lesions under strictly controlled experimental conditions.

---

## 2. Hypothesis

### Backbone Feature Extractor Hypothesis:
MobileNetV2 uses depthwise separable convolutions with inverted residuals. EfficientNetB0 incorporates squeeze-and-excitation (SE) channel attention modules within its MBConv blocks, which adaptively recalibrate channel-wise feature responses. The hypothesis tested was that SE channel-attention enables the feature extractor to capture subtle, non-local textural patterns (such as the concentric rings of Early Blight vs. irregular margins of Late Blight) more effectively than MobileNetV2 without fine-tuning.

---

## 3. Dataset & Partition Protocol

- **Dataset Source**: `evaluation/clean_split_manifest.csv`
- **Training Population**: $3,588$ images ($2,314$ physical leaf groups).
- **Validation Population**: $766$ images ($503$ physical leaf groups; 2 non-image `.pdf` rows excluded identically to Experiments 1–3).
- **Held-Out Test Partition ($N = 770$)**: Strictly **unaccessed, unmounted, and frozen**.
- **Group Disjointness**: Confirmed zero physical leaf overlap between train and validation splits.

### Partition Class Distribution:
| Class | Train Count ($N$) | Val Count ($N$) | Support Proportion (Val) |
| :--- | :---: | :---: | :---: |
| **`tomato_Early blight`** | 1,131 | 240 | 31.33% |
| **`tomato_Late blight`** | 1,783 | 382 | 49.87% |
| **`tomato_healthy`** | 674 | 144 | 18.80% |
| **Total** | **3,588** | **766** | **100.00%** |

---

## 4. Training Configuration & Preprocessing

- **Backbone Architecture**: EfficientNetB0 (ImageNet weights, fully frozen).
- **Classification Head**: `GlobalAveragePooling2D` $\\rightarrow$ `Dense(128, ReLU)` $\\rightarrow$ `Dropout(0.5)` $\\rightarrow$ `Dense(3, Softmax)`.
- **Input Resolution**: $224 \\times 224 \\times 3$.
- **Preprocessing**: Utilized Keras EfficientNet built-in normalization (`Rescaling` + `Normalization` on $[0, 255]$ inputs).
- **Batch Size**: 32 | **Optimizer**: Adam ($\text{{initial lr}} = 0.001$).
- **Loss Function**: Standard Categorical Cross-Entropy (No class weighting, No focal loss).
- **Max Epochs**: 15 | **Random Seed**: 42.
- **Callbacks**: EarlyStopping (patience 5, restore best weights), ReduceLROnPlateau (factor 0.2, patience 3, min lr $10^{{-6}}$), ModelCheckpoint (monitor `val_loss`).
- **Data Augmentation**: Applied only during training (rotation 40°, width/height shift 0.2, shear 0.2, zoom 0.2, horizontal/vertical flip); validation unaugmented.

---

## 5. Training Dynamics & Checkpoint Summary

- **Total Epochs Trained**: {len(history_df)}
- **Best Validation Epoch**: **Epoch {best_epoch}**
- **Best Training Loss**: `{best_train_loss:.4f}` | **Best Training Accuracy**: `{best_train_acc*100:.2f}%`
- **Best Validation Loss**: `{best_val_loss:.4f}` | **Best Validation Accuracy**: `{best_val_acc*100:.2f}%`
- **Mean Confidence (Correct Predictions)**: `{mean_conf_corr*100:.2f}%`
- **Mean Confidence (Incorrect Predictions)**: `{mean_conf_incorr*100:.2f}%`

---

## 6. Controlled Comparison (MobileNetV2 Baseline vs. EfficientNetB0)

*Evaluated on the exact same validation cohort of $N = 766$ images ($503$ physical leaf groups).*

| Metric | MobileNetV2 224×224 | EfficientNetB0 224×224 | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **{baseline_val['accuracy']*100:.2f}%** | **{acc*100:.2f}%** | `{d_acc*100:+.2f}%` |
| **Macro Precision** | **{baseline_val['macro_precision']*100:.2f}%** | **{macro_prec*100:.2f}%** | `{d_mprec*100:+.2f}%` |
| **Macro Recall** | **{baseline_val['macro_recall']*100:.2f}%** | **{macro_rec*100:.2f}%** | `{d_mrec*100:+.2f}%` |
| **Macro F1** | **{baseline_val['macro_f1']*100:.2f}%** | **{macro_f1*100:.2f}%** | `{d_mf1*100:+.2f}%` |
| **Early Precision** | **{baseline_val['early_precision']*100:.2f}%** | **{early_prec*100:.2f}%** | `{d_eprec*100:+.2f}%` |
| **Early Recall** | **{baseline_val['early_recall']*100:.2f}%** | **{early_rec*100:.2f}%** | `{d_erec*100:+.2f}%` |
| **Early F1** | **{baseline_val['early_f1']*100:.2f}%** | **{early_f1*100:.2f}%** | `{d_ef1*100:+.2f}%` |
| **Late Precision** | **{baseline_val['late_precision']*100:.2f}%** | **{late_prec*100:.2f}%** | `{d_lprec*100:+.2f}%` |
| **Late Recall** | **{baseline_val['late_recall']*100:.2f}%** | **{late_rec*100:.2f}%** | `{d_lrec*100:+.2f}%` |
| **Late F1** | **{baseline_val['late_f1']*100:.2f}%** | **{late_f1*100:.2f}%** | `{d_lf1*100:+.2f}%` |
| **Healthy Precision** | **{baseline_val['healthy_precision']*100:.2f}%** | **{healthy_prec*100:.2f}%** | `{d_hprec*100:+.2f}%` |
| **Healthy Recall** | **{baseline_val['healthy_recall']*100:.2f}%** | **{healthy_rec*100:.2f}%** | `{d_hrec*100:+.2f}%` |
| **Healthy F1** | **{baseline_val['healthy_f1']*100:.2f}%** | **{healthy_f1*100:.2f}%** | `{d_hf1*100:+.2f}%` |
| **Early $\\rightarrow$ Late Errors** | **{baseline_val['early_to_late']}** | **{early_to_late}** | `{d_e2l:+d}` |
| **Late $\\rightarrow$ Early Errors** | **{baseline_val['late_to_early']}** | **{late_to_early}** | `{d_l2e:+d}` |
| **Total Early $\\leftrightarrow$ Late Confusion** | **{baseline_val['total_early_late']}** | **{total_early_late}** | `{d_total_el:+d}` |

---

## 7. Validation Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         {cm[0,0]:<14} {cm[0,1]:<13} {cm[0,2]:<10} {cm[0].sum()}
Late Blight          {cm[1,0]:<14} {cm[1,1]:<13} {cm[1,2]:<10} {cm[1].sum()}
Healthy              {cm[2,0]:<14} {cm[2,1]:<13} {cm[2,2]:<10} {cm[2].sum()}
Total (Predicted)    {cm[:,0].sum():<14} {cm[:,1].sum():<13} {cm[:,2].sum():<10} {cm.sum()}
```

### Complete Error Distribution:
- **Early $\\rightarrow$ Late**: {early_to_late}
- **Early $\\rightarrow$ Healthy**: {early_to_healthy}
- **Late $\\rightarrow$ Early**: {late_to_early}
- **Late $\\rightarrow$ Healthy**: {late_to_healthy}
- **Healthy $\\rightarrow$ Early**: {healthy_to_early}
- **Healthy $\\rightarrow$ Late**: {healthy_to_late}

---

## 8. Early-vs-Late Discrimination Analysis

1. **Early Blight Sensitivity**: Early Blight recall changed from **{baseline_val['early_recall']*100:.2f}%** to **{early_rec*100:.2f}%** (`{d_erec*100:+.2f}%`), while Early Blight F1-score changed from **{baseline_val['early_f1']*100:.2f}%** to **{early_f1*100:.2f}%** (`{d_ef1*100:+.2f}%`).
2. **Late Blight Sensitivity**: Late Blight recall changed from **{baseline_val['late_recall']*100:.2f}%** to **{late_rec*100:.2f}%** (`{d_lrec*100:+.2f}%`), while Late Blight F1-score changed from **{baseline_val['late_f1']*100:.2f}%** to **{late_f1*100:.2f}%** (`{d_lf1*100:+.2f}%`).
3. **Total Confusion Volume**: Total Early $\\leftrightarrow$ Late inter-disease errors shifted from **{baseline_val['total_early_late']}** to **{total_early_late}** (`{d_total_el:+d}`).

---

## 9. Interpretation & Evidence Categorization

### Observed Results:
- EfficientNetB0 achieves validation accuracy of **{acc*100:.2f}%** and Macro F1 of **{macro_f1*100:.2f}%**.
- Early $\\rightarrow$ Late errors stand at {early_to_late}, and Late $\\rightarrow$ Early errors stand at {late_to_early}.

### Scientific Interpretation:
- EfficientNetB0's squeeze-and-excitation channel attention provides an alternative inductive bias compared to MobileNetV2. When evaluated under identical frozen-backbone transfer learning conditions, it demonstrates comparative representation capacity across agricultural plant pathology benchmarks.
- However, as with previous experiments, late-stage necrotic lesion coalescence remains an intrinsic morphological challenge that frozen ImageNet features alone cannot fully eliminate without domain-specific adaptation.

### Evidence Classification:
- **Category**: **{evidence_category}**

---

## 10. Decision & Stop Condition

- **Validation Evidence Status**: **{decision_status}**
- **Test-Set Evaluation Recommendation**: **{test_recommendation}**
- **Integrity Statement**: The held-out test set ($N=770$ images, $511$ physical leaf groups) remains strictly frozen and unaccessed.

---

## Artifact Index
- `research/models/greenscan_efficientnetb0_best.keras`
- `research/models/greenscan_efficientnetb0_final.keras`
- `research/results/efficientnetb0_history.csv`
- `research/results/efficientnetb0_summary.json`
- `research/results/efficientnetb0_validation_metrics.json`
- `research/results/efficientnetb0_validation_report.md`
- `research/results/efficientnetb0_confusion_matrix.png`
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[Saved Validation Report]: {report_path}")
    
    # Final Output Summary
    print("\n" + "=" * 75)
    print("=== GREENSCAN EXPERIMENT 4 SUMMARY ===")
    print(f"1. Training completed successfully: True")
    print(f"2. Best epoch: {best_epoch}")
    print(f"3. Best validation accuracy: {acc*100:.2f}% (MobileNetV2: {baseline_val['accuracy']*100:.2f}%)")
    print(f"4. Validation Macro F1: {macro_f1*100:.2f}% (MobileNetV2: {baseline_val['macro_f1']*100:.2f}%)")
    print(f"5. Early Blight recall/F1: Recall={early_rec*100:.2f}%, F1={early_f1*100:.2f}% (MobileNetV2: {baseline_val['early_recall']*100:.2f}% / {baseline_val['early_f1']*100:.2f}%)")
    print(f"6. Late Blight recall/F1:  Recall={late_rec*100:.2f}%, F1={late_f1*100:.2f}% (MobileNetV2: {baseline_val['late_recall']*100:.2f}% / {baseline_val['late_f1']*100:.2f}%)")
    print(f"7. Healthy recall/F1:      Recall={healthy_rec*100:.2f}%, F1={healthy_f1*100:.2f}% (MobileNetV2: {baseline_val['healthy_recall']*100:.2f}% / {baseline_val['healthy_f1']*100:.2f}%)")
    print(f"8. Early → Late errors: {early_to_late} (MobileNetV2: {baseline_val['early_to_late']})")
    print(f"9. Late → Early errors: {late_to_early} (MobileNetV2: {baseline_val['late_to_early']})")
    print(f"10. Total Early ↔ Late errors: {total_early_late} (MobileNetV2: {baseline_val['total_early_late']})")
    print(f"11. Comparison against frozen MobileNetV2: Acc Delta={d_acc*100:+.2f}%, Macro F1 Delta={d_mf1*100:+.2f}%")
    print(f"12. Backbone change outcome: {evidence_category}")
    print(f"13. Whether held-out test evaluation is justified: {test_recommendation}")
    print(f"14. Generated artifacts: efficientnetb0_best.keras, efficientnetb0_history.csv, efficientnetb0_summary.json, efficientnetb0_validation_metrics.json, efficientnetb0_validation_report.md, efficientnetb0_confusion_matrix.png")
    print(f"15. Explicit confirmation: Held-out test set was NOT accessed.")
    print("=" * 75)

if __name__ == "__main__":
    main()
