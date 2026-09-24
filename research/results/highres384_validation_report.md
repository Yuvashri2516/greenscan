# GreenScan Experiment 3: Higher-Resolution Training (384×384) Validation Report

## 1. Objective

The objective of Experiment 3 is to evaluate the impact of increasing the spatial input resolution from $224 \times 224$ to $384 \times 384$ pixels within a strictly controlled experimental framework. All other modeling components (frozen ImageNet MobileNetV2 backbone, classification head, standard categorical cross-entropy loss, optimizer, and augmentation policy) were kept identical to the baseline.

---

## 2. Hypothesis

### Fine-Grained Lesion/Texture Hypothesis:
The diagnostic study revealed that inter-disease confusion between Early Blight and Late Blight accounts for over 80% of all classification errors. Both diseases manifest as necrotic foliar lesions; however, Early Blight is characterized by subtle concentric ring patterns ("target-board" morphology), while Late Blight exhibits water-soaked, irregular necrotic margins. The hypothesis posited that downsampling native images to $224 \times 224$ discards critical high-frequency textural cues required to resolve concentric ring micro-structures, and that elevating input resolution to $384 \times 384$ would improve feature discriminability between Early Blight and Late Blight.

---

## 3. Dataset & Partition Protocol

- **Dataset Source**: `evaluation/clean_split_manifest.csv`
- **Training Population**: $3,588$ images ($2,314$ physical leaf groups).
- **Validation Population**: $766$ images ($503$ physical leaf groups; 2 non-image `.pdf` rows excluded identically to Experiments 1 & 2).
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

## 4. Training Configuration

- **Backbone Architecture**: MobileNetV2 (ImageNet weights, input shape $384 \times 384 \times 3$, fully frozen base).
- **Classification Head**: `GlobalAveragePooling2D` $\rightarrow$ `Dense(128, ReLU)` $\rightarrow$ `Dropout(0.5)` $\rightarrow$ `Dense(3, Softmax)`.
- **Input Resolution**: $384 \times 384 \times 3$ (Upscaled from baseline $224 \times 224 \times 3$).
- **Batch Size**: 16 (Reduced from 32 solely to accommodate the $2.94\times$ increase in activation tensor memory per sample).
- **Optimizer**: Adam ($	ext{initial lr} = 0.001$).
- **Loss Function**: Standard Categorical Cross-Entropy (No class weighting, No focal loss).
- **Max Epochs**: 15 | **Random Seed**: 42.
- **Callbacks**: EarlyStopping (patience 5, restore best weights), ReduceLROnPlateau (factor 0.2, patience 3, min lr $10^{-6}$), ModelCheckpoint (monitor `val_loss`).
- **Data Augmentation**: Applied only during training (rotation 40°, width/height shift 0.2, shear 0.2, zoom 0.2, horizontal/vertical flip); validation unaugmented.

---

## 5. Training Dynamics & Checkpoint Summary

- **Total Epochs Trained**: 15
- **Best Validation Epoch**: **Epoch 14**
- **Best Training Loss**: `0.2347` | **Best Training Accuracy**: `90.80%`
- **Best Validation Loss**: `0.2444` | **Best Validation Accuracy**: `89.82%`
- **Mean Confidence (Correct Predictions)**: `91.56%`
- **Mean Confidence (Incorrect Predictions)**: `69.33%`

---

## 6. Controlled Baseline Comparison (224×224 vs. 384×384)

*Evaluated on the exact same validation cohort of $N = 766$ images ($503$ physical leaf groups).*

