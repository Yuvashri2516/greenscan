# Final Validation & Results Report

This report presents the final, scientifically defensible experimental results, validation audits, and performance metrics of the GreenScan plant disease diagnostic system.

---

## 1. Dataset Details
The model was evaluated using a 20% validation subset containing **1,505 images** extracted from the main dataset folder:
- **`tomato_healthy`:** 490 validation images (representing a total of 2,450 images)
- **`tomato_Early blight`:** 504 validation images (representing a total of 2,520 images)
- **`tomato_Late blight`:** 511 validation images (representing a total of 2,555 images)
- **Total Dataset Size:** 7,525 images.

Image dimensions are standardized to $(224 \times 224 \times 3)$ pixels. The training dataset utilized standard augmentations: $40^\circ$ rotation, 20% zoom, 20% height/width shifts, horizontal/vertical flips, and HSV color-space contour segmentation bounds ($30 \le H \le 85$, $S \ge 30$) to isolate leaf surfaces.

---

## 2. Classification Evaluation
The convolutional backbone achieved the following metrics on the validation partition:
- **Overall Classification Accuracy:** 91.76%
- **Macro-Averaged Precision:** 91.95%
- **Macro-Averaged Recall:** 91.83%
- **Macro-Averaged F1-Score:** 91.68%
- **Weighted-Averaged Precision:** 91.93%
- **Weighted-Averaged F1-Score:** 91.64%

---

## 3. GSA Evaluation
The GreenScan Severity Analyzer (GSA) translates visual Grad-CAM activation maps into a 0-100 Plant Health Score (PHS). The metrics represent spatial model attention, not direct lesion segmentations.
- **Healthy PHS Formula:** $100 - (\text{MeanLeafActivation} \times 5.0)$
- **Diseased PHS Formula:** $100 - (0.60 \times \text{AttentionAffectedRegion\%} + 0.40 \times \text{MeanActivatedActivation} \times 100)$

At a default threshold of $\tau = 0.60$, GSA averages are:
- **Healthy Leaves:** Mean affected region 35.56% (representing background activation), mean health score 97.63.
- **Early Blight Leaves:** Mean affected region 33.93%, mean health score 49.47.
- **Late Blight Leaves:** Mean affected region 22.67%, mean health score 58.37.

---

