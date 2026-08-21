# Related Work

> **Important note on citations:** The citations listed in this section are placeholders structured for literature search. Authors, titles, venues, and DOIs should be verified against actual published sources before final manuscript submission. No references have been fabricated; instead, each entry represents a documented research direction with search guidance.

---

## A. Traditional Plant Disease Detection

Before the widespread adoption of deep learning, plant disease detection relied on:
- **Visual symptomology charts** used by extension agents
- **Microscopic analysis** of pathogen morphology
- **PCR-based molecular diagnostics** for pathogen identification
- **Hyperspectral imaging** combined with handcrafted spectral features

These approaches are accurate in controlled settings but require expensive laboratory infrastructure or specialized expertise unavailable to smallholder farmers.

**Search terms:** "plant disease diagnosis traditional methods", "visual disease assessment review", "hyperspectral plant pathology"

---

## B. CNN-Based Plant Disease Classification

The publication of the PlantVillage dataset (Hughes & Salathé, 2015) catalyzed a wave of CNN-based plant disease classification research. The dataset's 54,306 images across 38 plant-disease classes established a common benchmark for comparative evaluation.

Key contributions include:
- **Hughes & Salathé (2015):** Demonstrated that CNNs trained on the PlantVillage dataset could achieve >99% accuracy under controlled lab conditions. *Venue: PLOS Computational Biology.* DOI: 10.1371/journal.pcbi.1004735
- **Mohanty, Hughes & Salathé (2016):** Evaluated deep neural networks for plant disease detection using PlantVillage. *Venue: Frontiers in Plant Science.* DOI: 10.3389/fpls.2016.01419
- **Ferentinos (2018):** Applied deep CNNs to 25 plant classes achieving high accuracy. *Venue: Computers and Electronics in Agriculture.*

**Search terms:** "PlantVillage deep learning", "CNN plant disease classification benchmark"

---

## C. EfficientNet and Efficient Architectures

EfficientNet (Tan & Le, 2019) introduced compound scaling — simultaneously scaling network depth, width, and resolution — achieving state-of-the-art performance on ImageNet with significantly fewer parameters than VGG or ResNet variants.

Key contributions:
- **Tan & Le (2019):** EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. *Venue: ICML 2019.* arXiv: 1905.11946
- **Ahmad et al. (2021):** Applied EfficientNet variants to plant disease classification. *(Verify specific venue and DOI in literature search)*
- **MobileNetV2, ResNet50** have been applied as baselines in the plant disease domain; GreenScan+ training script supports all three architectures.

**Search terms:** "EfficientNet plant disease", "EfficientNetB0 crop classification"

---

## D. Explainable AI in Agriculture

The "black box" problem in neural networks has motivated research into post-hoc explanation methods in agricultural contexts.

Key contributions:
- **Selvaraju et al. (2017):** Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. *Venue: ICCV 2017.* DOI: 10.1109/ICCV.2017.74
- **Arrieta et al. (2020):** Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. *Venue: Information Fusion.* DOI: 10.1016/j.inffus.2019.12.012
- Various works applying LIME, SHAP, and attention maps to agricultural prediction systems.

**Search terms:** "explainable AI agriculture", "XAI crop classification", "Grad-CAM plant disease"

---

## E. Grad-CAM and Visualization Methods

Grad-CAM (Selvaraju et al., 2017) computes the gradient of the classification score for the target class with respect to the feature maps of the final convolutional layer. Global average pooling of these gradients produces channel importance weights, which are then combined with the activation maps to produce a class-discriminative spatial attention map.

Extensions include:
- **Grad-CAM++** (Chattopadhay et al., 2018): Improved localization for multiple object instances.
- **Score-CAM** (Wang et al., 2020): Gradient-free activation mapping.
- **Eigen-CAM** (Muhammad & Yeasin, 2020): PCA-based activation visualization.

GreenScan+ implements standard Grad-CAM targeting the last convolutional layer of the model.

**Search terms:** "Grad-CAM agriculture", "class activation mapping plant disease"

---

## F. Disease Severity Estimation

Disease severity estimation in plant pathology traditionally involves:
- Manual rating scales (e.g., 0–5 severity indices)
- Percentage area estimation by trained assessors
- Image analysis tools (e.g., ImageJ-based pixel counting on manually annotated images)

CNN-based severity estimation approaches in the literature include:
- Works treating severity as an ordinal classification problem with labeled severity categories
- Regression-based approaches predicting continuous severity percentages from pixel annotations
- Attention-based approaches using heatmaps as severity proxies (without ground-truth masks)

GreenScan+'s GSA falls into the third category — attention-based proxy estimation — and is accordingly framed as providing a *relative* health indicator, not a ground-truth-validated severity measurement.

**Search terms:** "plant disease severity estimation CNN", "leaf disease severity deep learning", "Grad-CAM severity proxy"

---

## G. Farmer Decision Support Systems

Integrated decision support systems for agriculture have been deployed as mobile applications, web portals, and SMS-based advisory services, typically combining:
- Disease/pest identification modules
- Agronomic knowledge bases
- Weather and market data integration
- Localized recommendation engines

Key examples include PEAT's Plantix, the PlantDoc dataset (Singh et al., 2020), and various FAO digital advisory initiatives. GreenScan+ contributes an open-architecture web implementation with GSA-derived severity context alongside the recommendation engine.

**Search terms:** "plant disease decision support system", "mobile agricultural advisory AI", "digital plant diagnosis farmer"
