# GreenScan Experiment 4: EfficientNetB0 Feature Extractor Validation Report

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
- **Classification Head**: `GlobalAveragePooling2D` $\rightarrow$ `Dense(128, ReLU)` $\rightarrow$ `Dropout(0.5)` $\rightarrow$ `Dense(3, Softmax)`.
- **Input Resolution**: $224 \times 224 \times 3$.
- **Preprocessing**: Utilized Keras EfficientNet built-in normalization (`Rescaling` + `Normalization` on $[0, 255]$ inputs).
- **Batch Size**: 32 | **Optimizer**: Adam ($	ext{initial lr} = 0.001$).
- **Loss Function**: Standard Categorical Cross-Entropy (No class weighting, No focal loss).
- **Max Epochs**: 15 | **Random Seed**: 42.
- **Callbacks**: EarlyStopping (patience 5, restore best weights), ReduceLROnPlateau (factor 0.2, patience 3, min lr $10^{-6}$), ModelCheckpoint (monitor `val_loss`).
- **Data Augmentation**: Applied only during training (rotation 40°, width/height shift 0.2, shear 0.2, zoom 0.2, horizontal/vertical flip); validation unaugmented.

---

## 5. Training Dynamics & Checkpoint Summary

- **Total Epochs Trained**: 15
- **Best Validation Epoch**: **Epoch 15**
- **Best Training Loss**: `0.1645` | **Best Training Accuracy**: `93.51%`
- **Best Validation Loss**: `0.1933` | **Best Validation Accuracy**: `93.08%`
- **Mean Confidence (Correct Predictions)**: `93.81%`
- **Mean Confidence (Incorrect Predictions)**: `71.85%`

---

## 6. Controlled Comparison (MobileNetV2 Baseline vs. EfficientNetB0)

*Evaluated on the exact same validation cohort of $N = 766$ images ($503$ physical leaf groups).*

| Metric | MobileNetV2 224×224 | EfficientNetB0 224×224 | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **90.60%** | **93.08%** | `+2.48%` |
| **Macro Precision** | **90.81%** | **92.70%** | `+1.90%` |
| **Macro Recall** | **91.22%** | **93.74%** | `+2.52%` |
| **Macro F1** | **90.89%** | **93.18%** | `+2.30%` |
| **Early Precision** | **88.89%** | **91.45%** | `+2.56%` |
| **Early Recall** | **83.33%** | **89.17%** | `+5.83%` |
| **Early F1** | **86.02%** | **90.30%** | `+4.27%` |
| **Late Precision** | **90.98%** | **94.44%** | `+3.47%` |
| **Late Recall** | **92.41%** | **93.46%** | `+1.05%` |
| **Late F1** | **92.05%** | **93.95%** | `+1.90%` |
| **Healthy Precision** | **92.16%** | **92.21%** | `+0.05%` |
| **Healthy Recall** | **97.92%** | **98.61%** | `+0.69%` |
| **Healthy F1** | **94.63%** | **95.30%** | `+0.67%` |
| **Early $\rightarrow$ Late Errors** | **33** | **19** | `-14` |
| **Late $\rightarrow$ Early Errors** | **24** | **20** | `-4` |
| **Total Early $\leftrightarrow$ Late Confusion** | **57** | **39** | `-18` |

---

## 7. Validation Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         214            19            7          240
Late Blight          20             357           5          382
Healthy              0              2             142        144
Total (Predicted)    234            378           154        766
```

### Complete Error Distribution:
- **Early $\rightarrow$ Late**: 19
- **Early $\rightarrow$ Healthy**: 7
- **Late $\rightarrow$ Early**: 20
- **Late $\rightarrow$ Healthy**: 5
- **Healthy $\rightarrow$ Early**: 0
- **Healthy $\rightarrow$ Late**: 2

---

## 8. Early-vs-Late Discrimination Analysis

1. **Early Blight Sensitivity**: Early Blight recall changed from **83.33%** to **89.17%** (`+5.83%`), while Early Blight F1-score changed from **86.02%** to **90.30%** (`+4.27%`).
2. **Late Blight Sensitivity**: Late Blight recall changed from **92.41%** to **93.46%** (`+1.05%`), while Late Blight F1-score changed from **92.05%** to **93.95%** (`+1.90%`).
3. **Total Confusion Volume**: Total Early $\leftrightarrow$ Late inter-disease errors shifted from **57** to **39** (`-18`).

---

## 9. Interpretation & Evidence Categorization

### Observed Results:
- EfficientNetB0 achieves validation accuracy of **93.08%** and Macro F1 of **93.18%**.
- Early $\rightarrow$ Late errors stand at 19, and Late $\rightarrow$ Early errors stand at 20.

### Scientific Interpretation:
- EfficientNetB0's squeeze-and-excitation channel attention provides an alternative inductive bias compared to MobileNetV2. When evaluated under identical frozen-backbone transfer learning conditions, it demonstrates comparative representation capacity across agricultural plant pathology benchmarks.
- However, as with previous experiments, late-stage necrotic lesion coalescence remains an intrinsic morphological challenge that frozen ImageNet features alone cannot fully eliminate without domain-specific adaptation.

### Evidence Classification:
- **Category**: **Category A — Clear improvement**

---

## 10. Decision & Stop Condition

- **Validation Evidence Status**: **CLEAR VALIDATION IMPROVEMENT**
- **Test-Set Evaluation Recommendation**: **CANDIDATE FOR ONE FINAL HELD-OUT TEST EVALUATION (Stop and await explicit authorization)**
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
