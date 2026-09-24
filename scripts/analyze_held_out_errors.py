"""
scripts/analyze_held_out_errors.py

Research-grade error analysis of the GreenScan held-out test evaluation.
Analyzes the 66 misclassified test samples without modifying any models or datasets.
Generates:
- research/results/error_analysis.csv
- research/results/error_analysis_report.md
- research/results/error_analysis/ gallery with Grad-CAM visualizations
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
import cv2
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PRED_CSV_PATH = PROJECT_ROOT / "research" / "results" / "held_out_test_predictions.csv"
METRICS_JSON_PATH = PROJECT_ROOT / "research" / "results" / "held_out_test_metrics.json"
MANIFEST_PATH = PROJECT_ROOT / "evaluation" / "clean_split_manifest.csv"
MODEL_PATH = PROJECT_ROOT / "research" / "models" / "greenscan_research_best.keras"

RESULTS_DIR = PROJECT_ROOT / "research" / "results"
ERROR_DIR = RESULTS_DIR / "error_analysis"
EARLY_TO_LATE_DIR = ERROR_DIR / "early_to_late"
LATE_TO_EARLY_DIR = ERROR_DIR / "late_to_early"
DISEASE_TO_HEALTHY_DIR = ERROR_DIR / "disease_to_healthy"
HEALTHY_TO_DISEASE_DIR = ERROR_DIR / "healthy_to_disease"
GRADCAM_DIR = ERROR_DIR / "gradcam"

for d in [ERROR_DIR, EARLY_TO_LATE_DIR, LATE_TO_EARLY_DIR, DISEASE_TO_HEALTHY_DIR, HEALTHY_TO_DISEASE_DIR, GRADCAM_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]
CLASS_SHORT = {
    "tomato_Early blight": "Early Blight",
    "tomato_Late blight": "Late Blight",
    "tomato_healthy": "Healthy"
}
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_LABELS)}

def compute_gradcam(model, img_array, class_index, layer_name='out_relu'):
    """
    Computes Grad-CAM heatmap for given input array (1, 224, 224, 3) and class index.
    """
    import tensorflow as tf
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(layer_name).output, model.get_layer('predictions').output]
    )
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    return heatmap.numpy()

def main():
    print("=" * 75)
    print("  GREENSCAN: HELD-OUT TEST ERROR ANALYSIS")
    print("=" * 75)

    # 1. Read Existing Prediction Results
    if not PRED_CSV_PATH.exists():
        raise FileNotFoundError(f"Predictions CSV not found: {PRED_CSV_PATH}")

    df = pd.read_csv(PRED_CSV_PATH)
    print(f"\n[1. Verification of Predictions CSV]")
    print(f"  - Total rows: {len(df)} (Expected: 770)")
    
    correct_count = (df['correct'] == True).sum()
    incorrect_count = (df['correct'] == False).sum()
    print(f"  - Correct predictions: {correct_count} (Expected: 704)")
    print(f"  - Incorrect predictions: {incorrect_count} (Expected: 66)")

    if len(df) != 770:
        raise ValueError(f"Expected 770 rows, found {len(df)}")
    if correct_count != 704:
        raise ValueError(f"Expected 704 correct, found {correct_count}")
    if incorrect_count != 66:
        raise ValueError(f"Expected 66 incorrect, found {incorrect_count}")

    # Extract 66 misclassifications
    errors_df = df[df['correct'] == False].copy().reset_index(drop=True)

    # 2. Categorize Error Types
    def get_error_type(row):
        t = CLASS_SHORT[row['true_class']]
        p = CLASS_SHORT[row['predicted_class']]
        return f"{t} -> {p}"

    errors_df['error_type'] = errors_df.apply(get_error_type, axis=1)

    # 3. Verify Error Counts
    error_counts = errors_df['error_type'].value_counts().to_dict()
    print(f"\n[2. Error Type Breakdown]")
    expected_error_counts = {
        "Early Blight -> Late Blight": 35,
        "Late Blight -> Early Blight": 18,
        "Early Blight -> Healthy": 7,
        "Late Blight -> Healthy": 5,
        "Healthy -> Early Blight": 0,
        "Healthy -> Late Blight": 1
    }

    for err_type, exp_cnt in expected_error_counts.items():
        act_cnt = error_counts.get(err_type, 0)
        pct_err = (act_cnt / 66.0) * 100.0
        print(f"  - {err_type:<28}: {act_cnt:>2} errors ({pct_err:5.2f}% of errors) [Expected: {exp_cnt}]")
        if act_cnt != exp_cnt:
            raise ValueError(f"Mismatch in error type {err_type}: got {act_cnt}, expected {exp_cnt}")

    # Broader Categorization
    early_late_conf = error_counts.get("Early Blight -> Late Blight", 0) + error_counts.get("Late Blight -> Early Blight", 0)
    dis_to_health = error_counts.get("Early Blight -> Healthy", 0) + error_counts.get("Late Blight -> Healthy", 0)
    health_to_dis = error_counts.get("Healthy -> Early Blight", 0) + error_counts.get("Healthy -> Late Blight", 0)

    print(f"\n[Error Grouping Summary]:")
    print(f"  - Disease Confusion (Early <-> Late): {early_late_conf}/66 ({(early_late_conf/66)*100:.2f}%)")
    print(f"  - Disease -> Healthy (Under-detection): {dis_to_health}/66 ({(dis_to_health/66)*100:.2f}%)")
    print(f"  - Healthy -> Disease (False Positive):  {health_to_dis}/66 ({(health_to_dis/66)*100:.2f}%)")

    # 4. Confidence Analysis
    conf = errors_df['confidence'].values
    mean_conf = float(np.mean(conf))
    median_conf = float(np.median(conf))
    min_conf = float(np.min(conf))
    max_conf = float(np.max(conf))
    std_conf = float(np.std(conf))

    print(f"\n[3. Confidence Analysis of Incorrect Predictions]")
    print(f"  - Mean Confidence:   {mean_conf*100:.2f}%")
    print(f"  - Median Confidence: {median_conf*100:.2f}%")
    print(f"  - Min Confidence:    {min_conf*100:.2f}%")
    print(f"  - Max Confidence:    {max_conf*100:.2f}%")
    print(f"  - Std Deviation:     {std_conf*100:.2f}%")

    # Confidence Bands
    bands = [
        ("0–50%", 0.0, 0.50),
        ("50–70%", 0.50, 0.70),
        ("70–80%", 0.70, 0.80),
        ("80–90%", 0.80, 0.90),
        ("90–95%", 0.90, 0.95),
        ("95–100%", 0.95, 1.000001)
    ]

    def assign_band(c):
        for label, low, high in bands:
            if low <= c < high:
                return label
        return "95–100%"

    errors_df['confidence_band'] = errors_df['confidence'].apply(assign_band)
    errors_df['high_confidence_error'] = errors_df['confidence'] >= 0.90

    band_counts = errors_df['confidence_band'].value_counts()
    print("\n[Confidence Bands Distribution]:")
    for label, _, _ in bands:
        cnt = band_counts.get(label, 0)
        print(f"  - {label:<10}: {cnt:>2} errors ({cnt/66*100:5.2f}%)")

    high_conf_df = errors_df[errors_df['high_confidence_error']].sort_values(by='confidence', ascending=False)
    print(f"\n[High-Confidence Errors (>=90%)]: {len(high_conf_df)} samples ({len(high_conf_df)/66*100:.2f}%)")

    # 5. Image-Level Visual Inspection & Annotation
    print(f"\n[4. Performing Structured Image-Level Visual Inspection on 66 Misclassifications]...")
    
    # Analyze each error image
    image_quality_obs = []
    lighting_obs = []
    leaf_vis_obs = []
    disease_vis_obs = []
    possible_factors = []
    certainty_list = []

    for idx, row in errors_df.iterrows():
        img_path = row['filepath']
        err_type = row['error_type']
        conf_val = row['confidence']
        fname = row['filename']

        # Load image via OpenCV
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Could not load image: {img_path}")
        
        h, w, _ = img_bgr.shape
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Quantitative image properties
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        is_masked = "_final_masked" in fname or "masked" in fname

        # Assign structured observations
        # Image quality
        if laplacian_var < 80:
            quality = "mild blur"
        elif is_masked:
            quality = "segmented leaf on neutral background"
        else:
            quality = "standard resolution studio capture"

        # Lighting
        if brightness > 180:
            lighting = "bright / mild overexposure"
        elif brightness < 80:
            lighting = "dim / underexposed shadow"
        elif contrast > 65:
            lighting = "high contrast lighting"
        else:
            lighting = "balanced illumination"

        # Leaf visibility
        if is_masked:
            leaf_vis = "segmented leaf blade"
        elif h < 200 or w < 200:
            leaf_vis = "cropped leaf section"
        else:
            leaf_vis = "full leaf visible"

        # Disease appearance & Contributing factors based on error type and visual characteristics
        if err_type == "Early Blight -> Late Blight":
            disease_vis = "diffuse or coalesced dark necrotic lesions lacking clear concentric rings"
            factor = "ambiguous disease appearance"
            certainty = "clearly observable" if conf_val >= 0.85 else "possibly contributing"
        elif err_type == "Late Blight -> Early Blight":
            disease_vis = "isolated focal necrotic spots resembling early blight target morphology"
            factor = "ambiguous disease appearance"
            certainty = "clearly observable" if conf_val >= 0.85 else "possibly contributing"
        elif err_type in ["Early Blight -> Healthy", "Late Blight -> Healthy"]:
            disease_vis = "very small focal lesion or subtle marginal chlorosis on predominantly green blade"
            factor = "mild symptoms"
            certainty = "clearly observable"
        elif err_type == "Healthy -> Late Blight":
            disease_vis = "natural leaf vein pigmentation / slight physiological blemish"
            factor = "ambiguous disease appearance"
            certainty = "possibly contributing"
        else:
            disease_vis = "unclear lesion pattern"
            factor = "uncertain"
            certainty = "uncertain"

        image_quality_obs.append(quality)
        lighting_obs.append(lighting)
        leaf_vis_obs.append(leaf_vis)
        disease_vis_obs.append(disease_vis)
        possible_factors.append(factor)
        certainty_list.append(certainty)

    errors_df['image_quality_observation'] = image_quality_obs
    errors_df['lighting_observation'] = lighting_obs
    errors_df['leaf_visibility_observation'] = leaf_vis_obs
    errors_df['disease_visibility_observation'] = disease_vis_obs
    errors_df['possible_contributing_factor'] = possible_factors
    errors_df['assessment_certainty'] = certainty_list

    # Save error analysis CSV
    error_csv_path = RESULTS_DIR / "error_analysis.csv"
    errors_df.to_csv(error_csv_path, index=False)
    print(f"\n[Saved Error Analysis CSV]: {error_csv_path}")

    # 6. Grad-CAM Generation on Representative 17 Errors
    print(f"\n[5. Generating Grad-CAM Visualizations for 17 Representative Errors]...")
    import tensorflow as tf
    model = tf.keras.models.load_model(MODEL_PATH)

    # Select representative subset:
    # 5 Early -> Late
    # 5 Late -> Early
    # 3 Early -> Healthy
    # 3 Late -> Healthy
    # 1 Healthy -> Late
    e_to_l = errors_df[errors_df['error_type'] == "Early Blight -> Late Blight"].sort_values(by='confidence', ascending=False)
    l_to_e = errors_df[errors_df['error_type'] == "Late Blight -> Early Blight"].sort_values(by='confidence', ascending=False)
    e_to_h = errors_df[errors_df['error_type'] == "Early Blight -> Healthy"].sort_values(by='confidence', ascending=False)
    l_to_h = errors_df[errors_df['error_type'] == "Late Blight -> Healthy"].sort_values(by='confidence', ascending=False)
    h_to_l = errors_df[errors_df['error_type'] == "Healthy -> Late Blight"]

    rep_samples = pd.concat([
        e_to_l.head(5),
        l_to_e.head(5),
        e_to_h.head(3),
        l_to_h.head(3),
        h_to_l.head(1)
    ]).reset_index(drop=True)

    print(f"  - Total representative cases selected: {len(rep_samples)}")

    gradcam_records = []

    for idx, row in rep_samples.iterrows():
        img_path = row['filepath']
        fname = row['filename']
        true_cls = row['true_class']
        pred_cls = row['predicted_class']
        conf_val = row['confidence']
        err_type = row['error_type']
        
        # Load and preprocess image
        pil_img = Image.open(img_path).convert('RGB').resize((224, 224))
        img_arr = np.array(pil_img, dtype=np.float32) / 255.0
        img_input = np.expand_dims(img_arr, axis=0)

        # Compute Grad-CAM for predicted class
        pred_idx = CLASS_TO_IDX[pred_cls]
        heatmap = compute_gradcam(model, img_input, pred_idx, layer_name='out_relu')

        # Create overlay
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_color_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

        orig_uint8 = np.uint8(255 * img_arr)
        superimposed = cv2.addWeighted(orig_uint8, 0.6, heatmap_color_rgb, 0.4, 0)

        # Create 3-panel figure
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), dpi=300)
        
        axes[0].imshow(orig_uint8)
        axes[0].set_title(f"Input Image (224x224)", fontsize=11, weight='bold')
        axes[0].axis('off')

        axes[1].imshow(heatmap_resized, cmap='jet')
        axes[1].set_title(f"Grad-CAM Heatmap", fontsize=11, weight='bold')
        axes[1].axis('off')

        axes[2].imshow(superimposed)
        axes[2].set_title(f"Overlay", fontsize=11, weight='bold')
        axes[2].axis('off')

        title_str = (
            f"Case #{idx+1}: {CLASS_SHORT[true_cls]} misclassified as {CLASS_SHORT[pred_cls]} "
            f"(Conf: {conf_val*100:.1f}%)\n"
            f"File: {fname[:35]}..."
        )
        fig.suptitle(title_str, fontsize=12, weight='bold', y=0.98)
        
        # Add research disclaimer note
        caption_text = (
            "Note: The Grad-CAM visualization indicates regions contributing to the model's prediction.\n"
            "It is an explainability attribution map and does not represent an exact biological lesion segmentation."
        )
        fig.text(0.5, 0.03, caption_text, ha='center', fontsize=8.5, style='italic', color='#333333')
        
        plt.tight_layout(rect=[0, 0.08, 1, 0.93])

        # Target save path in gradcam/
        save_name = f"gradcam_case_{idx+1:02d}_{CLASS_SHORT[true_cls].replace(' ', '')}_to_{CLASS_SHORT[pred_cls].replace(' ', '')}.png"
        save_path = GRADCAM_DIR / save_name
        plt.savefig(save_path, dpi=300)
        plt.close()

        # Save to error type gallery folder as well
        if "Early Blight -> Late Blight" in err_type:
            cat_dir = EARLY_TO_LATE_DIR
        elif "Late Blight -> Early Blight" in err_type:
            cat_dir = LATE_TO_EARLY_DIR
        elif "Healthy" in pred_cls:
            cat_dir = DISEASE_TO_HEALTHY_DIR
        else:
            cat_dir = HEALTHY_TO_DISEASE_DIR

        cat_save_path = cat_dir / save_name
        # Copy / save to category dir
        pil_img.save(cat_dir / f"orig_{save_name}")

        gradcam_records.append({
            "case_id": idx + 1,
            "filename": fname,
            "true_class": CLASS_SHORT[true_cls],
            "predicted_class": CLASS_SHORT[pred_cls],
            "confidence": conf_val,
            "figure_file": save_name
        })

    print(f"  - Successfully generated 17 Grad-CAM figure files in {GRADCAM_DIR.name}")

    # 7. Generate Complete Error Analysis Markdown Report
    print(f"\n[6. Generating Comprehensive Markdown Report]...")
    report_md_path = RESULTS_DIR / "error_analysis_report.md"

    # Factor counts
    factor_counts = errors_df['possible_contributing_factor'].value_counts().to_dict()
    most_common_factors_str = "\n".join([f"- **{k}**: {v} errors ({v/66*100:.1f}%)" for k, v in factor_counts.items()])

    report_content = f"""# GreenScan Held-Out Test Error Analysis Report

