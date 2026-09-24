# GreenScan — Experimental Comparison & Benchmarks

This document consolidates the controlled experimental comparisons conducted across the GreenScan research project.

---

## 1. Controlled Validation Comparison (All Experiments on Validation Cohort, $N = 766$)

All experimental iterations were evaluated on the exact same group-stratified validation partition ($N = 766$ images, $503$ physical leaf groups, strictly disjoint from training data).

| Experiment | Backbone | Input Res. | Core Intervention | Val Accuracy | Val Macro F1 | Early Recall | Late Recall | Early $\leftrightarrow$ Late Errors | Decision |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline** | MobileNetV2 | $224 \times 224$ | Frozen ImageNet Base | **90.60%** | **90.89%** | **83.33%** | **92.41%** | **57** | Baseline Benchmark |
| **Exp 1** | MobileNetV2 | $224 \times 224$ | Partial Fine-Tuning (Top 29 layers) | **90.86%** | **90.86%** | **80.83%** | **95.03%** | **52** | Not Sufficient |
| **Exp 2** | MobileNetV2 | $224 \times 224$ | Programmatic Class Weights | **89.95%** | **90.46%** | **83.75%** | **90.31%** | **64** | Not Sufficient |
| **Exp 3** | MobileNetV2 | $384 \times 384$ | Higher Spatial Resolution | **89.82%** | **90.29%** | **82.92%** | **92.41%** | **63** | Not Sufficient |
| **Exp 4** | EfficientNetB0 | $224 \times 224$ | Squeeze-and-Excitation Backbone | **93.08%** | **93.18%** | **89.17%** | **93.46%** | **39** | **Selected for Test** |

---

## 2. Detailed Per-Class Validation Progression

| Model / Experiment | Early Blight F1 | Late Blight F1 | Healthy F1 | Early $\rightarrow$ Late | Late $\rightarrow$ Early | Total Errors |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline MobileNetV2** | 86.02% | 92.05% | 94.63% | 33 | 24 | 72 |
| **Exp 1: Fine-Tuned** | 86.04% | 92.62% | 93.92% | 37 | 15 | 70 |
| **Exp 2: Class-Weighted** | 84.81% | 90.91% | 95.65% | 31 | 33 | 77 |
| **Exp 3: High-Res (384×384)** | 85.59% | 90.51% | 94.77% | 38 | 25 | 78 |
| **Exp 4: EfficientNetB0** | **90.30%** | **93.95%** | **95.30%** | **19** | **20** | **53** |

---

## 3. Final Held-Out Test Evaluation Comparison ($N = 770$ Images)

The final test evaluation compares the pre-selected **EfficientNetB0** model against the baseline **MobileNetV2** benchmark on the untouched, held-out test cohort ($N = 770$ images, $511$ physical leaf groups).

| Evaluation Metric | MobileNetV2 Baseline Test | EfficientNetB0 Final Test | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **91.43%** | **91.95%** | `+0.52%` |
| **Macro Precision** | **91.66%** | **91.93%** | `+0.27%` |
| **Macro Recall** | **92.00%** | **93.05%** | `+1.05%` |
| **Macro F1-Score** | **91.70%** | **92.46%** | `+0.76%` |
| **Weighted F1-Score** | **91.32%** | **91.92%** | `+0.59%` |
| **Early Blight Precision** | **91.78%** | **89.21%** | `-2.57%` |
| **Early Blight Recall** | **82.72%** | **88.48%** | `+5.76%` |
| **Early Blight F1** | **87.01%** | **88.84%** | `+1.83%` |
| **Late Blight Precision** | **90.89%** | **93.07%** | `+2.18%` |
| **Late Blight Recall** | **93.98%** | **91.36%** | `-2.62%` |
| **Late Blight F1** | **92.41%** | **92.21%** | `-0.20%` |
| **Healthy Precision** | **92.31%** | **93.51%** | `+1.20%` |
| **Healthy Recall** | **99.31%** | **99.31%** | `+0.00%` |
| **Healthy F1** | **95.68%** | **96.32%** | `+0.64%` |
| **Early $\rightarrow$ Late Errors** | **35** | **26** | `-9` |
| **Late $\rightarrow$ Early Errors** | **18** | **25** | `+7` |
| **Total Early $\leftrightarrow$ Late Errors** | **53** | **51** | `-2` |
| **Total Misclassifications** | **66** | **62** | `-4` |
