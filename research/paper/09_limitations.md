# Limitations

The following limitations apply to the current implementation and results of GreenScan+. These are reported transparently to support accurate scientific interpretation.

---

## L1. Limited Disease Scope

GreenScan+ classifies only **three tomato-specific conditions**: Healthy, Early Blight (*Alternaria solani*), and Late Blight (*Phytophthora infestans*). The system:
- Cannot identify other tomato diseases (e.g., Septoria Leaf Spot, Bacterial Spot, Mosaic Virus, Leaf Miner)
- Cannot classify diseases of other plant species (pepper, potato, wheat, rice, etc.)
- Returns only the highest-confidence class among these three, regardless of whether the input image genuinely depicts any of them

Any images of non-tomato plants, non-supported diseases, or non-plant subjects will be classified into one of the three supported classes with potentially high but misleading confidence.

---

## L2. Controlled Dataset — Limited Field Generalization

The training and validation data are sourced from the PlantVillage dataset, which was acquired under **controlled laboratory conditions**: uniform backgrounds, consistent lighting, single-leaf framing. Real agricultural field photographs exhibit:
- Variable and complex backgrounds
- Mixed lighting (shadow, direct sunlight, diffuse cloud)
- Multiple overlapping leaves in frame
- Motion blur from wind
- Lower image resolution from mobile cameras

Robustness testing on simulated degradations (Section: Results — Table 7) confirms that blur reduces accuracy to 46.67% and low resolution to 66.67%, suggesting that field performance may be substantially lower than the 91.76% controlled-setting accuracy.

---

## L3. Grad-CAM Does Not Measure Lesion Area

GreenScan+'s Grad-CAM heatmaps represent the model's gradient-based **attention** — not physical lesion segmentation. Specifically:
- The activation threshold τ = 0.60 is a heuristic parameter, not a biologically validated lesion boundary
- Healthy leaves exhibit non-trivial attention-affected regions (mean 35.56% at τ = 0.60), demonstrating that Grad-CAM activations exist in the absence of disease
- Correspondence between thresholded Grad-CAM regions and actual necrotic tissue boundaries cannot be established without pixel-level annotation masks

The GreenScan Severity Analyzer (GSA) is accordingly framed as providing a **relative attention-derived health indicator**, not a direct lesion area measurement.

---

## L4. No Pixel-Level Ground Truth

The PlantVillage dataset does not include pixel-level lesion annotation masks. Therefore:
- Intersection over Union (IoU) between activated regions and true lesion areas cannot be calculated
- No ground-truth-validated assessment of spatial attention accuracy is possible with this dataset
- Semantic segmentation metrics (Dice coefficient, boundary F1) are not applicable

---

## L5. Expert Validation Pending

The GSA severity framework has not yet been validated against independent clinical expert assessments. Specifically:
- The 90-sample expert annotation package is prepared but unannotated
- Disease classification agreement with expert pathologists is unknown
- Severity-tier agreement (Cohen's Kappa) with expert ratings is unknown
- Correlation between PHS and expert severity assessments (Spearman ρ) is unknown

Without completed expert validation, the scientific claim that "PHS correlates with disease severity" remains a hypothesis, not an empirical finding.

---

## L6. Threshold Selection is Heuristic

The GSA activation threshold τ = 0.60 was selected based on empirical observation of the severity tier distribution across the 90-sample evaluation subset. Without pixel-level or expert-labelled ground truth, it is not possible to determine which threshold value best corresponds to physical lesion boundaries. The threshold selection remains a heuristic design decision pending validation.

---

## L7. Android Component Untested

The Kotlin Android application source code is complete and reviewed, but hardware testing (build, installation, device execution, camera integration, API communication) has not been conducted due to the unavailability of an Android SDK build environment and connected device or emulator in the current development context.

---

## L8. Chatbot Dependency on External API

The AI chatbot component depends on the OpenRouter API for natural language response generation. Without a valid API key, the chatbot falls back to a rule-based response mode. The scientific validity of chatbot responses is not evaluated in this paper.

---

## L9. Absence of Multi-Lesion and Multi-Disease Scenarios

The system processes one image and produces one classification. It does not:
- Detect or count multiple distinct lesion regions
- Classify co-infections (simultaneous Early Blight and Late Blight)
- Handle images containing multiple leaves or plants
- Perform instance segmentation

---

## L10. Training Hardware Not Documented

Specific hardware details (GPU model, VRAM, training time, energy consumption) were not recorded during model training and cannot be reported retrospectively.
