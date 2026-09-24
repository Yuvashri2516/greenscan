"""
evaluation/audit_dataset_duplicates.py
Empirical Duplicate, Near-Duplicate, and Source-Independence Audit
Inspects ONLY the 5,137 original images in dataset/ (excluding all aug_* files).
"""

import os
import hashlib
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
import cv2
import pandas as pd

DATASET_PATH = Path(r"C:\Greenscan project\dataset")
OUTPUT_DIR = Path(r"C:\Greenscan project\evaluation")

def compute_phash(img_bgr, hash_size=8, highfreq_factor=4):
    """
    Computes a 64-bit perceptual hash (pHash) using Discrete Cosine Transform (DCT).
    Robust to slight rotations, scaling, contrast/brightness shifts, and re-compression.
    """
    img_size = hash_size * highfreq_factor
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (img_size, img_size), interpolation=cv2.INTER_AREA)
    
    # 2D DCT
    dct = cv2.dct(np.float32(resized))
    # Extract top-left low frequencies (excluding DC component at (0,0))
    dct_lowfreq = dct[:hash_size, :hash_size]
    med = np.median(dct_lowfreq)
    
    # Binary bitstring
    bit_array = (dct_lowfreq > med).flatten()
    # Convert to 64-bit uint
    hash_int = int("".join(["1" if b else "0" for b in bit_array]), 2)
    return hash_int

def hamming_distance(h1, h2):
    """Counts differing bits between two 64-bit integers."""
    return bin(h1 ^ h2).count("1")

