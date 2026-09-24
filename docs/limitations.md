# GreenScan — Research Limitations & Operational Scope

This document outlines the known scientific limitations, boundary conditions, and operational scope of the GreenScan tomato leaf disease detection system.

---

## 1. Taxonomic & Crop Scope Limitations

1. **Single-Crop Domain**: The current evaluation is restricted entirely to tomato foliage (*Solanum lycopersicum*). Performance cannot be assumed or generalized to other solanaceous crops (e.g., potato, eggplant, pepper) without dedicated training and cross-crop validation.
2. **Three-Class Taxonomy**: The classification system models three specific conditions: *Tomato Early Blight*, *Tomato Late Blight*, and *Tomato Healthy*. It does not diagnose other common tomato foliar afflictions such as *Septoria* leaf spot, bacterial spot (*Xanthomonas*), powdery mildew, or viral infections (e.g., Tomato Yellow Leaf Curl Virus). Exposure to unrepresented diseases may result in out-of-distribution misclassification.

---

## 2. Morphological Ambiguity & Biological Boundaries

1. **Coalescent Necrotic Lesions**: In advanced stages of Early Blight infection, concentric "target-board" ring structures degrade as necrotic tissue merges into diffuse patches, closely resembling Late Blight lesions. Deep learning visual feature extractors remain susceptible to inter-disease confusion in such edge cases ($82.26\%$ of all test errors).
2. **Multi-Pathogen Co-Infection**: The model assumes a single dominant label per image and has not been trained or evaluated on leaves exhibiting concurrent dual infections (e.g., Early Blight and Late Blight on the same leaf specimen).

---

## 3. Dataset & Environmental Domain Shift

1. **Dataset-Specific Pretraining & Distribution**: The benchmark metrics were established on the clean, group-stratified PlantVillage tomato leaf partition. Laboratory and controlled-illumination characteristics may not fully capture the variability of real-world agricultural fields.
2. **Field Environment Generalization**: Performance under extreme field conditions—including harsh direct sunlight, intense specular reflections, heavy deep shadows, high-density leaf overlap, severe wind motion blur, soil splatter, and non-foliar background clutter—requires empirical validation through dedicated in-field pilot trials.
3. **Sensor & Camera Heterogeneity**: Images were collected using specific digital camera sensors; variance across lower-end smartphone sensors, lens distortions, and automatic white-balance algorithms may impact prediction reliability.

---

## 4. Confidence Interpretation & Decision-Support Role

1. **Uncalibrated Softmax Probabilities**: Softmax output confidence scores should **not** be interpreted as mathematically calibrated posterior probabilities. As observed in error analysis, high-confidence misclassifications ($>90\%$ confidence) occur on ambiguous samples.
2. **Decision-Support Classification**: GreenScan is engineered as an **assistive agronomic decision-support heuristic** for farmers, agricultural extension workers, and agronomists. It is **not** a certified biological or diagnostic authority, and predictions should be complemented with physical field inspection and local expert agronomic consultation.
