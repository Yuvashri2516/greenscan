# Discussion

## 1. Classification Performance

The EfficientNet-B0 backbone achieves an overall validation accuracy of 91.76% and a macro F1-score of 91.68% across three tomato disease classes. Per-class analysis reveals that the model performs most reliably on the Healthy class (F1 = 98.88%), with somewhat lower but still strong performance on Early Blight (88.67%) and Late Blight (88.00%).

The inter-class confusion between Early and Late Blight is the primary source of classification error. Both diseases can exhibit similar brown-green necrotic lesion patterns in intermediate stages; the key discriminating visual features (concentric rings for Early Blight, water-soaked irregular margins for Late Blight) may be subtle in compressed images or early-infection samples. This confusion is an inherent challenge of appearance-based classification and is consistent with similar findings in related PlantVillage studies.

The 91.76% accuracy figure should be interpreted with caution for the following reasons:
- The PlantVillage dataset is acquired under controlled laboratory conditions with uniform, clean backgrounds. Field images with diverse backgrounds, shadows, or partial leaf captures may produce lower accuracy.
- The robustness experiments confirm this concern: blurred images yield only 46.67% accuracy, and low-resolution images yield 66.67%.
- No field-collected tomato leaf dataset was used for training or evaluation.

---

## 2. Explainability via Grad-CAM

Grad-CAM heatmaps provide spatial attention overlays that enable qualitative verification of the model's decision rationale. For diseased samples, high-activation regions typically correspond to observable lesion areas in the original images — providing a degree of face validity for the attention mechanism.

However, the following limitations must be explicitly acknowledged:
- Grad-CAM visualizes gradient-based model attention, not a direct segmentation of physical lesion tissue.
- For healthy-class images, Grad-CAM still produces non-trivial activation maps (mean affected region 35.56% at τ = 0.60), reflecting texture-based attention patterns that do not correspond to disease.
- Quantitative correspondence between Grad-CAM activated regions and physical lesion boundaries cannot be established without pixel-level lesion ground-truth masks, which are unavailable for the PlantVillage dataset used here.

The GSA's healthy-class PHS formula (`100 − μ_leaf × 5.0`) is specifically designed to decouple healthy-sample outputs from the diseased area formula, acknowledging that healthy-class Grad-CAM activations are not disease indicators.

---

## 3. GSA and Plant Health Score Behaviour

The mean PHS values across disease classes at τ = 0.60 — Healthy: 97.63, Early Blight: 49.47, Late Blight: 58.37 — suggest that the PHS index qualitatively discriminates between healthy and diseased tissue.

The counterintuitive result that Late Blight (58.37) scores *higher* than Early Blight (49.47) despite Late Blight being generally more destructive in agronomy is explained by the GSA formula structure:
- Late Blight samples in the validation set exhibit a lower mean attention-affected region (22.67%) compared to Early Blight (33.93%).
- This lower R_τ value produces a higher PHS under the weighted formula.
- This behavior reflects the spatial distribution of Grad-CAM activations in the dataset, not a clinical assessment that Late Blight is less severe.

This observation underscores the importance of the scientific framing adopted throughout this paper: PHS is an *attention-derived relative indicator*, not a biologically validated severity metric.

---

## 4. Confidence vs. Severity — A Key Conceptual Distinction

A central contribution of GreenScan+ is the explicit separation of:
- **Classification confidence:** How certain the model is about the predicted disease class
- **Attention-affected region (R_τ):** What proportion of the leaf attention exceeds the threshold
- **Plant Health Score (PHS):** A relative health indicator derived from attention statistics

The data confirm these are independent quantities. High confidence does not imply large affected area — a single distinct lesion spot may produce 99.9% classification confidence but only 13.7% R_τ (PHS ≈ 64, Moderate). Conversely, a diffusely affected leaf may produce similar confidence with R_τ > 50% (PHS ≈ 37, Severe).

This distinction is practically significant for farmers: a confident "Early Blight" prediction combined with a PHS of 85 (Mild) suggests early-stage infection amenable to organic intervention, while the same prediction with PHS of 35 (Severe) suggests urgent chemical treatment.

---

## 5. Threshold Sensitivity

Threshold τ = 0.70 produces more spatially concentrated activation regions and eliminates more diffuse background activations. This may be preferable if the goal is to restrict analysis to regions with strong, confident gradient signals. However, without expert or pixel-level ground-truth validation, it is not possible to determine whether τ = 0.60 or τ = 0.70 better corresponds to actual physical lesion boundaries.

τ = 0.40 and τ = 0.50 produce very high affected-region percentages for healthy samples (58.4% and 46.5% respectively), indicating that lower thresholds incorporate diffuse background activations that are not disease-relevant. This observation supports the exclusion of lower threshold values as defaults.

---

## 6. Expert Validation Status

Expert validation remains the critical missing component of GreenScan+'s scientific validation. The prepared 90-sample annotation package, which combines original leaf images with Grad-CAM overlays and GSA outputs, awaits review by an agricultural pathologist.

Until expert labels are collected:
- Disease classification agreement between GreenScan+ and expert diagnosis cannot be quantified
- PHS-to-expert-severity correlation (Spearman ρ) cannot be calculated
- Cohen's Kappa for severity tier agreement cannot be reported

These metrics are explicitly left blank in the results tables. Any version of this paper submitted to peer review should either include completed expert validation data or clearly frame their absence as a limitation requiring future work.

---

## 7. System Performance and Practical Deployment

A warm inference latency of approximately 1.19 seconds places GreenScan+ in a practical operating range for interactive web-based diagnosis. The complete pipeline — from image upload to structured JSON response including recommendations — completes within a single user interaction cycle.

The system's reliance on a Python virtual environment and locally hosted model means that deployment requires a server with Python 3.10+, TensorFlow, and approximately 4–8 GB RAM (TensorFlow working memory). Cloud deployment on a mid-tier VM is feasible.