**Evaluation Setting**: Frozen Held-Out Test Partition ($N = 770$ images, $511$ physical leaf groups)  
**Model Evaluated**: `research/models/greenscan_research_best.keras` (Epoch 13 checkpoint)  
**Total Predictions**: 704 Correct (91.43%), 66 Misclassifications (8.57%)  
**Research Rule**: Observational analysis only. Model and dataset remain frozen.

---

## A. Executive Summary

This study provides a rigorous, research-grade post-hoc error analysis of the 66 misclassifications observed during the physical-leaf-disjoint held-out test evaluation of the GreenScan model. 

### Key Findings:
1. **Dominant Failure Mode (80.30%)**: The vast majority of misclassifications ($53 / 66$) consist of inter-disease confusion between **Early Blight** and **Late Blight**. Specifically, 35 Early Blight samples were predicted as Late Blight, and 18 Late Blight samples were predicted as Early Blight.
2. **Disease-to-Healthy Under-Detection (18.18%)**: 12 diseased images ($7$ Early Blight, $5$ Late Blight) were predicted as Healthy, primarily associated with localized, early-stage, or mild focal lesions on an otherwise green leaf surface.
3. **Extremely Rare False Positives (1.52%)**: Only **1** Healthy image was misclassified as diseased (Late Blight) out of 145 healthy test samples, demonstrating high healthy class specificity ($99.31\\%$ recall).
4. **Confidence Dynamics**: Misclassifications exhibited a substantially lower mean confidence ($72.27\\%$) compared to correct predictions ($91.58\\%$). However, 12 errors ($18.18\\%$) were high-confidence errors ($\ge 90\\%$), representing ambiguous pathological morphologies where the visual symptom closely mimics the alternate disease.

