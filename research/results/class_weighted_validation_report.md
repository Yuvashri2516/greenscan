# GreenScan Experiment 2: Class-Weighted Training Validation Report

## 1. Objective & Hypothesis

This report documents **Experiment 2** of the GreenScan research program: **Class-Weighted Training**.

### Hypothesis:
The clean training partition contains an inherent class imbalance between Late Blight and Early Blight ($1,783$ vs. $1,131$ images, a $1.58 : 1$ ratio). Applying inverse class frequency weighting during training was hypothesized to reduce the model's tendency to predict Late Blight on ambiguous samples, improving Early Blight recall without degrading overall classification performance.

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
$$	ext{weight}_c = rac{N_{	ext{train}}}{	ext{num\_classes} 	imes N_c}$$

| Class | Train Count ($N_c$) | Proportion | Calculated Weight |
| :--- | :---: | :---: | :---: |
| **`tomato_Early blight`** | 1,131 | 31.52% | **1.057471** |
| **`tomato_Late blight`** | 1,783 | 49.69% | **0.670780** |
| **`tomato_healthy`** | 674 | 18.78% | **1.774481** |
| **Total / Average** | **3,588** | **100.00%** | **1.000000** |

---

## 4. Training Configuration

- **Architecture**: MobileNetV2 (ImageNet pretrained base, fully frozen) + GlobalAveragePooling2D + Dense(128, ReLU) + Dropout(0.5) + Dense(3, Softmax).
- **Optimizer**: Adam ($	ext{initial lr} = 0.001$).
- **Loss Function**: Categorical cross-entropy with `class_weight` applied.
- **Batch Size**: 32 | **Max Epochs**: 15.
- **Callbacks**: EarlyStopping (patience 5, restore best weights), ReduceLROnPlateau (factor 0.2, patience 3, min lr $10^{-6}$), ModelCheckpoint (monitor `val_loss`).
- **Data Augmentation**: Applied only during training (rotation 40°, width/height shift 0.2, shear 0.2, zoom 0.2, horizontal/vertical flip); validation unaugmented.

---

## 5. Training Dynamics

- **Total Epochs Trained**: 15
- **Best Validation Epoch**: **Epoch 10**
- **Best Training Loss**: `0.2904` | **Best Training Accuracy**: `86.12%`
- **Best Validation Loss**: `0.2556` | **Best Validation Accuracy**: `89.95%`
- **Mean Confidence (Correct Predictions)**: `88.56%`
- **Mean Confidence (Incorrect Predictions)**: `66.46%`

---

## 6. Controlled Comparison Against Frozen Baseline

*Both models evaluated on the exact same validation population ($N = 766$ images).*

| Metric | Frozen Baseline (Val) | Class-Weighted (Val) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **90.60%** | **89.95%** | `-0.65%` |
| **Macro Precision** | **90.81%** | **89.89%** | `-0.92%` |
| **Macro Recall** | **91.22%** | **91.12%** | `-0.10%` |
| **Macro F1-Score** | **90.89%** | **90.46%** | `-0.43%` |
| **Early Blight Recall** | **83.33%** | **83.75%** | `+0.42%` |
| **Early Blight F1** | **86.02%** | **84.81%** | `-1.21%` |
| **Late Blight Recall** | **92.41%** | **90.31%** | `-2.09%` |
| **Late Blight F1** | **92.05%** | **90.91%** | `-1.14%` |
| **Healthy Recall** | **97.92%** | **99.31%** | `+1.39%` |
| **Healthy F1** | **94.63%** | **95.65%** | `+1.02%` |
| **Early $\rightarrow$ Late Errors** | **33** | **31** | `-2` |
| **Late $\rightarrow$ Early Errors** | **24** | **33** | `+9` |
| **Total Early $\leftrightarrow$ Late Errors** | **57** | **64** | `+7` |

---

## 7. Validation Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         201            31            8          240
Late Blight          33             345           4          382
Healthy              0              1             143        144
Total (Predicted)    234            377           155        766
```

---

## 8. Early vs Late Confusion Analysis & Interpretation

### Observed Results:
1. **Early Blight Sensitivity**: Early Blight recall shifted from **83.33%** to **83.75%** (`+0.42%`), while Early $\rightarrow$ Late errors changed from 33 to 31 (`-2`).
2. **Late Blight Sensitivity**: Late Blight recall shifted from **92.41%** to **90.31%** (`-2.09%`), while Late $\rightarrow$ Early errors changed from 24 to 33 (`+9`).
3. **Total Confusion Volume**: Total inter-disease confusion changed from **57** to **64** errors (`+7`).

### Interpretation:
- Class weighting slightly shifts the decision boundary, but because feature embeddings in the frozen MobileNetV2 backbone are shared across necrotic patterns, penalizing Late Blight errors does not fundamentally resolve morphological lesion overlap.
- Overall accuracy dropped by `-0.65%` (89.95% vs 90.60%) with negligible Macro F1 change (`-0.43%`).

### Limitations:
- Class weighting only rescales the loss gradient; it does not introduce new discriminative visual features into the frozen convolutional representation.
- The held-out test partition remained strictly unaccessed during this experiment.

---

## 9. Decision & Test-Set Rule

- **Experiment 2 Status**: **NOT SUFFICIENT**
- **Decision Recommendation**: **DO NOT PROCEED TO HELD-OUT TEST**

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
