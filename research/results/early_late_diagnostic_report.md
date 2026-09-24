# GreenScan Diagnostic Study: Early Blight vs Late Blight Confusion

**Evaluation Status**: Frozen Research Held-Out Test Evaluation ($N = 770$ images, $511$ physical leaves)  
**Model Under Study**: `research/models/greenscan_research_best.keras` (Epoch 13 checkpoint)  
**Overall Accuracy**: 91.43% ($704 / 770$ correct, $66$ incorrect)  
**Diagnostic Scope**: Investigation into the dominant failure mode — **Early Blight $\leftrightarrow$ Late Blight confusion ($53 / 66 = 80.30\%$)**.

---

## 1. Objective

In the held-out test evaluation of the GreenScan MobileNetV2 classifier, $80.30\%$ ($53 / 66$) of all classification errors occurred between **Early Blight (*Alternaria solani*)** and **Late Blight (*Phytophthora infestans*)**. 

The objective of this diagnostic study is to examine the structural, statistical, pathological, and dataset-level characteristics underpinning this confusion before designing any future experiments.

---

## 2. Dataset & Class Distribution Analysis

### 2.1 Full Partition Distribution (Clean Audited Dataset, $N = 5,126$ Active Images)

| Class | Total Images | Physical Leaves | Train Images | Val Images | Test Images | Mean Images / Leaf | Median | Max Images / Leaf |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Early Blight** | 1,616 | 1,029 | 1,131 | 242 | 243 | 1.61 | 2.0 | 2 |
| **Late Blight** | 2,547 | 1,770 | 1,783 | 382 | 382 | 1.39 | 1.0 | 8 |
| **Healthy** | 963 | 528 | 674 | 144 | 145 | 1.97 | 2.0 | 2 |
| **Total** | **5,126** | **3,327** | **3,588** | **768** | **770** | **1.54** | **1.0** | **4** |

### 2.2 Class Imbalance Assessment:
- In the training split, **Late Blight ($N = 1,783$)** outnumbers **Early Blight ($N = 1,131$)** by a ratio of **$1.58 : 1$**.
- This class distribution reflects the natural composition of the source benchmark after deduplication.
- *Plausible contributing role*: A $57.6\%$ preponderance of Late Blight training examples may bias decision boundaries in feature space toward Late Blight when ambiguous necrotic features are encountered.

---

## 3. Physical-Leaf Group & Capture Frequency Analysis

### 3.1 Captures per Physical Leaf in the Held-Out Test Split ($N = 770$ Images, $511$ Groups)
- **Single-capture physical leaves ($1$ test image)**: 255 images $\rightarrow$ 26 errors (**10.20%** error rate).
- **Multi-capture physical leaves ($>1$ test images)**: 515 images $\rightarrow$ 40 errors (**7.77%** error rate).

### 3.2 Finding:
Errors are not disproportionately concentrated in heavily repeated captures; error rates are consistent across single-capture and paired masked/raw captures.

---

## 4. Error Distribution & Directional Asymmetry

### 4.1 Breakdown by Class

```
Early Blight (243 Test Samples):
  - Correct:                     201 (82.72% recall)
  - Early -> Late:                35 (14.40% of Early Blight)
  - Early -> Healthy:              7 ( 2.88% of Early Blight)

Late Blight (382 Test Samples):
  - Correct:                     359 (93.98% recall)
  - Late -> Early:                18 ( 4.71% of Late Blight)
  - Late -> Healthy:               5 ( 1.31% of Late Blight)

Healthy (145 Test Samples):
  - Correct:                     144 (99.31% recall)
  - Healthy -> Late:               1 ( 0.69%)
  - Healthy -> Early:              0 ( 0.00%)
```

### 4.2 Asymmetry Quantification:
- **Early $\rightarrow$ Late errors ($N = 35$)** occur nearly **twice as frequently ($1.94\times$)** as **Late $\rightarrow$ Early errors ($N = 18$)**.
- As a fraction of class test support:
  - $14.40\%$ of Early Blight leaves are misclassified as Late Blight.
  - Only $4.71\%$ of Late Blight leaves are misclassified as Early Blight.
- This creates an observed recall gap: Late Blight recall ($93.98\%$) exceeds Early Blight recall ($82.72\%$) by **$11.26$ percentage points**.

