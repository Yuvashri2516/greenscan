"""
scripts/train_research_clean.py

Deterministic Clean Training Pipeline for GreenScan Research:
- Strictly utilizes the verified group-stratified dataset partition from evaluation/clean_split_manifest.csv.
- Strictly separates Train (3,588 images) and Validation (768 images).
- Held-out Test (770 images) is verified for completeness but NEVER loaded or evaluated during training.
- Uses GreenScan MobileNetV2 architecture (rescaling 1/255, transfer learning on ImageNet).
- Online augmentation is applied ONLY to the Training partition.
- Saves best & final model checkpoints to research/models/ and metrics to research/results/.
"""

import os
import sys
import json
import random
import time
from pathlib import Path
import numpy as np
import pandas as pd

# Set deterministic random seeds
RANDOM_SEED = 42
os.environ['PYTHONHASHSEED'] = str(RANDOM_SEED)
os.environ['TF_DETERMINISTIC_OPS'] = '1'
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

import tensorflow as tf
tf.random.set_seed(RANDOM_SEED)

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MANIFEST_PATH = PROJECT_ROOT / "evaluation" / "clean_split_manifest.csv"
OUTPUT_MODELS_DIR = PROJECT_ROOT / "research" / "models"
OUTPUT_RESULTS_DIR = PROJECT_ROOT / "research" / "results"

OUTPUT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
INITIAL_EPOCHS = 15
INITIAL_LR = 0.001

def verify_and_prepare_manifest():
    print("=" * 70)
    print("  GREENSCAN RESEARCH: VERIFYING CLEAN DATASET PARTITION")
    print("=" * 70)
    
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")
    
    df = pd.read_csv(MANIFEST_PATH)
    
    # Assertions
    assert "split" in df.columns, "Missing 'split' column in manifest"
    assert "class" in df.columns, "Missing 'class' column in manifest"
    assert "filepath" in df.columns, "Missing 'filepath' column in manifest"
    assert "physical_leaf_id" in df.columns, "Missing 'physical_leaf_id' column in manifest"
    
    # Check for aug_ files
    aug_files = df[df['filename'].str.startswith('aug_')]
    if len(aug_files) > 0:
        raise ValueError(f"Found {len(aug_files)} aug_* files in manifest! Must strictly contain original images.")
    
    # Normalize split names
    split_norm = df['split'].str.lower()
    train_mask = split_norm == 'train'
    val_mask = (split_norm == 'val') | (split_norm == 'validation')
    test_mask = (split_norm == 'test') | (split_norm == 'held_out_test')
    dup_mask = (split_norm == 'excluded_duplicate') | (df['is_exact_duplicate'] == True)
    
    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()
    dup_df = df[dup_mask].copy()
    
    print(f"\n[Verification Counts]")
    print(f"  - TRAIN images:      {len(train_df):>5} (Expected: 3588)")
    print(f"  - VALIDATION images: {len(val_df):>5} (Expected: 768)")
    print(f"  - HELD-OUT TEST:     {len(test_df):>5} (Expected: 770)")
    print(f"  - EXCLUDED DUPS:     {len(dup_df):>5} (Expected: 11)")
    print(f"  - TOTAL AUDITED:     {len(df):>5} (Expected: 5137)")
    
    # Strict validation assertions
    if len(train_df) != 3588:
        raise ValueError(f"Train count mismatch: {len(train_df)} != 3588")
    if len(val_df) != 768:
        raise ValueError(f"Validation count mismatch: {len(val_df)} != 768")
    if len(test_df) != 770:
        raise ValueError(f"Test count mismatch: {len(test_df)} != 770")
    
    # Verify group disjointness
    train_groups = set(train_df['physical_leaf_id'])
    val_groups = set(val_df['physical_leaf_id'])
    test_groups = set(test_df['physical_leaf_id'])
    
    overlap_tv = train_groups & val_groups
    overlap_tt = train_groups & test_groups
    overlap_vt = val_groups & test_groups
    
    if overlap_tv or overlap_tt or overlap_vt:
        raise ValueError(f"Subject leakage detected! Overlaps: Train-Val={len(overlap_tv)}, Train-Test={len(overlap_tt)}, Val-Test={len(overlap_vt)}")
    
    print(f"\n[Group Verification]")
    print(f"  - Train physical leaf groups:      {len(train_groups):>5}")
    print(f"  - Validation physical leaf groups: {len(val_groups):>5}")
    print(f"  - Test physical leaf groups:       {len(test_groups):>5}")
    print(f"  - Group Leakage: ZERO (Disjointness verified)")
    
    # Verify files exist on disk
    missing_train = [p for p in train_df['filepath'] if not os.path.exists(p)]
    missing_val = [p for p in val_df['filepath'] if not os.path.exists(p)]
    if missing_train or missing_val:
        raise FileNotFoundError(f"Missing image files: {len(missing_train)} in train, {len(missing_val)} in val")
    
    print("\n[Per-Class Breakdown]")
    for c in CLASS_LABELS:
        n_tr = len(train_df[train_df['class'] == c])
        n_va = len(val_df[val_df['class'] == c])
        n_te = len(test_df[test_df['class'] == c])
        g_tr = len(set(train_df[train_df['class'] == c]['physical_leaf_id']))
        g_va = len(set(val_df[val_df['class'] == c]['physical_leaf_id']))
        g_te = len(set(test_df[test_df['class'] == c]['physical_leaf_id']))
        print(f"  - {c:<22}: Train={n_tr} ({g_tr} grps) | Val={n_va} ({g_va} grps) | Test={n_te} ({g_te} grps)")
        
    return train_df, val_df, test_df, df

