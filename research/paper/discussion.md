# Discussion: Classification Certainty vs. Visual Severity

This section discusses the conceptual and mathematical differences between classification confidence and infection severity within the GreenScan framework.

---

## 1. Classification Confidence vs. Disease Severity

A common point of confusion in deep-learning-based plant diagnostics is the interpretation of model confidence. Model confidence (classification certainty) and disease severity are fundamentally different metrics:

- **Classification Confidence ($C_{\text{class}}$):** This is the softmax probability output by the final layer of the network. It represents the model's certainty that the input image contains features characteristic of a specific class. For example, a model might be 99% certain that a leaf exhibits Late Blight, even if the leaf has only a single small lesion.
- **Disease Severity:** This represents the physical extent of the pathogen's spread across the leaf surface. A leaf with a single lesion has low disease severity, whereas a leaf covered in necrotic spots has high disease severity.

In traditional classification systems, a high confidence score is often misinterpreted as indicating a severe infection. In GreenScan, we address this by separating classification confidence from severity. The model classifies the disease type (establishing confidence), while the GreenScan Severity Analyzer (GSA) computes the Plant Health Score (PHS) to estimate relative severity.

---

## 2. Grad-CAM as Spatial Attention, Not Semantic Lesion Masks

It is important to qualify how GSA calculates the Attention-Affected Region Percentage:

- **Model Attention:** Grad-CAM maps highlight the image regions that contributed most to the network's prediction. They represent where the model is looking, not necessarily the exact boundary of the physical lesions.
- **Segmentation Limitations:** Unlike semantic segmentation models (such as U-Net or Mask R-CNN) trained on pixel-level lesion annotations, a classification CNN with Grad-CAM does not generate precise lesion masks.
- **Relative Indexing:** The GSA's estimated affected region percentage is a relative indicator of spatial attention, not a direct measurement of physical biomass decay. It serves as a proxy for severity, providing a defensible way to estimate health without requiring pixel-level annotations during training.

---

## 3. Interpreting Spurious Activations in Healthy Leaves

In the evaluation of healthy leaves (`tomato_healthy`), the mean Grad-CAM activation inside the leaf boundary was 35.56%. This indicates that even when classifying a leaf as healthy, the model focuses on specific leaf structures (such as veins, margins, or lighting variations). 

To prevent these healthy features from reducing the Plant Health Score, the GSA uses a dedicated formula for healthy leaves:
$$\text{PHS}_{\text{healthy}} = 100 - (\text{MeanLeafActivation} \times 5.0)$$
This ensures that healthy leaves maintain a score above 90.0, avoiding false severity alerts.
