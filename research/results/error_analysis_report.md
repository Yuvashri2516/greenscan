# GreenScan Held-Out Test Error Analysis Report

**Evaluation Setting**: Frozen Held-Out Test Partition ($N = 770$ images, $511$ physical leaf groups)  
**Model Evaluated**: `research/models/greenscan_research_best.keras` (Epoch 13 checkpoint)  
**Total Predictions**: 704 Correct (91.43%), 66 Misclassifications (8.57%)  
**Research Rule**: Observational analysis only. Model and dataset remain frozen.

---

## A. Executive Summary

This study provides a rigorous, research-grade post-hoc error analysis of the 66 misclassifications observed during the physical-leaf-disjoint held-out test evaluation of the GreenScan model. 

### Key Findings:
1. **Dominant Failure Mode (80.30%)**: The vast majority of misclassifications ($53 / 66$) consist of inter-disease confusion between **Early Blight** and **Late Blight**. Specifically, 35 Early Blight samples were predicted as Late Blight, and 18 Late Blight samples were predicted as Early Blight.
2. **Disease-to-Healthy Under-Detection (18.18%)**: 12 diseased images ($7$ Early Blight, $5$ Late Blight) were predicted as Healthy, primarily associated with localized, early-stage, or mild focal lesions on an otherwise green leaf surface.
3. **Extremely Rare False Positives (1.52%)**: Only **1** Healthy image was misclassified as diseased (Late Blight) out of 145 healthy test samples, demonstrating high healthy class specificity ($99.31\%$ recall).
4. **Confidence Dynamics**: Misclassifications exhibited a substantially lower mean confidence ($72.27\%$) compared to correct predictions ($91.58\%$). However, 12 errors ($18.18\%$) were high-confidence errors ($\ge 90\%$), representing ambiguous pathological morphologies where the visual symptom closely mimics the alternate disease.

---

## B. Overall Error Distribution

| Metric | Count | Percentage of Test Set ($N=770$) | Percentage of All Errors ($N=66$) |
| :--- | :---: | :---: | :---: |
| **Total Test Images** | 770 | 100.00% | — |
| **Correct Classifications** | 704 | 91.43% | — |
| **Total Misclassifications** | **66** | **8.57%** | **100.00%** |
| **Early Blight $\rightarrow$ Late Blight** | 35 | 4.55% | 53.03% |
| **Late Blight $\rightarrow$ Early Blight** | 18 | 2.34% | 27.27% |
| **Early Blight $\rightarrow$ Healthy** | 7 | 0.91% | 10.61% |
| **Late Blight $\rightarrow$ Healthy** | 5 | 0.65% | 7.58% |
| **Healthy $\rightarrow$ Late Blight** | 1 | 0.13% | 1.52% |
| **Healthy $\rightarrow$ Early Blight** | 0 | 0.00% | 0.00% |

---

## C. Confusion Analysis: Early Blight $\leftrightarrow$ Late Blight

Inter-disease confusion represents **$80.30\%$ ($53 / 66$)** of all model errors.

```
                         Predicted
                 Early Blight   Late Blight
True Early            201            35       (35 misclassified as Late)
True Late              18           359       (18 misclassified as Early)
```

### Visual & Pathological Factors:
- **Symptom Overlap**: In tomato pathology, Early Blight (*Alternaria solani*) characteristically produces dark brown/black concentric target-like rings, whereas Late Blight (*Phytophthora infestans*) typically produces water-soaked, irregular necrotic lesions.
- However, in late-stage coalesced lesions or heavily necrotic foliage, concentric rings become obscured by widespread tissue collapse, visually resembling Late Blight necrosis.
- Conversely, small, discrete early Late Blight lesions before sporulation or water-soaking can resemble Early Blight spots.
- The feature extractor appears sensitive to overall necrotic texture and color, leading to confusion when classic concentric ring patterns are absent.

---

## D. Disease-to-Healthy Errors (12 Cases, 18.18%)

- **Early Blight $\rightarrow$ Healthy**: 7 images (mean confidence: $70.81\%$)
- **Late Blight $\rightarrow$ Healthy**: 5 images (mean confidence: $68.42\%$)

### Visual Observations:
- In nearly all 12 cases, the leaf presents a large expanse of healthy green tissue with only tiny, isolated focal spots or mild edge chlorosis.
- Global Average Pooling (GAP) aggregates feature maps across the entire $7 \times 7$ spatial grid; when a healthy green background dominates $>90\%$ of the spatial area, the background response can dilute subtle localized activation signals.

---

## E. Healthy-to-Disease Errors (1 Case, 1.52%)

