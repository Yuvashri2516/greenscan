# Future Work

The following directions are identified as the most impactful extensions to GreenScan+. None of these directions is currently implemented.

---

## F1. Expert Pathologist Validation (Highest Priority)

The most critical near-term priority is completing the expert annotation campaign. The 90-sample composite annotation package is ready for expert review. Completing annotations will enable:
- Disease classification agreement measurement
- PHS-to-expert-severity Spearman correlation
- Cohen's Kappa for severity tier agreement
- Statistical basis for threshold selection (τ optimization with ground truth)

Expansion to a larger expert-validated sample (n > 200) would further improve the reliability of reported agreement metrics.

---

## F2. Pixel-Level Lesion Annotation

Acquiring or creating pixel-level lesion annotation masks for a subset of evaluation images would enable:
- Intersection over Union (IoU) measurement between Grad-CAM activated regions and true lesion boundaries
- Quantitative validation of the spatial attention claim
- Threshold selection optimization against ground-truth lesion boundaries
- Comparison with dedicated semantic segmentation architectures (U-Net, DeepLab)

This is a significant manual annotation effort and may benefit from crowdsourced annotation platforms.

---

## F3. Semantic Segmentation Integration

While GreenScan+ currently uses HSV-based colour segmentation, future work could integrate a deep semantic segmentation model (e.g., U-Net, DeepLabV3+) trained on lesion-annotated data. This would provide:
- Direct pixel-level lesion boundary delineation
- A more defensible "lesion area percentage" metric
- Quantitative comparison with Grad-CAM attention regions

---

## F4. Additional Disease Classes

Expanding the supported disease taxonomy to include:
- Tomato Septoria Leaf Spot (*Septoria lycopersici*)
- Tomato Bacterial Spot (*Xanthomonas campestris*)
- Tomato Mosaic Virus
- Tomato Yellow Leaf Curl Virus
- Additional solanaceous crop diseases (pepper, potato)

This requires both additional annotated training data and re-training/fine-tuning of the classification backbone.

---

## F5. Field Dataset Collection and Validation

A dedicated field image collection campaign (using mobile cameras under realistic agricultural conditions) would enable:
- Evaluation of model performance under real-world imaging variability
- Training augmentation with genuine field-acquired samples
- Reduced distribution shift between training and deployment environments

---

## F6. Mobile (Android/iOS) Deployment and Testing

The Android Kotlin application source code requires:
- Full build and compilation testing
- Integration testing with a physical device and camera
- Offline inference mode (TensorFlow Lite model conversion and deployment)
- App store readiness review

TensorFlow Lite model conversion would reduce inference latency and remove server dependency for mobile users.

---

## F7. Multi-Crop and Multi-Disease Platform

Extending GreenScan+ beyond tomato to a broader multi-crop platform would require:
- A larger, hierarchically organized disease taxonomy
- Per-crop recommendation knowledge bases
- A routing mechanism to direct input images to appropriate per-crop models
- Significantly larger and more diverse training datasets

---

## F8. Longitudinal Health Tracking

The current SQLite scan history stores individual scan records. A future enhancement could:
- Track PHS over multiple scans of the same plant or field section
- Visualize temporal disease progression
- Generate trend-based alerts when PHS declines consistently
- Integrate with calendar or irrigation management systems

---

## F9. Agronomist Network Integration

Connecting GreenScan+ outputs to a network of certified agronomists would enable:
- On-demand expert second opinions
- Verification and correction of automated outputs
- Collection of high-quality expert annotations for ongoing model improvement

---

## F10. Comparative Architecture Study

A systematic comparison of classification backbone architectures (EfficientNetB0, B3, B7, MobileNetV3, ViT, ConvNeXt) under identical training conditions would provide:
- Empirical basis for architecture selection
- Accuracy vs. latency trade-off analysis
- Reproducible benchmark for the tomato disease classification task
