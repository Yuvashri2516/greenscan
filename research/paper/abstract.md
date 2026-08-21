# Abstract

**Background:** Early identification and control of crop pathogens are vital to global food security. While deep learning convolutional neural networks (CNNs) have achieved high classification accuracy, they act as "black boxes" that fail to explain their predictions or estimate disease severity, hindering agricultural adoption.

**Problem:** Standard classification pipelines output confidence scores indicating certainty in classification rather than physical disease severity. Furthermore, a lack of transparency prevents experts from verifying model rationale, limiting deployment in field operations.

**Method:** We propose GreenScan, an explainable decision support system that integrates plant disease classification, visual spatial attention mapping, and leaf-aware severity indexing. The pipeline pre-processes leaf samples, segments the region of interest using HSV-based OpenCV algorithms, and classifies foliar condition using an EfficientNet-B0 backbone. GreenScan generates Gradient-weighted Class Activation Maps (Grad-CAM) at the final convolutional layer to visualize spatial model attention.

**Innovation:** We introduce the GreenScan Severity Analyzer (GSA), an engine that isolates Grad-CAM intensities inside the segmented leaf boundary. The GSA calculates a Plant Health Score (PHS) on a 0-100 scale by combining the spatial extent of thresholded activation (threshold = 0.60) and the average intensity of features. These scores translate directly into severity tiers (Healthy, Mild, Moderate, Severe) and trigger precise organic and chemical chemical remedies.

**Experimental Evaluation:** The system was evaluated using 1,505 validation images split across three classes (490 healthy, 504 early blight, and 511 late blight). The classification model achieved an overall accuracy of 91.76%, a macro-averaged precision of 91.95%, and an F1-score of 91.68%. At a Grad-CAM threshold of 0.60, the GSA mapped diseased leaves to moderate (895) and severe (63) tiers, maintaining an average inference response latency of 1.19 seconds.

**Limitations:** Spatial activations indicate model attention zones rather than semantic lesion boundaries. Biologically exact severity metrics and Spearman correlations are currently pending as clinical domain expert validation remains in progress.

**Conclusion:** By coupling explainable deep learning outputs with structural leaf segmentations, GreenScan provides a scientifically defensible method to build agricultural trust and deliver precision decision support.