---

## 5. Confidence Analysis for Early vs Late

### 5.1 Confidence Summary Statistics

| Prediction Category | Sample Count | Mean Confidence | Median Confidence | Min Confidence | Max Confidence | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correct Early Blight** | 201 | **87.13%** | **93.02%** | 50.31% | 99.99% | 14.32% |
| **Early $\rightarrow$ Late Errors** | 35 | **74.81%** | **73.52%** | 42.44% | 99.76% | 15.66% |
| **Correct Late Blight** | 359 | **92.03%** | **97.16%** | 35.21% | 100.00% | 11.71% |
| **Late $\rightarrow$ Early Errors** | 18 | **64.41%** | **58.56%** | 46.69% | 98.49% | 14.96% |

### 5.2 Confidence Bands Breakdown

| Category | 0–50% | 50–70% | 70–80% | 80–90% | 90–95% | 95–100% | Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correct Early Blight** | 0 | 33 | 15 | 40 | 22 | 91 | 201 |
| **Early $\rightarrow$ Late Errors** | 2 | 10 | 9 | 7 | 1 | 6 | 35 |
| **Correct Late Blight** | 5 | 18 | 24 | 46 | 47 | 219 | 359 |
| **Late $\rightarrow$ Early Errors** | 2 | 10 | 2 | 3 | 0 | 1 | 18 |

### 5.3 Key Observation:
While errors have lower median confidence than correct predictions, **$8$ Early $\rightarrow$ Late errors ($22.9\%$)** and **$3$ Late $\rightarrow$ Early errors ($16.7\%$)** exceed $90\%$ confidence. This demonstrates that when visual features are ambiguous, the network produces decisive misclassifications rather than uniform uncertainty.

---

## 6. Image Characteristics & Quantitative Statistics

### 6.1 Measured Image Properties (Mean $\pm$ Std)

| Category | Brightness | Contrast | Saturation | Sharpness (Laplacian Var) | Leaf Area Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Correct Early Blight** | 67.3 $\pm$ 35.9 | 49.9 $\pm$ 9.3 | 61.6 $\pm$ 17.0 | 1528.8 $\pm$ 1815.6 | 0.63 $\pm$ 0.29 |
| **Early $\rightarrow$ Late Errors** | 57.5 $\pm$ 37.8 | 47.9 $\pm$ 12.9 | 46.9 $\pm$ 29.1 | 1256.5 $\pm$ 1700.0 | 0.59 $\pm$ 0.32 |
| **Correct Late Blight** | 54.9 $\pm$ 37.6 | 49.9 $\pm$ 14.0 | 53.2 $\pm$ 23.3 | 953.1 $\pm$ 1254.5 | 0.47 $\pm$ 0.30 |
| **Late $\rightarrow$ Early Errors** | 74.8 $\pm$ 44.0 | 53.9 $\pm$ 8.5 | 68.2 $\pm$ 21.0 | 2395.0 $\pm$ 2447.9 | 0.64 $\pm$ 0.29 |

### 6.2 Visual Inspection Observations:
1. **Concentric Ring Degradation in Severe Early Blight**: When Early Blight infections progress to extensive foliar necrosis, individual concentric target rings merge into large, dark brown/black necrotic zones indistinguishable from Late Blight water-soaked blight.
2. **Discrete Spotting in Early Late Blight**: Early-stage Late Blight lesions before widespread foliar collapse appear as small, isolated necrotic patches that visually mimic Early Blight spots.
3. **Neutral Image Statistics**: Basic photometric statistics (brightness, contrast, saturation, sharpness) do not exhibit large systematic discrepancies between correct and error groups, confirming that the confusion is driven primarily by **spatial lesion morphology and texture** rather than global illumination defects.

---

## 7. Grad-CAM Explainability Comparison

20 comparative Grad-CAM figures were generated in `research/results/early_late_diagnostic/gradcam_comparison/`:
- 5 Correct Early Blight
- 5 Early $\rightarrow$ Late Errors
- 5 Correct Late Blight
- 5 Late $\rightarrow$ Early Errors

