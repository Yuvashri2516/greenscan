"""
scripts/test_predict.py - Test /predict endpoint locally or against cloud backend.
"""

import sys
import time
import argparse
import io
import json
import requests
from pathlib import Path
import numpy as np
import cv2

def generate_sample_leaf_bytes():
    """Generates a synthetic 256x256 green leaf image with lesions for testing."""
    img = np.full((256, 256, 3), 40, dtype=np.uint8) # Dark background
    # Draw green leaf ellipse
    cv2.ellipse(img, (128, 128), (90, 60), 45, 0, 360, (34, 139, 34), -1)
    # Draw leaf veins
    cv2.line(img, (50, 50), (200, 200), (46, 170, 46), 2)
    # Draw brown lesion spots
    cv2.circle(img, (120, 110), 14, (30, 70, 139), -1)
    cv2.circle(img, (150, 140), 10, (20, 50, 100), -1)
    
    _, buf = cv2.imencode('.jpg', img)
    return buf.tobytes()

def main():
    parser = argparse.ArgumentParser(description="Test GreenScan /predict endpoint")
    parser.add_argument("--url", default="http://127.0.0.1:8001", help="Base URL of backend (default: http://127.0.0.1:8001)")
    parser.add_argument("--image", default=None, help="Path to sample image file (optional)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    predict_url = f"{base_url}/predict"
    health_url = f"{base_url}/health"

    print("==================================================")
    print("GreenScan /predict Diagnostics Test")
    print(f"Target Base URL: {base_url}")
    print("==================================================")

    # 1. Health check
    try:
        t0 = time.perf_counter()
        h_res = requests.get(health_url, timeout=10)
        h_latency = (time.perf_counter() - t0) * 1000
        print(f"Health Status: {h_res.status_code} ({h_latency:.1f}ms)")
        print(f"Health Body:   {h_res.text}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

    # 2. Prepare sample image
    image_bytes = None
    filename = "test_leaf.jpg"
    if args.image and Path(args.image).is_file():
        image_bytes = Path(args.image).read_bytes()
        filename = Path(args.image).name
        print(f"Using image: {args.image} ({len(image_bytes)} bytes)")
    else:
        # Check standard sample images
        candidates = [
            Path(__file__).parent.parent / "frontend" / "dist" / "assets" / "disease_early_blight.png",
            Path(__file__).parent.parent / "frontend" / "public" / "disease_early_blight.png",
        ]
        for c in candidates:
            if c.is_file():
                image_bytes = c.read_bytes()
                filename = c.name
                print(f"Using standard sample: {c} ({len(image_bytes)} bytes)")
                break

        if image_bytes is None:
            image_bytes = generate_sample_leaf_bytes()
            filename = "sample_synthetic_leaf.jpg"
            print(f"Using synthetic leaf image ({len(image_bytes)} bytes)")

    # 3. Post to /predict
    print(f"\nSending POST to {predict_url} ...")
    files = {"file": (filename, image_bytes, "image/jpeg")}
    
    t0 = time.perf_counter()
    try:
        res = requests.post(predict_url, files=files, timeout=90)
        latency_ms = (time.perf_counter() - t0) * 1000
        latency_s = latency_ms / 1000.0

        print("\n==================================================")
        print(f"Response Status Code: {res.status_code}")
        print(f"Total Client Latency: {latency_ms:.2f} ms ({latency_s:.3f} s)")
        print("==================================================")

        if res.status_code == 200:
            data = res.json()
            print("\nResponse Top-Level JSON Keys:")
            for k in sorted(data.keys()):
                val_type = type(data[k]).__name__
                if isinstance(data[k], dict):
                    print(f"  - {k} (dict, {len(data[k])} keys: {list(data[k].keys())[:5]})")
                elif isinstance(data[k], list):
                    print(f"  - {k} (list, {len(data[k])} items)")
                else:
                    print(f"  - {k} ({val_type}): {data[k]}")
            print("\nKey Diagnostics Summary:")
            print(f"  - Disease:      {data.get('disease')}")
            print(f"  - Confidence:   {data.get('confidence')}%")
            print(f"  - Health Score: {data.get('gsa_metrics', {}).get('plant_health_score')}")
            print(f"  - Severity:     {data.get('gsa_metrics', {}).get('severity_level')}")
            print(f"  - Valid Leaf:   {data.get('is_valid')}")
        else:
            print(f"Error Response Body:\n{res.text}")

    except Exception as e:
        latency_ms = (time.perf_counter() - t0) * 1000
        print(f"Request Error after {latency_ms:.2f}ms: {e}")

if __name__ == "__main__":
    main()
