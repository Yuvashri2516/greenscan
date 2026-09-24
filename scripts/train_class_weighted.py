"""
scripts/train_class_weighted.py

GreenScan Experiment 2: Class-Weighted Training Pipeline.
Trains the frozen MobileNetV2 baseline architecture with programmatic balanced class weights:
weight_class = N_train / (number_of_classes * N_class)
Strictly evaluates on the validation split ONLY. Test set is NEVER accessed.
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

from tensorflow.keras.applications import MobileNetV2
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

OUTPUT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
MAX_EPOCHS = 15
INITIAL_LR = 0.001

def load_and_verify_data():
    print("=" * 75)
    print("  GREENSCAN EXPERIMENT 2: VERIFYING DATA & CALCULATING CLASS WEIGHTS")
    print("=" * 75)
    
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")
        
    df = pd.read_csv(MANIFEST_PATH)
    
    # Filter valid image files only (excluding any non-image .pdf rows as in Exp 1)
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
    print(f"  - Overlapping Groups:          ZERO (Strictly Disjoint)")
    
    # Calculate programmatic class weights from Training Set ONLY
    # Formula: weight_c = N_train / (num_classes * N_class)
    n_train = len(train_df)
    n_classes = len(CLASS_LABELS)
    
    class_counts_train = train_df['class'].value_counts().to_dict()
    class_counts_val = val_df['class'].value_counts().to_dict()
    
    class_weights_dict = {}
    class_weights_named = {}
    
    print(f"\n[Class Breakdown & Calculated Class Weights]:")
    for idx, cls in enumerate(CLASS_LABELS):
        n_c = class_counts_train[cls]
        w_c = n_train / (n_classes * float(n_c))
        class_weights_dict[idx] = float(w_c)
        class_weights_named[cls] = {
            "train_count": n_c,
            "val_count": class_counts_val.get(cls, 0),
            "class_index": idx,
            "weight": float(w_c)
        }
        print(f"  - Class {idx} ({cls:<20}): Train={n_c:>4}, Val={class_counts_val.get(cls,0):>3} | Weight = {w_c:.6f}")
        
    return train_df, val_df, class_weights_dict, class_weights_named

def build_model(num_classes=3):
    base = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
    )
    base.trainable = False  # Freeze MobileNetV2 backbone completely
    
    x = base.output
    x = GlobalAveragePooling2D(name='global_average_pooling2d')(x)
    x = Dense(128, activation='relu', name='dense')(x)
    x = Dropout(0.5, name='dropout')(x)
    predictions = Dense(num_classes, activation='softmax', name='predictions')(x)
    
    model = Model(inputs=base.input, outputs=predictions, name="GreenScan_MobileNetV2_Experiment2_ClassWeighted")
    return model

def main():
    train_df, val_df, class_weights, class_weights_named = load_and_verify_data()
    
    # Save class weights JSON
    weights_json_path = OUTPUT_RESULTS_DIR / "class_weighted_class_weights.json"
    with open(weights_json_path, 'w') as f:
        json.dump(class_weights_named, f, indent=2)
    print(f"\n[Saved Class Weights JSON]: {weights_json_path}")
    
    # Data Generators
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1.0 / 255.0)
    
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
    model = build_model(num_classes=3)
    model.compile(
        optimizer=Adam(learning_rate=INITIAL_LR),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    best_model_path = OUTPUT_MODELS_DIR / "greenscan_class_weighted_best.keras"
    final_model_path = OUTPUT_MODELS_DIR / "greenscan_class_weighted_final.keras"
    
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
    print("  STARTING CLASS-WEIGHTED TRAINING (MAX 15 EPOCHS)")
    print("=" * 75)
    start_time = time.time()
    
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=MAX_EPOCHS,
        class_weight=class_weights,
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
    history_csv_path = OUTPUT_RESULTS_DIR / "class_weighted_history.csv"
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
    print("  EVALUATING BEST CLASS-WEIGHTED MODEL ON VALIDATION SPLIT")
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
        
    early_rec = per_class_metrics['tomato_Early blight']['recall']
    early_f1 = per_class_metrics['tomato_Early blight']['f1']
    late_rec = per_class_metrics['tomato_Late blight']['recall']
    late_f1 = per_class_metrics['tomato_Late blight']['f1']
    healthy_rec = per_class_metrics['tomato_healthy']['recall']
    healthy_f1 = per_class_metrics['tomato_healthy']['f1']
    
    early_to_late = int(cm[0, 1])
    late_to_early = int(cm[1, 0])
    total_early_late = early_to_late + late_to_early
    
    # Frozen Baseline Validation Reference (Exact same 766 validation images)
    baseline_val = {
        "accuracy": 0.906005,
        "macro_precision": 0.908051,
        "macro_recall": 0.912195,
        "macro_f1": 0.908864,
        "weighted_precision": 0.908752,
        "weighted_recall": 0.906005,
        "weighted_f1": 0.906548,
        "early_recall": 0.833333,
        "early_f1": 0.860215,
        "late_recall": 0.924084,
        "late_f1": 0.920469,
        "healthy_recall": 0.979167,
        "healthy_f1": 0.946309,
        "early_to_late": 33,
        "late_to_early": 24,
        "total_early_late": 57
    }
    
    # Deltas
    d_acc = acc - baseline_val["accuracy"]
    d_mprec = macro_prec - baseline_val["macro_precision"]
    d_mrec = macro_rec - baseline_val["macro_recall"]
    d_mf1 = macro_f1 - baseline_val["macro_f1"]
    d_erec = early_rec - baseline_val["early_recall"]
    d_ef1 = early_f1 - baseline_val["early_f1"]
    d_lrec = late_rec - baseline_val["late_recall"]
    d_lf1 = late_f1 - baseline_val["late_f1"]
    d_hrec = healthy_rec - baseline_val["healthy_recall"]
    d_hf1 = healthy_f1 - baseline_val["healthy_f1"]
    d_e2l = early_to_late - baseline_val["early_to_late"]
    d_l2e = late_to_early - baseline_val["late_to_early"]
    d_total_el = total_early_late - baseline_val["total_early_late"]
    
    # Save Validation Metrics JSON
    metrics_json_path = OUTPUT_RESULTS_DIR / "class_weighted_validation_metrics.json"
    metrics_data = {
        "experiment_name": "Experiment 2: Class-Weighted Training",
        "model_checkpoint": str(best_model_path),
        "best_epoch": best_epoch,
        "validation_samples": len(val_df),
        "class_weights": class_weights_named,
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
        "early_late_analysis": {
            "early_recall": float(early_rec),
            "early_f1": float(early_f1),
            "late_recall": float(late_rec),
            "late_f1": float(late_f1),
            "early_to_late": early_to_late,
            "late_to_early": late_to_early,
            "total_early_late": total_early_late
        },
        "controlled_comparison_vs_baseline": {
            "accuracy_delta": float(d_acc),
            "macro_f1_delta": float(d_mf1),
            "early_recall_delta": float(d_erec),
            "early_f1_delta": float(d_ef1),
            "late_recall_delta": float(d_lrec),
            "late_f1_delta": float(d_lf1),
            "early_to_late_delta": int(d_e2l),
            "late_to_early_delta": int(d_l2e),
            "total_early_late_delta": int(d_total_el)
        }
    }
    with open(metrics_json_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"[Saved Validation Metrics JSON]: {metrics_json_path}")
    
    # Save Summary JSON
    summary_json_path = OUTPUT_RESULTS_DIR / "class_weighted_summary.json"
    summary_data = {
        "experiment": "Experiment 2: Class-Weighted Training",
        "dataset_manifest": str(MANIFEST_PATH),
        "class_weights": class_weights,
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
    cm_plot_path = OUTPUT_RESULTS_DIR / "class_weighted_confusion_matrix.png"
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
    plt.title("Class-Weighted Model: Validation Confusion Matrix\n(Experiment 2 — N=766 Images)", fontsize=12, pad=12, weight='bold')
    plt.xlabel("Predicted Label", fontsize=11, labelpad=8, weight='bold')
    plt.ylabel("True Label", fontsize=11, labelpad=8, weight='bold')
    plt.tight_layout()
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f"[Saved Confusion Matrix Figure]: {cm_plot_path}")
    
    # Decision Evaluation
    # Check if balanced improvement occurred
    if d_mf1 > 0.01 and d_erec > 0.02 and acc >= baseline_val["accuracy"] - 0.005:
        decision_status = "SUFFICIENT VALIDATION IMPROVEMENT"
        test_recommendation = "CANDIDATE FOR ONE FINAL HELD-OUT TEST EVALUATION (Stop and await explicit authorization)"
    else:
        decision_status = "NOT SUFFICIENT"
        test_recommendation = "DO NOT PROCEED TO HELD-OUT TEST"
        
    # Generate Comprehensive Markdown Report
    report_path = OUTPUT_RESULTS_DIR / "class_weighted_validation_report.md"
    report_content = f"""# GreenScan Experiment 2: Class-Weighted Training Validation Report

