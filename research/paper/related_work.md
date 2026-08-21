# Related Work

This section outlines the literature themes, search keywords, and research areas relevant to explainable plant pathology classification and severity estimation.

---

## 1. Core Literature Themes

### A. CNN-based Plant Disease Classification
- *Focus:* Review the evolution of CNN architectures (from AlexNet and VGG to ResNet and MobileNet) applied to datasets like PlantVillage. Discuss how these models achieve high classification accuracies on crops but typically lack explanations or severity outputs.
- *Search Keywords:* `CNN plant disease classification`, `PlantVillage dataset deep learning`, `convolutional neural networks crop disease`.

### B. EfficientNet for Agricultural Deployment
- *Focus:* Review the benefits of EfficientNet architectures, specifically EfficientNet-B0, which uses compound scaling (balancing depth, width, and resolution) to achieve high performance with a fraction of the parameter count, making it ideal for mobile/web deployment.
- *Search Keywords:* `EfficientNet-B0 plant disease`, `compound scaling agriculture computer vision`, `lightweight CNN crop diagnosis`.

### C. Explainable AI (XAI) in Agriculture
- *Focus:* Review the transition toward transparent deep learning in precision agriculture. Analyze why black-box models cause distrust among growers and the necessity of interpreting model reasoning to validate scientific findings.
- *Search Keywords:* `Explainable AI agriculture`, `XAI crop protection`, `interpretable deep learning plant pathology`.

### D. Grad-CAM for Visual Explanations in Crop Science
- *Focus:* Inspect the use of Gradient-weighted Class Activation Mapping (Grad-CAM) to generate coarse localization maps highlighting the final convolutional layer's gradients. Discuss how Grad-CAM has been used to debug models and provide visual validation in crop disease classification.
- *Search Keywords:* `Grad-CAM plant disease`, `Class Activation Mapping crop features`, `visual explanations deep learning agriculture`.

### E. Plant Disease Severity Estimation
- *Focus:* Review methodologies for estimating disease severity, including traditional visual assessment scales (e.g., Horsfall-Barratt scale), and computer vision approaches like semantic segmentation, clustering, and thresholding. Compare relative spatial scoring with exact lesion area calculations.
- *Search Keywords:* `plant disease severity estimation`, `automated crop severity indexing`, `lesion area computation computer vision`.

### F. Leaf Segmentation and Preprocessing
- *Focus:* Examine methods to isolate leaf structures from background noise (e.g., soil, pots, shadows) using thresholding, color space conversions (HSV, Lab), and active contours to focus CNN/Grad-CAM analysis solely on leaf biomass.
- *Search Keywords:* `leaf segmentation HSV color space`, `background subtraction agricultural images`, `OpenCV leaf region of interest`.

### G. Precision Agriculture Decision Support
- *Focus:* Analyze decision support systems (DSS) that translate computer vision diagnostic outputs into practical remedies, including fertilizer adjustments, spray dosage calculations, and localized risk forecasting.
- *Search Keywords:* `agricultural decision support system AI`, `precision crop treatment DSS`, `precision farming dosage calculator`.
