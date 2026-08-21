import os
import cv2
import numpy as np
import pandas as pd
import random
from pathlib import Path
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from image_enhancer import enhance_leaf_image
from gradcam_engine import get_gradcam_activation_matrix
from leaf_segmenter import segment_leaf
import gsa_engine
import config

def overlay_heatmap(img_bgr, heatmap, alpha=0.4):
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    return cv2.addWeighted(heatmap_colored, alpha, img_bgr, 1 - alpha, 0)

import config

DATASET_PATH = PROJECT_ROOT / "dataset"
MODEL_PATH = PROJECT_ROOT / "model" / "greenscan_model.keras"
CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

OUTPUT_DIR = PROJECT_ROOT / "gsa_visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)
EXAMPLES_DIR = PROJECT_ROOT / "gsa_research_examples"
EXAMPLES_DIR.mkdir(exist_ok=True)

THRESHOLDS = [0.40, 0.50, 0.60, 0.70, 0.80]

def main():
    print("Loading Model...")
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    # Load validation sample
    test_files = []
    for cls in CLASS_LABELS:
        cls_dir = DATASET_PATH / cls
        all_imgs = list(cls_dir.glob("*.JPG")) + list(cls_dir.glob("*.jpg"))
        random.seed(42)
        if all_imgs:
            sample = random.sample(all_imgs, min(30, len(all_imgs)))
            for img_path in sample:
                test_files.append((img_path, cls))
                
    results = []
    examples_saved = {cls: 0 for cls in CLASS_LABELS}
    
    for idx, (img_path, true_class) in enumerate(test_files):
        if idx % 10 == 0:
            print(f"Processing Image {idx+1}/{len(test_files)}")
            
        orig_img = cv2.imread(str(img_path))
        if orig_img is None: continue
        
        enhanced_bgr, _ = enhance_leaf_image(orig_img)
        leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)
        
        rgb_img = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        input_arr = np.expand_dims(rgb_img.astype(np.float32) / 255.0, axis=0)
        
        preds = model.predict(input_arr, verbose=0)
        pred_idx = int(np.argmax(preds[0]))
        conf = float(np.max(preds[0]))
        pred_class = CLASS_LABELS[pred_idx]
        
        gradcam = get_gradcam_activation_matrix(model, input_arr, pred_idx)
        
        # Test multiple thresholds
        for thresh in THRESHOLDS:
            gsa_engine.GRADCAM_THRESHOLD = thresh
            gsa_res = gsa_engine.run_gsa_pipeline(gradcam, leaf_mask, leaf_pixels, conf, pred_class)
            
            results.append({
                "Image ID": img_path.name,
                "Disease": true_class,
                "Predicted Disease": pred_class,
                "Threshold": thresh,
                "Confidence": conf,
                "Affected Region %": gsa_res["attention_affected_region_percent"],
                "Weighted Activation": gsa_res["mean_leaf_activation"],
                "Health Score": gsa_res["plant_health_score"],
                "Severity": gsa_res["severity_level"]
            })
            
        # Save 3 examples per class for research validation using default threshold (0.60)
        if examples_saved[true_class] < 3:
            gsa_engine.GRADCAM_THRESHOLD = 0.60
            gsa_res = gsa_engine.run_gsa_pipeline(gradcam, leaf_mask, leaf_pixels, conf, pred_class)
            
            # Visualize
            plt.figure(figsize=(15, 3))
            
            # 1. Original
            plt.subplot(1, 5, 1)
            plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
            plt.title("Original")
            plt.axis('off')
            
            # 2. Leaf Mask
            plt.subplot(1, 5, 2)
            plt.imshow(leaf_mask, cmap='gray')
            plt.title("Leaf Mask")
            plt.axis('off')
            
            # 3. Grad-CAM overlay
            heatmap_resized = cv2.resize(gradcam, (224, 224))
            overlay = overlay_heatmap(enhanced_bgr, heatmap_resized)
            plt.subplot(1, 5, 3)
            plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
            plt.title("Grad-CAM Overlay")
            plt.axis('off')
            
            # 4. Thresholded Activation
            plt.subplot(1, 5, 4)
            activation_mask = np.where((heatmap_resized >= 0.60) & (leaf_mask == 1), 1, 0)
            plt.imshow(activation_mask, cmap='jet')
            plt.title("Activation Mask (>=0.60)")
            plt.axis('off')
            
            # 5. Stats
            plt.subplot(1, 5, 5)
            plt.axis('off')
            stat_text = (
                f"Conf: {conf*100:.1f}%\n"
                f"Affected: {gsa_res['attention_affected_region_percent']:.1f}%\n"
                f"W. Activ: {gsa_res['mean_leaf_activation']:.3f}\n"
                f"Health: {gsa_res['plant_health_score']}\n"
                f"Severity: {gsa_res['severity_level']}"
            )
            plt.text(0.1, 0.5, stat_text, fontsize=12, verticalalignment='center')
            
            plt.tight_layout()
            plt.savefig(EXAMPLES_DIR / f"example_{true_class}_{examples_saved[true_class]}.png")
            plt.close()
            examples_saved[true_class] += 1

    df = pd.DataFrame(results)
    
    # --- Output 1: Threshold Analysis ---
    thresh_summary = df.groupby(['Threshold', 'Disease']).agg({
        'Affected Region %': ['mean', 'std'],
        'Weighted Activation': 'mean',
        'Health Score': 'mean'
    }).reset_index()
    # Flatten multi-index columns
    thresh_summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in thresh_summary.columns.values]
    thresh_summary.to_csv(PROJECT_ROOT / "gsa_threshold_analysis.csv", index=False)
    
    # --- Output 2: Disease Statistics at Default Threshold (0.60) ---
    df_060 = df[df['Threshold'] == 0.60]
    disease_stats = df_060.groupby('Disease').agg({
        'Confidence': 'mean',
        'Affected Region %': ['mean', 'median', 'std'],
        'Weighted Activation': 'mean',
        'Health Score': 'mean'
    }).reset_index()
    disease_stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in disease_stats.columns.values]
    disease_stats.to_csv(PROJECT_ROOT / "gsa_disease_statistics.csv", index=False)
    
    # --- Output 3: Full Analysis ---
    df_060.to_csv(PROJECT_ROOT / "gsa_severity_analysis.csv", index=False)
    
    # --- Output 4: Manual Validation Template ---
    template_df = df_060[['Image ID', 'Disease', 'Confidence', 'Affected Region %', 'Health Score']].copy()
    template_df['expert_severity'] = ""
    template_df['comments'] = ""
    template_df.to_csv(PROJECT_ROOT / "gsa_manual_validation_template.csv", index=False)
    
    # --- Generating Visualizations ---
    sns.set_theme(style="whitegrid")
    
    # 1. Affected Region Distribution
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_060, x="Disease", y="Affected Region %")
    plt.title("Affected Region % Distribution by Disease")
    plt.savefig(OUTPUT_DIR / "affected_region_dist.png")
    plt.close()
    
    # 2. Health Score Distribution
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_060, x="Disease", y="Health Score")
    plt.title("Health Score Distribution by Disease")
    plt.savefig(OUTPUT_DIR / "health_score_dist.png")
    plt.close()
    
    # 3. Confidence vs Affected Region
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df_060, x="Confidence", y="Affected Region %", hue="Disease")
    plt.title("Confidence vs Affected Region %")
    plt.savefig(OUTPUT_DIR / "conf_vs_affected.png")
    plt.close()
    
    # 4. Confidence vs Health Score
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df_060, x="Confidence", y="Health Score", hue="Disease")
    plt.title("Confidence vs Health Score")
    plt.savefig(OUTPUT_DIR / "conf_vs_health.png")
    plt.close()
    
    # 5. Threshold Sensitivity
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=df, x="Threshold", y="Affected Region %", hue="Disease", marker="o")
    plt.title("Threshold vs Mean Affected Region %")
    plt.savefig(OUTPUT_DIR / "threshold_vs_affected.png")
    plt.close()

    print("GSA Calibration complete. Check CSVs and gsa_visualizations folder.")

if __name__ == "__main__":
    main()
