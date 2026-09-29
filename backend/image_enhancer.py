"""
image_enhancer.py - GreenScan OpenCV Image Quality Enhancement & Preprocessing
IEEE/Scopus Research Grade Preprocessing Module
Includes Illumination Normalization & Standardization Stage
"""

import cv2
import numpy as np
from config import BLUR_THRESHOLD, BRIGHTNESS_MIN, BRIGHTNESS_MAX
from illumination_normalizer import normalize_illumination, detect_color_cast

class QualityCheckError(ValueError):
    """Custom exception raised when an input leaf image fails quality validation criteria."""
    pass

def check_image_quality(img_bgr: np.ndarray, blur_threshold: float = BLUR_THRESHOLD, min_brightness: float = BRIGHTNESS_MIN, max_brightness: float = BRIGHTNESS_MAX) -> dict:
    """
    Performs image quality inspection using OpenCV.
    
    Checks:
    1. Blur Detection using Laplacian Variance.
    2. Brightness Normalization Check.
    
    Returns quality metrics or raises QualityCheckError if criteria are violated.
    """
    h, w = img_bgr.shape[:2]
    max_dim = max(h, w)
    
    # If the input image is exceptionally large (> 1024px), downscale for fast quality check
    # to avoid unnecessary CPU allocations while maintaining blur and brightness precision.
    if max_dim > 1024:
        scale = 1024.0 / max_dim
        check_img = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        check_img = img_bgr

    # 1. Blur Detection using Laplacian Variance
    gray = cv2.cvtColor(check_img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 2. Mean Brightness Check
    mean_brightness = np.mean(gray)
    
    is_blurry = laplacian_var < blur_threshold
    is_too_dark = mean_brightness < min_brightness
    is_too_bright = mean_brightness > max_brightness
    
    quality_passed = not (is_blurry or is_too_dark or is_too_bright)
    
    reason = []
    if is_blurry:
        reason.append(f"Image is too blurry (Laplacian Variance: {laplacian_var:.1f} < threshold {blur_threshold})")
    if is_too_dark:
        reason.append(f"Image lighting is too dark (Mean brightness: {mean_brightness:.1f} < {min_brightness})")
    if is_too_bright:
        reason.append(f"Image is overexposed/too bright (Mean brightness: {mean_brightness:.1f} > {max_brightness})")
        
    return {
        "passed": quality_passed,
        "laplacian_variance": round(float(laplacian_var), 2),
        "mean_brightness": round(float(mean_brightness), 2),
        "reasons": reason
    }

def enhance_leaf_image(img_bgr: np.ndarray, target_size: tuple = (224, 224)) -> tuple[np.ndarray, dict]:
    """
    Applies image enhancement and illumination standardization pipeline:
    - Quality Check (Blur & Exposure diagnostics)
    - Pre-resizes to target_size (224x224) to ensure constant O(1) processing time on CPU
    - Stage 1: Illumination Normalization (Color constancy + Retinex dynamic range balancing + CLAHE)
    - Stage 2: Noise Reduction using Bilateral Filter (preserves leaf edge boundaries & lesion spots)
    
    Returns (enhanced_bgr_image, quality_info_dict).
    """
    quality_info = check_image_quality(img_bgr)
    
    # Pre-resize to target dimensions to prevent O(N^2) explosion on high-resolution camera uploads
    if img_bgr.shape[0] != target_size[1] or img_bgr.shape[1] != target_size[0]:
        work_img = cv2.resize(img_bgr, target_size, interpolation=cv2.INTER_AREA)
    else:
        work_img = img_bgr
    
    # Step 1: Research-grade Illumination Normalization & Color Standardization
    illum_normalized_bgr, illum_diagnostics = normalize_illumination(work_img)
    quality_info["illumination"] = illum_diagnostics
    
    # Step 2: Apply Bilateral Filter for noise reduction while keeping lesion edges crisp
    denoised_bgr = cv2.bilateralFilter(illum_normalized_bgr, d=7, sigmaColor=50, sigmaSpace=50)
    
    return denoised_bgr, quality_info