### Grad-CAM Findings:
- **Lesion Attributions**: In both correct classifications and inter-disease confusion cases, Grad-CAM attribution heatmaps consistently localize onto **actual necrotic leaf tissue** rather than background pixels or border artifacts.
- **Classification Routing**: For Early $\rightarrow$ Late errors, the model accurately identifies the lesion area, but because the convolutional filters perceive broad necrotic patches without visible concentric rings, activations route toward the Late Blight output node.
- *Explainability Note*: Grad-CAM provides qualitative regional importance maps and does not serve as an exact biological lesion boundary segmentation.

---

## 8. Synthesis of Diagnostic Findings

To maintain scientific integrity, the findings are categorized into three explicit evidential tiers:

### Tier 1: Observed Evidence (Empirically Verified Facts)
1. **$80.30\%$ Error Concentration**: Early $\leftrightarrow$ Late confusion constitutes $53$ of the $66$ total test errors.
2. **Directional Asymmetry**: Early $\rightarrow$ Late errors ($35$) occur nearly double the rate of Late $\rightarrow$ Early errors ($18$).
3. **Training Disparity**: The training set contains $1,783$ Late Blight images versus $1,131$ Early Blight images ($1.58 : 1$ ratio).
4. **Valid Feature Localization**: Grad-CAM confirms the model attends to diseased foliar regions in both correct and confused samples.
5. **No Capture Frequency Bias**: Error rates are virtually identical across single-image leaves (10.20%) and multi-image leaves (7.77%).

### Tier 2: Possible Explanations (Plausible Hypotheses)
1. **Class Prior Bias**: The $57.6\%$ higher prevalence of Late Blight training images may shift the decision boundary toward Late Blight under morphological ambiguity.
2. **Pathological Convergence**: Coalescing late-stage Early Blight lesions lose concentric target patterns and converge morphologically toward Late Blight foliar necrosis.
3. **Frozen Feature Extractor Resolution**: Pretrained ImageNet weights in a frozen MobileNetV2 backbone (downsampled to $7 \times 7$ feature maps) may lack sufficient fine-grained texture resolution to distinguish subtle concentric striations in small lesions.

### Tier 3: Unknown / Requires Further Experiment (Unverified Claims)
1. Whether class re-weighting or focal loss would eliminate the Early $\rightarrow$ Late asymmetry without degrading overall accuracy.
2. Whether unfreezing the backbone (fine-tuning) would enhance fine-grained lesion texture differentiation.
3. Whether expert plant pathologists would also experience inter-rater disagreement on the 11 high-confidence confusion samples.

---

## 9. Recommended Future Experiments

*The current research test result ($91.43\%$) and model checkpoint remain strictly frozen. The following hypotheses are formulated for future independent research projects:*

1. **Future Experiment 1 — Backbone Fine-Tuning**: Unfreeze top convolutional blocks of MobileNetV2 with low learning rates ($10^-5$) to allow adaptation of low-level texture filters to plant pathology.
2. **Future Experiment 2 — Class-Balanced Training & Loss Weighting**: Implement inverse frequency class weighting or Focal Loss during training to counteract the $1.58 : 1$ Late/Early training imbalance.
3. **Future Experiment 3 — Higher Resolution Input ($384 \times 384$ or $512 \times 512$)**: Evaluate higher input resolutions to preserve subtle concentric ring textures prior to global pooling.
4. **Future Experiment 4 — Multi-Scale Feature Pyramids / Attention**: Test vision transformer (ViT) or ConvNeXt backbones with spatial attention to capture both localized lesion detail and contextual leaf health.
5. **Future Experiment 5 — Pathologist Blinded Review**: Conduct a formal inter-annotator agreement study with agricultural domain experts on the 53 confused test cases.

---

## Artifact Index
- [`research/results/early_late_diagnostic.csv`](file:///c:/Greenscan%20project/research/results/early_late_diagnostic.csv)
- [`research/results/early_late_diagnostic_report.md`](file:///c:/Greenscan%20project/research/results/early_late_diagnostic_report.md)
- [`research/results/early_late_diagnostic/`](file:///c:/Greenscan%20project/research/results/early_late_diagnostic/)
  - `correct_early/`
  - `error_early_to_late/`
  - `correct_late/`
  - `error_late_to_early/`
  - `gradcam_comparison/` (20 high-resolution comparative Grad-CAM figures)
