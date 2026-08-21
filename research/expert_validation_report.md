# GreenScan Expert Validation Report

**Status:** ⏳ Expert validation pending. Genuine agricultural expert annotations are required.

---

## 1. Dataset
The validation task package consists of a curated set of **90 composite images** located at [`research/expert_annotation_task/images/`](file:///c:/Greenscan%20project/research/expert_annotation_task/images/) and a central database tracking sheet [`research/expert_annotation_task/gsa_expert_validation.csv`](file:///c:/Greenscan%20project/research/expert_annotation_task/gsa_expert_validation.csv). 
The 90 validation images correspond to:
- **tomato_healthy:** 30 samples
- **tomato_Early blight:** 30 samples
- **tomato_Late blight:** 30 samples
- **Total Images:** 90
- **Total CSV rows:** 90
- **Missing images:** 0
- **Extra images:** 0
- **Duplicate IDs:** 0

---

## 2. Expert Protocol & Workflow
The agricultural pathologist/expert must follow the independent evaluation workflow detailed in [`research/expert_validation_instructions.md`](file:///c:/Greenscan%20project/research/expert_validation_instructions.md):
1. Review the original leaf image (leftmost panel of the composite image) first.
2. Formulate an independent visual assessment of disease type and severity.
3. Treat Grad-CAM overlays only as supporting/secondary information; do not copy model focus area boundaries.
4. Record the independent classification in the `expert_disease` column (`Healthy`, `Early Blight`, `Late Blight`, or `Uncertain`).
5. Record the severity tier in the `expert_severity` column (`Healthy`, `Mild`, `Moderate`, `Severe`, or `Uncertain`).
6. Document notes/observations in `expert_comments`.

---

## 3. Disease Agreement
`PENDING / NOT AVAILABLE`
*No metrics (Accuracy, Precision, Recall, F1-Score) can be calculated because expert labels are currently blank. Data fabrication is strictly prohibited.*

---

## 4. Severity Agreement
`PENDING / NOT AVAILABLE`
*No severity agreement metrics (Accuracy, Cohen's Kappa) can be calculated because expert labels are currently blank. Data fabrication is strictly prohibited.*

---

## 5. Health Score Correlation
`PENDING / NOT AVAILABLE`
*No Spearman rank correlation coefficient can be calculated because expert labels are currently blank. Data fabrication is strictly prohibited.*

---

## 6. Threshold Sensitivity Analysis (0.60 vs 0.70)
`PENDING / NOT AVAILABLE`
*Calibration comparison of GSA threshold levels ($\tau = 0.60$ vs $\tau = 0.70$) cannot be performed because expert labels are currently blank. Data fabrication is strictly prohibited.*

---

## 7. Confusion Matrices
`PENDING / NOT AVAILABLE`
*No disease or severity confusion matrices can be generated because expert labels are currently blank. Data fabrication is strictly prohibited.*

---

## 8. Limitations
- **Lack of Expert Annotations:** The primary constraint is the pending validation status, meaning the GSA's Plant Health Score (PHS) mapping has not yet been correlated with visual pathology severity.
- **Attention vs. Lesion Boundary:** Grad-CAM is an explainability tool representing where the CNN focuses. It is not a semantic segmentation mask and can include spurious margins or healthy areas, particularly on healthy leaf tissue (which shows a mean background activation of 35.56%).
- **Controlled Imagery:** Images are captured under relatively standardized environments, which may limit validation under field canopy conditions.

---

## 9. Interpretation
Without completed expert annotations, we cannot evaluate the scientific alignment of the GSA algorithm with real-world plant pathologists. GSA remains a mathematically consistent relative severity metric derived from visual feature activations but lacks clinical validity.

---

## 10. Conclusion
The GreenScan model successfully classifies Solanaceous leaf pathology, and the GSA computes a consistent relative health index. However, the system's agronomic utility cannot be confirmed until the expert validation campaign is completed and the corresponding correlation metrics are calculated.
