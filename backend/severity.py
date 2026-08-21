import cv2
import numpy as np
import io
from PIL import Image

def analyze_severity(image_bytes: bytes) -> dict:
    """
    OpenCV-based disease severity analysis.
    Estimates infected area percentage using color thresholding.
    """
    try:
        # Load image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image")

        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define ranges for "diseased" colors (browns, yellows, pale greens)
        # These are heuristic ranges for common tomato blight symptoms
        lower_diseased = np.array([10, 50, 20])
        upper_diseased = np.array([30, 255, 200])
        
        # Define ranges for "healthy" green
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        # Create masks
        mask_diseased = cv2.inRange(hsv, lower_diseased, upper_diseased)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        
        # Calculate areas
        total_pixels = img.shape[0] * img.shape[1]
        diseased_pixels = cv2.countNonZero(mask_diseased)
        green_pixels = cv2.countNonZero(mask_green)
        
        # If total leaf area (green + diseased) is very small, might be a bad image
        leaf_pixels = diseased_pixels + green_pixels
        if leaf_pixels < (total_pixels * 0.05):
            return {
                "severity_pct": 0,
                "stage": "Unknown",
                "infected_area_ratio": 0,
                "leaf_coverage_pct": round((leaf_pixels / total_pixels) * 100, 2)
            }

        severity_pct = (diseased_pixels / leaf_pixels) * 100
        
        # Determine stage
        if severity_pct < 15:
            stage = "Mild"
        elif severity_pct < 40:
            stage = "Moderate"
        else:
            stage = "Severe"

        return {
            "severity_pct": round(severity_pct, 2),
            "stage": stage,
            "infected_area_ratio": round(diseased_pixels / leaf_pixels, 4),
            "leaf_coverage_pct": round((leaf_pixels / total_pixels) * 100, 2)
        }

    except Exception as e:
        print(f"[SeverityAnalysis] Error: {e}")
        return {
            "severity_pct": 0,
            "stage": "Error",
            "infected_area_ratio": 0,
            "error": str(e)
        }