def compute_sha256(filepath):
    """Calculates SHA-256 checksum of raw file bytes."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 70)
    print("  GREENSCAN DATASET DUPLICATE & SOURCE INDEPENDENCE AUDIT")
    print("=" * 70)
    
    classes = [d.name for d in DATASET_PATH.iterdir() if d.is_dir()]
    
    original_images = []
    
    for c in sorted(classes):
        class_dir = DATASET_PATH / c
        files = [f for f in class_dir.iterdir() if f.is_file()]
        
        orig_files = [f for f in files if not (f.name.lower().startswith("aug_") or f.name.lower().startswith("aug"))]
        aug_files = [f for f in files if (f.name.lower().startswith("aug_") or f.name.lower().startswith("aug"))]
        
        print(f"Class '{c}': {len(orig_files)} original images ({len(aug_files)} augmented excluded)")
        
        for f in orig_files:
            original_images.append({
                "class": c,
                "filename": f.name,
                "filepath": str(f),
                "size_bytes": f.stat().st_size
            })
            
    total_orig = len(original_images)
    print(f"\nTotal Original Images to Audit: {total_orig}")
    print("-" * 70)
    
    print("[1] Computing File SHA-256 and Perceptual Hashes (pHash)...")
    start_time = time.time()
    
    sha_map = defaultdict(list)
    phash_list = []
    dimension_map = defaultdict(int)
    filename_patterns = defaultdict(int)
    
    for i, item in enumerate(original_images):
        if (i + 1) % 1000 == 0 or i == total_orig - 1:
            print(f"    Processed {i+1}/{total_orig} images in {time.time()-start_time:.1f}s...")
            
        fpath = item["filepath"]
        sha = compute_sha256(fpath)
        item["sha256"] = sha
        sha_map[sha].append(item)
        
        # Read image for dimension and pHash
        img = cv2.imread(fpath)
        if img is not None:
            h, w = img.shape[:2]
            dimension_map[f"{w}x{h}"] += 1
            phash = compute_phash(img)
            item["phash"] = phash
            item["width"] = w
            item["height"] = h
            phash_list.append(item)
        else:
            item["phash"] = None
            item["width"] = 0
            item["height"] = 0
            
        # Filename prefix pattern analysis
        name = item["filename"]
        if "___" in name:
            prefix = name.split("___")[0]
        elif "_" in name:
            prefix = name.split("_")[0]
        else:
            prefix = "other"
        filename_patterns[prefix] += 1
        
    print(f"\n[2] Exact Binary Duplicate Analysis (SHA-256 Collisions)...")
    exact_dup_groups = {k: v for k, v in sha_map.items() if len(v) > 1}
    exact_dup_affected = sum(len(v) for v in exact_dup_groups.values())
    print(f"    Exact Duplicate Groups: {len(exact_dup_groups)}")
    print(f"    Total Affected Images: {exact_dup_affected}")
    
    # Near Duplicate Analysis using pHash
    print(f"\n[3] Near-Duplicate Perceptual Hash Analysis (pHash)...")
    print(f"    Comparing all pairs within each class to detect near-duplicates/crops/burst shots...")
    
    # We compare within class and cross-class
    near_dup_groups = []
    visited = set()
    
    # Thresholds: distance == 0 (identical visual content), distance <= 2 (near identical / re-encoded), distance <= 4 (near duplicate / slight crop)
    dist_0_pairs = []
    dist_2_pairs = []
    dist_4_pairs = []
    
    num_valid = len(phash_list)
    
    # Group by class for efficiency
    class_groups = defaultdict(list)
    for item in phash_list:
        class_groups[item["class"]].append(item)
        
    for c, items in class_groups.items():
        n = len(items)
        print(f"    Scanning class '{c}' ({n} images)...")
        for i in range(n):
            h1 = items[i]["phash"]
            if h1 is None: continue
            for j in range(i + 1, n):
                h2 = items[j]["phash"]
                if h2 is None: continue
                
                dist = hamming_distance(h1, h2)
                if dist == 0:
                    dist_0_pairs.append((items[i], items[j], dist))
                elif dist <= 2:
                    dist_2_pairs.append((items[i], items[j], dist))
                elif dist <= 4:
                    dist_4_pairs.append((items[i], items[j], dist))
                    
    print(f"\n--- PAIRWISE NEAR-DUPLICATE FINDINGS ---")
    print(f"  Exact Visual Duplicates (pHash Distance = 0): {len(dist_0_pairs)} pairs")
    print(f"  Very High Visual Similarity (pHash Distance <= 2): {len(dist_2_pairs)} pairs")
    print(f"  High Visual Similarity / Near-Duplicates (pHash Distance <= 4): {len(dist_4_pairs)} pairs")
    
    # Calculate affected unique images for threshold <= 4
    near_dup_images = set()
    for p1, p2, _ in dist_0_pairs + dist_2_pairs + dist_4_pairs:
        near_dup_images.add(p1["filepath"])
        near_dup_images.add(p2["filepath"])
        
    print(f"  Total Unique Images Affected (Distance <= 4): {len(near_dup_images)} ({len(near_dup_images)/total_orig*100:.1f}%)")
    
    # Group connected components of near-duplicates (Distance <= 4)
    adj = defaultdict(set)
    for p1, p2, _ in dist_0_pairs + dist_2_pairs + dist_4_pairs:
        adj[p1["filepath"]].add(p2["filepath"])
        adj[p2["filepath"]].add(p1["filepath"])
        
    clusters = []
    seen_nodes = set()
    for node in adj:
        if node not in seen_nodes:
            cluster = []
            queue = [node]
            seen_nodes.add(node)
            for curr in queue:
                cluster.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in seen_nodes:
                        seen_nodes.add(neighbor)
                        queue.append(neighbor)
            clusters.append(cluster)
            
    print(f"  Total Connected Near-Duplicate Clusters (Threshold <= 4): {len(clusters)} clusters")
    
    # Cross-class contamination check (Are any images in class A identical to class B?)
    print(f"\n[4] Cross-Class Contamination Check (Identical image in 2 different classes)...")
    cross_class_dups = []
    for sha, items in sha_map.items():
        classes_in_group = set(it["class"] for it in items)
        if len(classes_in_group) > 1:
            cross_class_dups.append((sha, items))
    print(f"    Cross-Class Exact Duplicates: {len(cross_class_dups)} instances")
    
    # Metadata & Source Patterns
    print(f"\n[5] Image Dimensions & Source Metadata Analysis...")
    print(f"    Image Resolutions: {dict(dimension_map)}")
    print(f"    Filename Prefix Patterns (Top 10):")
    for k, v in sorted(filename_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"      {k}: {v} images")
        
    # Save detailed CSV records
    records_out = []
    for item in original_images:
        records_out.append({
            "class": item["class"],
            "filename": item["filename"],
            "filepath": item["filepath"],
            "sha256": item.get("sha256"),
            "width": item.get("width"),
            "height": item.get("height"),
            "is_near_duplicate": (item["filepath"] in near_dup_images)
        })
    df_out = pd.DataFrame(records_out)
    df_out.to_csv(OUTPUT_DIR / "original_dataset_duplicate_audit.csv", index=False)
    print(f"\nSaved detailed audit log: {OUTPUT_DIR / 'original_dataset_duplicate_audit.csv'}")
    print("=" * 70)

if __name__ == "__main__":
    main()
