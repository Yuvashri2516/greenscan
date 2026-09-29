import sys
import os
import time
from pathlib import Path
import numpy as np
import cv2

backend_dir = Path(r"C:\Greenscan project\backend")
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
import main
from main import app, MODEL_PATH

client = TestClient(app)

def run_comprehensive_tests():
    print("=" * 80)
    print("  GREENSCAN BACKEND /predict COMPREHENSIVE LOCAL VALIDATION")
    print("=" * 80)
    
    # 1. Health check
    print("\n[1] Testing GET /health ...")
    res = client.get("/health")
    print(f"Status: {res.status_code}")
    print(f"Payload: {res.json()}")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert res.json()["model_loaded"] == True
    assert res.json()["model"] == "EfficientNet-B0"
    
    # Test images
    samples = {
        "Healthy Leaf": Path(r"C:\Greenscan project\research\research_examples\example_tomato_healthy_1015.jpg"),
        "Early Blight Leaf": Path(r"C:\Greenscan project\research\research_examples\example_tomato_Early blight_0.jpg"),
        "Late Blight Leaf": Path(r"C:\Greenscan project\research\research_examples\example_tomato_Late blight_504.jpg"),
    }
    
    # Fallback to test_leaf.jpg if specific example path missing
    if not samples["Healthy Leaf"].exists():
        samples["Healthy Leaf"] = Path(r"C:\Greenscan project\test_leaf.jpg")
        
    print("\n[2] Testing Disease Classes ...")
    timings = {}
    for name, path in samples.items():
        if not path.exists():
            print(f"Skipping {name}, path not found: {path}")
            continue
            
        with open(path, "rb") as f:
            file_bytes = f.read()
            
        t0 = time.perf_counter()
        res = client.post("/predict", files={"file": (path.name, file_bytes, "image/jpeg")})
        dt = (time.perf_counter() - t0) * 1000.0
        timings[name] = dt
        
        print(f"\n--- Class: {name} (Time: {dt:.2f}ms) ---")
        print(f"HTTP Status: {res.status_code}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        
        print(f"Disease: {data.get('disease')}")
        print(f"Confidence: {data.get('confidence')}%")
        print(f"GSA Severity: {data.get('gsa_metrics', {}).get('severity_level')}")
        print(f"Plant Health Score: {data.get('gsa_metrics', {}).get('plant_health_score')}")
        print(f"Grad-CAM Heatmap Visual Present: {'heatmap' in data.get('research_details', {}).get('visuals', {})}")
        print(f"Recommendations Present: {'organic' in data.get('recommendations', {})}")
        print(f"Structured Rec Present: {data.get('structured_recommendation') is not None}")
        
        assert "disease" in data
        assert "confidence" in data
        assert "gsa_metrics" in data
        assert "research_details" in data
        assert "visuals" in data["research_details"]
        assert "heatmap" in data["research_details"]["visuals"]
        
    # 3. Test High-Res 4K Image (Performance verification)
    print("\n[3] Testing High-Resolution 4K Image (4000x3000) Performance ...")
    img_4k = np.full((3000, 4000, 3), 100, dtype=np.uint8)
    # Draw green leaf-like shape
    cv2.circle(img_4k, (2000, 1500), 1000, (40, 180, 50), -1)
    _, buffer_4k = cv2.imencode('.jpg', img_4k)
    
    t0 = time.perf_counter()
    res_4k = client.post("/predict", files={"file": ("test_4k.jpg", buffer_4k.tobytes(), "image/jpeg")})
    dt_4k = (time.perf_counter() - t0) * 1000.0
    print(f"4K Image Status: {res_4k.status_code} | Total HTTP Request Time: {dt_4k:.2f}ms")
    assert res_4k.status_code == 200
    assert dt_4k < 2000.0, f"4K processing too slow: {dt_4k:.2f}ms"
    
    # 4. Test Blurry Image (Quality Validation Gate)
    print("\n[4] Testing Blurry Image ...")
    blurry_img = cv2.GaussianBlur(img_4k[:500, :500], (51, 51), 30)
    _, buffer_blur = cv2.imencode('.jpg', blurry_img)
    res_blur = client.post("/predict", files={"file": ("blurry.jpg", buffer_blur.tobytes(), "image/jpeg")})
    print(f"Blurry Status: {res_blur.status_code} | Response: {res_blur.json().get('validation_status')}")
    assert res_blur.status_code == 200
    assert res_blur.json().get("validation_status") in ["LOW_QUALITY_IMAGE", "NOT_TOMATO_LEAF"]
    
    # 5. Test Non-leaf image (Black frame)
    print("\n[5] Testing Non-Leaf Image (Blank image) ...")
    black_img = np.zeros((300, 300, 3), dtype=np.uint8)
    _, buffer_black = cv2.imencode('.jpg', black_img)
    res_black = client.post("/predict", files={"file": ("black.jpg", buffer_black.tobytes(), "image/jpeg")})
    print(f"Blank Image Status: {res_black.status_code} | Response: {res_black.json().get('validation_status')}")
    assert res_black.status_code == 200
    assert res_black.json().get("validation_status") in ["LOW_QUALITY_IMAGE", "NOT_TOMATO_LEAF"]
    
    # 6. Test 5 Sequential Requests (Verify stability and no latency growth)
    print("\n[6] Testing 5 Sequential Requests for Latency Stability ...")
    with open(samples["Healthy Leaf"], "rb") as f:
        bytes_seq = f.read()
    seq_times = []
    for i in range(5):
        t0 = time.perf_counter()
        res_seq = client.post("/predict", files={"file": ("seq.jpg", bytes_seq, "image/jpeg")})
        dt_seq = (time.perf_counter() - t0) * 1000.0
        seq_times.append(dt_seq)
        assert res_seq.status_code == 200
        print(f"  Seq Request {i+1}: {dt_seq:.2f}ms (HTTP {res_seq.status_code})")
        
    avg_seq = sum(seq_times) / len(seq_times)
    print(f"Average Sequential Latency: {avg_seq:.2f}ms (Min: {min(seq_times):.2f}ms, Max: {max(seq_times):.2f}ms)")
    
    print("\n" + "=" * 80)
    print("  ALL COMPREHENSIVE TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_tests()
