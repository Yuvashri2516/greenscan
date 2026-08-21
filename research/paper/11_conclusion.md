# Conclusion

This paper presented GreenScan+, an integrated web-based decision support system for tomato leaf disease classification and spatial attention-based plant health assessment. The system combines an EfficientNet-B0 convolutional neural network, Grad-CAM explainability, HSV-based leaf segmentation, and the novel GreenScan Severity Analyzer (GSA) into a unified, farmer-accessible platform.

## Summary of Findings

On a held-out 20% validation partition of the PlantVillage tomato subset (n = 1,505 images), the classification backbone achieved:
- **Overall accuracy: 91.76%**
- **Macro F1-score: 91.68%**
- **Per-class F1:** Healthy 98.88%, Early Blight 88.67%, Late Blight 88.00%

The GSA demonstrated qualitatively differentiated Plant Health Scores across disease classes at threshold τ = 0.60 — mean PHS of 97.63 (Healthy), 49.47 (Early Blight), and 58.37 (Late Blight) — supporting the utility of attention-derived health scoring as a severity proxy beyond raw classification confidence.

Robustness testing identified blur (46.67% accuracy) and low-resolution compression (66.67%) as the principal vulnerability conditions, providing actionable guidance for image capture quality requirements.

## Scientific Framing

The contributions of this paper are framed explicitly within their scientifically defensible scope:
- **Classification accuracy (91.76%)** is established through standard evaluation on a held-out validation partition.
- **Grad-CAM heatmaps** are presented as model attention visualizations, not direct lesion segmentations.
- **Plant Health Score** is presented as a relative, attention-derived indicator, not a clinically validated severity measurement.
- **Expert validation** of GSA severity outputs against pathologist annotations is **pending** and will be required before clinical severity claims can be supported.
- **Pixel-level IoU** validation is **not available** due to the absence of lesion annotation masks in the dataset.

## Contribution

GreenScan+ advances the integration of explainable deep learning, spatial attention analysis, and farmer-oriented decision support for plant disease management. By explicitly separating classification confidence from attention-derived severity, providing visual explanations, and packaging outputs within an accessible web interface, GreenScan+ demonstrates a technically sound and practically useful approach to AI-assisted crop disease advisory — while maintaining scientific honesty about the boundaries of its current validation evidence.

Future work will prioritize expert pathologist validation of the GSA framework, pixel-level spatial accuracy assessment, field dataset collection, and extension to additional disease classes and plant species.
