import pandas as pd
from pathlib import Path

def validate_csv(csv_path):
    print("--- CSV Validation Checker ---")
    if not Path(csv_path).exists():
        print("ERROR: CSV file not found.")
        return False

    df = pd.read_csv(csv_path)
    
    # 1. Missing expert disease / severity
    missing_disease = df['expert_disease'].isna().sum() + (df['expert_disease'] == "").sum()
    missing_severity = df['expert_severity'].isna().sum() + (df['expert_severity'] == "").sum()
    
    print(f"Missing expert_disease: {missing_disease} / {len(df)}")
    print(f"Missing expert_severity: {missing_severity} / {len(df)}")
    
    # 2. Invalid labels
    valid_diseases = {"Healthy", "Early Blight", "Late Blight"}
    valid_severities = {"Healthy", "Mild", "Moderate", "Severe"}
    
    provided_diseases = set(df['expert_disease'].dropna().astype(str).str.strip().str.title().unique()) - {""}
    provided_severities = set(df['expert_severity'].dropna().astype(str).str.strip().str.title().unique()) - {""}
    
    invalid_diseases = provided_diseases - valid_diseases
    invalid_severities = provided_severities - valid_severities
    
    if invalid_diseases:
        print(f"WARNING: Invalid expert_disease labels found: {invalid_diseases}")
    if invalid_severities:
        print(f"WARNING: Invalid expert_severity labels found: {invalid_severities}")
        
    # 3. Duplicate image IDs
    duplicates = df.duplicated(subset=['image_id']).sum()
    if duplicates > 0:
        print(f"ERROR: Found {duplicates} duplicate image IDs.")
        
    # 4. Total Images
    print(f"Total rows: {len(df)}")
    if len(df) != 90:
        print(f"ERROR: Expected 90 images, found {len(df)}")
        
    # Final check
    if missing_severity == len(df):
        print("\nRESULT: Expert validation pending.")
        return False
    elif missing_severity > 0:
        print("\nRESULT: Partial expert data. Still missing entries.")
        return False
    else:
        print("\nRESULT: Expert data is COMPLETE.")
        return True

if __name__ == "__main__":
    csv_path = Path(__file__).parent.parent / "research" / "expert_annotation_task" / "gsa_expert_validation.csv"
    validate_csv(csv_path)
