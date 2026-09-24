"""
backend/test_predict_smoke.py

Smoke test for GreenScan FastAPI backend with frozen EfficientNetB0 model.
Uses strictly NON-TEST training images. Test partition is NEVER accessed.
"""

import sys
import os
from pathlib import Path
import json

backend_dir = Path(__file__).parent.resolve()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
import main
from main import app, MODEL_PATH

client = TestClient(app)

SAMPLES = {
    "Healthy": r"C:\Greenscan project\dataset\tomato_healthy\4959798b-5c9b-4f8e-b0a0-3778259614b1___CG1.JPG",
    "Early Blight": r"C:\Greenscan project\dataset\tomato_Early blight\8d70db5b-7916-4397-836d-6a73a2faaead___RS_Erly.B 6330.JPG",
    "Late Blight": r"C:\Greenscan project\dataset\tomato_Late blight\63bd9158-43c2-4b8f-b4ee-a8935f8e3096___GHLB Leaf 1 Day 6_final_masked.jpg"
}

def run_tests():
    print("=" * 75)
    print("  GREENSCAN BACKEND /predict SMOKE TEST (Frozen EfficientNetB0)")
    print("=" * 75)
    print(f"Loaded Model Path: {MODEL_PATH}")
    print(f"Model exists: {MODEL_PATH.exists()}")
    assert MODEL_PATH.exists(), f"Model checkpoint not found: {MODEL_PATH}"
    
    # 1. Health Endpoint Test
    res_health = client.get("/health")
    print(f"\n[GET /health]: Status={res_health.status_code}")
    print(f"Response: {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json()["model_loaded"] == True
    
    # 2. Predict Smoke Tests for Each Class
    results = {}
    for name, path_str in SAMPLES.items():
        print(f"\n[Testing Class: {name}]")
        print(f"  File: {Path(path_str).name}")
        assert os.path.exists(path_str), f"Sample file not found: {path_str}"
        
        with open(path_str, "rb") as f:
            files = {"file": (Path(path_str).name, f, "image/jpeg")}
            res = client.post("/predict", files=files)
            
        print(f"  HTTP Status: {res.status_code}")
        data = res.json()
        
        # Verify core response keys expected by frontend
        expected_keys = ["disease", "confidence", "status", "gsa_metrics"]
        present_keys = [k for k in expected_keys if k in data]
        print(f"  Present Keys: {present_keys}")
        print(f"  Predicted Disease: {data.get('disease')}")
        print(f"  Confidence: {data.get('confidence')}")
        print(f"  Validation Status: {data.get('validation_status')}")
        
        results[name] = {
            "status_code": res.status_code,
            "disease": data.get("disease"),
            "confidence": data.get("confidence"),
            "is_valid": data.get("is_valid", True),
            "response_keys": list(data.keys())
        }
        
    print("\n" + "=" * 75)
    print("  SMOKE TEST SUMMARY")
    print("=" * 75)
    for name, r in results.items():
        print(f"  - {name:<15}: HTTP {r['status_code']} | Predicted: {r['disease']} (Conf: {r['confidence']})")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
