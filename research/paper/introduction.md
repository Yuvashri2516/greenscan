# Introduction

Foliar plant diseases present a significant risk to global agricultural productivity, causing extensive crop failures and threatening food security worldwide. Among solanaceous crops, tomatoes (*Solanum lycopersicum*) are highly vulnerable to devastating fungal and oomycete pathogens such as Early Blight (*Alternaria solani*) and Late Blight (*Phytophthora infestans*). If left unmanaged, these pathogens can decimate entire fields within days, highlighting the critical importance of early and accurate disease identification.

Traditionally, crop disease diagnostics have relied on visual inspection by agricultural experts or laboratory-based assays. However, manual inspections are slow, labor-intensive, and prone to subjective error, while laboratory methods require specialized equipment and long turnaround times, rendering them impractical for rapid field operations.

To address these challenges, deep learning and computer vision frameworks have emerged as powerful tools for automated plant disease classification. Convolutional neural networks (CNNs) have shown near-human performance in recognizing visual symptoms directly from field photos. Despite their high classification accuracy, traditional classification-only systems have two major limitations:

1. **The Black Box Problem:** CNN models do not explain why they made a prediction. An algorithm might classify a leaf as diseased by focusing on background dirt, shadows, or image artifacts rather than the actual lesion, which limits trust among domain experts and growers.
2. **Lack of Severity Quantitation:** Standard classifiers only output categorical labels and certainty scores (confidence) rather than estimating the severity of the infection. For example, a model might predict "Late Blight" with 99% confidence on both a leaf with a single spot and a leaf that is completely decayed.

To overcome these barriers, there is an urgent research gap for frameworks that combine model explainability (interpreting what features drive predictions) with relative health/severity estimation.

### Proposed GreenScan Solution
This paper introduces GreenScan, an explainable decision support system designed to address the black box and severity quantitation problems. The system combines:
1. **EfficientNet-B0 Backbone:** A lightweight convolutional network optimized for mobile and edge deployment.
2. **OpenCV HSV Segmentation:** A preprocessing pipeline that isolates the leaf structure and filters out background noise.
3. **Grad-CAM Attention Mapping:** A visual explainability layer that highlights the spatial regions in the final convolutional layer that influenced the prediction.
4. **GreenScan Severity Analyzer (GSA):** A novel heuristic engine that calculates a 0-100 Plant Health Score (PHS) based on the spatial coverage and intensity of Grad-CAM activations inside the segmented leaf boundaries.

### Core Contributions
The primary contributions of this work are:
- **Interpretable Agricultural Diagnostics:** We implement Grad-CAM visual attention mapping alongside HSV-based OpenCV leaf segmentation, enabling growers to visually verify that the model is focusing on pathology features rather than background clutter.
- **Novel Severity Indexing (GSA):** We define and implement the GreenScan Severity Analyzer (GSA), translating spatial Grad-CAM activations inside the segmented leaf boundary into a quantitative 0-100 Plant Health Score (PHS) and severity tiers (Healthy, Mild, Moderate, Severe).
- **Distinction of Confidence vs. Severity:** We mathematically separate classification certainty (confidence) from infection severity (PHS), providing a more realistic assessment for treatment planning.
- **Actionable Decision Support:** We integrate explainable metrics with precise agricultural calculators (organic/chemical dosage dilution per acre, soil NPK diagnostics, and interactive chatbot context) to deliver immediate, field-ready support.
