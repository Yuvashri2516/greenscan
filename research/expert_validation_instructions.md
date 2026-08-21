# GreenScan GSA: Expert Validation Instructions

This document provides instructions for the agricultural expert validating the GreenScan Severity Analyzer (GSA). 

Please follow these guidelines strictly to ensure a scientifically valid validation process.

---

## 1. Validation Workflow

For each sample in the validation dataset, follow this process:

```
[Composite Image]
       │
       ▼
1. Inspect Original Leaf (left panel)
       │
       ▼
2. Independent Visual Assessment
       │
       ▼
3. Determine Disease Label
       │
       ▼
4. Determine Severity Tier
       │
       ▼
5. (Optional) Write Comments
       │
       ▼
6. Record in validation CSV
```

---

## 2. Key Instructions for the Expert

1. **Review the Original Leaf First:** Always inspect the raw leaf image (the left panel in the composite image) before examining the AI outputs.
2. **Independent Assessment:** Determine the disease classification and severity based on visible physical evidence on the leaf, rather than simply agreeing with the AI prediction.
3. **Use Grad-CAM Heatmaps as Secondary Context:** Do not follow the Grad-CAM overlay blindly. Grad-CAM represents model focus regions and is not a ground-truth segmentation. Use it only as supporting information.
4. **Assign Severity Class Separately:** Rate leaf severity based on the visible extent of pathology spots (Mild, Moderate, Severe, or Healthy). Do not try to reverse-engineer or match the numerical Plant Health Score computed by the AI.
5. **Do Not Overwrite AI Columns:** Only populate the expert columns (`expert_disease`, `expert_severity`, `expert_comments`). Do not modify the values in the AI-generated columns (`predicted_disease`, `green_scan_health_score`, `green_scan_severity`, etc.).
6. **Handle Uncertainty Honestly:** If you cannot confidently identify a disease or severity tier from the visual panel, record `"Uncertain"` in the field and document the reason in the `expert_comments` column.

---

## 3. Allowed Labels

To ensure clean validation analysis, use only the following values:

- **`expert_disease`:**
  - `Healthy`
  - `Early Blight`
  - `Late Blight`
  - `Uncertain` (if indeterminable)

- **`expert_severity`:**
  - `Healthy`
  - `Mild`
  - `Moderate`
  - `Severe`
  - `Uncertain` (if indeterminable)