| Metric | 224×224 Baseline | 384×384 High-Res | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **90.60%** | **89.82%** | `-0.78%` |
| **Macro Precision** | **90.81%** | **90.75%** | `-0.06%` |
| **Macro Recall** | **91.22%** | **89.92%** | `-1.30%` |
| **Macro F1** | **90.89%** | **90.29%** | `-0.59%` |
| **Early Precision** | **88.89%** | **88.44%** | `-0.44%` |
| **Early Recall** | **83.33%** | **82.92%** | `-0.42%` |
| **Early F1** | **86.02%** | **85.59%** | `-0.43%` |
| **Late Precision** | **90.98%** | **88.69%** | `-2.29%` |
| **Late Recall** | **92.41%** | **92.41%** | `-0.00%` |
| **Late F1** | **92.05%** | **90.51%** | `-1.53%` |
| **Healthy Precision** | **92.16%** | **95.10%** | `+2.95%` |
| **Healthy Recall** | **97.92%** | **94.44%** | `-3.47%` |
| **Healthy F1** | **94.63%** | **94.77%** | `+0.14%` |
| **Early $\rightarrow$ Late Errors** | **33** | **38** | `+5` |
| **Late $\rightarrow$ Early Errors** | **24** | **25** | `+1` |
| **Total Early $\leftrightarrow$ Late Confusion** | **57** | **63** | `+6` |

---

## 7. Validation Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         199            38            3          240
Late Blight          25             353           4          382
Healthy              1              7             136        144
Total (Predicted)    225            398           143        766
```

### Complete Error Distribution:
- **Early $\rightarrow$ Late**: 38
- **Early $\rightarrow$ Healthy**: 3
- **Late $\rightarrow$ Early**: 25
- **Late $\rightarrow$ Healthy**: 4
- **Healthy $\rightarrow$ Early**: 1
- **Healthy $\rightarrow$ Late**: 7

---

## 8. Early-vs-Late Discrimination Analysis

1. **Early Blight Performance**: Early Blight recall changed from **83.33%** to **82.92%** (`-0.42%`), while Early Blight F1-score changed from **86.02%** to **85.59%** (`-0.43%`).
2. **Late Blight Performance**: Late Blight recall changed from **92.41%** to **92.41%** (`-0.00%`), while Late Blight F1-score changed from **92.05%** to **90.51%** (`-1.53%`).
3. **Total Confusion Volume**: Inter-disease errors shifted from **57** to **63** (`+6`).

---

## 9. Interpretation & Evidence Categorization

### Observed Results:
- Higher resolution (384×384) yields validation accuracy of **89.82%** and Macro F1 of **90.29%**.
- The direction of Early $\leftrightarrow$ Late errors showed Early $\rightarrow$ Late errors at 38 and Late $\rightarrow$ Early errors at 25.

### Scientific Interpretation:
- While increasing spatial resolution from 224×224 to 384×384 provides finer pixel sampling of necrotic margins, the frozen MobileNetV2 feature extractor filters were pretrained on ImageNet at standard resolution. Because the backbone remained frozen (to isolate the single variable of input size), the higher-dimensional spatial feature maps after Global Average Pooling are aggregated into the same 1280-dimensional channel vector.
- Consequently, spatial resolution alone without structural feature adaptation or multi-scale attention does not resolve the morphological ambiguity between coalescent late-stage lesions.

### Limitations:
- The MobileNetV2 backbone weights were frozen; higher resolution was not evaluated in conjunction with backbone fine-tuning in this single-variable experiment.
- Evaluated strictly on the validation partition; the frozen held-out test partition remained strictly unaccessed.

### Evidence Classification:
- **Category**: **C. No meaningful improvement**

---

## 10. Decision & Stop Condition

- **Validation Evidence Status**: **NO MEANINGFUL IMPROVEMENT**
- **Test-Set Evaluation Recommendation**: **DO NOT PROCEED TO HELD-OUT TEST**
- **Integrity Statement**: The held-out test set ($N=770$ images, $511$ physical leaf groups) remains strictly frozen and unaccessed.

---

## Artifact Index
- `research/models/greenscan_highres384_best.keras`
- `research/models/greenscan_highres384_final.keras`
- `research/results/highres384_history.csv`
- `research/results/highres384_summary.json`
- `research/results/highres384_validation_metrics.json`
- `research/results/highres384_validation_report.md`
- `research/results/highres384_confusion_matrix.png`
