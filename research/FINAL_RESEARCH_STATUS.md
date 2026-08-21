# Final Research Status

This document provides the final research and validation readiness overview for the GreenScan system.

---

## 1. Readiness Dashboard

- **Dataset:** `READY`
  *Details:* 7,525 images total (6,020 training, 1,505 validation subset), 3 classes, fully verified preprocessing and augmentations.
  
- **Classification Evaluation:** `READY`
  *Details:* Overall accuracy of 91.76% and macro F1-score of 91.68% verified on a 20% validation subset.
  
- **GSA Evaluation:** `READY`
  *Details:* Health Score (PHS) calculated via reproducible spatial attention mathematical models.
  
- **Expert Validation:** `PENDING`
  *Details:* Labels in `gsa_expert_validation.csv` are blank. Agricultural expert annotation campaign is in progress.
  
- **Pixel-Level Validation:** `NOT AVAILABLE`
  *Details:* Pixel-level lesion ground-truth masks are unavailable. Intersection over Union (IoU) is not calculated.
  
- **Threshold Validation:** `READY`
  *Details:* GSA sensitivity metrics analyzed across five activation threshold values ($\tau \in [0.40, 0.80]$).
  
- **Robustness Testing:** `READY`
  *Details:* Evaluated across low resolution (66.67%), blurring (46.67%), dark illumination (73.33%), overexposure (96.67%), uneven lighting (86.67%), rotations (80.00%), and partial framing (86.67%).
  
- **Performance Testing:** `READY`
  *Details:* Warm inference latency of ~1.19 seconds and API response metrics fully verified.
  
- **Statistical Analysis:** `PARTIAL`
  *Details:* Classification and threshold sensitivity statistics are complete, but expert disease/severity agreement, Cohen's Kappa, and Spearman correlation remain pending.
  
- **Paper Readiness:** `PARTIAL`
  *Details:* Draft sections are complete, but final manuscript requires expert validation numbers.
  
- **GitHub Readiness:** `READY`
  *Details:* Repository research and scripts paths are clean and organized.
