import os
import requests
import time
import json
from pathlib import Path
import random

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "dataset"
API_BASE = "http://127.0.0.1:8000"

def test_health():
    print("Testing Backend Health...", flush=True)
    try:
        start = time.time()
        res = requests.get(f"{API_BASE}/health")
        latency = time.time() - start
        print(f"Health check status: {res.status_code}")
        print(f"Health response: {res.json()}")
        print(f"Latency: {latency:.4f}s\n")
        return True
    except Exception as e:
        print(f"Health check failed: {e}\n")
        return False

def test_prediction(image_path, expected_label):
    print(f"Testing Prediction on {expected_label}...", flush=True)
    if not image_path.exists():
        print(f"Image not found: {image_path}\n")
        return False

    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, "image/jpeg")}
        start = time.time()
        res = requests.post(f"{API_BASE}/predict", files=files)
        latency = time.time() - start

    if res.status_code == 200:
        data = res.json()
        print(f"SUCCESS: Status 200")
        print(f"Disease: {data.get('disease_name')} (Confidence: {data.get('confidence')}%)")
        print(f"Health Score: {data.get('gsa_metrics', {}).get('plant_health_score')}")
        print(f"Severity: {data.get('gsa_metrics', {}).get('severity_level')}")
        print(f"Affected Region: {data.get('gsa_metrics', {}).get('attention_affected_region_percent')}%")
        print(f"Latency: {latency:.4f}s")
        if data.get('research_details') and 'visuals' in data['research_details']:
            print("Visuals included: YES")
        else:
            print("Visuals included: NO")
        print()
        return True
    else:
        print(f"FAILED: Status {res.status_code}")
        print(f"Response: {res.text}\n")
        return False

def test_edge_cases():
    print("Testing Edge Cases...", flush=True)
    
    # 1. Invalid file type (Text file)
    txt_path = PROJECT_ROOT / "scratch" / "dummy.txt"
    txt_path.parent.mkdir(exist_ok=True)
    with open(txt_path, "w") as f:
        f.write("This is not an image.")
        
    with open(txt_path, "rb") as f:
        files = {"file": ("dummy.txt", f, "text/plain")}
        res = requests.post(f"{API_BASE}/predict", files=files)
        print(f"Text file upload status: {res.status_code} (Expected 400 or 500 with friendly error)")
        print(f"Response: {res.text}")

    print()

def test_chatbot():
    print("Testing Chatbot...", flush=True)
    start = time.time()
    res = requests.post(f"{API_BASE}/chat", json={"message": "What is early blight?"})
    latency = time.time() - start
    print(f"Chatbot status: {res.status_code}")
    print(f"Latency: {latency:.4f}s")
    if res.status_code == 200:
        safe_reply = res.json().get('reply') or ''
        clean_excerpt = safe_reply[:100].encode('ascii', errors='replace').decode('ascii')
        print(f"Response excerpt: {clean_excerpt}...\n")

def main():
    if not test_health():
        print("Backend is not running. Aborting tests.")
        return

    # Select random images
    random.seed(42)
    healthy_dir = DATASET_PATH / "tomato_healthy"
    eb_dir = DATASET_PATH / "tomato_Early blight"
    lb_dir = DATASET_PATH / "tomato_Late blight"
    
    healthy_img = random.choice(list(healthy_dir.glob("*.JPG")))
    eb_img = random.choice(list(eb_dir.glob("*.JPG")))
    lb_img = random.choice(list(lb_dir.glob("*.JPG")))

    test_prediction(healthy_img, "Healthy Tomato")
    test_prediction(eb_img, "Early Blight")
    test_prediction(lb_img, "Late Blight")

    test_edge_cases()
    test_chatbot()
    
    print("Testing History DB Endpoint...")
    res = requests.get(f"{API_BASE}/history")
    print(f"History status: {res.status_code}")
    if res.status_code == 200:
        records = res.json().get("history", [])
        print(f"Records found: {len(records)}\n")
        
    print("All backend tests completed.")

if __name__ == "__main__":
    main()
