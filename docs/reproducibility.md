# GreenScan — Research Reproducibility Guide

This document specifies the exact environment, data handling, training protocols, and execution scripts required to reproduce the GreenScan research benchmarks.

---

## 1. Software Environment & Dependencies

- **Operating System**: Windows 11 (64-bit) / Native Python virtual environment
- **Python Version**: `3.10+`
- **Deep Learning Framework**: `TensorFlow 2.21.0` / `Keras 3`
- **Key Python Libraries**:
  - `numpy==2.2.6`
  - `pandas==2.2.3`
  - `scikit-learn==1.7.0`
  - `opencv-python==4.11.0.86`
  - `matplotlib==3.10.0`
  - `seaborn==0.13.2`
- **Random Seed**: `42` (Fixed across Python `random`, `numpy.random`, `os.environ['PYTHONHASHSEED']`, and `tf.random.set_seed`).

---

## 2. Dataset Auditing & Group Stratification

### 2.1 Raw Population & Duplicate Audit
The initial raw dataset contained **5,137 original images** across three classes (`tomato_Early blight`, `tomato_Late blight`, `tomato_healthy`).
- **Exact Duplicate Audit**: SHA-256 cryptographic hash analysis identified **11 exact duplicate file pairs** (22 files total). Exactly 11 redundant copies were flagged as `excluded_duplicate` and removed from active splitting.
- **Active Curated Population**: **5,126 unique original images**.
- **Physical Leaf Identification**: Filename parsing and background masking signatures revealed that individual physical leaves were frequently photographed multiple times under different angles, zoom levels, and orientations (e.g., standard vs. masked pairs).
- **Leakage Prevention**: To eliminate optimistic bias from subject leakage, images were mapped into **3,328 physical leaf clusters**. Random splitting at the image level was strictly avoided.

### 2.2 Split Partitioning (70% Train / 15% Validation / 15% Held-Out Test)
Group-stratified splitting was conducted using [`evaluation/create_clean_split.py`](file:///c:/Greenscan%20project/evaluation/create_clean_split.py) with seed 42.

| Partition | Images ($N$) | Physical Leaf Groups | Split Proportion | Role in Research |
| :--- | :---: | :---: | :---: | :--- |
| **Train** | 3,588 | 2,314 | 70.00% | Model training with online augmentation |
| **Validation** | 766* | 503 | 14.94% | Model selection & hyperparameter comparison (Unaugmented) |
| **Held-Out Test** | 770 | 511 | 15.02% | Final unbiased benchmark (Frozen, evaluated once) |
| **Excluded Duplicates**| 11 | — | — | Removed from all splits |
| **Total Audited** | **5,137** | **3,328** | **100.00%** | Comprehensive audit |

*\*Note: 768 rows in manifest minus 2 legacy non-image `.pdf` rows filtered out across all experiment loaders.*

---

## 3. Model Architecture & Preprocessing

### Final Model: EfficientNetB0 Feature Extractor
- **Backbone**: `tf.keras.applications.EfficientNetB0(weights="imagenet", include_top=False, input_shape=(224, 224, 3))`
- **Backbone State**: Completely frozen (`trainable = False`, 4,049,571 non-trainable parameters).
- **Classification Head**:
  - `GlobalAveragePooling2D()`
  - `Dense(128, activation='relu')`
  - `Dropout(0.5)`
  - `Dense(3, activation='softmax')` (164,355 trainable parameters)
- **Preprocessing**: Native Keras EfficientNet normalization (raw $[0, 255]$ pixel values fed to model; internal `Rescaling(1./255)` and `Normalization` layers).
- **Online Training Augmentation**:
  - `rotation_range=40`
  - `width_shift_range=0.2`
  - `height_shift_range=0.2`
  - `shear_range=0.2`
  - `zoom_range=0.2`
  - `horizontal_flip=True`
  - `vertical_flip=True`
  - `fill_mode='nearest'`
- **Validation / Test Pipeline**: Strictly unaugmented, deterministic sequential loading.

---

## 4. Controlled Experiments Summary

| Phase | Script | Core Intervention | Validation Result | Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** | [`scripts/train_research_clean.py`](file:///c:/Greenscan%20project/scripts/train_research_clean.py) | Frozen MobileNetV2 ($224 \times 224$) | Val Acc: 90.60%, Macro F1: 90.89% | Baseline Established |
| **Exp 1** | [`scripts/train_experiment1_finetune.py`](file:///c:/Greenscan%20project/scripts/train_experiment1_finetune.py) | Partial MobileNetV2 fine-tuning (top 29 layers, lr $10^{-5}$) | Val Acc: 90.86%, Early Recall: 80.83% | Not Sufficient |
| **Exp 2** | [`scripts/train_class_weighted.py`](file:///c:/Greenscan%20project/scripts/train_class_weighted.py) | Programmatic class weights ($1.057, 0.671, 1.774$) | Val Acc: 89.95%, Early Recall: 83.75% | Not Sufficient |
| **Exp 3** | [`scripts/train_high_resolution.py`](file:///c:/Greenscan%20project/scripts/train_high_resolution.py) | Higher input resolution ($384 \times 384 \times 3$) | Val Acc: 89.82%, Early Recall: 82.92% | Not Sufficient |
| **Exp 4** | [`scripts/train_efficientnetb0.py`](file:///c:/Greenscan%20project/scripts/train_efficientnetb0.py) | Backbone substitution to EfficientNetB0 ($224 \times 224$) | Val Acc: 93.08%, Macro F1: 93.18% | **Selected for Test** |

---

## 5. Step-by-Step Reproduction Instructions

### Step 1: Create Dataset Manifest & Group Separation
```bash
python evaluation/create_clean_split.py
```

### Step 2: Train the Final EfficientNetB0 Model
```bash
python scripts/train_efficientnetb0.py
```
*Outputs saved to `research/models/greenscan_efficientnetb0_best.keras` and `research/results/efficientnetb0_summary.json`.*

### Step 3: Run the Final Held-Out Test Evaluation
```bash
python scripts/evaluate_efficientnetb0_test.py
```
*Evaluates the pre-selected checkpoint on the 770-image test set, outputting `research/results/efficientnetb0_held_out_test_metrics.json` and `research/results/efficientnetb0_held_out_test_predictions.csv`.*