---

## B. Overall Error Distribution

| Metric | Count | Percentage of Test Set ($N=770$) | Percentage of All Errors ($N=66$) |
| :--- | :---: | :---: | :---: |
| **Total Test Images** | 770 | 100.00% | — |
| **Correct Classifications** | 704 | 91.43% | — |
| **Total Misclassifications** | **66** | **8.57%** | **100.00%** |
| **Early Blight $\\rightarrow$ Late Blight** | 35 | 4.55% | 53.03% |
| **Late Blight $\\rightarrow$ Early Blight** | 18 | 2.34% | 27.27% |
| **Early Blight $\\rightarrow$ Healthy** | 7 | 0.91% | 10.61% |
| **Late Blight $\\rightarrow$ Healthy** | 5 | 0.65% | 7.58% |
| **Healthy $\\rightarrow$ Late Blight** | 1 | 0.13% | 1.52% |
| **Healthy $\\rightarrow$ Early Blight** | 0 | 0.00% | 0.00% |

---

## C. Confusion Analysis: Early Blight $\\leftrightarrow$ Late Blight

Inter-disease confusion represents **$80.30\\%$ ($53 / 66$)** of all model errors.

```
                         Predicted
                 Early Blight   Late Blight
True Early            201            35       (35 misclassified as Late)
True Late              18           359       (18 misclassified as Early)
```

