"""
leaf_segmenter.py - GreenScan Leaf Segmentation & Area Calculation
Step 1 of the GreenScan Severity Analyzer Pipeline
"""

import cv2
import numpy as np

def segment_leaf(img_bgr: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Segments the leaf region from the background using a hybrid HSV color mask
    and Otsu adaptive thresholding.
    
    Returns:
    - leaf_mask: Binary numpy array (224x224) where Leaf pixels = 1 and Background = 0.
    - leaf_pixels: Integer count of total leaf pixels (N_leaf).
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Define broad color range for plant foliage (greens, chlorotic yellows, necrotic browns)
    # Range 1: Green vegetation (Hue: 30-90)
    lower_green = np.array([25, 25, 25])
    upper_green = np.array([95, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Range 2: Necrotic brown/yellow lesion patches (Hue: 5-30)
    lower_brown = np.array([5, 30, 20])
    upper_brown = np.array([25, 255, 220])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Combine HSV masks
    hsv_mask = cv2.bitwise_or(mask_green, mask_brown)
    
    # Otsu thresholding on grayscale channel as fallback / refinement
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Logical OR to retain foliage detail
    combined_mask = cv2.bitwise_or(hsv_mask, otsu_mask)
    
    # Morphological operations to remove noise and fill internal holes in the leaf contour
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    cleaned = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_close)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel_open)
    
    # Find largest contour (assuming main leaf object in frame)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    final_mask = np.zeros_like(cleaned)
    if contours:
        # Filter contours by size, pick largest contour or sum of valid leaf contours
        c = max(contours, key=cv2.contourArea)
        cv2.drawContours(final_mask, [c], -1, 255, -1)
    else:
        final_mask = cleaned
        
    # Convert to binary mask (1 for leaf, 0 for background)
    binary_leaf_mask = (final_mask > 0).astype(np.uint8)
    leaf_pixel_count = int(np.sum(binary_leaf_mask))
    
    # Fallback safety if segmentation produces 0 pixels (e.g. extreme crop)
    total_pixels = img_bgr.shape[0] * img_bgr.shape[1]
    if leaf_pixel_count < 100:
        binary_leaf_mask = np.ones((img_bgr.shape[0], img_bgr.shape[1]), dtype=np.uint8)
        leaf_pixel_count = total_pixels
        
    return binary_leaf_mask, leaf_pixel_count
