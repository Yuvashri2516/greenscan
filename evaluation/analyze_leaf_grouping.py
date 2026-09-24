import pandas as pd
import re
from collections import defaultdict

df = pd.read_csv('evaluation/original_dataset_duplicate_audit.csv')

def extract_leaf_id(filename):
    if '___' in filename:
        rest = filename.split('___')[1]
        clean = re.sub(r'(_final_masked)?\.(jpg|jpeg|png)', '', rest, flags=re.IGNORECASE)
        base_leaf = re.sub(r' Day \d+(\.\d+)?', '', clean)
        return base_leaf.strip()
    return filename

df['leaf_id'] = df['filename'].apply(extract_leaf_id)
leaf_counts = df['leaf_id'].value_counts()

print("=== PHYSICAL LEAF / SOURCE GROUPING ANALYSIS ===")
print(f"Total Original Images: {len(df)}")
print(f"Unique Physical Leaf / Subject Groups: {len(leaf_counts)}")
print(f"Images belonging to multi-capture leaf groups (>1 image of same leaf): {(df['leaf_id'].isin(leaf_counts[leaf_counts > 1].index)).sum()}")
print(f"Single-capture unique leaves: {(df['leaf_id'].isin(leaf_counts[leaf_counts == 1].index)).sum()}")

print("\nTop 10 Most Photographed / Replicated Leaves:")
for leaf, cnt in leaf_counts.head(10).items():
    print(f"  Leaf ID: '{leaf}' -> {cnt} image files")

# Check class breakdown of physical groups
print("\nUnique Physical Leaf Groups by Class:")
for c in df['class'].unique():
    c_df = df[df['class'] == c]
    c_groups = c_df['leaf_id'].nunique()
    print(f"  {c}: {len(c_df)} images -> {c_groups} unique physical leaf groups")