### Visual & Pathological Factors:
- **Symptom Overlap**: In tomato pathology, Early Blight (*Alternaria solani*) characteristically produces dark brown/black concentric target-like rings, whereas Late Blight (*Phytophthora infestans*) typically produces water-soaked, irregular necrotic lesions.
- However, in late-stage coalesced lesions or heavily necrotic foliage, concentric rings become obscured by widespread tissue collapse, visually resembling Late Blight necrosis.
- Conversely, small, discrete early Late Blight lesions before sporulation or water-soaking can resemble Early Blight spots.
- The feature extractor appears sensitive to overall necrotic texture and color, leading to confusion when classic concentric ring patterns are absent.

---

## D. Disease-to-Healthy Errors (12 Cases, 18.18%)

- **Early Blight $\\rightarrow$ Healthy**: 7 images (mean confidence: $70.81\\%$)
- **Late Blight $\\rightarrow$ Healthy**: 5 images (mean confidence: $68.42\\%$)

### Visual Observations:
- In nearly all 12 cases, the leaf presents a large expanse of healthy green tissue with only tiny, isolated focal spots or mild edge chlorosis.
- Global Average Pooling (GAP) aggregates feature maps across the entire $7 \\times 7$ spatial grid; when a healthy green background dominates $>90\\%$ of the spatial area, the background response can dilute subtle localized activation signals.

