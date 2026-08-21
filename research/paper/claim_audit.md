# Claim Audit — GreenScan+ Research Paper

This document audits every major scientific claim made in the GreenScan+ paper against available evidence.

**Classification:**
- ✅ **SUPPORTED** — Directly confirmed by code, experiments, or verified data
- ⚠️ **PARTIALLY SUPPORTED** — Plausible and directionally supported but lacks complete validation
- ❌ **NOT SUPPORTED** — Not established by current evidence; must not be claimed without further validation

---

## Classification Claims

| Claim | Classification | Evidence |
|---|---|---|
| "EfficientNet-B0 backbone is used for classification" | ✅ SUPPORTED | `scripts/train_disease.py`, `backend/main.py`, `model/greenscan_model.keras` |
| "Three tomato disease classes are supported" | ✅ SUPPORTED | `CLASS_LABELS` in `main.py`, `DISEASE_DB` in `disease_db.py` |
| "Overall validation accuracy is 91.76%" | ✅ SUPPORTED | `research/final_results/classification_results.csv` from `evaluate_greenscan.py` |
| "Macro F1-score is 91.68%" | ✅ SUPPORTED | `research/final_results/classification_results.csv` |
| "Healthy class F1 = 98.88%" | ✅ SUPPORTED | `evaluate_greenscan.py` per-class output |
| "Early Blight F1 = 88.67%" | ✅ SUPPORTED | `evaluate_greenscan.py` per-class output |
| "Late Blight F1 = 88.00%" | ✅ SUPPORTED | `evaluate_greenscan.py` per-class output |
| "Validation set size is 1,505 images" | ✅ SUPPORTED | 20% of 7,525 verified from dataset directory counts |

---

## Preprocessing Claims

| Claim | Classification | Evidence |
|---|---|---|
| "CLAHE normalization applied to L channel in LAB space" | ✅ SUPPORTED | `image_enhancer.py` lines 65–74 |
| "Bilateral filter applied for edge-preserving denoising" | ✅ SUPPORTED | `image_enhancer.py` line 77 |
| "Laplacian variance used for blur detection" | ✅ SUPPORTED | `image_enhancer.py` line 26 |
| "Images resized to 224×224" | ✅ SUPPORTED | `image_enhancer.py` line 80, training scripts |
| "Pixel values normalized to [0,1]" | ✅ SUPPORTED | `main.py` line 162 |

---

## Leaf Segmentation Claims

| Claim | Classification | Evidence |
|---|---|---|
| "Leaf segmentation uses HSV colour-space masking" | ✅ SUPPORTED | `leaf_segmenter.py` lines 18–32 |
| "Green vegetation HSV range: H∈[25,95]" | ✅ SUPPORTED | `leaf_segmenter.py` lines 22–24 |
| "Necrotic brown/yellow range: H∈[5,25]" | ✅ SUPPORTED | `leaf_segmenter.py` lines 26–29 |
| "Otsu thresholding applied as secondary mask" | ✅ SUPPORTED | `leaf_segmenter.py` lines 35–37 |
| "Largest contour selected as leaf mask" | ✅ SUPPORTED | `leaf_segmenter.py` lines 50–56 |
| "This is semantic segmentation of lesions" | ❌ NOT SUPPORTED | The segmentation isolates leaf foreground from background only — it does NOT classify lesion vs healthy tissue pixels |

---

## Grad-CAM Claims

| Claim | Classification | Evidence |
|---|---|---|
| "Grad-CAM computes gradient of class score w.r.t. last conv layer" | ✅ SUPPORTED | `gradcam_engine.py` lines 62–68 |
| "Global average pooling applied to gradients" | ✅ SUPPORTED | `gradcam_engine.py` line 68 |
| "ReLU applied to retain positive activations" | ✅ SUPPORTED | `gradcam_engine.py` line 75 |
| "Heatmap normalized to [0,1]" | ✅ SUPPORTED | `gradcam_engine.py` lines 76–78 |
| "Heatmap resized to 224×224" | ✅ SUPPORTED | `gradcam_engine.py` lines 84–85 |
| "Grad-CAM provides spatial explanation of model decision" | ✅ SUPPORTED | Functionally correct description of Grad-CAM |
| "Grad-CAM represents exact lesion boundaries" | ❌ NOT SUPPORTED | Grad-CAM is gradient-based attention; no ground-truth lesion masks to validate spatial correspondence |
| "Grad-CAM measures percentage of diseased tissue" | ❌ NOT SUPPORTED | Activated region % is attention-based proxy, not lesion area |

---

## GSA Claims

