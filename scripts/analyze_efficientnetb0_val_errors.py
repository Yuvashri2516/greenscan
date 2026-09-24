"""
scripts/analyze_efficientnetb0_val_errors.py

Analyzes validation misclassifications for Experiment 4 (EfficientNetB0).
Evaluates strictly on the validation split (N=766). Test set is NEVER touched.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import cv2

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.preprocessing.image import ImageDataGenerator

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MANIFEST_PATH = PROJECT_ROOT / "evaluation" / "clean_split_manifest.csv"
MODEL_PATH = PROJECT_ROOT / "research" / "models" / "greenscan_efficientnetb0_best.keras"
OUTPUT_RESULTS_DIR = PROJECT_ROOT / "research" / "results"
ERROR_DIR = OUTPUT_RESULTS_DIR / "efficientnetb0_error_analysis"

ERROR_DIR.mkdir(parents=True, exist_ok=True)
(ERROR_DIR / "early_to_late").mkdir(parents=True, exist_ok=True)
(ERROR_DIR / "late_to_early").mkdir(parents=True, exist_ok=True)
(ERROR_DIR / "other_errors").mkdir(parents=True, exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]
IMAGE_SIZE = (224, 224)

def main():
    print("=" * 70)
    print("  EFFICIENTNETB0 VALIDATION ERROR ANALYSIS")
    print("=" * 70)
    
    df = pd.read_csv(MANIFEST_PATH)
    df = df[df['filename'].str.lower().str.endswith(('.jpg', '.jpeg', '.png'))].copy()
    val_df = df[df['split'].str.lower().isin(['val', 'validation'])].copy().reset_index(drop=True)
    
    val_datagen = ImageDataGenerator(preprocessing_function=efficientnet_preprocess)
    val_gen = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col='filepath',
        y_col='class',
        target_size=IMAGE_SIZE,
        batch_size=32,
        class_mode='categorical',
        classes=CLASS_LABELS,
        shuffle=False
    )
    
    model = tf.keras.models.load_model(str(MODEL_PATH))
    preds = model.predict(val_gen, verbose=1)
    
    pred_idx = np.argmax(preds, axis=1)
    confidences = np.max(preds, axis=1)
    class_map = {c: i for i, c in enumerate(CLASS_LABELS)}
    true_idx = np.array([class_map[c] for c in val_df['class']])
    
    val_df['true_class'] = val_df['class']
    val_df['pred_class'] = [CLASS_LABELS[i] for i in pred_idx]
    val_df['confidence'] = confidences
    val_df['is_correct'] = (pred_idx == true_idx)
    
    for i, c in enumerate(CLASS_LABELS):
        val_df[f"prob_{c}"] = preds[:, i]
        
    error_df = val_df[~val_df['is_correct']].copy().reset_index(drop=True)
    print(f"\n[Validation Set Summary]:")
    print(f"  - Total samples: {len(val_df)}")
    print(f"  - Correct:       {len(val_df) - len(error_df)} ({(len(val_df)-len(error_df))/len(val_df)*100:.2f}%)")
    print(f"  - Errors:        {len(error_df)} ({len(error_df)/len(val_df)*100:.2f}%)")
    
    # Save error manifest
    error_csv_path = ERROR_DIR / "validation_errors.csv"
    error_df.to_csv(error_csv_path, index=False)
    print(f"[Saved Error Manifest]: {error_csv_path}")
    
    # Export representative error visualizations
    for _, row in error_df.iterrows():
        src_path = Path(row['filepath'])
        if not src_path.exists():
            continue
            
        t_cls = row['true_class']
        p_cls = row['pred_class']
        conf = row['confidence']
        
        if t_cls == 'tomato_Early blight' and p_cls == 'tomato_Late blight':
            subfolder = ERROR_DIR / "early_to_late"
        elif t_cls == 'tomato_Late blight' and p_cls == 'tomato_Early blight':
            subfolder = ERROR_DIR / "late_to_early"
        else:
            subfolder = ERROR_DIR / "other_errors"
            
        dst_name = f"{src_path.stem}_true_{t_cls.replace('tomato_', '')}_pred_{p_cls.replace('tomato_', '')}_conf_{conf:.2f}{src_path.suffix}"
        dst_path = subfolder / dst_name
        
        # Load, annotate with banner, and save
        img = cv2.imread(str(src_path))
        if img is not None:
            # Add overlay header
            h, w, _ = img.shape
            banner = np.zeros((50, w, 3), dtype=np.uint8)
            text = f"True: {t_cls.replace('tomato_', '')} | Pred: {p_cls.replace('tomato_', '')} ({conf*100:.1f}%)"
            cv2.putText(banner, text, (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
            annotated = np.vstack([banner, img])
            cv2.imwrite(str(dst_path), annotated)
            
    print(f"[Generated Error Visualizations]: {ERROR_DIR}")

if __name__ == "__main__":
    main()