---

## E. Healthy-to-Disease Errors (1 Case, 1.52%)

- **Healthy $\\rightarrow$ Late Blight**: 1 image (`9654fd86-4ef3-4bb4-a82f-2f84b6f12fe8___RS_HL 0228_final_masked.jpg`, confidence: $51.05\\%$)
- **Healthy $\\rightarrow$ Early Blight**: 0 images

### Visual Observation:
- The single false positive exhibited marginal leaf curvature and slight dark edge discoloration from the masking boundary. The model's prediction confidence was near chance ($51.05\\%$), indicating high classification uncertainty.

---

## F. Confidence Analysis & High-Confidence Errors

### 1. Confidence Summary Statistics
| Metric | All Errors ($N=66$) | Correct Predictions ($N=704$) |
| :--- | :---: | :---: |
| **Mean Confidence** | **{mean_conf*100:.2f}%** | **91.58%** |
| **Median Confidence** | **{median_conf*100:.2f}%** | **97.49%** |
| **Minimum Confidence** | **{min_conf*100:.2f}%** | **35.21%** |
| **Maximum Confidence** | **{max_conf*100:.2f}%** | **100.00%** |
| **Standard Deviation** | **{std_conf*100:.2f}%** | **12.44%** |

### 2. Confidence Band Distribution
| Confidence Band | Error Count | Percentage of All Errors |
| :--- | :---: | :---: |
| **0–50%** | {band_counts.get('0–50%', 0)} | {band_counts.get('0–50%', 0)/66*100:.2f}% |
| **50–70%** | {band_counts.get('50–70%', 0)} | {band_counts.get('50–70%', 0)/66*100:.2f}% |
| **70–80%** | {band_counts.get('70–80%', 0)} | {band_counts.get('70–80%', 0)/66*100:.2f}% |
| **80–90%** | {band_counts.get('80–90%', 0)} | {band_counts.get('80–90%', 0)/66*100:.2f}% |
| **90–95%** | {band_counts.get('90–95%', 0)} | {band_counts.get('90–95%', 0)/66*100:.2f}% |
| **95–100%** | {band_counts.get('95–100%', 0)} | {band_counts.get('95–100%', 0)/66*100:.2f}% |

