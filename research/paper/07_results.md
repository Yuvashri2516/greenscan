# Results

## Table 1 — Dataset Distribution

| Class Label | Disease | Training (80%) | Validation (20%) | Total |
|---|---|---|---|---|
| `tomato_Early blight` | *Alternaria solani* | 2,016 | 504 | 2,520 |
| `tomato_Late blight` | *Phytophthora infestans* | 2,044 | 511 | 2,555 |
| `tomato_healthy` | No disease | 1,960 | 490 | 2,450 |
| **Total** | | **6,020** | **1,505** | **7,525** |

---

## Table 2 — Model Configuration

| Hyper-parameter | Value |
|---|---|
| Base Architecture | EfficientNetB0 (ImageNet weights) |
| Custom Head | GAP → Dense(128, ReLU) → Dropout(0.5) → Dense(3, Softmax) |
| Input Shape | 224 × 224 × 3 |
| Optimizer | Adam |
| Loss Function | Categorical Crossentropy |
| Batch Size | 32 |
| Max Epochs | 10 |
| Early Stopping | patience=5 |

---

## Table 3 — Classification Performance (Validation Set, n = 1,505)

| Metric | Value |
|---|---|
| Overall Accuracy | **91.76%** |
| Macro Precision | 91.95% |
| Macro Recall | 91.83% |
| Macro F1-Score | 91.68% |
| Weighted Precision | 91.93% |
| Weighted Recall | 91.76% |
| Weighted F1-Score | 91.64% |

### Per-Class Performance (from evaluate_greenscan.py results)

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| tomato_healthy | 98.78% | 98.98% | 98.88% | 490 |
| tomato_Early blight | 88.06% | 89.29% | 88.67% | 504 |
| tomato_Late blight | 88.93% | 87.08% | 88.00% | 511 |

> **Source:** `research/final_results/classification_results.csv` — produced by `backend/evaluate_greenscan.py` against the 20% validation partition.

---

## Table 4 — GSA Results at τ = 0.60 (n = 30 per class, 90 total)

| Disease | Mean Confidence | Mean Affected Region % | Std Affected Region % | Mean Health Score |
|---|---|---|---|---|
| tomato_healthy | 98.33% | 35.56% | 22.28% | **97.63** |
| tomato_Early blight | 94.04% | 33.93% | 12.73% | **49.47** |
| tomato_Late blight | 96.00% | 22.67% | 12.07% | **58.37** |

> **Source:** `research/final_results/gsa_results.csv`

**Observation 1 — Healthy leaf activation:** Healthy leaves exhibit a mean attention-affected region of 35.56%, which is non-trivially high. This occurs because the model attends to general leaf texture features during healthy-class classification, not because disease lesions are present. The healthy branch of the PHS formula accordingly uses `μ_leaf × 5.0` (a small scaling factor) rather than the diseased formula, resulting in a mean PHS of 97.63 for healthy samples.

**Observation 2 — Confidence vs. Severity Independence:** Mean classification confidence for Early Blight (94.04%) is similar to Late Blight (96.00%), but their mean PHS values differ (49.47 vs 58.37), confirming that confidence and attention-derived severity are independent quantities.

---

## Table 5 — Expert Validation

**Status: PENDING**

Expert pathologist annotations for the 90-sample validation set have not been collected at the time of writing.

| Metric | Value |
|---|---|
| Prepared annotation samples | 90 (30 per class) |
| Expert disease agreement | Not available |
| Expert severity agreement | Not available |
| Cohen's Kappa | Not available |
| Spearman correlation (PHS vs expert severity) | Not available |

> Pixel-level lesion ground-truth masks are **not available** for this dataset. IoU-based spatial accuracy cannot be computed.

---

## Table 6 — GSA Threshold Sensitivity Analysis

### τ = 0.40
| Disease | Mean Affected Region % | Mean Health Score |
|---|---|---|
| tomato_Early blight | 61.13% | 37.73 |
| tomato_Late blight | 39.00% | 53.40 |
| tomato_healthy | 58.40% | 97.63 |

### τ = 0.50
| Disease | Mean Affected Region % | Mean Health Score |
|---|---|---|
| tomato_Early blight | 47.24% | 43.77 |
| tomato_Late blight | 30.68% | 55.93 |
| tomato_healthy | 46.47% | 97.63 |

### τ = 0.60 *(Selected Default)*
| Disease | Mean Affected Region % | Mean Health Score |
|---|---|---|
| tomato_Early blight | 33.93% | 49.47 |
| tomato_Late blight | 22.67% | 58.37 |
| tomato_healthy | 35.56% | 97.63 |

### τ = 0.70
| Disease | Mean Affected Region % | Mean Health Score |
|---|---|---|
| tomato_Early blight | 21.63% | 54.43 |
| tomato_Late blight | 15.59% | 60.30 |
| tomato_healthy | 24.90% | 97.63 |

### τ = 0.80
| Disease | Mean Affected Region % | Mean Health Score |
|---|---|---|
| tomato_Early blight | 11.88% | 58.07 |
| tomato_Late blight | 8.89% | 62.10 |
| tomato_healthy | 12.89% | 97.63 |

> **Source:** `research/final_results/threshold_comparison.csv`

**Threshold Selection Rationale (τ = 0.60):**
- τ = 0.60 was selected as the default because it captures moderate-intensity attention gradients while excluding low-confidence background noise.
- τ = 0.70 was investigated as a candidate because it produces more spatially concentrated activation regions (reducing false-area inclusion from diffuse background gradients).
- τ = 0.70 is **not claimed to be superior** to τ = 0.60 in the absence of expert or pixel-level ground truth to validate which threshold better corresponds to actual lesion areas.
- At τ = 0.40, all three classes produce high affected-region percentages (39–61%), suggesting that lower thresholds include substantial background/texture activations that may not correspond to disease-relevant regions.

---

## Table 7 — Robustness Test Results (n = 30 per condition)

| Condition | Correct Predictions | Accuracy |
|---|---|---|
| A. Normal | 28/30 | **93.33%** |
| E. Overexposed | 29/30 | **96.67%** |
| F. Uneven Lighting | 26/30 | **86.67%** |
| H. Partial Leaf | 26/30 | **86.67%** |
| I. Rotated | 24/30 | **80.00%** |
| K. Small Portion | 24/30 | **80.00%** |
| D. Dark | 22/30 | **73.33%** |
| B. Low Resolution | 20/30 | **66.67%** |
| C. Slightly Blurred | 14/30 | **46.67%** |

> **Source:** `backend/evaluate_robustness.py`

**Key Findings:**
- The model is most robust to brightness increase (overexposure: 96.67%) and least robust to out-of-focus blur (46.67%).
- Low-resolution compression reduces accuracy to 66.67%, suggesting sensitivity to high-frequency texture features used in classification.
- Partial leaf and rotation conditions maintain reasonable accuracy (80–87%), which is encouraging for practical field capture scenarios.

---

## Table 8 — System Latency

| Sub-system | Latency |
|---|---|
| HSV Leaf Segmentation | ~0.15 s (12.6%) |
| CNN Forward Pass | ~0.45 s (37.8%) |
| Grad-CAM Backpropagation | ~0.48 s (40.3%) |
| GSA + Logging | ~0.11 s (9.3%) |
| **Total Warm Inference** | **~1.19 s** |
| First (Cold) Inference | ~2.84 s |
