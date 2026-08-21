# Results

This section presents the classification accuracy and GSA severity estimation results obtained from the evaluation of the validation set (1,505 images).

---

## 1. Classification Performance

The model's classification performance on the validation set is summarized below:

- **Validation Classification Accuracy:** 91.76% (0.9176)
- **Macro-Averaged Precision:** 91.95% (0.9194)
- **Macro-Averaged Recall:** 91.83% (0.9183)
- **Macro-Averaged F1-Score:** 91.68% (0.9168)

- **Weighted-Averaged Precision:** 91.93% (0.9193)
- **Weighted-Averaged Recall:** 91.76% (0.9176)
- **Weighted-Averaged F1-Score:** 91.64% (0.9164)

---

## 2. GSA Disease and Severity Statistics

The GSA statistics (using a threshold of $\tau = 0.60$, area weight = 0.60, and activation weight = 0.40) computed across the validation set are summarized in the table below:

| Disease Class | Validation Samples | Mean Classification Confidence | Mean Attention-Affected Region % | Median Attention-Affected Region % | Std Dev Affected Region % | Mean GSA Health Score (PHS) | GSA Severity Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **tomato_healthy** | 490 | 98.33% | 35.56% | 28.57% | 22.28% | 97.63 | Healthy (PHS $\ge 90$) |
| **tomato_Early blight** | 504 | 94.04% | 33.93% | 31.70% | 12.73% | 49.47 | Moderate ($40 \le$ PHS $< 70$) |
| **tomato_Late blight** | 511 | 96.00% | 22.67% | 18.84% | 12.07% | 58.37 | Moderate ($40 \le$ PHS $< 70$) |

*Note on Healthy Class:* For the `tomato_healthy` class, the GSA uses a dedicated formula: $\text{PHS} = 100 - (\text{MeanLeafActivation} \times 5.0)$. This ensures that background activation and spurious gradients do not artificially reduce the health score.

---

## 3. Threshold Sensitivity Analysis

To calibrate the GSA pipeline, we analyzed leaf classifications across five Grad-CAM threshold values ($\tau \in \{0.4, 0.5, 0.6, 0.7, 0.8\}$) on the validation dataset:

| Threshold ($\tau$) | Mean Attention-Affected Region % | Mean GSA Health Score (PHS) | Classified Healthy (PHS $\ge 90$) | Classified Mild ($70 \le$ PHS $< 90$) | Classified Moderate ($40 \le$ PHS $< 70$) | Classified Severe (PHS $< 40$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.40** | 51.68% | 63.91 | 532 | 12 | 671 | 290 |
| **0.50** | 40.76% | 66.45 | 533 | 15 | 793 | 164 |
| **0.60 (Selected)** | **29.88%** | **68.84** | **534** | **13** | **895** | **63** |
| **0.70** | 19.62% | 71.01 | 537 | 2 | 950 | 16 |
| **0.80** | 10.71% | 72.73 | 539 | 0 | 965 | 1 |

*Analysis:* Lower thresholds (e.g., 0.40) include weaker gradients, leading to larger estimated affected regions (51.68%) and classifying more cases as severe (290). Higher thresholds (e.g., 0.80) restrict GSA focus to peak activations, resulting in smaller estimated affected regions (10.71%) and classifying almost all diseased cases as moderate (965) with only 1 severe case. The $\tau = 0.60$ threshold provides a balanced distribution.

---

## 4. System Performance and Response Latency

The computational performance of the GreenScan web service was measured on warm inferences:
- **Average Warm Inference Latency:** ~1.19 seconds (evaluated across sequential tomato leaf uploads).
- **Sub-system Latency Breakdown:**
  - OpenCV HSV segmentation: ~0.15 seconds
  - CNN classification forward pass: ~0.45 seconds
  - Grad-CAM gradient calculation: ~0.48 seconds
  - GSA indexing and database logging: ~0.11 seconds