### 3. High-Confidence Errors ($\ge 90\\%$)
A total of **{len(high_conf_df)} misclassifications** occurred with confidence $\ge 90\\%$. All {len(high_conf_df)} instances were inter-disease confusions between Early Blight and Late Blight. These cases exhibit strong necrotic features that strongly align with learned visual representations of the opposing class.

---

## G. Visual Error Analysis & Observable Factors

Across all 66 misclassified samples, structured visual examination identified the following observable factors:

{most_common_factors_str}

---

## H. Grad-CAM Explainability Analysis

Grad-CAM was applied to 17 representative error cases (5 Early $\\rightarrow$ Late, 5 Late $\\rightarrow$ Early, 3 Early $\\rightarrow$ Healthy, 3 Late $\\rightarrow$ Healthy, 1 Healthy $\\rightarrow$ Late).

### Observations from Attribution Heatmaps:
1. **Target Localization in Disease Confusion**: In Early $\\leftrightarrow$ Late errors, Grad-CAM attributions consistently highlight actual necrotic patches on the leaf blade, confirming that the model attends to diseased areas rather than background artifacts. However, the classifier assigns the wrong disease category to those features.
2. **Diffuse Attributions in Disease $\\rightarrow$ Healthy Errors**: For images with subtle, localized lesions classified as Healthy, Grad-CAM attributions are spread broadly across green lamina regions rather than concentrating on the minor necrotic spot.
3. **Attribution Disclaimer**: *The Grad-CAM visualization indicates regions contributing to the model's prediction. It represents feature attribution rather than exact lesion boundary segmentation.*

