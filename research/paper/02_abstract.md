# Abstract

**Title:** GreenScan+: An Explainable Deep Learning Framework for Tomato Disease Classification and Spatial Attention-Based Plant Health Assessment

---

## Structured Abstract

**Background:**
Tomato (*Solanum lycopersicum*) is a globally important crop susceptible to fungal and oomycete diseases including Early Blight (*Alternaria solani*) and Late Blight (*Phytophthora infestans*). Timely and accurate disease identification is critical for preventing yield losses, yet conventional visual inspection by farmers is subjective, inconsistent, and requires trained expertise that is often inaccessible in smallholder agricultural contexts.

**Problem:**
Existing deep learning systems for plant disease classification typically report classification accuracy as the primary output, providing no spatial context for the disease manifestation. Furthermore, model confidence is frequently conflated with disease severity — a conceptual conflation that can mislead treatment decisions. The lack of explainability in black-box neural networks further reduces farmer trust and adoption.

**Method:**
GreenScan+ presents an integrated, web-deployed decision support framework comprising: (1) an EfficientNet-B0 convolutional neural network fine-tuned on 7,525 tomato leaf images across three classes (Healthy, Early Blight, Late Blight); (2) an OpenCV-based image quality assurance and CLAHE-enhanced preprocessing pipeline; (3) a hybrid HSV colour-space and Otsu-threshold leaf segmentation module; (4) Gradient-weighted Class Activation Mapping (Grad-CAM) for spatial attention visualization; and (5) the GreenScan Severity Analyzer (GSA), a novel post-hoc analysis engine that converts thresholded Grad-CAM activation statistics into a relative Plant Health Score (PHS) on a normalized 0–100 scale.

**Results:**
On a held-out 20% validation partition (n = 1,505 images), the classification backbone achieved an overall accuracy of 91.76%, a macro F1-score of 91.68%, a macro precision of 91.95%, and a macro recall of 91.83%. Per-class F1-scores were: Tomato Healthy 98.88%, Tomato Early Blight 88.67%, Tomato Late Blight 88.00%. At the default GSA activation threshold τ = 0.60, mean Plant Health Scores were 97.63 (Healthy), 49.47 (Early Blight), and 58.37 (Late Blight). Threshold sensitivity analysis was conducted across τ ∈ {0.40, 0.50, 0.60, 0.70, 0.80}. Average warm-inference API latency was 1.19 seconds.

**Limitations:**
Expert pathologist validation of GSA severity outputs against independent clinical annotations is currently pending. Pixel-level lesion ground-truth masks are unavailable for this dataset; consequently, Intersection over Union (IoU)-based validation of spatial attention accuracy cannot be performed. The system supports only three tomato-specific classes and has not been evaluated on other plant species or field conditions.

**Conclusion:**
GreenScan+ demonstrates that integrating convolutional disease classification with Grad-CAM explainability and attention-derived health scoring produces a practically accessible and scientifically interpretable agricultural decision-support system. The relative Plant Health Score provides actionable severity context beyond raw confidence, while the web-based interface enables immediate deployment without specialized hardware. GreenScan+ is not presented as a clinically validated severity measurement tool; rather, it is framed as a reproducible, explainable, and farmer-oriented AI advisory system requiring continued expert-label validation.

---

**Keywords:** Tomato Disease Classification, EfficientNet-B0, Grad-CAM, Explainable AI, Plant Health Score, GreenScan Severity Analyzer, Deep Learning, Computer Vision, Precision Agriculture