- **Healthy $\rightarrow$ Late Blight**: 1 image (`9654fd86-4ef3-4bb4-a82f-2f84b6f12fe8___RS_HL 0228_final_masked.jpg`, confidence: $51.05\%$)
- **Healthy $\rightarrow$ Early Blight**: 0 images

### Visual Observation:
- The single false positive exhibited marginal leaf curvature and slight dark edge discoloration from the masking boundary. The model's prediction confidence was near chance ($51.05\%$), indicating high classification uncertainty.

---

## F. Confidence Analysis & High-Confidence Errors

### 1. Confidence Summary Statistics
| Metric | All Errors ($N=66$) | Correct Predictions ($N=704$) |
| :--- | :---: | :---: |
| **Mean Confidence** | **72.27%** | **91.58%** |
| **Median Confidence** | **72.32%** | **97.49%** |
| **Minimum Confidence** | **42.44%** | **35.21%** |
| **Maximum Confidence** | **99.76%** | **100.00%** |
| **Standard Deviation** | **15.78%** | **12.44%** |

### 2. Confidence Band Distribution
| Confidence Band | Error Count | Percentage of All Errors |
| :--- | :---: | :---: |
| **0–50%** | 4 | 6.06% |
| **50–70%** | 25 | 37.88% |
| **70–80%** | 14 | 21.21% |
| **80–90%** | 12 | 18.18% |
| **90–95%** | 3 | 4.55% |
| **95–100%** | 8 | 12.12% |

### 3. High-Confidence Errors ($\ge 90\%$)
A total of **11 misclassifications** occurred with confidence $\ge 90\%$. All 11 instances were inter-disease confusions between Early Blight and Late Blight. These cases exhibit strong necrotic features that strongly align with learned visual representations of the opposing class.

---

## G. Visual Error Analysis & Observable Factors

Across all 66 misclassified samples, structured visual examination identified the following observable factors:

- **ambiguous disease appearance**: 54 errors (81.8%)
- **mild symptoms**: 12 errors (18.2%)

---

## H. Grad-CAM Explainability Analysis

Grad-CAM was applied to 17 representative error cases (5 Early $\rightarrow$ Late, 5 Late $\rightarrow$ Early, 3 Early $\rightarrow$ Healthy, 3 Late $\rightarrow$ Healthy, 1 Healthy $\rightarrow$ Late).

### Observations from Attribution Heatmaps:
1. **Target Localization in Disease Confusion**: In Early $\leftrightarrow$ Late errors, Grad-CAM attributions consistently highlight actual necrotic patches on the leaf blade, confirming that the model attends to diseased areas rather than background artifacts. However, the classifier assigns the wrong disease category to those features.
2. **Diffuse Attributions in Disease $\rightarrow$ Healthy Errors**: For images with subtle, localized lesions classified as Healthy, Grad-CAM attributions are spread broadly across green lamina regions rather than concentrating on the minor necrotic spot.
3. **Attribution Disclaimer**: *The Grad-CAM visualization indicates regions contributing to the model's prediction. It represents feature attribution rather than exact lesion boundary segmentation.*

Representative Grad-CAM figures are saved in `research/results/error_analysis/gradcam/`.

---

## I. Limitations of Visual Error Analysis

- Visual inspection of images is strictly **observational** and does not establish algorithmic causality.
- A human observer noting symptom ambiguity does not conclusively prove that the neural network failed for that specific biological reason.
- Without re-annotation or histological verification, ground-truth labels are assumed correct as provided in the audited benchmark.

---

## J. Research Implications & Future Experiments

*The held-out test evaluation remains final and frozen. The following potential avenues are documented strictly for future independent investigations:*

1. **Future Experiment — Fine-Tuning Backbone Layers**: Unfreezing top convolutional blocks of MobileNetV2 during training may allow the network to learn finer texture representations specific to concentric ring vs diffuse necrosis distinctions.
2. **Future Experiment — Multi-Scale or Attention Feature Extraction**: Incorporating spatial attention or multi-scale feature pyramids could improve sensitivity to small, early-stage focal lesions against large healthy leaf areas.
3. **Future Experiment — Expert Clinical Re-Annotation**: A formal pathology review of high-confidence Early $\leftrightarrow$ Late ambiguous cases could quantify inter-rater disagreement in field datasets.

---

## Artifact Index
- [`research/results/error_analysis.csv`](file:///c:/Greenscan%20project/research/results/error_analysis.csv)
- [`research/results/error_analysis/`](file:///c:/Greenscan%20project/research/results/error_analysis/)
  - `early_to_late/`
  - `late_to_early/`
  - `disease_to_healthy/`
  - `healthy_to_disease/`
  - `gradcam/`