| Claim | Classification | Evidence |
|---|---|---|
| "GSA applies threshold τ = 0.60 by default" | ✅ SUPPORTED | `gsa_engine.py` line 12, `config.py` line 11 |
| "AREA_WEIGHT = 0.60, ACTIVATION_WEIGHT = 0.40" | ✅ SUPPORTED | `gsa_engine.py` lines 13–14 |
| "Diseased PHS formula: 100 − (0.60×R_τ + 0.40×μ_act×100)" | ✅ SUPPORTED | `gsa_engine.py` lines 84–87 |
| "Healthy PHS formula: 100 − (μ_leaf × 5.0)" | ✅ SUPPORTED | `gsa_engine.py` line 80 |
| "Severity tiers: Healthy≥90, Mild 70–89, Moderate 40–69, Severe<40" | ✅ SUPPORTED | `gsa_engine.py` lines 92–115 |
| "Mean healthy PHS = 97.63 (at τ = 0.60)" | ✅ SUPPORTED | `research/final_results/gsa_results.csv` |
| "Mean Early Blight PHS = 49.47" | ✅ SUPPORTED | `research/final_results/gsa_results.csv` |
| "Mean Late Blight PHS = 58.37" | ✅ SUPPORTED | `research/final_results/gsa_results.csv` |
| "PHS correlates with actual disease severity" | ⚠️ PARTIALLY SUPPORTED | Directionally plausible (healthy vs diseased separation is clear); expert/ground-truth correlation not yet established |
| "GSA is validated by expert pathologists" | ❌ NOT SUPPORTED | Expert annotations are blank; validation campaign in progress |
| "PHS measures exact lesion coverage" | ❌ NOT SUPPORTED | PHS measures attention-derived proxy, not physical lesion area |

---

## Robustness Claims

| Claim | Classification | Evidence |
|---|---|---|
| "Robustness tested across 9 conditions (30 samples each)" | ✅ SUPPORTED | `evaluate_robustness.py`, 270 total tests |
| "Normal condition accuracy: 93.33%" | ✅ SUPPORTED | Robustness results CSV |
| "Blurred condition accuracy: 46.67%" | ✅ SUPPORTED | Robustness results CSV |
| "Low-resolution accuracy: 66.67%" | ✅ SUPPORTED | Robustness results CSV |
| "Overexposed accuracy: 96.67%" | ✅ SUPPORTED | Robustness results CSV |

---

## Expert Validation Claims

| Claim | Classification | Evidence |
|---|---|---|
| "Expert validation package prepared (90 samples)" | ✅ SUPPORTED | `research/expert_annotation_task/` contains 90 images and CSV |
| "Expert validation is pending" | ✅ SUPPORTED | `expert_disease`, `expert_severity` columns are empty in CSV |
| "Expert disease agreement rate = X%" | ❌ NOT SUPPORTED | Annotations blank — value unknown |
| "Cohen's Kappa = X" | ❌ NOT SUPPORTED | Annotations blank — cannot compute |
| "Spearman ρ between PHS and expert severity = X" | ❌ NOT SUPPORTED | Annotations blank — cannot compute |

---

## Pixel-Level Claims

| Claim | Classification | Evidence |
|---|---|---|
| "Pixel-level lesion masks are unavailable" | ✅ SUPPORTED | PlantVillage dataset contains no annotation masks |
| "IoU cannot be calculated" | ✅ SUPPORTED | Direct consequence of no ground-truth masks |
| "IoU of Grad-CAM vs lesions = X%" | ❌ NOT SUPPORTED | No ground-truth masks exist |

---

## System Claims

| Claim | Classification | Evidence |
|---|---|---|
| "FastAPI backend deployed on port 8001" | ✅ SUPPORTED | `main.py`, confirmed live at `GET /health` |
| "React frontend at localhost:5173" | ✅ SUPPORTED | Vite dev server confirmed |
| "SQLite scan history stored" | ✅ SUPPORTED | `database.py`, `greenscan.db` |
| "Warm inference ~1.19 seconds" | ✅ SUPPORTED | Measured latency breakdown |
| "Frontend build successful (538 kB)" | ✅ SUPPORTED | `npm run build` exit code 0 |
| "Android app tested on device" | ❌ NOT SUPPORTED | SDK environment unavailable; untested |

---

## Summary Statistics

| Classification | Count |
|---|---|
| ✅ SUPPORTED | 38 |
| ⚠️ PARTIALLY SUPPORTED | 1 |
| ❌ NOT SUPPORTED | 11 |

**All NOT SUPPORTED claims must either be removed from the manuscript or replaced with honest hedged language before submission.**