def build_model(num_classes=3):
    """
    Builds the GreenScan MobileNetV2 architecture with ImageNet weights.
    """
    base = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
    )
    base.trainable = False  # Freeze base for feature extraction transfer learning
    
    x = base.output
    x = GlobalAveragePooling2D(name='global_average_pooling2d')(x)
    x = Dense(128, activation='relu', name='dense')(x)
    x = Dropout(0.5, name='dropout')(x)
    predictions = Dense(num_classes, activation='softmax', name='predictions')(x)
    
    model = Model(inputs=base.input, outputs=predictions, name="GreenScan_MobileNetV2_CleanResearch")
    return model

def main():
    train_df, val_df, test_df, full_df = verify_and_prepare_manifest()
    
    print("\n" + "=" * 70)
    print("  DATA GENERATORS INITIALIZATION")
    print("=" * 70)
    
    # 1. Training Generator WITH online augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest'
    )
    
    # 2. Validation Generator with RAW images only (rescaling 1/255, NO augmentation)
    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0
    )
    
    train_generator = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        x_col='filepath',
        y_col='class',
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        shuffle=True,
        seed=RANDOM_SEED
    )
    
    val_generator = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col='filepath',
        y_col='class',
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CLASS_LABELS,
        shuffle=False
    )
    
    print("\nNOTE: The 770 held-out test images are NOT loaded into any generator.")
    print("Test set remains strictly isolated and held out.")
    
    # Build Model
    print("\n" + "=" * 70)
    print("  MODEL COMPILATION & ARCHITECTURE")
    print("=" * 70)
    model = build_model(num_classes=len(CLASS_LABELS))
    
    optimizer = Adam(learning_rate=INITIAL_LR)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    model.summary()
    
    # Checkpoints & Callbacks
    best_model_path = OUTPUT_MODELS_DIR / "greenscan_research_best.keras"
    final_model_path = OUTPUT_MODELS_DIR / "greenscan_research_final.keras"
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=str(best_model_path),
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    print("\n" + "=" * 70)
    print(f"  STARTING DETERMINISTIC CLEAN TRAINING ({INITIAL_EPOCHS} EPOCHS)")
    print("=" * 70)
    start_time = time.time()
    
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=INITIAL_EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    total_training_time = time.time() - start_time
    print(f"\nTraining completed in {total_training_time:.2f} seconds.")
    
    # Save Final Model
    print(f"\n[Saving Models]")
    print(f"  - Best Model:  {best_model_path}")
    print(f"  - Final Model: {final_model_path}")
    model.save(str(final_model_path))
    
    # Extract History & Best Metrics
    history_dict = history.history
    epochs_ran = len(history_dict['loss'])
    
    # Find best epoch according to val_loss
    best_epoch_idx = int(np.argmin(history_dict['val_loss']))
    best_epoch = best_epoch_idx + 1
    best_val_loss = float(history_dict['val_loss'][best_epoch_idx])
    best_val_acc = float(history_dict['val_accuracy'][best_epoch_idx])
    best_train_loss = float(history_dict['loss'][best_epoch_idx])
    best_train_acc = float(history_dict['accuracy'][best_epoch_idx])
    
    # Save History CSV
    history_df = pd.DataFrame(history_dict)
    history_df['epoch'] = range(1, epochs_ran + 1)
    history_csv_path = OUTPUT_RESULTS_DIR / "training_history.csv"
    history_df.to_csv(history_csv_path, index=False)
    print(f"  - Training History CSV: {history_csv_path}")
    
    # Compile Training Summary JSON
    train_groups_count = len(set(train_df['physical_leaf_id']))
    val_groups_count = len(set(val_df['physical_leaf_id']))
    test_groups_count = len(set(test_df['physical_leaf_id']))
    
    summary = {
        "dataset_manifest": str(MANIFEST_PATH),
        "random_seed": RANDOM_SEED,
        "counts": {
            "train_images": len(train_df),
            "train_physical_leaf_groups": train_groups_count,
            "validation_images": len(val_df),
            "validation_physical_leaf_groups": val_groups_count,
            "held_out_test_images": len(test_df),
            "held_out_test_physical_leaf_groups": test_groups_count,
            "excluded_duplicates": len(full_df[full_df['is_exact_duplicate'] == True])
        },
        "class_distribution": {
            "train": {c: int(len(train_df[train_df['class'] == c])) for c in CLASS_LABELS},
            "validation": {c: int(len(val_df[val_df['class'] == c])) for c in CLASS_LABELS},
            "test": {c: int(len(test_df[test_df['class'] == c])) for c in CLASS_LABELS}
        },
        "model_architecture": {
            "name": "MobileNetV2",
            "weights": "imagenet",
            "base_trainable": False,
            "dense_head": [
                {"layer": "GlobalAveragePooling2D"},
                {"layer": "Dense", "units": 128, "activation": "relu"},
                {"layer": "Dropout", "rate": 0.5},
                {"layer": "Dense", "units": 3, "activation": "softmax"}
            ]
        },
        "input_size": list(IMAGE_SIZE) + [3],
        "preprocessing": {
            "rescale": "1./255",
            "color_mode": "RGB"
        },
        "augmentation_config": {
            "train_only": True,
            "rotation_range": 40,
            "width_shift_range": 0.2,
            "height_shift_range": 0.2,
            "shear_range": 0.2,
            "zoom_range": 0.2,
            "horizontal_flip": True,
            "vertical_flip": True,
            "fill_mode": "nearest"
        },
        "optimizer": {
            "name": "Adam",
            "initial_learning_rate": INITIAL_LR
        },
        "loss": "categorical_crossentropy",
        "batch_size": BATCH_SIZE,
        "max_epochs": INITIAL_EPOCHS,
        "actual_epochs_trained": epochs_ran,
        "callbacks": {
            "EarlyStopping": {"monitor": "val_loss", "patience": 5, "restore_best_weights": True},
            "ReduceLROnPlateau": {"monitor": "val_loss", "factor": 0.2, "patience": 3, "min_lr": 1e-6},
            "ModelCheckpoint": {"monitor": "val_loss", "save_best_only": True}
        },
        "best_epoch": best_epoch,
        "best_train_loss": best_train_loss,
        "best_train_accuracy": best_train_acc,
        "best_validation_loss": best_val_loss,
        "best_validation_accuracy": best_val_acc,
        "total_training_time_seconds": total_training_time,
        "output_paths": {
            "best_model": str(best_model_path),
            "final_model": str(final_model_path),
            "training_history_csv": str(history_csv_path)
        }
    }
    
    summary_json_path = OUTPUT_RESULTS_DIR / "training_summary.json"
    with open(summary_json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  - Training Summary JSON: {summary_json_path}")
    
    print("\n" + "=" * 70)
    print("  TRAINING RUN SUMMARY")
    print("=" * 70)
    print(f"  - Total Epochs Trained:   {epochs_ran}")
    print(f"  - Best Epoch:             {best_epoch}")
    print(f"  - Best Train Accuracy:    {best_train_acc * 100:.2f}% (Loss: {best_train_loss:.4f})")
    print(f"  - Best Validation Acc:    {best_val_acc * 100:.2f}% (Loss: {best_val_loss:.4f})")
    print(f"  - Best Model Saved At:    {best_model_path}")
    print(f"  - Final Model Saved At:   {final_model_path}")
    print("=" * 70)
    print("STOP: Held-out test evaluation has NOT been run, per research protocol.")
    print("=" * 70)

if __name__ == "__main__":
    main()
