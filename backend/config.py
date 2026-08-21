import os
from dotenv import load_dotenv

load_dotenv()

# Farmer Safety & Validation Thresholds
MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.65"))
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "80.0"))
BRIGHTNESS_MIN = float(os.getenv("BRIGHTNESS_MIN", "30.0"))
BRIGHTNESS_MAX = float(os.getenv("BRIGHTNESS_MAX", "230.0"))
GRADCAM_THRESHOLD = float(os.getenv("GRADCAM_THRESHOLD", "0.60"))