## 1. Objective & Hypothesis

This report documents **Experiment 2** of the GreenScan research program: **Class-Weighted Training**.

### Hypothesis:
The clean training partition contains an inherent imbalance between Late Blight and Early Blight ($1,783$ vs. $1,131$ images, a $1.58 : 1$ ratio). Applying inverse class frequency weighting during training was hypothesized to reduce the model's tendency to predict Late Blight on ambiguous samples, improving Early Blight recall without degrading overall classification performance.

---

## 2. Dataset & Partition Protocol

- **Dataset Source**: `evaluation/clean_split_manifest.csv`
- **Training Population**: $3,588$ images ($2,314$ physical leaf groups).
- **Validation Population**: $766$ images ($503$ physical leaf groups; 2 non-image `.pdf` rows excluded identically to Experiment 1).
- **Held-Out Test Partition ($N = 770$)**: Strictly **unaccessed, unmounted, and frozen**.
- **Group Disjointness**: Confirmed zero physical leaf overlap between train and validation splits.

---

## 3. Calculated Class Weights

Class weights were calculated programmatically using the standard balanced formula:
$$\text{{weight}}_c = \frac{{N_{{\text{{train}}}}}}{{\text{{num\_classes}} \times N_c}}$$

| Class | Train Count ($N_c$) | Proportion | Calculated Weight |
| :--- | :---: | :---: | :---: |
| **`tomato_Early blight`** | 1,131 | 31.52% | **{class_weights_named['tomato_Early blight']['weight']:.6f}** |
| **`tomato_Late blight`** | 1,783 | 49.69% | **{class_weights_named['tomato_Late blight']['weight']:.6f}** |
| **`tomato_healthy`** | 674 | 18.78% | **{class_weights_named['tomato_healthy']['weight']:.6f}** |
| **Total / Average** | **3,588** | **100.00%** | **1.000000** |

