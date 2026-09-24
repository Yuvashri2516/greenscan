# GreenScan — Final Research Model Freeze Record

**Freeze Date / Timestamp**: 2026-09-24T09:34:18.736902  
**Status**: **STRICTLY FROZEN**  

---

## 1. Final Model Specification

- **Architecture**: `EfficientNetB0` (Pretrained on ImageNet, fully frozen backbone) + Custom Classification Head
- **Classification Head**:
  ```text
  GlobalAveragePooling2D
  Dense(128, activation="relu")
  Dropout(0.5)
  Dense(3, activation="softmax")
  ```
- **Model Checkpoint Path**: [`research/models/greenscan_efficientnetb0_best.keras`](file:///c:/Greenscan%20project/research/models/greenscan_efficientnetb0_best.keras)
- **Input Resolution**: $224 \times 224 \times 3$ (RGB)
- **Target Classes ($K=3$)**:
  1. `tomato_Early blight` (Index 0)
  2. `tomato_Late blight` (Index 1)
  3. `tomato_healthy` (Index 2)
- **Preprocessing Pipeline**: Keras built-in `EfficientNetB0` internal normalization (`Rescaling(1./255)` + ImageNet `Normalization`).

---

## 2. Frozen Held-Out Test Results ($N = 770$ Images | $511$ Physical Leaf Groups)

| Metric | EfficientNetB0 (Final Test) | MobileNetV2 Baseline Test | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **91.95%** | **91.43%** | `+0.52%` |
| **Macro Precision** | **91.93%** | **91.66%** | `+0.27%` |
| **Macro Recall** | **93.05%** | **92.00%** | `+1.05%` |
| **Macro F1-Score** | **92.46%** | **91.70%** | `+0.76%` |
| **Weighted Precision** | **91.93%** | **91.44%** | `+0.49%` |
| **Weighted Recall** | **91.95%** | **91.43%** | `+0.52%` |
| **Weighted F1-Score** | **91.92%** | **91.32%** | `+0.59%` |
| **Early Blight Precision** | **89.21%** | **91.78%** | `-2.57%` |
| **Early Blight Recall** | **88.48%** | **82.72%** | `+5.76%` |
| **Early Blight F1** | **88.84%** | **87.01%** | `+1.83%` |
| **Late Blight Precision** | **93.07%** | **90.89%** | `+2.18%` |
| **Late Blight Recall** | **91.36%** | **93.98%** | `-2.62%` |
| **Late Blight F1** | **92.21%** | **92.41%** | `-0.20%` |
| **Healthy Precision** | **93.51%** | **92.31%** | `+1.20%` |
| **Healthy Recall** | **99.31%** | **99.31%** | `+0.00%` |
| **Healthy F1** | **96.32%** | **95.68%** | `+0.64%` |
| **Early $\rightarrow$ Late Errors** | **26** | **35** | `-9` |
| **Late $\rightarrow$ Early Errors** | **25** | **18** | `+7` |
| **Total Early $\leftrightarrow$ Late Errors** | **51** | **53** | `-2` |

---

## 3. Freeze & Integrity Declarations

1. **Held-Out Test Completed Once**: The held-out test evaluation has been executed exactly once on the pre-selected checkpoint.
2. **No Further Tuning**: No hyperparameter tuning, model modification, threshold shifting, or retraining shall be conducted using the held-out test set.
3. **Artifact Immutability**: All model checkpoints, evaluation predictions, confusion matrices, and metrics records are strictly frozen.
