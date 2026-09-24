"""
evaluation/create_clean_split.py
GreenScan 2.0 Research Dataset Splitter:
Creates a deterministic, group-stratified 70% Train / 15% Validation / 15% Test split
based on physical leaf subject identity (physical_leaf_id).
Prevents identity leakage, excludes binary duplicate files, and enforces strict partition disjointness.
"""

import os
import re
import json
import random
import hashlib
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

DATASET_PATH = Path(r"C:\Greenscan project\dataset")
OUTPUT_DIR = Path(r"C:\Greenscan project\evaluation")
RANDOM_SEED = 42

def compute_sha256(filepath):
    """Calculates SHA-256 checksum of raw file bytes."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def extract_leaf_id(filename):
    """
    Extracts the unique Physical Leaf Subject Identifier from PlantVillage filename metadata.
    Pattern: <UUID>___<Group_Name> <Leaf_Number> [Day X][_final_masked].JPG
    """
    if "___" in filename:
        rest = filename.split("___")[1]
        clean = re.sub(r'(_final_masked)?\.(jpg|jpeg|png)', '', rest, flags=re.IGNORECASE)
        # Remove temporal ' Day XX' tags so multi-day photos of the same physical leaf group together
        base_leaf = re.sub(r' Day \d+(\.\d+)?', '', clean)
        return base_leaf.strip()
    return filename

def create_clean_split(seed=RANDOM_SEED):
    print("=" * 70)
    print("  GREENSCAN RESEARCH DATASET CLEAN SPLIT GENERATION")
    print(f"  Random Seed: {seed} | Target: 70% Train / 15% Val / 15% Test (Group-Stratified)")
    print("=" * 70)
    
    # 1. Collect all original images (strictly exclude aug_*)
    classes = sorted([d.name for d in DATASET_PATH.iterdir() if d.is_dir()])
    raw_records = []
    
    for c in classes:
        class_dir = DATASET_PATH / c
        files = sorted([f for f in class_dir.iterdir() if f.is_file()])
        
        orig_files = [f for f in files if not (f.name.lower().startswith("aug_") or f.name.lower().startswith("aug"))]
        aug_files = [f for f in files if (f.name.lower().startswith("aug_") or f.name.lower().startswith("aug"))]
        
        print(f"  Class '{c}': {len(orig_files)} original images ({len(aug_files)} augmented excluded)")
        
        for f in orig_files:
            raw_records.append({
                "filename": f.name,
                "filepath": str(f),
                "class": c,
                "physical_leaf_id": extract_leaf_id(f.name),
                "sha256": compute_sha256(f)
            })
            
    df_all = pd.DataFrame(raw_records)
    total_original_count = len(df_all)
    print(f"\n[1] Total Original Images Loaded: {total_original_count}")
    
    # 2. Identify and isolate exact binary duplicate files (SHA-256 collisions)
    sha_groups = df_all.groupby("sha256")
    exact_dup_map = {}
    dup_group_counter = 1
    
    df_all["is_exact_duplicate"] = False
    df_all["duplicate_group_id"] = None
    df_all["split"] = None
    
    excluded_duplicates = []
    
    for sha, group in sha_groups:
        if len(group) > 1:
            dup_id = f"DUP_GRP_{dup_group_counter:03d}"
            dup_group_counter += 1
            
            # Keep first file as active, mark remaining as EXCLUDED_DUPLICATE
            for idx, (row_idx, row) in enumerate(group.iterrows()):
                df_all.loc[row_idx, "duplicate_group_id"] = dup_id
                if idx > 0:
                    df_all.loc[row_idx, "is_exact_duplicate"] = True
                    df_all.loc[row_idx, "split"] = "EXCLUDED_DUPLICATE"
                    excluded_duplicates.append({
                        "filename": row["filename"],
                        "class": row["class"],
                        "sha256": sha,
                        "duplicate_group_id": dup_id,
                        "primary_file_retained": group.iloc[0]["filename"]
                    })
                    
    num_excluded_dups = len(excluded_duplicates)
    df_active = df_all[df_all["split"] != "EXCLUDED_DUPLICATE"].copy()
    print(f"\n[2] Exact Binary Duplicate Handling:")
    print(f"    Total Exact Duplicate Pairs Found: {num_excluded_dups}")
    print(f"    Excluded Exact Duplicate Files: {num_excluded_dups}")
    print(f"    Active Unique Original Images for Splitting: {len(df_active)}")
    
    # 3. Perform Group-Stratified Partitioning by physical_leaf_id within each Class
    print(f"\n[3] Executing Group-Stratified Partitioning (70% Train / 15% Val / 15% Test)...")
    
    rng = random.Random(seed)
    
    assigned_records = []
    
    split_summary_by_class = {}
    
    for c in classes:
        c_df = df_active[df_active["class"] == c]
        
        # Group active images by physical_leaf_id
        groups_dict = defaultdict(list)
        for _, row in c_df.iterrows():
            groups_dict[row["physical_leaf_id"]].append(row)
            
        unique_groups = list(groups_dict.keys())
        rng.shuffle(unique_groups)
        
        total_class_images = len(c_df)
        target_train = int(round(total_class_images * 0.70))
        target_val = int(round(total_class_images * 0.15))
        target_test = total_class_images - target_train - target_val
        
        train_groups = []
        val_groups = []
        test_groups = []
        
        train_img_count = 0
        val_img_count = 0
        test_img_count = 0
        
        for g in unique_groups:
            img_list = groups_dict[g]
            cnt = len(img_list)
            
            # Greedy allocation to maintain exact 70/15/15 image balance
            if train_img_count + cnt <= target_train or (val_img_count >= target_val and test_img_count >= target_test):
                train_groups.append(g)
                train_img_count += cnt
                for r in img_list:
                    df_all.loc[r.name, "split"] = "train"
            elif val_img_count + cnt <= target_val or test_img_count >= target_test:
                val_groups.append(g)
                val_img_count += cnt
                for r in img_list:
                    df_all.loc[r.name, "split"] = "val"
            else:
                test_groups.append(g)
                test_img_count += cnt
                for r in img_list:
                    df_all.loc[r.name, "split"] = "test"
                    
        split_summary_by_class[c] = {
            "total_images": total_class_images,
            "total_groups": len(unique_groups),
            "train_images": train_img_count,
            "train_groups": len(train_groups),
            "val_images": val_img_count,
            "val_groups": len(val_groups),
            "test_images": test_img_count,
            "test_groups": len(test_groups),
            "train_pct": round(train_img_count / total_class_images * 100, 2),
            "val_pct": round(val_img_count / total_class_images * 100, 2),
            "test_pct": round(test_img_count / total_class_images * 100, 2),
        }
        
    # 4. Strict Validation Checks (Must pass or raise AssertionError)
    print(f"\n[4] Running Rigorous Dataset Independence & Partition Validation Checks...")
    
    df_train = df_all[df_all["split"] == "train"]
    df_val = df_all[df_all["split"] == "val"]
    df_test = df_all[df_all["split"] == "test"]
    df_excluded = df_all[df_all["split"] == "EXCLUDED_DUPLICATE"]
    
    train_groups = set(df_train["physical_leaf_id"])
    val_groups = set(df_val["physical_leaf_id"])
    test_groups = set(df_test["physical_leaf_id"])
    
    train_files = set(df_train["filepath"])
    val_files = set(df_val["filepath"])
    test_files = set(df_test["filepath"])
    
    # Check 1: Group disjointness
    assert len(train_groups.intersection(val_groups)) == 0, "FATAL: physical_leaf_id overlap between Train and Val!"
    assert len(train_groups.intersection(test_groups)) == 0, "FATAL: physical_leaf_id overlap between Train and Test!"
    assert len(val_groups.intersection(test_groups)) == 0, "FATAL: physical_leaf_id overlap between Val and Test!"
    print("  [PASS] 1. Zero physical_leaf_id overlap across Train, Val, and Test (Strict Subject Disjointness).")
    
    # Check 2: Filepath disjointness
    assert len(train_files.intersection(val_files)) == 0, "FATAL: File overlap between Train and Val!"
    assert len(train_files.intersection(test_files)) == 0, "FATAL: File overlap between Train and Test!"
    assert len(val_files.intersection(test_files)) == 0, "FATAL: File overlap between Val and Test!"
    print("  [PASS] 2. Zero file overlap across Train, Val, and Test (Train INTERSECT Val INTERSECT Test = 0).")
    
    # Check 3: No aug_* files present
    aug_leaks = df_all[df_all["filename"].str.lower().str.startswith("aug")]
    assert len(aug_leaks) == 0, "FATAL: Augmented aug_* files found in manifest!"
    print("  [PASS] 3. Zero augmented (aug_*) files in research split manifest.")
    
    # Check 4: Exact count conservation
    active_count = len(df_train) + len(df_val) + len(df_test)
    assert active_count + len(df_excluded) == total_original_count, "FATAL: Image count mismatch!"
    print(f"  [PASS] 4. Exact count conservation verified: {active_count} active + {len(df_excluded)} excluded = {total_original_count} total.")
    
    # 5. Export Manifest and Summary
    print(f"\n[5] Saving Split Artifacts to evaluation/ ...")
    
    manifest_cols = [
        "filename", "filepath", "class", "physical_leaf_id",
        "split", "sha256", "is_exact_duplicate", "duplicate_group_id"
    ]
    df_all_sorted = df_all[manifest_cols].sort_values(by=["class", "split", "physical_leaf_id", "filename"])
    manifest_path = OUTPUT_DIR / "clean_split_manifest.csv"
    df_all_sorted.to_csv(manifest_path, index=False)
    print(f"  Saved manifest: {manifest_path} ({len(df_all_sorted)} rows)")
    
    summary_data = {
        "random_seed": seed,
        "split_ratios_target": {"train": 0.70, "val": 0.15, "test": 0.15},
        "total_original_images": total_original_count,
        "exact_duplicate_files_excluded": num_excluded_dups,
        "total_active_images_split": active_count,
        "total_unique_physical_leaf_groups": len(set(df_active["physical_leaf_id"])),
        "overall_split_counts": {
            "train": {"images": len(df_train), "pct": round(len(df_train)/active_count*100, 2), "groups": len(train_groups)},
            "val": {"images": len(df_val), "pct": round(len(df_val)/active_count*100, 2), "groups": len(val_groups)},
            "test": {"images": len(df_test), "pct": round(len(df_test)/active_count*100, 2), "groups": len(test_groups)},
        },
        "per_class_breakdown": split_summary_by_class,
        "excluded_duplicates_list": excluded_duplicates
    }
    
    summary_path = OUTPUT_DIR / "clean_split_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"  Saved summary: {summary_path}")
    
    print("\n" + "=" * 70)
    print("  GREENSCAN CLEAN RESEARCH SPLIT SUMMARY")
    print("=" * 70)
    print(f"  Total Original Images: {total_original_count}")
    print(f"  Excluded Exact Binary Duplicates: {num_excluded_dups}")
    print(f"  Active Images in Research Split: {active_count}")
    print(f"  Unique Physical Leaf Subjects: {len(set(df_active['physical_leaf_id']))}")
    print("\n  Overall Partition Breakdown:")
    print(f"    TRAIN:      {len(df_train):4d} images ({len(df_train)/active_count*100:.2f}%) across {len(train_groups):4d} physical leaf groups")
    print(f"    VALIDATION: {len(df_val):4d} images ({len(df_val)/active_count*100:.2f}%) across {len(val_groups):4d} physical leaf groups")
    print(f"    TEST:       {len(df_test):4d} images ({len(df_test)/active_count*100:.2f}%) across {len(test_groups):4d} physical leaf groups")
    print("\n  Per-Class Split Matrix:")
    
    summary_table = []
    for c, stats in split_summary_by_class.items():
        summary_table.append({
            "Class": c,
            "Total Images": stats["total_images"],
            "Unique Groups": stats["total_groups"],
            "Train Img (Grp)": f"{stats['train_images']} ({stats['train_groups']})",
            "Val Img (Grp)": f"{stats['val_images']} ({stats['val_groups']})",
            "Test Img (Grp)": f"{stats['test_images']} ({stats['test_groups']})",
            "Train %": f"{stats['train_pct']}%",
            "Val %": f"{stats['val_pct']}%",
            "Test %": f"{stats['test_pct']}%"
        })
    df_sum_table = pd.DataFrame(summary_table)
    print(df_sum_table.to_string(index=False))
    print("=" * 70)

if __name__ == "__main__":
    create_clean_split()
