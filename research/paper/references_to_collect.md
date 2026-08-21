# References to Collect

This document lists the literature references, databases, and papers to collect when compiling the bibliography for the GreenScan research paper.

---

## 1. Core Reference Categories

### A. Deep Learning Backbones in Agriculture
- **Focus:** Papers describing the application of lightweight CNNs (like MobileNetV2 and EfficientNet-B0) to crop disease classification.
- **Key Papers to Find:**
  - *EfficientNet:* Tan, M., & Le, Q. V. (2019). "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks." arXiv preprint arXiv:1905.11946.
  - *MobileNetV2:* Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). "MobileNetV2: Inverted Residuals and Linear Bottlenecks." IEEE CVPR.
  - *Agricultural Applications:* Look for papers in *Computers and Electronics in Agriculture* describing MobileNet/EfficientNet models evaluated on the PlantVillage dataset.

### B. Explainable AI and Class Activation Mapping (Grad-CAM)
- **Focus:** Foundations of class activation mapping and its application to agricultural image explainability.
- **Key Papers to Find:**
  - *Grad-CAM:* Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). "Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization." IEEE ICCV.
  - *CAM:* Zhou, B., Khosla, A., Lapedriza, A., Oliva, A., & Torralba, A. (2016). "Learning Deep Features for Discriminative Localization." IEEE CVPR.
  - *XAI in Agriculture:* Search for review articles on explainable deep learning models for plant pathology in journals like *Frontiers in Plant Science* or *IEEE Access*.

### C. Image Segmentation and Leaf Boundaries
- **Focus:** Preprocessing and segmentation algorithms in agricultural image processing.
- **Key Papers to Find:**
  - *Otsu Thresholding:* Otsu, N. (1979). "A Threshold Selection Method from Gray-Level Histograms." IEEE Transactions on Systems, Man, and Cybernetics.
  - *HSV Color Masking:* Search for classical computer vision papers on color-based segmentation for weed detection and canopy extraction.

### D. Plant Pathology and Disease Severity Scales
- **Focus:** Standard agronomic scoring systems used to measure crop disease severity in the field.
- **Key Papers to Find:**
  - *Horsfall-Barratt Scale:* Horsfall, J. G., & Barratt, R. W. (1945). "An Improved Method for Measuring Plant Disease." Phytopathology.
  - *Severity Estimation:* Look for computer vision papers comparing automated severity indexing with manual visual scales.

---

## 2. Recommended Search Queries
Use the following queries on academic search engines (e.g., Google Scholar, Scopus, IEEE Xplore):
- `"Explainable AI" AND "plant disease classification"`
- `"Grad-CAM" AND "agriculture" AND "severity"`
- `"EfficientNet-B0" AND "tomato leaf disease"`
- `"leaf segmentation" AND "HSV color space" AND "OpenCV"`
- `"crop disease severity estimation" AND "deep learning"`
