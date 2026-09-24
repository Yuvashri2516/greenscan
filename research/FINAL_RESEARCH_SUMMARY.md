# GreenScan — Final Research Summary

## 1. Project Overview
- **Project Title**: GreenScan Agricultural Decision Support System
- **Research Domain**: Explainable Deep Learning for Plant Pathology & Foliar Health Assessment
- **Target Crop**: Tomato (*Solanum lycopersicum*)
- **Target Categories**: Tomato Early Blight, Tomato Late Blight, Tomato Healthy

---

## 2. Final Verified Model & Performance Benchmark

- **Final Model Architecture**: **EfficientNetB0** (ImageNet pretrained weights, frozen backbone) with custom classification head (`GlobalAveragePooling2D` $\rightarrow$ `Dense(128, ReLU)` $\rightarrow$ `Dropout(0.5)` $\rightarrow$ `Dense(3, Softmax)`).
- **Final Model Checkpoint**: [`research/models/greenscan_efficientnetb0_best.keras`](file:///c:/Greenscan%20project/research/models/greenscan_efficientnetb0_best.keras)
- **Held-Out Test Cohort**: **$770$ original images** mapped to **$511$ physical leaf groups** (Strictly group-disjoint from training and validation partitions).

### Primary Benchmark Results:
- **Overall Accuracy**: **91.95%** ($708 / 770$ correct)
- **Macro Precision**: **91.93%**
- **Macro Recall**: **93.05%**
- **Macro F1-Score**: **92.46%**
- **Weighted F1-Score**: **91.92%**

### Per-Class Test Performance:
- **Tomato Early Blight**: Precision **89.21%** | Recall **88.48%** | F1 **88.84%** (Support: 243)
- **Tomato Late Blight**: Precision **93.07%** | Recall **91.36%** | F1 **92.21%** (Support: 382)
- **Tomato Healthy**: Precision **93.51%** | Recall **99.31%** | F1 **96.32%** (Support: 145)

---

## 3. Core Research Findings

1. **Improvement Over Baseline**: EfficientNetB0 improved overall test accuracy by $+0.52\%$ ($91.43\% \rightarrow 91.95\%$) and test Macro F1 by $+0.76\%$ ($91.70\% \rightarrow 92.46\%$) over the initial frozen MobileNetV2 baseline.
2. **Substantial Early Blight Sensitivity Gain**: Early Blight recall improved by **$+5.76\%$** ($82.72\% \rightarrow 88.48\%$), addressing the primary failure mode of the baseline system.
3. **Architectural Inductive Bias**: Squeeze-and-excitation channel attention in EfficientNetB0 provided superior feature recalibration for distinguishing subtle concentric ring textures compared to depthwise separable convolutions without attention.
4. **Main Remaining Diagnostic Challenge**: Inter-disease confusion between Early Blight and Late Blight remains the primary error mode ($51 / 62$ errors = $82.26\%$), predominantly occurring in advanced coalesced necrosis where morphological ring structures dissolve into broad necrotic blights.

---

## 4. Key Methodological Contributions

1. **Group-Disjoint Partitioning Protocol**: Identified that raw plant pathology datasets contain multiple masked/unmasked captures of the same leaf; developed a physical-leaf clustering protocol to eliminate optimistic subject leakage across train, validation, and test splits.
2. **Cryptographic Duplicate Elimination**: Audited and excluded exact file duplicates using SHA-256 hashing.
3. **Controlled Single-Variable Experimental Design**: Systematically evaluated four hypotheses (fine-tuning, loss re-weighting, spatial resolution, and backbone architecture) on a frozen validation cohort before accessing the test partition.
4. **Post-Hoc Model Explainability**: Integrated Gradient-Weighted Class Activation Mapping (Grad-CAM) to inspect visual features contributing to predictions.
5. **Strict Research Integrity**: Enforced strict separation and freezing of the held-out test set, executing test inference exactly once on the pre-selected model candidate without post-hoc hyperparameter tuning.

---

## 5. Artifact Index

- **Model Weights**: [`research/models/greenscan_efficientnetb0_best.keras`](file:///c:/Greenscan%20project/research/models/greenscan_efficientnetb0_best.keras)
- **Model Metadata**: [`research/final_model_metadata.json`](file:///c:/Greenscan%20project/research/final_model_metadata.json)
- **Freeze Record**: [`research/FINAL_MODEL_FREEZE.md`](file:///c:/Greenscan%20project/research/FINAL_MODEL_FREEZE.md)
- **Test Metrics**: [`research/results/efficientnetb0_held_out_test_metrics.json`](file:///c:/Greenscan%20project/research/results/efficientnetb0_held_out_test_metrics.json)
- **Test Predictions**: [`research/results/efficientnetb0_held_out_test_predictions.csv`](file:///c:/Greenscan%20project/research/results/efficientnetb0_held_out_test_predictions.csv)
- **Test Errors**: [`research/results/efficientnetb0_final_errors.csv`](file:///c:/Greenscan%20project/research/results/efficientnetb0_final_errors.csv)
- **Test Report**: [`research/results/efficientnetb0_held_out_test_report.md`](file:///c:/Greenscan%20project/research/results/efficientnetb0_held_out_test_report.md)
- **Documentation Suite**:
  - [`docs/methodology.md`](file:///c:/Greenscan%20project/docs/methodology.md)
  - [`docs/reproducibility.md`](file:///c:/Greenscan%20project/docs/reproducibility.md)
  - [`docs/experiment_comparison.md`](file:///c:/Greenscan%20project/docs/experiment_comparison.md)
  - [`docs/error_analysis.md`](file:///c:/Greenscan%20project/docs/error_analysis.md)
  - [`docs/limitations.md`](file:///c:/Greenscan%20project/docs/limitations.md)
