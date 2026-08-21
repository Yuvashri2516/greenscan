# Conclusion

This paper presents GreenScan, an explainable decision support system designed to classify plant diseases and estimate relative severity. By combining HSV color space leaf segmentation, an EfficientNet-B0 backbone, and Grad-CAM spatial activation mapping, GreenScan addresses the "black box" limitation of traditional classification CNNs.

Our findings demonstrate that GreenScan achieves a classification accuracy of 91.76% on a validation dataset of 1,505 solanaceous leaf images, with an average warm inference latency of ~1.19 seconds. 

The primary contribution of this work is the GreenScan Severity Analyzer (GSA) engine. By isolating Grad-CAM activations within the leaf mask boundary, the GSA computes a relative Plant Health Score (PHS) on a 0-100 scale. This score translates model attention maps into severity tiers (Healthy, Mild, Moderate, Severe), providing actionable recommendations for farmers.

Model explainability is essential for building trust in AI-driven agricultural tools. Visualizing spatial attention maps helps farmers and pathologists verify that the model is focusing on actual disease features rather than background noise.

While clinical severity validation and correlation indices remain pending expert annotations, the GreenScan framework provides a solid foundation for transparent, quantitative crop diagnostics. Future work will focus on completing expert validation campaigns, integrating pixel-level lesion segmentation, and deploying models to mobile edge devices.