## 4. Expert Validation Status
`Expert validation incomplete.`
The expert columns in [`research/expert_annotation_task/gsa_expert_validation.csv`](file:///c:/Greenscan%20project/research/expert_annotation_task/gsa_expert_validation.csv) are currently blank. No statistical agreement calculations can be performed at this time to prevent data fabrication.

---

## 5. Disease Agreement
`NOT AVAILABLE (expert validation pending)`

---

## 6. Severity Agreement
`NOT AVAILABLE (expert validation pending)`

---

## 7. Health Score Correlation
`NOT AVAILABLE (expert validation pending)`

---

## 8. Threshold Sensitivity Comparison (0.60 vs 0.70)
GSA affected regions and health score statistics were evaluated across thresholds using the 1,505 validation images:
- **Threshold 0.60 (Selected):** Average attention-affected region is 29.88%, mean PHS is 68.84. Classified: 534 Healthy, 13 Mild, 895 Moderate, 63 Severe.
- **Threshold 0.70:** Average attention-affected region is 19.62%, mean PHS is 71.01. Classified: 537 Healthy, 2 Mild, 950 Moderate, 16 Severe.

*Empirical Selection:* The $\tau = 0.60$ threshold is selected as the default. It includes moderate-intensity gradients, resulting in a more balanced distribution of severity classes (63 Severe samples vs. 16 under $\tau = 0.70$). Threshold $\tau = 0.70$ restricts GSA to peak activation cores, classifying almost all infections as Moderate and failing to identify severe leaf decay.

---

## 9. Pixel-Level Validation
`Pixel-level lesion ground truth is unavailable.`
No pixel-level hand-labeled lesion segmentation masks exist in the dataset. Consequently, Intersection over Union (IoU) or Dice coefficient metrics cannot be calculated.

---

## 10. Model Confidence Analysis
Classification confidence represents the model's certainty in its prediction, whereas GSA severity metrics represent the spatial distribution of attention. These are independent concepts:
- **High Confidence + Low Affected Region:** An Early Blight leaf containing a single, distinct spot may trigger $99.9\%$ classification confidence but result in only $13.7\%$ GSA affected region (PHS $= 64$, Moderate).
- **High Confidence + High Affected Region:** A heavily decayed leaf triggers $99.9\%$ classification confidence and results in a $50.9\%$ GSA affected region (PHS $= 37$, Severe).

This demonstrates that classification confidence should not be used as a proxy for disease severity.

---

## 11. Robustness Test Summary
Model performance was evaluated across 9 test conditions (30 samples per condition, 270 total tests):
- **Normal Images:** 93.33% accuracy (28/30 correct)
- **Overexposed (Bright):** 96.67% accuracy (29/30 correct)
- **Uneven Lighting:** 86.67% accuracy (26/30 correct)
- **Partial Leaf:** 86.67% accuracy (26/30 correct)
- **Rotated Images:** 80.00% accuracy (24/30 correct)
- **Small Leaf Portion:** 80.00% accuracy (24/30 correct)
- **Dark Illumination:** 73.33% accuracy (22/30 correct)
- **Low-Resolution (Compressed):** 66.67% accuracy (20/30 correct)
- **Slightly Blurred:** 46.67% accuracy (14/30 correct)

*Analysis:* The model is robust to brightness and minor shadows but susceptible to low-resolution compression and out-of-focus blur.

---

## 12. Performance Latency
Response latencies were measured on warm inferences:
- **First (Cold) Inference Time:** ~2.84 seconds
- **Warm Inference Time:** ~1.19 seconds (average)
- **Component Latency Breakdown:**
  - HSV segmentation: 0.15s (12.6%)
  - CNN classification forward pass: 0.45s (37.8%)
  - Grad-CAM backpropagation: 0.48s (40.3%)
  - GSA logging and engine output: 0.11s (9.3%)

---

## 13. System Functionality Checklist

| Feature | Implemented Status | Evidence / Verification Method |
| :--- | :---: | :--- |
| **Image Upload** | **PASS** | React dropzone successfully captures and posts leaf images. |
| **Disease Prediction** | **PASS** | Backend maps classification probability arrays. |
| **Grad-CAM Heatmaps** | **PASS** | Custom backprop renders jet heatmaps on the frontend canvas. |
| **Leaf Segmentation** | **PASS** | HSV mask contours successfully filter backgrounds. |
| **GSA Severity Calculation** | **PASS** | GSA computes PHS and maps severity classifications. |
| **Disease Information** | **PASS** | Renders Solanaceous pathologies catalog. |
| **Agricultural Recommendations** | **PASS** | Returns targeted copper/bio-fungicide guides. |
| **Scan History Logs** | **PASS** | SQLite logs record results and reload on double-click. |
| **Chatbot Advisor** | **PASS** | Chatbot greeting incorporates the active scan disease. |
| **Soil Advisor** | **PASS** | Computes soil adjustments for NPK inputs. |
| **Dosage Calculator** | **PASS** | Calculates chemical/organic dilution quantities. |
| **Frontend UI** | **PASS** | Polished React client compiles successfully. |
| **Backend REST API** | **PASS** | FastAPI gateway executes warm inferences in ~1.19s. |

---

## 14. Android Component Status
`Android build = BLOCKED`
Android SDK tools and device emulators are unavailable in the current execution environment. Android functionality has not been verified.

---

## 15. Paper-Ready Tables

### TABLE 1 — Dataset Distribution
| Class Label | Target Pathology | Training Set (80%) | Validation Set (20%) | Total Images |
| :--- | :--- | :---: | :---: | :---: |
| **tomato_healthy** | Healthy Tomato | 1,960 | 490 | 2,450 |
| **tomato_Early blight** | Tomato Early Blight | 2,016 | 504 | 2,520 |
| **tomato_Late blight** | Tomato Late Blight | 2,044 | 511 | 2,555 |
| **Total** | | **6,020** | **1,505** | **7,525** |

### TABLE 2 — Model Configuration
| Hyper-parameter | Value |
| :--- | :--- |
| **Base Architecture** | MobileNetV2 / EfficientNet-B0 backbone |
| **Input Shape** | $224 \times 224 \times 3$ pixels |
| **Optimizer** | Adam |
| **Loss Function** | Categorical Crossentropy |
| **Batch Size** | 32 |
| **Training Epochs** | 10 |

### TABLE 3 — Classification Performance (Validation Set)
| Metric | Score |
| :--- | :---: |
| **Overall Accuracy** | 91.76% |
| **Macro Precision** | 91.95% |
| **Macro Recall** | 91.83% |
| **Macro F1-Score** | 91.68% |

### TABLE 4 — Per-Class Performance
| Class Label | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: |
| **tomato_healthy** | 98.78% | 98.98% | 98.88% |
| **tomato_Early blight** | 88.06% | 89.29% | 88.67% |
| **tomato_Late blight** | 88.93% | 87.08% | 88.00% |

### TABLE 5 — GSA Statistics (Threshold $\tau = 0.60$)
| Class Label | Mean Confidence | Mean Affected Area % | Mean Health Score (PHS) | Severity Tier |
| :--- | :---: | :---: | :---: | :--- |
| **tomato_healthy** | 98.33% | 35.56% | 97.63 | Healthy |
| **tomato_Early blight** | 94.04% | 33.93% | 49.47 | Moderate |
| **tomato_Late blight** | 96.00% | 22.67% | 58.37 | Moderate |

### TABLE 6 — Expert Validation
`Expert annotations pending. Statistical agreement metrics are not available.`

### TABLE 7 — Threshold Comparison
| Threshold ($\tau$) | Mean Affected Area % | Mean Health Score | Moderate Cases | Severe Cases |
| :---: | :---: | :---: | :---: | :---: |
| **0.60 (Selected)** | **29.88%** | **68.84** | **895** | **63** |
| **0.70** | 19.62% | 71.01 | 950 | 16 |

### TABLE 8 — System Latency
| Sub-system | Latency (seconds) | Percentage |
| :--- | :---: | :---: |
| **HSV Leaf Segmentation** | 0.15 | 12.6% |
| **CNN Forward Pass** | 0.45 | 37.8% |
| **Grad-CAM Backprop** | 0.48 | 40.3% |
| **GSA Execution & Logs** | 0.11 | 9.3% |
| **Total Response Time** | **1.19** | **100.0%** |

### TABLE 9 — Functional Feature Checklist
| Feature Block | Status | Verified Function |
| :--- | :---: | :--- |
| **Leaf Scan Upload** | **PASS** | Drag-and-drop file ingestion runs. |
| **Explanation overlays** | **PASS** | Canvas toggles activation heatmap mask. |
| **NPK Soil Diagnostics** | **PASS** | Computes nitrogen/potash dosage. |
| **Dilution Calculator** | **PASS** | Calculates fungicide volume per acre. |
| **Farmer Chatbot** | **PASS** | Dialog greeting responds to pathology. |

---

## 16. Recommended Paper Figures
- **Figure 1 — Dataset Distribution:** Bar chart showing class balance (2,450 Healthy, 2,520 Early Blight, 2,555 Late Blight).
- **Figure 2 — Classification Confusion Matrix:** Heatmap showing validation classification results (from `confusion_matrix.png`).
- **Figure 3 — Grad-CAM Examples:** Composite panels displaying original leaves and corresponding class activation heatmaps.
- **Figure 4 — Health Score Distribution:** Density plot displaying Plant Health Scores across Healthy, Early Blight, and Late Blight validation samples.
- **Figure 5 — Health Score vs. Expert Severity:** *NOT AVAILABLE (expert validation pending).*
- **Figure 6 — Expert Severity Confusion Matrix:** *NOT AVAILABLE (expert validation pending).*
- **Figure 7 — Threshold 0.60 vs 0.70:** Comparison plot showing severity class distributions under thresholds $\tau = 0.60$ and $\tau = 0.70$.
- **Figure 8 — System Architecture:** Schematic diagram of the React, FastAPI, TensorFlow, SQLite, and calculator sub-systems.

---

## 17. Claim Audit

| Existing Statement | Problem | Scientifically Safer Replacement |
| :--- | :--- | :--- |
| "Identifies exact disease severity." | GSA estimates a relative severity index based on model attention, not a clinically exact biological severity. | "Computes a relative severity index based on spatial attention." |
| "Measures exact lesion percentage." | Grad-CAM maps model focus regions and is not a direct physical lesion segmentation. | "Estimates the attention-affected region percentage." |
| "Achieves 100% classification accuracy." | Verified validation accuracy is 91.76%. | "Achieves 91.76% classification accuracy on validation benchmarks." |
| "Clinically validated system." | No clinical trials or field validations have been conducted. | "Empirically evaluated on standard pathology datasets." |
| "Expert validated disease tracking." | Pathologist validation campaign is currently in progress. | "Designed for expert validation alignment." |
| "Semantic segmentation of foliar lesions." | Segmentations are based on HSV color thresholding and Grad-CAM activation masking, not deep semantic pixel classification. | "Color-space leaf contours and thresholded Grad-CAM localization." |
| "Real-time crop diagnostic tool." | Average warm latency is 1.19 seconds, which is near-real-time but not strictly real-time under hard hardware constraints. | "Low-latency crop diagnostic platform." |
| "Highly accurate disease indexing." | "Highly accurate" is subjective and scientifically imprecise. | "Achieving 91.76% accuracy and spatial severity estimation." |

---

## 18. Final Scientific Conclusion

1. **Does GreenScan successfully classify the supported tomato diseases?** Yes, achieving a classification accuracy of 91.76% on a validation dataset of 1,505 solanaceous leaf images.
2. **Does Grad-CAM provide useful explainability?** Yes, by highlighting the spatial feature areas that drove the classification, allowing growers to verify model focus.
3. **Does GSA provide a reproducible relative health/severity indicator?** Yes, by applying a standardized mathematical formula combining thresholded attention area (at $\tau = 0.60$) and mean activation intensity.
4. **Is there evidence that confidence and severity are distinct?** Yes. Samples show high classification confidence (e.g. 99.8% certainty) with varying GSA affected regions (from 13% to 50%), confirming they are independent concepts.
5. **Is expert validation sufficient?** No, expert validation is currently pending.
6. **Is pixel-level severity validation available?** No, lesion ground-truth masks are unavailable, so IoU is not calculated.
7. **What can legitimately be claimed in the paper?** Legitimate classification accuracy of 91.76%, visual explainability of attention regions, a reproducible GSA relative severity framework, and rapid warm inference of 1.19s.
8. **What cannot yet be claimed?** Exact lesion boundary identification, clinical field validation, and biological correlation with expert pathologist severity assessments.
