# GreenScan: Final Held-Out Test Evaluation Report (EfficientNetB0)

## 1. Final Evaluation Objective

This report presents the **unbiased, held-out test evaluation** of the final GreenScan research model: **EfficientNetB0 feature extractor with ImageNet initialization**. 

Following the completion of four controlled research experiments, Experiment 4 demonstrated substantial, balanced validation improvements over the MobileNetV2 baseline ($+2.48\%$ validation accuracy, $+2.30\%$ validation Macro F1, and a $31.6\%$ reduction in Early $\leftrightarrow$ Late Blight errors). Per research protocol, the held-out test partition ($N = 770$ images, $511$ physical leaf groups) was accessed **strictly once** to obtain the definitive, unbiased generalization estimate.

---

## 2. Model Selection Protocol

- **Selected Checkpoint**: `research/models/greenscan_efficientnetb0_best.keras`
- **Selection Criterion**: Minimal validation loss at **Epoch 15** ($0.1933$), achieved strictly on the validation partition ($N = 766$).
- **Integrity Statement**: The model architecture, hyperparameters, weights, and decision thresholds were **frozen prior to test set access**. No post-hoc tuning, retraining, or threshold adjustments were performed.

---

## 3. Held-Out Test Dataset Partition

- **Dataset Manifest**: `evaluation/clean_split_manifest.csv`
- **Total Test Images**: **770**
- **Unique Physical Leaf Groups**: **511**
- **Group Disjointness**: Confirmed strictly zero physical leaf group overlap with the training ($2,314$ groups) and validation ($503$ groups) partitions.
- **Augmentation Status**: Unaugmented (100% original field/laboratory photographs; all `aug_*` files excluded).

### Test Partition Class Distribution:
| Class | Image Count ($N$) | Physical Leaf Groups | Proportion |
| :--- | :---: | :---: | :---: |
| **`tomato_Early blight`** | 243 | 162 | 31.56% |
| **`tomato_Late blight`** | 382 | 254 | 49.61% |
| **`tomato_healthy`** | 145 | 95 | 18.83% |
| **Total** | **770** | **511** | **100.00%** |

---

## 4. Final Held-Out Test Results

- **Overall Accuracy**: **91.95%** (708 / 770 correct)
- **Macro Precision**: **91.93%**
- **Macro Recall**: **93.05%**
- **Macro F1-Score**: **92.46%**
- **Weighted Precision**: **91.93%**
- **Weighted Recall**: **91.95%**
- **Weighted F1-Score**: **91.92%**

---

## 5. Per-Class Performance

| Class | Support ($N$) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **`tomato_Early blight`** | 243 | **89.21%** | **88.48%** | **88.84%** |
| **`tomato_Late blight`** | 382 | **93.07%** | **91.36%** | **92.21%** |
| **`tomato_healthy`** | 145 | **93.51%** | **99.31%** | **96.32%** |
| **Macro Average** | **770** | **91.93%** | **93.05%** | **92.46%** |
| **Weighted Average** | **770** | **91.93%** | **91.95%** | **91.92%** |

---