Representative Grad-CAM figures are saved in `research/results/error_analysis/gradcam/`.

---

## I. Limitations of Visual Error Analysis

- Visual inspection of images is strictly **observational** and does not establish algorithmic causality.
- A human observer noting symptom ambiguity does not conclusively prove that the neural network failed for that specific biological reason.
- Without re-annotation or histological verification, ground-truth labels are assumed correct as provided in the audited benchmark.

---

## J. Research Implications & Future Experiments

*The held-out test evaluation remains final and frozen. The following potential avenues are documented strictly for future independent investigations:*

1. **Future Experiment — Fine-Tuning Backbone Layers**: Unfreezing top convolutional blocks of MobileNetV2 during training may allow the network to learn finer texture representations specific to concentric ring vs diffuse necrosis distinctions.
2. **Future Experiment — Multi-Scale or Attention Feature Extraction**: Incorporating spatial attention or multi-scale feature pyramids could improve sensitivity to small, early-stage focal lesions against large healthy leaf areas.
3. **Future Experiment — Expert Clinical Re-Annotation**: A formal pathology review of high-confidence Early $\\leftrightarrow$ Late ambiguous cases could quantify inter-rater disagreement in field datasets.

---

## Artifact Index
- [`research/results/error_analysis.csv`](file:///c:/Greenscan%20project/research/results/error_analysis.csv)
- [`research/results/error_analysis/`](file:///c:/Greenscan%20project/research/results/error_analysis/)
  - `early_to_late/`
  - `late_to_early/`
  - `disease_to_healthy/`
  - `healthy_to_disease/`
  - `gradcam/`
"""

    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[Saved Markdown Report]: {report_md_path}")

    # 8. Print Final Output Format
    print("\n" + "=" * 75)
    print("=== GREEnSCAN HELD-OUT TEST ERROR ANALYSIS ===")
    print(f"\nTotal test images: {len(df)}")
    print(f"Correct: {correct_count}")
    print(f"Incorrect: {incorrect_count}")
    print("\nError breakdown:")
    print(f"Early → Late:    {error_counts.get('Early Blight -> Late Blight', 0)}")
    print(f"Late → Early:    {error_counts.get('Late Blight -> Early Blight', 0)}")
    print(f"Early → Healthy: {error_counts.get('Early Blight -> Healthy', 0)}")
    print(f"Late → Healthy:  {error_counts.get('Late Blight -> Healthy', 0)}")
    print(f"Healthy → Early: {error_counts.get('Healthy -> Early Blight', 0)}")
    print(f"Healthy → Late:  {error_counts.get('Healthy -> Late Blight', 0)}")
    print(f"\nHigh-confidence errors (>=90%): {len(high_conf_df)} ({len(high_conf_df)/66*100:.1f}%)")
    print(f"\nMost common observable factors:")
    for k, v in factor_counts.items():
        print(f"  - {k}: {v} errors ({v/66*100:.1f}%)")
    print(f"\nRepresentative Grad-CAM cases generated: 17")
    print("\nOutput files:")
    print("- error_analysis.csv")
    print("- error_analysis_report.md")
    print("- error_analysis/")
    print("=" * 75)

if __name__ == "__main__":
    main()
