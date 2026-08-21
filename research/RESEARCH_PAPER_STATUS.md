# Research Paper Status

This document provides a summary of the current research status, experimental evidence, and paper draft readiness for the GreenScan project.

---

## 1. Project Status Dashboard

- **Research Contribution:**
  `CLEAR`
  *Description:* Legitimate frame focuses on Explainable disease classification + Grad-CAM spatial attention + OpenCV HSV leaf contours + relative severity estimation via GSA scoring + actionable decision support.

- **Experimental Evidence:**
  `SUFFICIENT`
  *Description:* Classification performance and GSA threshold experiments were successfully evaluated on a 1,505 validation subset image dataset.

- **Expert Validation:**
  `PENDING`
  *Description:* Agricultural pathology expert annotations in `expert_annotation_task/gsa_expert_validation.csv` are blank. Spearman correlation and Cohen's Kappa coefficients are pending.

- **Ground-Truth Lesion Masks:**
  `NOT AVAILABLE`
  *Description:* Models do not use pixel-level lesion boundary annotations. Grad-CAM represents spatial model attention, not direct lesion segmentation.

- **Classification Results:**
  `AVAILABLE`
  *Description:* Overall accuracy is 91.76%, macro F1-score is 91.68% (verified from `greenscan_metrics.json`).

- **GSA Results:**
  `AVAILABLE`
  *Description:* Average Plant Health Scores (Early Blight: 49.47, Late Blight: 58.37, Healthy: 97.63) and threshold sensitivities calibrated across $\tau \in [0.40, 0.80]$ are fully documented.

- **Paper Readiness:**
  `MORE VALIDATION REQUIRED`
  *Description:* While draft sections (Abstract, Intro, Methodology, Results) are prepared, the final manuscript requires completion of the expert validation campaign to establish biological correlation metrics.

- **GitHub Readiness:**
  `READY`
  *Description:* Research folder structure is cleaned and organized.

---

## 2. Directory Layout of Paper Drafts

Draft sections are available in [`research/paper/`](file:///c:/Greenscan%20project/research/paper/):
- [**Title Options**](file:///c:/Greenscan%20project/research/paper/title_options.md): 5 scientifically appropriate paper titles.
- [**Abstract**](file:///c:/Greenscan%20project/research/paper/abstract.md): Background, problem, method, and verified outcomes.
- [**Introduction**](file:///c:/Greenscan%20project/research/paper/introduction.md): Structured agricultural problem context and contributions.
- [**Related Work**](file:///c:/Greenscan%20project/research/paper/related_work.md): Search keywords and themes.
- [**Methodology**](file:///c:/Greenscan%20project/research/paper/methodology.md): Technical pipeline stages.
- [**Experiments**](file:///c:/Greenscan%20project/research/paper/experiments.md): Preprocessing, data augmentations, and training configurations.
- [**Results**](file:///c:/Greenscan%20project/research/paper/results.md): Populated metrics and GSA stats tables.
- [**Discussion**](file:///c:/Greenscan%20project/research/paper/discussion.md): Separating classification confidence from physical severity.
- [**Limitations**](file:///c:/Greenscan%20project/research/paper/limitations.md): Transparency regarding Grad-CAM boundaries and pending status.
- [**Future Work**](file:///c:/Greenscan%20project/research/paper/future_work.md): Outlining expert correlation and semantic segmentation steps.
- [**Conclusion**](file:///c:/Greenscan%20project/research/paper/conclusion.md): Main summary.
- [**Figures**](file:///c:/Greenscan%20project/research/paper/figures.md): Detailed schematics list.
- [**Tables**](file:///c:/Greenscan%20project/research/paper/tables.md): Pre-populated validation statistics tables.
- [**References to Collect**](file:///c:/Greenscan%20project/research/paper/references_to_collect.md): Keywords and bibliography guide.
