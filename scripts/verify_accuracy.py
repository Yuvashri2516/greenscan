import csv
import time
import requests
from pathlib import Path
import json
import collections

MANIFEST_PATH = Path("scripts/verify_manifest.csv")
OUTPUT_CSV = Path("scripts/verify_results.csv")
LOCAL_URL = "http://127.0.0.1:8000"
PROD_URL = "https://greenscan-api-4rhz.onrender.com"

CLASSES = ["tomato_Early blight", "tomato_healthy", "tomato_Late blight"]

def wait_for_health(base_url, name, max_retries=15):
    health_url = f"{base_url}/health"
    print(f"Waiting for {name} health & model_ready ({health_url})...", flush=True)
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(health_url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("model_ready") is True:
                    print(f"[{name}] is HEALTHY and model is ready!", flush=True)
                    return True
                else:
                    print(f"[{name}] attempt {attempt}: model_ready is False (warming up)...", flush=True)
            else:
                print(f"[{name}] attempt {attempt}: status {r.status_code}", flush=True)
        except Exception as e:
            print(f"[{name}] attempt {attempt}: {e}", flush=True)
        time.sleep(5)
    return False

def predict_single(base_url, image_path, retry_503=True):
    url = f"{base_url}/predict"
    img_bytes = Path(image_path).read_bytes()
    filename = Path(image_path).name
    files = {"file": (filename, img_bytes, "image/jpeg")}
    
    t0 = time.perf_counter()
    try:
        res = requests.post(url, files=files, timeout=90)
        dt = (time.perf_counter() - t0) * 1000
        
        if res.status_code == 503 and retry_503:
            print(f"    -> 503 received from {base_url}. Retrying after 15s...", flush=True)
            time.sleep(15)
            return predict_single(base_url, image_path, retry_503=False)
            
        if res.status_code == 200:
            data = res.json()
            return {
                "status": 200,
                "latency_ms": dt,
                "pred_class": data.get("prediction") or data.get("disease_name"),
                "confidence": data.get("confidence"),
                "is_valid": data.get("is_valid"),
                "validation_status": data.get("validation_status")
            }
        else:
            return {
                "status": res.status_code,
                "latency_ms": dt,
                "pred_class": None,
                "confidence": None,
                "is_valid": None,
                "error": res.text
            }
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        return {
            "status": "error",
            "latency_ms": dt,
            "pred_class": None,
            "confidence": None,
            "is_valid": None,
            "error": str(e)
        }

def compute_metrics(records, prefix="local"):
    matrix = collections.defaultdict(lambda: collections.defaultdict(int))
    class_totals = collections.defaultdict(int)
    class_correct = collections.defaultdict(int)
    total_correct = 0
    total = len(records)
    
    for r in records:
        true_lbl = r["true_label"]
        pred_lbl = r[f"{prefix}_pred"]
        class_totals[true_lbl] += 1
        matrix[true_lbl][pred_lbl] += 1
        if pred_lbl == true_lbl:
            class_correct[true_lbl] += 1
            total_correct += 1
            
    acc_per_class = {}
    for cls in CLASSES:
        tot = class_totals[cls]
        corr = class_correct[cls]
        acc_per_class[cls] = (corr / tot * 100.0) if tot > 0 else 0.0
        
    overall_acc = (total_correct / total * 100.0) if total > 0 else 0.0
    return overall_acc, acc_per_class, matrix

def main():
    if not wait_for_health(LOCAL_URL, "LOCAL"):
        print("ERROR: Local backend is not ready. Aborting.")
        return
    if not wait_for_health(PROD_URL, "PRODUCTION"):
        print("ERROR: Production backend is not ready. Aborting.")
        return
        
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        
    print(f"\nRunning accuracy verification on {len(reader)} images...", flush=True)
    results = []
    disagreements = []
    
    for idx, item in enumerate(reader, 1):
        img_p = item["path"]
        true_lbl = item["true_label"]
        filename = Path(img_p).name
        print(f"\n[{idx:02d}/{len(reader):02d}] Testing: {filename} (True: {true_lbl})", flush=True)
        
        # 1. Local predict
        loc = predict_single(LOCAL_URL, img_p)
        print(f"  -> Local: Status={loc['status']} | Pred={loc['pred_class']} | Conf={loc['confidence']}% | {loc['latency_ms']:.0f}ms", flush=True)
        
        # 2. Production predict (single-flight)
        prod = predict_single(PROD_URL, img_p)
        print(f"  -> Prod:  Status={prod['status']} | Pred={prod['pred_class']} | Conf={prod['confidence']}% | {prod['latency_ms']:.0f}ms", flush=True)
        
        row = {
            "filename": filename,
            "true_label": true_lbl,
            "local_status": loc["status"],
            "local_pred": loc["pred_class"],
            "local_conf": loc["confidence"],
            "local_latency_ms": round(loc["latency_ms"], 1),
            "prod_status": prod["status"],
            "prod_pred": prod["pred_class"],
            "prod_conf": prod["confidence"],
            "prod_latency_ms": round(prod["latency_ms"], 1),
            "match_truth_local": (loc["pred_class"] == true_lbl),
            "match_truth_prod": (prod["pred_class"] == true_lbl),
            "local_prod_agree": (loc["pred_class"] == prod["pred_class"]),
        }
        results.append(row)
        
        if loc["pred_class"] != prod["pred_class"]:
            disagreements.append(row)
            print(f"  >>> WARNING: Local and Production DISAGREE on {filename}! (Local: {loc['pred_class']}, Prod: {prod['pred_class']})", flush=True)
            
        time.sleep(1) # Politeness buffer
        
    # Write full CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nWrote full verification results to {OUTPUT_CSV}", flush=True)
    
    # Compute metrics
    loc_acc, loc_per_cls, loc_cm = compute_metrics(results, "local")
    prod_acc, prod_per_cls, prod_cm = compute_metrics(results, "prod")
    
    print("\n=======================================================")
    print("ACCURACY COMPARISON (30 Images: 10 per class)")
    print("=======================================================")
    print(f"{'Class':<22} | {'Local Accuracy':<16} | {'Prod Accuracy':<16}")
    print("-" * 58)
    for cls in CLASSES:
        print(f"{cls:<22} | {loc_per_cls[cls]:>6.1f}%          | {prod_per_cls[cls]:>6.1f}%")
    print("-" * 58)
    print(f"{'OVERALL ACCURACY':<22} | {loc_acc:>6.1f}%          | {prod_acc:>6.1f}%")
    print("=======================================================")
    
    print("\n=======================================================")
    print("CONFUSION MATRIX: LOCAL")
    print("=======================================================")
    header = "True \\ Pred".ljust(22) + " | " + " | ".join(f"{c:<18}" for c in CLASSES)
    print(header)
    print("-" * len(header))
    for r in CLASSES:
        row_str = f"{r:<22} | " + " | ".join(f"{loc_cm[r][c]:<18}" for c in CLASSES)
        print(row_str)
        
    print("\n=======================================================")
    print("CONFUSION MATRIX: PRODUCTION")
    print("=======================================================")
    print(header)
    print("-" * len(header))
    for r in CLASSES:
        row_str = f"{r:<22} | " + " | ".join(f"{prod_cm[r][c]:<18}" for c in CLASSES)
        print(row_str)
        
    print("\n=======================================================")
    print(f"DISAGREEMENTS BETWEEN LOCAL AND PROD ({len(disagreements)} total):")
    print("=======================================================")
    if not disagreements:
        print("PERFECT PARITY: 0 disagreements found between Local and Production predictions!")
    else:
        for d in disagreements:
            print(f"- {d['filename']}: True={d['true_label']} | Local={d['local_pred']} (conf {d['local_conf']}%) vs Prod={d['prod_pred']} (conf {d['prod_conf']}%)")

if __name__ == "__main__":
    main()
