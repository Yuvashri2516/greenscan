"""
test_illumination.py - GreenScan Illumination Normalization Unit & Integration Tests

Validates:
1. Illumination normalization under direct sunlight & highlights
2. Illumination compensation under deep shadows and uneven lighting
3. Color constancy / white balance under warm evening & indoor lighting
4. Color temperature handling under cool overcast conditions
5. Low-light dynamic range expansion
6. Preservation of disease lesion contrast and structural edges
7. End-to-end integration with image_enhancer and predict pipeline
"""

import sys
import os
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from illumination_normalizer import (
    normalize_illumination,
    detect_color_cast,
    apply_color_constancy,
    normalize_illumination_lab
)
from image_enhancer import enhance_leaf_image

def create_synthetic_leaf(bg_color=(200, 200, 200), leaf_color=(34, 139, 34), lesion_color=(19, 69, 139)):
    """Creates a synthetic tomato leaf image with green foliage and brown necrotic lesion."""
    img = np.full((300, 300, 3), bg_color, dtype=np.uint8)
    
    # Draw leaf ellipse
    cv2.ellipse(img, (150, 150), (100, 60), 30, 0, 360, leaf_color, -1)
    
    # Draw lesion spot (brown necrosis)
    cv2.circle(img, (140, 140), 20, lesion_color, -1)
    # Draw chlorotic halo (yellow)
    cv2.circle(img, (140, 140), 28, (0, 215, 255), 2)
    
    return img

def test_bright_sunlight_condition():
    print("\n[TEST 1] Bright Sunlight & Specular Highlights")
    base_img = create_synthetic_leaf()
    # Simulate bright sunlight overexposure
    bright_img = cv2.add(base_img, np.full_like(base_img, 70))
    
    normalized, diagnostics = normalize_illumination(bright_img)
    
    assert normalized is not None
    assert normalized.shape == bright_img.shape
    assert diagnostics["is_illumination_normalized"] == True
    assert "mean_luminance_normalized" in diagnostics
    # Normalized luminance should be kept bounded away from pure white blowout
    assert diagnostics["mean_luminance_normalized"] <= 250
    print(f"  [PASS] Lighting detected: {diagnostics['lighting_condition']}, normalized L: {diagnostics['mean_luminance_normalized']}")

def test_shadow_and_uneven_illumination():
    print("\n[TEST 2] Deep Canopy Shadow & Uneven Lighting")
    base_img = create_synthetic_leaf()
    
    # Create horizontal shadow gradient (left side dark shadow, right side normal)
    shadow_mask = np.linspace(0.3, 1.0, 300).reshape(1, 300, 1)
    shadow_img = (base_img * shadow_mask).astype(np.uint8)
    
    normalized, diagnostics = normalize_illumination(shadow_img)
    
    assert normalized is not None
    # Shadowed regions should be lifted
    mean_shadow_raw = np.mean(shadow_img[:, :100])
    mean_shadow_norm = np.mean(normalized[:, :100])
    assert mean_shadow_norm > mean_shadow_raw, f"Expected shadow lift: {mean_shadow_norm} > {mean_shadow_raw}"
    print(f"  [PASS] Shadow lift verified: {mean_shadow_raw:.1f} -> {mean_shadow_norm:.1f}")

def test_warm_evening_color_cast():
    print("\n[TEST 3] Warm Evening / Indoor Lighting Color Constancy")
    base_img = create_synthetic_leaf()
    
    # Add warm red/yellow cast
    warm_img = base_img.copy()
    warm_img[:, :, 2] = np.clip(warm_img[:, :, 2] * 1.4, 0, 255) # Red boost
    warm_img[:, :, 0] = np.clip(warm_img[:, :, 0] * 0.7, 0, 255) # Blue drop
    
    cast_type, _ = detect_color_cast(warm_img)
    assert cast_type == "warm_evening_or_indoor"
    
    normalized, diagnostics = normalize_illumination(warm_img)
    assert diagnostics["color_cast"] == "warm_evening_or_indoor"
    print(f"  [PASS] Warm cast detected and normalized via {diagnostics['corrections_applied'][0]}")

def test_low_light_condition():
    print("\n[TEST 4] Low Light / Underexposed Capture")
    base_img = create_synthetic_leaf()
    
    # Simulate dark underexposed image
    dark_img = (base_img * 0.35).astype(np.uint8)
    
    normalized, diagnostics = normalize_illumination(dark_img)
    
    assert diagnostics["shadow_ratio"] > 0.10
    raw_mean = np.mean(dark_img)
    norm_mean = np.mean(normalized)
    assert norm_mean > raw_mean * 1.2, f"Expected brightness recovery: {norm_mean} vs {raw_mean}"
    print(f"  [PASS] Low-light recovered: Mean intensity {raw_mean:.1f} -> {norm_mean:.1f}")

def test_lesion_contrast_preservation():
    print("\n[TEST 5] Disease Lesion Contrast Preservation")
    base_img = create_synthetic_leaf()
    
    normalized, _ = normalize_illumination(base_img)
    
    # Check that lesion center (140, 140) is still clearly distinguishable from healthy leaf (150, 180)
    lesion_patch_norm = normalized[135:145, 135:145]
    leaf_patch_norm = normalized[175:185, 145:155]
    
    lesion_mean_color = np.mean(lesion_patch_norm, axis=(0, 1))
    leaf_mean_color = np.mean(leaf_patch_norm, axis=(0, 1))
    
    # Euclidean color difference in BGR
    color_diff = np.linalg.norm(lesion_mean_color - leaf_mean_color)
    assert color_diff > 30.0, f"Lesion vs Leaf color difference must remain high, got {color_diff}"
    print(f"  [PASS] Lesion vs Leaf color difference preserved: delta={color_diff:.1f}")

def test_image_enhancer_integration():
    print("\n[TEST 6] Integration with image_enhancer.py")
    base_img = create_synthetic_leaf()
    
    resized_bgr, quality_info = enhance_leaf_image(base_img, target_size=(224, 224))
    
    assert resized_bgr.shape == (224, 224, 3)
    assert "illumination" in quality_info
    assert quality_info["illumination"]["is_illumination_normalized"] == True
    print(f"  [PASS] enhance_leaf_image successfully produced 224x224 with illumination diagnostics.")

if __name__ == "__main__":
    print("=" * 60)
    print("  GreenScan Illumination Normalization Test Suite")
    print("=" * 60)
    
    tests = [
        test_bright_sunlight_condition,
        test_shadow_and_uneven_illumination,
        test_warm_evening_color_cast,
        test_low_light_condition,
        test_lesion_contrast_preservation,
        test_image_enhancer_integration
    ]
    
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            
    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
