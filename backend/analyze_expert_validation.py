import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, cohen_kappa_score
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "research" / "expert_annotation_task" / "gsa_expert_validation.csv"
REPORT_PATH = PROJECT_ROOT / "research" / "expert_validation_report.md"

def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found. Run prepare_expert_annotation.py first.")
        return

    df = pd.read_csv(CSV_PATH)
    
    if df['expert_severity'].isna().all() or (df['expert_severity'] == "").all():
        print("Expert validation pending.")
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("# GreenScan Expert Validation Report\n\n")
            f.write("**Status**: ⏳ Expert validation pending.\n\n")
            f.write("Please ask the agricultural expert to fill out the `expert_severity` and `expert_disease` columns in `expert_annotation_task/gsa_expert_validation.csv` based on the composite images provided.\n")
        return

    df = df.dropna(subset=['expert_severity'])
    
    severity_map = {"Healthy": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
    
    y_true_disease = df['expert_disease']
    y_pred_disease = df['predicted_disease']
    
    y_true_sev = df['expert_severity'].str.strip().str.title()
    y_pred_sev = df['green_scan_severity'].str.strip().str.title()

    print("Analyzing Expert Validations...")

    disease_acc = accuracy_score(y_true_disease, y_pred_disease) if not y_true_disease.isna().all() else None

    sev_acc = accuracy_score(y_true_sev, y_pred_sev)
    sev_prec = precision_score(y_true_sev, y_pred_sev, average='macro', zero_division=0)
    sev_rec = recall_score(y_true_sev, y_pred_sev, average='macro', zero_division=0)
    sev_f1 = f1_score(y_true_sev, y_pred_sev, average='macro', zero_division=0)
    kappa = cohen_kappa_score(y_true_sev, y_pred_sev)
    
    df['expert_num'] = y_true_sev.map(severity_map)
    spearman_corr, p_value = spearmanr(df['green_scan_health_score'], df['expert_num'])

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# GreenScan Expert Validation Report\n\n")
        f.write("## 1. Disease Classification Performance\n")
        if disease_acc is not None:
            f.write(f"- **Accuracy**: {disease_acc:.2%}\n\n")
        else:
            f.write("Expert disease labels not provided.\n\n")

        f.write("## 2. Severity Classification Metrics\n")
        f.write(f"- **Accuracy**: {sev_acc:.2%}\n")
        f.write(f"- **Precision (Macro)**: {sev_prec:.4f}\n")
        f.write(f"- **Recall (Macro)**: {sev_rec:.4f}\n")
        f.write(f"- **F1-Score (Macro)**: {sev_f1:.4f}\n")
        f.write(f"- **Cohen's Kappa**: {kappa:.4f} (Agreement beyond chance)\n\n")

        f.write("## 3. Continuous Correlation\n")
        f.write("Correlation between AI Plant Health Score (0-100) and Expert Severity (0-3):\n")
        f.write(f"- **Spearman Rank Correlation**: {spearman_corr:.4f} (p-value: {p_value:.4e})\n")
        f.write("*(Note: A strong negative correlation indicates the Health Score correctly decreases as Expert Severity increases.)*\n\n")

        f.write("## 4. Confusion Matrix (Severity)\n")
        f.write("```\n")
        labels = ["Healthy", "Mild", "Moderate", "Severe"]
        cm = confusion_matrix(y_true_sev, y_pred_sev, labels=labels)
        f.write(f"{'':>10} | {'Pred Healthy':>12} | {'Pred Mild':>10} | {'Pred Mod':>10} | {'Pred Sev':>10}\n")
        f.write("-" * 65 + "\n")
        for i, row_label in enumerate(labels):
            f.write(f"True {row_label:<5} | {cm[i][0]:>12} | {cm[i][1]:>10} | {cm[i][2]:>10} | {cm[i][3]:>10}\n")
        f.write("```\n")

    print(f"Analysis complete. Report saved to {REPORT_PATH}")

if __name__ == "__main__":
    main()
