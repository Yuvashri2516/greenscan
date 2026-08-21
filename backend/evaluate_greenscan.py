import os
import cv2
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

# Import pipeline components
from image_enhancer import enhance_leaf_image
from leaf_segmenter import segment_leaf
from gradcam_engine import get_gradcam_activation_matrix
import gsa_engine

# Setup paths
DATASET_PATH = PROJECT_ROOT / "dataset"
MODEL_PATH = PROJECT_ROOT / "model" / "greenscan_model.keras"

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

def main():
    print("Loading Model...")
    model = tf.keras.models.load_model(str(MODEL_PATH))
    
    print("Setting up Dataset Generator...")
    # Note: Using the exact same seed and logic as training to hit the validation set
    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
    val_data = datagen.flow_from_directory(
        str(DATASET_PATH),
        target_size=(224, 224),
        batch_size=1,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    class_indices = val_data.class_indices
    idx_to_class = {v: k for k, v in class_indices.items()}
    print(f"Class Indices: {idx_to_class}")
    
    filepaths = val_data.filepaths
    true_labels = val_data.classes
    
    print(f"Total Test Images: {len(filepaths)}")
    
    results = []
    threshold_results = []
    
    os.makedirs(PROJECT_ROOT / "research_examples", exist_ok=True)
    examples_saved = {"tomato_Early blight": 0, "tomato_Late blight": 0, "tomato_healthy": 0}
    
    for i, (filepath, true_class_idx) in enumerate(zip(filepaths, true_labels)):
        true_class = idx_to_class[true_class_idx]
        
        # 1. OpenCV Preprocessing
        img_bgr = cv2.imread(filepath)
        if img_bgr is None:
            continue
            
        enhanced_bgr, quality_info = enhance_leaf_image(img_bgr, target_size=(224, 224))
        leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)
        
        # 2. Prediction
        rgb_img = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        input_arr = np.expand_dims(rgb_img.astype(np.float32) / 255.0, axis=0)
        
        preds = model.predict(input_arr, verbose=0)
        predicted_idx = int(np.argmax(preds[0]))
        confidence = float(np.max(preds[0]))
        predicted_class = CLASS_LABELS[predicted_idx]
        
        # 3. Grad-CAM
        gradcam_matrix = get_gradcam_activation_matrix(model, input_arr, predicted_idx)
        
        # 4. Threshold Experiment
        thresholds = [0.40, 0.50, 0.60, 0.70, 0.80]
        for t in thresholds:
            gsa_engine.GRADCAM_THRESHOLD = t
            t_res = gsa_engine.run_gsa_pipeline(gradcam_matrix, leaf_mask, leaf_pixels, confidence, predicted_class)
            
            threshold_results.append({
                "Image ID": Path(filepath).name,
                "True Class": true_class,
                "Threshold": t,
                "Attention-Affected Region %": t_res["attention_affected_region_percent"],
                "Health Score": t_res["plant_health_score"],
                "Severity": t_res["severity_level"]
            })
            
            # Save the default 0.60 result for main metrics
            if t == 0.60:
                record = {
                    "Image ID": Path(filepath).name,
                    "True Class": true_class,
                    "Predicted Class": predicted_class,
                    "Confidence": confidence,
                    "Leaf Pixels": t_res["leaf_pixels"],
                    "Activated Pixels": t_res["activated_pixels"],
                    "Activation Threshold": t_res["threshold_used"],
                    "Attention-Affected Region %": t_res["attention_affected_region_percent"],
                    "Mean Leaf Activation": t_res["mean_leaf_activation"],
                    "Mean Activated Activation": t_res["mean_activated_activation"],
                    "Weighted Activation": t_res["weighted_activation_score"],
                    "Health Score": t_res["plant_health_score"],
                    "Severity": t_res["severity_level"]
                }
                results.append(record)
                
                # Visual validation example
                if examples_saved[true_class] < 3:
                    heatmap_color = cv2.applyColorMap(np.uint8(255 * gradcam_matrix), cv2.COLORMAP_JET)
                    overlay = cv2.addWeighted(enhanced_bgr, 0.6, heatmap_color, 0.4, 0)
                    mask_vis = (leaf_mask * 255).astype(np.uint8)
                    act_mask_vis = (t_res["_internal_activated_mask"] * 255).astype(np.uint8)
                    
                    mask_bgr = cv2.cvtColor(mask_vis, cv2.COLOR_GRAY2BGR)
                    act_mask_bgr = cv2.cvtColor(act_mask_vis, cv2.COLOR_GRAY2BGR)
                    
                    # Original | Grad-CAM | Leaf Mask | Act Mask | Overlay
                    collage = np.hstack((enhanced_bgr, heatmap_color, mask_bgr, act_mask_bgr, overlay))
                    cv2.imwrite(str(PROJECT_ROOT / f"research_examples/example_{true_class}_{i}.jpg"), collage)
                    examples_saved[true_class] += 1
        
        if i % 10 == 0:
            print(f"Processed {i+1}/{len(filepaths)}...", flush=True)
            
    # Convert to DataFrame
    df = pd.DataFrame(results)
    df_thresh = pd.DataFrame(threshold_results)
    
    print("\nSaving Data Files...")
    df.to_csv(PROJECT_ROOT / "greenscan_evaluation.csv", index=False)
    
    # Analyze Thresholds
    thresh_summary = df_thresh.groupby('Threshold')[['Attention-Affected Region %', 'Health Score']].mean().reset_index()
    # Add severity distribution per threshold
    sev_dist = df_thresh.groupby(['Threshold', 'Severity']).size().unstack(fill_value=0).reset_index()
    thresh_final = pd.merge(thresh_summary, sev_dist, on='Threshold')
    thresh_final.to_csv(PROJECT_ROOT / "threshold_analysis.csv", index=False)
    
    # Metrics
    y_true = df["True Class"]
    y_pred = df["Predicted Class"]
    
    acc = accuracy_score(y_true, y_pred)
    prec_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    prec_weighted = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec_weighted = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    metrics_json = {
        "dataset": {
            "total_test_images": len(df),
            "healthy_images": int((y_true == "tomato_healthy").sum()),
            "early_blight_images": int((y_true == "tomato_Early blight").sum()),
            "late_blight_images": int((y_true == "tomato_Late blight").sum()),
        },
        "classification": {
            "accuracy": float(acc),
            "macro_avg": {
                "precision": float(prec_macro),
                "recall": float(rec_macro),
                "f1": float(f1_macro)
            },
            "weighted_avg": {
                "precision": float(prec_weighted),
                "recall": float(rec_weighted),
                "f1": float(f1_weighted)
            }
        },
        "severity_analysis": {}
    }
    
    # Severity stats
    for c in CLASS_LABELS:
        c_df = df[df["True Class"] == c]
        if len(c_df) > 0:
            metrics_json["severity_analysis"][c] = {
                "mean_affected_region_pct": float(c_df["Attention-Affected Region %"].mean()),
                "std_affected_region_pct": float(c_df["Attention-Affected Region %"].std()),
                "mean_weighted_activation": float(c_df["Mean Leaf Activation"].mean()),
                "mean_health_score": float(c_df["Health Score"].mean())
            }
            
    with open(PROJECT_ROOT / "greenscan_metrics.json", "w") as f:
        json.dump(metrics_json, f, indent=4)
        
    print("Generating Plots...")
    # 1. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=CLASS_LABELS)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS)
    plt.title("Confusion Matrix")
    plt.ylabel('True Class')
    plt.xlabel('Predicted Class')
    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "confusion_matrix.png")
    plt.close()
    
    # 3. Confidence Distribution
    plt.figure(figsize=(8,6))
    sns.histplot(data=df, x="Confidence", hue="Predicted Class", kde=True, bins=20)
    plt.title("Confidence Distribution")
    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "confidence_distribution.png")
    plt.close()
    
    # 4. Affected Region Distribution
    plt.figure(figsize=(8,6))
    sns.histplot(data=df, x="Attention-Affected Region %", hue="True Class", kde=True, bins=20)
    plt.title("Estimated Attention-Affected Region Distribution")
    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "affected_region_distribution.png")
    plt.close()
    
    # 5. Health Score Distribution
    plt.figure(figsize=(8,6))
    sns.histplot(data=df, x="Health Score", hue="True Class", kde=True, bins=20)
    plt.title("Plant Health Score Distribution")
    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "health_score_distribution.png")
    plt.close()
    
    # 6. Severity Distribution
    plt.figure(figsize=(8,6))
    sns.countplot(data=df, x="Severity", hue="True Class", order=["Healthy", "Mild", "Moderate", "Severe"])
    plt.title("Severity Classification Distribution")
    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "severity_distribution.png")
    plt.close()
    
    print("Evaluation Complete!")

if __name__ == "__main__":
    main()