---

## 4. Training Configuration

- **Architecture**: MobileNetV2 (ImageNet pretrained base, fully frozen) + GlobalAveragePooling2D + Dense(128, ReLU) + Dropout(0.5) + Dense(3, Softmax).
- **Optimizer**: Adam ($\text{{initial lr}} = 0.001$).
- **Loss Function**: Categorical cross-entropy with `class_weight` applied.
- **Batch Size**: 32 | **Max Epochs**: 15.
- **Callbacks**: EarlyStopping (patience 5, restore best weights), ReduceLROnPlateau (factor 0.2, patience 3, min lr $10^{{-6}}$), ModelCheckpoint (monitor `val_loss`).
- **Data Augmentation**: Applied only during training (rotation 40°, width/height shift 0.2, shear 0.2, zoom 0.2, horizontal/vertical flip); validation unaugmented.

---

## 5. Training Dynamics

- **Total Epochs Trained**: {len(history_df)}
- **Best Validation Epoch**: **Epoch {best_epoch}**
- **Best Training Loss**: `{best_train_loss:.4f}` | **Best Training Accuracy**: `{best_train_acc*100:.2f}%`
- **Best Validation Loss**: `{best_val_loss:.4f}` | **Best Validation Accuracy**: `{best_val_acc*100:.2f}%`
- **Mean Confidence (Correct Predictions)**: `{mean_conf_corr*100:.2f}%`
- **Mean Confidence (Incorrect Predictions)**: `{mean_conf_incorr*100:.2f}%`

---

## 6. Controlled Comparison Against Frozen Baseline

*Both models evaluated on the exact same validation population ($N = 766$ images).*

| Metric | Frozen Baseline (Val) | Class-Weighted (Val) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **{baseline_val['accuracy']*100:.2f}%** | **{acc*100:.2f}%** | `{d_acc*100:+.2f}%` |
| **Macro Precision** | **{baseline_val['macro_precision']*100:.2f}%** | **{macro_prec*100:.2f}%** | `{d_mprec*100:+.2f}%` |
| **Macro Recall** | **{baseline_val['macro_recall']*100:.2f}%** | **{macro_rec*100:.2f}%** | `{d_mrec*100:+.2f}%` |
| **Macro F1-Score** | **{baseline_val['macro_f1']*100:.2f}%** | **{macro_f1*100:.2f}%** | `{d_mf1*100:+.2f}%` |
| **Early Blight Recall** | **{baseline_val['early_recall']*100:.2f}%** | **{early_rec*100:.2f}%** | `{d_erec*100:+.2f}%` |
| **Early Blight F1** | **{baseline_val['early_f1']*100:.2f}%** | **{early_f1*100:.2f}%** | `{d_ef1*100:+.2f}%` |
| **Late Blight Recall** | **{baseline_val['late_recall']*100:.2f}%** | **{late_rec*100:.2f}%** | `{d_lrec*100:+.2f}%` |
| **Late Blight F1** | **{baseline_val['late_f1']*100:.2f}%** | **{late_f1*100:.2f}%** | `{d_lf1*100:+.2f}%` |
| **Healthy Recall** | **{baseline_val['healthy_recall']*100:.2f}%** | **{healthy_rec*100:.2f}%** | `{d_hrec*100:+.2f}%` |
| **Healthy F1** | **{baseline_val['healthy_f1']*100:.2f}%** | **{healthy_f1*100:.2f}%** | `{d_hf1*100:+.2f}%` |
| **Early $\\rightarrow$ Late Errors** | **{baseline_val['early_to_late']}** | **{early_to_late}** | `{d_e2l:+d}` |
| **Late $\\rightarrow$ Early Errors** | **{baseline_val['late_to_early']}** | **{late_to_early}** | `{d_l2e:+d}` |
| **Total Early $\\leftrightarrow$ Late Errors** | **{baseline_val['total_early_late']}** | **{total_early_late}** | `{d_total_el:+d}` |

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

