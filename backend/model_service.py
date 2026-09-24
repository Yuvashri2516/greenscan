"""
backend/model_service.py

Dedicated inference and model management service for GreenScan.
Loads the frozen research EfficientNetB0 checkpoint (research/models/greenscan_efficientnetb0_best.keras)
and executes standardized preprocessing (RGB, 224x224, raw [0, 255] float32 tensor without double normalization).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger("greenscan.model_service")

# Project root calculation
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
FROZEN_MODEL_PATH = (PROJECT_ROOT / "research" / "models" / "greenscan_efficientnetb0_best.keras").resolve()
FALLBACK_MODEL_PATH = (PROJECT_ROOT / "model" / "greenscan_model.keras").resolve()

# Class mapping (Strict research ordering)
CLASS_LABELS = [
    "tomato_Early blight",  # Index 0
    "tomato_Late blight",   # Index 1
    "tomato_healthy"        # Index 2
]

DISPLAY_NAMES = {
    "tomato_Early blight": "Tomato Early Blight",
    "tomato_Late blight": "Tomato Late Blight",
    "tomato_healthy": "Tomato Healthy"
}

_cached_model = None

def get_model_path() -> Path:
    """Returns the primary frozen model path if it exists, otherwise fallback."""
    if FROZEN_MODEL_PATH.is_file():
        return FROZEN_MODEL_PATH
    elif FALLBACK_MODEL_PATH.is_file():
        logger.warning("Frozen research model not found at %s. Using fallback at %s", FROZEN_MODEL_PATH, FALLBACK_MODEL_PATH)
        return FALLBACK_MODEL_PATH
    else:
        raise FileNotFoundError(f"No valid model checkpoint found at {FROZEN_MODEL_PATH} or {FALLBACK_MODEL_PATH}")

def load_model(model_path: Optional[str] = None):
    """
    Loads and caches the TensorFlow Keras model.
    """
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    target_path = Path(model_path).resolve() if model_path else get_model_path()
    
    if not target_path.is_file():
        logger.error("Model file not found at %s", target_path)
        return None

    try:
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        _cached_model = tf.keras.models.load_model(str(target_path))
        logger.info("Successfully loaded frozen EfficientNet-B0 model from %s", target_path)
        return _cached_model
    except Exception as e:
        logger.error("Failed to load model from %s: %s", target_path, e)
        return None

def preprocess_image(img_input) -> np.ndarray:
    """
    Standardized preprocessing for EfficientNetB0:
    - Input can be PIL.Image or OpenCV BGR numpy array or RGB numpy array.
    - Converts to RGB.
    - Resizes to (224, 224).
    - Preserves raw [0, 255] float32 range (EfficientNetB0 has internal Rescaling(1./255) and Normalization).
    - Avoids double-normalization.
    - Returns tensor of shape (1, 224, 224, 3).
    """
    if isinstance(img_input, Image.Image):
        rgb = np.array(img_input.convert("RGB"))
    elif isinstance(img_input, np.ndarray):
        if len(img_input.shape) == 2:
            rgb = cv2.cvtColor(img_input, cv2.COLOR_GRAY2RGB)
        elif img_input.shape[2] == 4:
            rgb = cv2.cvtColor(img_input, cv2.COLOR_RGBA2RGB)
        else:
            # Assume BGR if from OpenCV or check if already RGB
            rgb = img_input
    else:
        raise ValueError(f"Unsupported image input type: {type(img_input)}")

    # Resize to target 224x224
    if rgb.shape[0] != 224 or rgb.shape[1] != 224:
        rgb_resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_AREA)
    else:
        rgb_resized = rgb

    # Float32 in range [0, 255] WITHOUT dividing by 255.0
    input_arr = np.expand_dims(rgb_resized.astype(np.float32), axis=0)
    return input_arr

def predict(img_input) -> Tuple[str, float, Dict[str, float], int]:
    """
    Runs single-image inference.
    Returns:
        (predicted_class, confidence, probabilities_dict, predicted_index)
    """
    model = load_model()
    if model is None:
        raise RuntimeError("Model is not loaded.")

    tensor = preprocess_image(img_input)
    raw_preds = model.predict(tensor, verbose=0)[0]
    
    predicted_idx = int(np.argmax(raw_preds))
    confidence = float(np.max(raw_preds))
    predicted_class = CLASS_LABELS[predicted_idx]
    
    probs = {CLASS_LABELS[i]: float(raw_preds[i]) for i in range(len(CLASS_LABELS))}
    return predicted_class, confidence, probs, predicted_idx
