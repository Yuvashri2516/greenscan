# GreenScan — Error Analysis & Interpretability Report

This document presents the detailed error analysis and post-hoc visual interpretability results for the final GreenScan research model (**EfficientNetB0**, frozen ImageNet backbone) on the held-out test partition ($N = 770$ images, $511$ physical leaf groups).

---

## 1. Overall Test Misclassifications

- **Total Test Samples**: **770**
- **Correct Predictions**: **708** (**91.95%**)
- **Misclassifications**: **62** (**8.05%**)

### Test Confusion Matrix:
```text
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         215            26            2          243
Late Blight          25             349           8          382
Healthy              1              0             144        145
Total (Predicted)    241            375           154        770
```

---

## 2. Dominant Failure Mode: Early Blight ↔ Late Blight Confusion

Inter-disease confusion between Early Blight and Late Blight remains the primary error mode:
- **Early $\rightarrow$ Late Errors**: **26** ($10.70\%$ of all Early Blight test images)
- **Late $\rightarrow$ Early Errors**: **25** ($6.54\%$ of all Late Blight test images)
- **Total Inter-Disease Confusion**: **51** errors out of 62 total errors (**82.26%** of all test mistakes).

### Empirical Observations on Failure Modes:
1. **Lesion Coalescence in Advanced Disease**: In severe infections, localized Early Blight lesions expand and merge into extensive necrotic patches. As necrotic tissue coalesces, the characteristic concentric "target rings" become less distinguishable, resulting in visual convergence with diffuse Late Blight necrosis.
2. **Early-Stage Punctate Lesions**: Minute, nascent necrotic spots lack sufficient spatial footprint to exhibit distinct morphological signatures, occasionally leading to confusion between disease categories or minor confusion with healthy tissue.
3. **Reduction Relative to Baseline**: Compared to the MobileNetV2 baseline (which produced 35 Early $\rightarrow$ Late errors), EfficientNetB0 reduced Early $\rightarrow$ Late misclassifications to 26, reflecting enhanced feature discrimination of concentric ring micro-textures.

---

## 3. Post-Hoc Explainability (Grad-CAM)

Gradient-Weighted Class Activation Mapping (Grad-CAM) was computed using the final convolutional activation map (`top_activation`) of the frozen EfficientNetB0 backbone to examine visual feature attribution.

> **Methodological Note on Grad-CAM**:
> Grad-CAM provides a **post-hoc visualization of image regions that contribute strongly to the model's logits**. It does **not** represent automated lesion segmentation, boundary delineation, or quantitative biological pathology mapping.

### Key Grad-CAM Insights from Representative Test Errors:
- **True Early Blight Predicted as Late Blight**: Heatmaps focus heavily on extensive, dark necrotic foliar margins where concentric ring structures have degraded, indicating the model attributes high importance to the broad necrotic area rather than localized textural rings.
- **True Late Blight Predicted as Early Blight**: Activations concentrate on localized, circular dry necrotic spots within a leaf, where water-soaked borders are less apparent.
- **Visual Artifacts**: All Grad-CAM visualizations generated for test misclassifications are stored in [`research/results/efficientnetb0_test_gradcam/`](file:///c:/Greenscan%20project/research/results/efficientnetb0_test_gradcam).

---

## 4. Prediction Confidence Analysis

| Prediction Subgroup | Sample Count ($N$) | Mean Confidence | Median Confidence | Min Confidence | Max Confidence |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **All Test Samples** | 770 | **92.45%** | **98.62%** | 41.78% | 100.00% |
| **Correct Predictions** | 708 | **93.97%** | **98.96%** | 45.46% | 100.00% |
| **Incorrect Predictions** | 62 | **75.08%** | **75.65%** | 41.78% | 99.99% |

### Confidence Distribution Across Errors:
- **$< 50\%$**: 1 sample ($1.6\%$)
- **$50\% - 70\%$**: 27 samples ($43.5\%$)
- **$70\% - 80\%$**: 6 samples ($9.7\%$)
- **$80\% - 90\%$**: 11 samples ($17.7\%$)
- **$90\% - 95\%$**: 4 samples ($6.5\%$)
- **$95\% - 100\%$**: 13 samples ($21.0\%$)

> **Important Caution on Model Confidence**:
> Softmax prediction confidence **should not be interpreted as calibrated posterior probability**, because formal temperature scaling or Platt calibration was not applied. High-confidence errors exist (e.g., 13 misclassifications with confidence $>95\%$), reinforcing the necessity of presenting confidence values as decision-support heuristics rather than definitive certainty metrics.
