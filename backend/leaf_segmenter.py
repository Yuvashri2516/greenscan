"""
leaf_segmenter.py - GreenScan Leaf Segmentation & Area Calculation
Step 1 of the GreenScan Severity Analyzer Pipeline
"""

import cv2
import numpy as np

def segment_leaf(img_bgr: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Segments the leaf region from the background using a hybrid HSV foliage color mask
    and Excess Green (ExG) adaptive thresholding. Eliminates inverted Otsu grayscale
    thresholding that previously misclassified dark background shadows as leaf pixels.
    
    Returns:
    - leaf_mask: Binary numpy array (224x224) where Leaf pixels = 1 and Background = 0.
    - leaf_pixels: Integer count of total leaf pixels (N_leaf).
    """
    h, w = img_bgr.shape[:2]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Range 1: Green vegetation (Hue: 25-95, Sat: 20-255, Val: 20-255)
    lower_green = np.array([25, 20, 20])
    upper_green = np.array([95, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Range 2: Chlorotic yellow & Necrotic brown patches (Hue: 5-25, Sat: 30-255, Val: 30-240)
    lower_brown = np.array([5, 30, 30])
    upper_brown = np.array([25, 255, 240])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Combine HSV foliage masks
    hsv_mask = cv2.bitwise_or(mask_green, mask_brown)
    
    # Excess Green Index (ExG = 2*G - R - B) for robust vegetation contrast
    b, g, r = cv2.split(img_bgr.astype(np.float32))
    exg = 2.0 * g - r - b
    exg_scaled = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, exg_mask = cv2.threshold(exg_scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Intersect HSV foliage mask with ExG vegetation mask
    combined_mask = cv2.bitwise_and(hsv_mask, exg_mask)
    
    # Fallback to hsv_mask if ExG intersection is overly restrictive (< 5% of frame)
    total_pixels = h * w
    if np.sum(combined_mask > 0) < total_pixels * 0.05:
        combined_mask = hsv_mask
        
    # Morphological operations (close internal leaf holes, open background noise)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    cleaned = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_close)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel_open)
    
    # Find external contours and keep valid leaf regions (>= 1% of image size)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    final_mask = np.zeros((h, w), dtype=np.uint8)
    if contours:
        valid_contours = [c for c in contours if cv2.contourArea(c) >= (total_pixels * 0.01)]
        if valid_contours:
            cv2.drawContours(final_mask, valid_contours, -1, 255, -1)
        else:
            largest_c = max(contours, key=cv2.contourArea)
            cv2.drawContours(final_mask, [largest_c], -1, 255, -1)
    else:
        final_mask = cleaned
        
    # Convert to binary mask (1 for leaf, 0 for background)
    binary_leaf_mask = (final_mask > 0).astype(np.uint8)
    leaf_pixel_count = int(np.sum(binary_leaf_mask))
    
    # Safety fallback if segmentation produces < 100 pixels
    if leaf_pixel_count < 100:
        binary_leaf_mask = np.ones((h, w), dtype=np.uint8)
        leaf_pixel_count = total_pixels
        
    return binary_leaf_mask, leaf_pixel_count

