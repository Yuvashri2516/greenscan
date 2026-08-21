# Limitations

This section outlines the limitations of the current GreenScan system. Acknowledging these constraints is essential for maintaining scientific integrity and guiding future research.

---

## 1. Expert Validation Status (PENDING)

The most significant current limitation is that **expert severity validation is pending**. Although the GreenScan Severity Analyzer (GSA) is mathematically defined, its severity classifications (Healthy, Mild, Moderate, Severe) have not yet been validated against a completed dataset annotated by agricultural domain experts. The Spearman rank correlation and Cohen's Kappa indices between GSA predictions and expert severity labels remain uncalculated.

---

## 2. Grad-CAM Spatial Limitations

The GSA uses Grad-CAM activation mapping as a proxy for disease severity. However, Grad-CAM maps represent **model spatial attention rather than exact lesion boundaries**. Because classification CNNs are not trained on pixel-level lesion annotations, they can sometimes highlight healthy structures or surrounding areas. GSA estimates should be interpreted as relative attention-affected regions rather than exact biological lesion percentages.

---

## 3. Dataset and Class Constraints

The current model was trained and evaluated on a limited dataset containing only three classes: `tomato_healthy`, `tomato_Early blight`, and `tomato_Late blight`. Under field conditions, crops are susceptible to a wider range of pathogens (e.g., bacterial spot, septoria leaf spot, tomato yellow leaf curl virus) and nutrient deficiencies. Additionally, the images in the dataset were captured under controlled lighting and background conditions, which may differ from real-world field conditions (e.g., varying daylight, soil background, overlapping leaves).

---

## 4. Pathological Class Confusion

As documented in preliminary testing, classification models can sometimes confuse early stages of Early Blight and Late Blight. In the early stages, both diseases manifest as small dark spots, which can lead to low-confidence predictions or misclassifications (such as predicting Late Blight on an Early Blight sample).
