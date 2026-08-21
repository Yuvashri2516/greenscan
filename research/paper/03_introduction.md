# Introduction

## 1. Background and Motivation

Tomato (*Solanum lycopersicum*) is one of the most economically significant vegetable crops worldwide, cultivated across diverse climatic zones for food, nutrition, and commercial export. Global tomato production exceeds 180 million tonnes annually, yet crop losses attributable to foliar diseases routinely reduce yields by 20–30% and, under severe epidemic conditions, approach total crop failure [citation needed from literature review].

Among the most economically consequential tomato diseases are Early Blight, caused by the necrotrophic fungus *Alternaria solani*, and Late Blight, caused by the oomycete *Phytophthora infestans* — the latter being historically responsible for the Irish Potato Famine of 1845–1852. Both diseases manifest as visually distinguishable lesion patterns on foliar tissue but differ substantially in their infection kinetics, optimal environmental conditions, and effective treatment regimens.

## 2. Limitations of Conventional Detection

Traditional disease identification in field settings depends predominantly on visual inspection by farmers or extension workers. This approach is subject to several well-documented limitations:

- **Subjectivity and inconsistency:** Diagnosis quality varies with the experience of the observer. Early-stage infection patterns are frequently misidentified or confused between disease classes.
- **Delay:** Symptoms may not become visually unambiguous until infection has already progressed beyond the optimal intervention window.
- **Scalability:** Individual expert inspection of large plantations is time-consuming and economically impractical.
- **Accessibility:** In smallholder agricultural contexts — which constitute the majority of global tomato production — trained plant pathologists are rarely accessible.

## 3. Computer Vision and Deep Learning for Plant Disease Detection

The widespread availability of mobile camera technology and the rapid development of convolutional neural networks (CNNs) have enabled a new paradigm of automated, image-based crop disease detection. Seminal work using the PlantVillage dataset demonstrated that CNNs could achieve high classification accuracy across dozens of crop-disease combinations under controlled imaging conditions [citation needed]. Subsequent research explored progressively more efficient architectures — including VGG, ResNet, InceptionNet, MobileNet, and the EfficientNet family — achieving competitive accuracy with reduced computational overhead.

However, the majority of these systems function as black-box classifiers, providing only a predicted class label and a confidence score. This creates two practical problems:

1. **Lack of spatial explanation:** The farmer cannot see *which part* of the leaf influenced the model's decision, reducing trust and making error investigation impossible.
2. **Confidence ≠ Severity:** A model's classification confidence (e.g., 99.9% certainty that a leaf has Early Blight) communicates nothing about *how much* of the leaf is affected. A single small spot may trigger equally high confidence as a leaf that is 60% necrotic.

## 4. Explainable AI in Agricultural Diagnostics

Explainability methods — particularly Gradient-weighted Class Activation Mapping (Grad-CAM) — have emerged as practical tools for visualizing the spatial attention patterns that drive CNN predictions. Grad-CAM generates a coarse activation heatmap by computing the gradient of the predicted class score with respect to the activations of the final convolutional layer, producing a spatial map that highlights regions most relevant to the classification decision.

Applying Grad-CAM to plant disease images provides a visually interpretable overlay that allows end users to verify that the model is focusing on genuine lesion regions rather than artefactual background features. This addresses the "right answer for the wrong reason" failure mode common in black-box classifiers.

## 5. Research Gap

Despite the maturity of CNN-based plant disease classification and the availability of Grad-CAM explainability tools, the combination of:

- Automated disease classification
- Visual spatial attention explanation
- Leaf-region-constrained attention analysis
- Quantitative relative health scoring derived from attention statistics
- Integrated farmer-oriented treatment recommendations

...has not been systematically integrated into a unified, web-deployed, open-architecture decision support platform targeting tomato disease. Existing systems tend to address one or two of these objectives in isolation. GreenScan+ is motivated by this integration gap.

> **Note:** A claim that GreenScan+ is the *first* system of its kind would require a comprehensive systematic literature review, which has not been completed at the time of writing. This paper accordingly claims an *integration contribution* rather than a priority claim.

## 6. Contributions

This paper presents the following contributions:

1. **Disease Classification:** Fine-tuning of EfficientNet-B0 on a 7,525-image tomato leaf dataset (three classes: Healthy, Early Blight, Late Blight) achieving 91.76% validation accuracy.

2. **Image Quality Pipeline:** An OpenCV-based preprocessing module performing Laplacian blur detection, CLAHE contrast normalization, bilateral noise filtering, and HSV-based quality assurance prior to inference.

3. **Leaf Segmentation:** A hybrid HSV colour-space and Otsu-threshold segmentation module that isolates the leaf foreground from image backgrounds, enabling attention analysis to be restricted to actual leaf pixels.

4. **Grad-CAM Explainability:** Integration of Gradient-weighted Class Activation Mapping to produce spatial activation heatmaps aligned with the model's prediction rationale.

5. **GreenScan Severity Analyzer (GSA):** A novel post-hoc spatial attention analysis engine that applies a configurable activation threshold (τ = 0.60 by default), computes attention-affected region percentage and mean activation intensity, and derives a normalized Plant Health Score (PHS, 0–100 scale).

6. **Severity Classification Framework:** A four-tier severity taxonomy (Healthy ≥ 90, Mild 70–89, Moderate 40–69, Severe < 40) mapped to traffic-light indicators and treatment priority guidance.

7. **Integrated Decision Support Interface:** A full-stack web application (React + FastAPI) with scan history, disease information, treatment recommendations, soil health advisory, dosage calculator, and AI chatbot.

The remainder of this paper is organized as follows: Section 2 reviews related work; Section 3 presents the methodology; Section 4 describes the experimental setup; Section 5 reports results; Section 6 discusses findings and limitations; Section 7 concludes.
