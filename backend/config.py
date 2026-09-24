import os
from dotenv import load_dotenv

load_dotenv()

# ─── Farmer Safety & Image Quality Thresholds ─────────────────────────────────
MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.65"))
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "80.0"))
BRIGHTNESS_MIN = float(os.getenv("BRIGHTNESS_MIN", "30.0"))
BRIGHTNESS_MAX = float(os.getenv("BRIGHTNESS_MAX", "230.0"))
GRADCAM_THRESHOLD = float(os.getenv("GRADCAM_THRESHOLD", "0.60"))

# ─── Phase 1: Hierarchical Leaf Validation Thresholds ─────────────────────────
# Minimum percentage of image pixels that must be identified as leaf/plant
# material for the image to be considered a valid tomato leaf image.
# If leaf coverage is below this, the system returns NOT_TOMATO_LEAF.
LEAF_COVERAGE_MIN_PCT = float(os.getenv("LEAF_COVERAGE_MIN_PCT", "10.0"))

# Absolute minimum leaf pixel count (safety floor regardless of percentage).
# Images with very few absolute leaf pixels are rejected as non-leaf.
LEAF_PIXEL_MIN = int(os.getenv("LEAF_PIXEL_MIN", "1000"))

# If model confidence is above MIN_CONFIDENCE_THRESHOLD but below this value,
# a soft "low confidence" warning is added to the response without blocking
# the prediction. Used to flag uncertain predictions to the farmer.
LOW_CONFIDENCE_WARNING_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_WARNING_THRESHOLD", "0.75"))
