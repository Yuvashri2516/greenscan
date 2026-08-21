# Future Work

This section outlines realistic future research directions to improve the accuracy, validation, and applicability of the GreenScan framework.

---

## 1. Expert Annotation Campaign

Completing the expert annotation campaign is a high priority. Agricultural domain experts will evaluate the validation dataset to fill out the `expert_disease` and `expert_severity` columns in `gsa_expert_validation.csv`. Once these annotations are complete, we will compute:
- **Spearman Rank Correlation:** To assess the relationship between the GSA Plant Health Score (PHS) and expert severity ratings.
- **Cohen's Kappa Coefficient:** To measure the agreement between GSA-assigned severity tiers and expert classifications.

---

## 2. Transition to Pixel-Level Lesion Segmentation

To transition from relative spatial attention mapping to exact disease area calculations, future iterations will implement semantic segmentation models (such as U-Net, Mask R-CNN, or Segment Anything Model). This requires:
- Generating pixel-level lesion masks to train the model.
- Evaluating model performance using **Intersection over Union (IoU)** and Dice coefficients against ground-truth masks.

---

## 3. Dataset Expansion

To improve model generalization, the dataset will be expanded to include:
- A wider variety of tomato leaf diseases (e.g., Bacterial Spot, Septoria, Spider Mites, Yellow Leaf Curl).
- Other solanaceous crops (e.g., potatoes, eggplants, bell peppers).
- Images captured across multiple geographical locations under varying field conditions (e.g., natural sunlight, wet foliage, complex canopy backgrounds).

---

## 4. Advanced Modeling Techniques

Future software updates will explore:
- **Uncertainty-Aware Predictions:** Implementing Bayesian neural networks or MC-Dropout to output confidence intervals alongside categorical classifications.
- **Temporal Disease Progression:** Analyzing time-series images to model the rate of pathogen spread and predict future crop health.
- **On-Device Edge Optimization:** Quantizing models (e.g., converting to TensorFlow Lite or ONNX formats) to enable offline diagnostics on mobile devices.