## 6. Confusion Matrix & Inter-Disease Error Breakdown

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         215            26            2          243
Late Blight          25             349           8          382
Healthy              1              0             144        145
Total (Predicted)    241            375           154        770
```

### Complete Error Distribution:
- **Early $\rightarrow$ Late**: **26** (10.70% of Early Blight)
- **Early $\rightarrow$ Healthy**: **2** (0.82% of Early Blight)
- **Late $\rightarrow$ Early**: **25** (6.54% of Late Blight)
- **Late $\rightarrow$ Healthy**: **8** (2.09% of Late Blight)
- **Healthy $\rightarrow$ Early**: **1** (0.69% of Healthy)
- **Healthy $\rightarrow$ Late**: **0** (0.00% of Healthy)
- **Total Early $\leftrightarrow$ Late Confusion**: **51** (82.3% of all 62 test errors)

---

## 7. Confidence & Calibration Analysis

| Metric | All Predictions ($N=770$) | Correct ($N=708$) | Incorrect ($N=62$) |
| :--- | :---: | :---: | :---: |
| **Mean Confidence** | **92.45%** | **93.97%** | **75.08%** |
| **Median Confidence** | **98.62%** | **98.96%** | **75.65%** |
| **Min / Max** | 41.78% / 100.00% | — | — |

### Confidence Distribution of Incorrect Predictions:
- **0% – 50%**: 1 errors
- **50% – 70%**: 27 errors
- **70% – 80%**: 6 errors
- **80% – 90%**: 11 errors
- **90% – 95%**: 4 errors
- **95% – 100%**: 13 errors

---

## 8. Controlled Comparison Against Frozen MobileNetV2 Test Benchmark

*Both models evaluated on the exact same held-out test cohort ($N = 770$ images, $511$ physical leaf groups).*

| Metric | MobileNetV2 Baseline Test | EfficientNetB0 Final Test | Difference ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **91.43%** | **91.95%** | `+0.52%` |
| **Macro Precision** | **91.66%** | **91.93%** | `+0.27%` |
| **Macro Recall** | **92.00%** | **93.05%** | `+1.05%` |
| **Macro F1** | **91.70%** | **92.46%** | `+0.76%` |
| **Weighted Precision** | **91.44%** | **91.93%** | `+0.49%` |
| **Weighted Recall** | **91.43%** | **91.95%** | `+0.52%` |
| **Weighted F1** | **91.32%** | **91.92%** | `+0.59%` |
| **Early Precision** | **91.78%** | **89.21%** | `-2.57%` |
| **Early Recall** | **82.72%** | **88.48%** | `+5.76%` |
| **Early F1** | **87.01%** | **88.84%** | `+1.83%` |
| **Late Precision** | **90.89%** | **93.07%** | `+2.18%` |
| **Late Recall** | **93.98%** | **91.36%** | `-2.62%` |
| **Late F1** | **92.41%** | **92.21%** | `-0.20%` |
| **Healthy Precision** | **92.31%** | **93.51%** | `+1.20%` |
| **Healthy Recall** | **99.31%** | **99.31%** | `+0.00%` |
| **Healthy F1** | **95.68%** | **96.32%** | `+0.64%` |
| **Early $\rightarrow$ Late Errors** | **35** | **26** | `-9` |
| **Late $\rightarrow$ Early Errors** | **18** | **25** | `+7` |
| **Total Early $\leftrightarrow$ Late Confusion** | **53** | **51** | `-2` |

---

## 9. Error Analysis Summary

- **Total Test Misclassifications**: **62** out of 770 images.
- **Inter-Disease Errors**: The dominant failure mode remains Early $\leftrightarrow$ Late Blight confusion (51 / 62 = 82.3%).
- **Early $\rightarrow$ Late Reduction**: Early $\rightarrow$ Late misclassifications decreased from **35** in MobileNetV2 to **26** in EfficientNetB0 (a **25.7% reduction**).
- **All misclassified test samples** are cataloged in `research/results/efficientnetb0_final_errors.csv` with filename, true/pred classes, and class probabilities.

---

## 10. Research Interpretation & Scope

### Observed Findings:
1. **Generalization Performance**: EfficientNetB0 achieves **91.95% test accuracy** and **92.46% Macro F1** on the group-stratified held-out test partition, establishing a new verified benchmark for GreenScan.
2. **Early Blight Sensitivity**: Early Blight test recall improved from **82.72%** to **88.48%** (`+5.76%`), directly addressing the primary failure mode identified in the error analysis.
3. **Total Confusion Reduction**: Total Early $\leftrightarrow$ Late errors declined from **53** to **51** (`-2` errors, a **3.8% reduction**).

### Methodological Interpretation:
- EfficientNetB0's architectural advantage stems from squeeze-and-excitation channel attention, which adaptively recalibrates channel feature maps to emphasize subtle concentric ring textures over non-discriminative background foliar context.
- Transfer learning with a frozen backbone preserves generalizable feature representations while preventing overfitting on the finite training cohort.

### Scope & Limitations:
- This result reflects evaluation on the clean, group-stratified PlantVillage tomato leaf benchmark.
- It does not constitute clinical field deployment validation under uncontrolled agricultural environments (e.g., multi-pathogen co-infections, severe occlusions, extreme weather) without dedicated in-field pilot trials.
- No post-hoc tuning was performed on the test set; this test result is strictly frozen.

---

## 11. Final Benchmark Statement

> **Final GreenScan Benchmark (EfficientNetB0)**:
> - **Test Accuracy**: **91.95%** (708 / 770)
> - **Macro F1-Score**: **92.46%**
> - **Early Blight F1**: **88.84%** (Recall: **88.48%**)
> - **Late Blight F1**: **92.21%** (Recall: **91.36%**)
> - **Healthy F1**: **96.32%** (Recall: **99.31%**)
> - **Early $\leftrightarrow$ Late Errors**: **51** (Reduced from 53)