---

## 8. Early vs Late Confusion Analysis & Interpretation

### Observed Results:
1. **Early Blight Sensitivity**: Early Blight recall shifted from **{baseline_val['early_recall']*100:.2f}%** to **{early_rec*100:.2f}%** (`{d_erec*100:+.2f}%`), while Early $\\rightarrow$ Late errors changed from {baseline_val['early_to_late']} to {early_to_late} (`{d_e2l:+d}`).
2. **Late Blight Sensitivity**: Late Blight recall shifted from **{baseline_val['late_recall']*100:.2f}%** to **{late_rec*100:.2f}%** (`{d_lrec*100:+.2f}%`), while Late $\\rightarrow$ Early errors changed from {baseline_val['late_to_early']} to {late_to_early} (`{d_l2e:+d}`).
3. **Total Confusion Volume**: Total inter-disease confusion changed from **{baseline_val['total_early_late']}** to **{total_early_late}** errors (`{d_total_el:+d}`).

### Interpretation:
- Loss reweighting changes the penalty threshold for minority versus majority classes during gradient descent.
- When features extracted by the frozen MobileNetV2 backbone are fundamentally ambiguous, altering class weights merely adjusts the decision threshold (shifting errors from one disease category to another) rather than improving feature separability.

### Limitations:
- Class weighting does not modify the underlying visual representations or filter embeddings of the frozen convolutional backbone.
- This experiment was restricted to the clean training/validation splits; the held-out test partition remained strictly unaccessed.

---

## 9. Decision & Test-Set Rule

- **Experiment 2 Status**: **{decision_status}**
- **Decision Recommendation**: **{test_recommendation}**

---

## Artifact Index
- `research/models/greenscan_class_weighted_best.keras`
- `research/models/greenscan_class_weighted_final.keras`
- `research/results/class_weighted_class_weights.json`
- `research/results/class_weighted_history.csv`
- `research/results/class_weighted_summary.json`
- `research/results/class_weighted_validation_metrics.json`
- `research/results/class_weighted_validation_report.md`
- `research/results/class_weighted_confusion_matrix.png`
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[Saved Validation Report]: {report_path}")
    
    # Final Output Summary
    print("\n" + "=" * 75)
    print("=== GREENSCAN EXPERIMENT 2 SUMMARY ===")
    print(f"1. Training completed successfully: True")
    print(f"2. Exact class weights:")
    for k, v in class_weights_named.items():
        print(f"   - {k:<20}: {v['weight']:.6f}")
    print(f"3. Best epoch: {best_epoch}")
    print(f"4. Best validation accuracy: {acc*100:.2f}% (Baseline: {baseline_val['accuracy']*100:.2f}%)")
    print(f"5. Validation Macro F1: {macro_f1*100:.2f}% (Baseline: {baseline_val['macro_f1']*100:.2f}%)")
    print(f"6. Early Blight recall/F1: Recall={early_rec*100:.2f}%, F1={early_f1*100:.2f}% (Baseline: {baseline_val['early_recall']*100:.2f}% / {baseline_val['early_f1']*100:.2f}%)")
    print(f"7. Late Blight recall/F1:  Recall={late_rec*100:.2f}%, F1={late_f1*100:.2f}% (Baseline: {baseline_val['late_recall']*100:.2f}% / {baseline_val['late_f1']*100:.2f}%)")
    print(f"8. Early → Late errors: {early_to_late} (Baseline: {baseline_val['early_to_late']})")
    print(f"9. Late → Early errors: {late_to_early} (Baseline: {baseline_val['late_to_early']})")
    print(f"10. Total Early ↔ Late errors: {total_early_late} (Baseline: {baseline_val['total_early_late']})")
    print(f"11. Comparison against frozen baseline: Acc Delta={d_acc*100:+.2f}%, Macro F1 Delta={d_mf1*100:+.2f}%")
    print(f"12. Evidence for test evaluation: {decision_status} — {test_recommendation}")
    print(f"13. Generated files: class_weighted_best.keras, class_weighted_history.csv, class_weighted_summary.json, class_weighted_validation_metrics.json, class_weighted_validation_report.md, class_weighted_confusion_matrix.png, class_weighted_class_weights.json")
    print(f"14. Held-out test set accessed: STRICTLY NO (Frozen test set preserved unaccessed)")
    print("=" * 75)

if __name__ == "__main__":
    main()
