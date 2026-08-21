import os
import shutil
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "research" / "results"
FINAL_RESULTS_DIR = PROJECT_ROOT / "research" / "final_results"
FINAL_RESULTS_DIR.mkdir(exist_ok=True)

print("Starting final results compilation...")

# 1. Copy Confusion Matrix Image
cm_src = RESULTS_DIR / "confusion_matrix.png"
cm_dest = FINAL_RESULTS_DIR / "confusion_matrix.png"
if cm_src.exists():
    shutil.copy(cm_src, cm_dest)
    print(f"Copied confusion matrix to {cm_dest}")
else:
    print(f"Warning: {cm_src} not found.")

# 2. Compile classification_results.csv
metrics_path = RESULTS_DIR / "greenscan_metrics.json"
if metrics_path.exists():
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
    
    records = []
    # Add Overall Accuracy
    records.append({"Metric": "Overall Accuracy", "Value": metrics["classification"]["accuracy"]})
    
    # Add Macro Averages
    records.append({"Metric": "Macro Precision", "Value": metrics["classification"]["macro_avg"]["precision"]})
    records.append({"Metric": "Macro Recall", "Value": metrics["classification"]["macro_avg"]["recall"]})
    records.append({"Metric": "Macro F1-Score", "Value": metrics["classification"]["macro_avg"]["f1"]})
    
    # Add Weighted Averages
    records.append({"Metric": "Weighted Precision", "Value": metrics["classification"]["weighted_avg"]["precision"]})
    records.append({"Metric": "Weighted Recall", "Value": metrics["classification"]["weighted_avg"]["recall"]})
    records.append({"Metric": "Weighted F1-Score", "Value": metrics["classification"]["weighted_avg"]["f1"]})
    
    df_class = pd.DataFrame(records)
    df_class.to_csv(FINAL_RESULTS_DIR / "classification_results.csv", index=False)
    print(f"Created classification_results.csv at {FINAL_RESULTS_DIR}")
else:
    print("Warning: greenscan_metrics.json not found.")

# 3. Compile gsa_results.csv
gsa_src = RESULTS_DIR / "gsa_disease_statistics.csv"
if gsa_src.exists():
    df_gsa = pd.read_csv(gsa_src)
    df_gsa.to_csv(FINAL_RESULTS_DIR / "gsa_results.csv", index=False)
    print(f"Created gsa_results.csv at {FINAL_RESULTS_DIR}")
else:
    print("Warning: gsa_disease_statistics.csv not found.")

# 4. Compile threshold_comparison.csv
thresh_src = RESULTS_DIR / "gsa_threshold_analysis.csv"
if thresh_src.exists():
    df_thresh = pd.read_csv(thresh_src)
    df_thresh.to_csv(FINAL_RESULTS_DIR / "threshold_comparison.csv", index=False)
    print(f"Created threshold_comparison.csv at {FINAL_RESULTS_DIR}")
else:
    print("Warning: gsa_threshold_analysis.csv not found.")

# 5. Compile expert_validation_results.csv
expert_src = PROJECT_ROOT / "research" / "expert_annotation_task" / "gsa_expert_validation.csv"
if expert_src.exists():
    df_exp = pd.read_csv(expert_src)
    df_exp.to_csv(FINAL_RESULTS_DIR / "expert_validation_results.csv", index=False)
    print(f"Created expert_validation_results.csv at {FINAL_RESULTS_DIR} (validation pending)")
else:
    print("Warning: gsa_expert_validation.csv not found.")

# 6. Parse and Summarize Robustness Results
robust_src = RESULTS_DIR / "greenscan_robustness_results.csv"
if robust_src.exists():
    df_rob = pd.read_csv(robust_src)
    summary = df_rob.groupby("Test Condition").agg(
        Total_Tested=("Correct", "count"),
        Correct_Predictions=("Correct", lambda x: (x == True).sum()),
        Accuracy=("Correct", "mean")
    ).reset_index()
    print("\nRobustness Experiment Summary:")
    print(summary.to_string(index=False))
else:
    print("Warning: greenscan_robustness_results.csv not found.")

print("\nFinal results compilation completed successfully!")
