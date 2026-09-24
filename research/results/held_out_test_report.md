# GreenScan Final Held-Out Test Evaluation Report

## 1. Executive Summary & Evaluation Protocol

This report documents the **final held-out test evaluation** for the GreenScan tomato disease diagnosis model. 

### Critical Protocol Rules Observed:
- **Physical-Leaf-Disjoint Held-Out Partition**: All 770 test images belong to 511 distinct physical leaf groups that are strictly disjoint from the training (2,314 groups) and validation (503 groups) partitions. Zero subject/image leakage exists.
- **First-Time Access**: The test partition was never loaded, evaluated, or accessed during training or model development.
- **No Model Selection on Test**: The model checkpoint evaluated (`greenscan_research_best.keras`) was selected strictly based on best validation loss performance at **Epoch 13** of clean training.
- **Exact Preprocessing Match**: Evaluated with deterministic image rescaling ($1/255$), RGB color mode, input resolution $224 \times 224$, and zero data augmentation.
- **Excluded Duplicates**: 11 exact duplicate image files identified in the original dataset audit were permanently excluded prior to dataset splitting.
- **Independent Evaluation**: This evaluation reflects genuine generalization performance on unseen physical leaves and supersedes prior non-disjoint evaluations.

---

## 2. Dataset & Split Verification

| Metric / Parameter | Value | Verification Status |
| :--- | :--- | :--- |
| **Total Test Images** | **770** | Verified (100% matched) |
| **Physical Leaf Groups** | **511** | Verified (Strictly Disjoint) |
| **Early Blight Images** | **243** (153 leaf groups) | Verified |
| **Late Blight Images** | **382** (284 leaf groups) | Verified |
| **Healthy Images** | **145** (74 leaf groups) | Verified |
| **Excluded Duplicates** | **11** | Verified (Removed prior to split) |

---

## 3. Overall Performance Summary

| Metric | Score | Exact Value |
| :--- | :---: | :---: |
| **Overall Accuracy** | **91.43%** | `0.914286` (704 / 770) |
| **Macro Precision** | **91.66%** | `0.916582` |
| **Macro Recall** | **92.00%** | `0.920018` |
| **Macro F1-Score** | **91.70%** | `0.917002` |
| **Weighted Precision** | **91.44%** | `0.914362` |
| **Weighted Recall** | **91.43%** | `0.914286` |
| **Weighted F1-Score** | **91.32%** | `0.913211` |

---

## 4. Per-Class Performance Breakdown

| Class | Precision | Recall | F1-Score | Support (Images) | Physical Leaf Groups |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **tomato_Early blight** | **91.78%** | **82.72%** | **87.01%** | 243 | 153 |
| **tomato_Late blight** | **90.89%** | **93.98%** | **92.41%** | 382 | 284 |
| **tomato_healthy** | **92.31%** | **99.31%** | **95.68%** | 145 | 74 |

---

## 5. Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         201            35            7          243
Late Blight          18             359           5          382
Healthy              0              1             144        145
Total (Predicted)    219            395           156        770
```

- **Correct Predictions**: **704** (91.43%)
- **Incorrect Predictions**: **66** (8.57%)

---

## 6. Prediction Confidence Statistics

| Prediction Subset | Mean Confidence | Median Confidence | Min Confidence | Max Confidence |
| :--- | :---: | :---: | :---: | :---: |
| **All Predictions (N=770)** | **89.92%** | **96.98%** | **35.21%** | **100.00%** |
| **Correct Predictions (N=704)** | **91.58%** | **97.49%** | **35.21%** | **100.00%** |
| **Incorrect Predictions (N=66)** | **72.27%** | **72.32%** | **42.44%** | **99.76%** |

---

## 7. Artifact Manifest

1. `research/results/held_out_test_predictions.csv`: Row-level predictions for all 770 test samples.
2. `research/results/held_out_test_metrics.json`: Structured machine-readable metrics and confidence distribution data.
3. `research/results/held_out_confusion_matrix.png`: High-resolution annotated confusion matrix plot.
4. `research/results/held_out_test_report.md`: This comprehensive evaluation report.
