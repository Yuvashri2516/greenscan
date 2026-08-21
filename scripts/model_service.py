"""Utility module for loading the TensorFlow model and running predictions.
This isolates the heavy ML logic from the Streamlit UI and uses caching so the
model is loaded only once per session.
"""
import tensorflow as tf
import numpy as np
from PIL import Image
import streamlit as st

# Cache the model loading – it runs only once per app start
@st.cache_resource
def load_model(model_path: str = r"C:\Greenscan project\model\greenscan_model.keras"):
    """Load and return the TensorFlow model.
    The function is cached by Streamlit to avoid re‑loading on every rerun.
    """
    return tf.keras.models.load_model(model_path)

# Class labels – keep in sync with app.py
CLASS_LABELS = [
    "tomato_Early blight",
    "tomato_Late blight",
    "tomato_healthy",
]

def preprocess_image(image: Image.Image) -> np.ndarray:
    img = image.resize((224, 224))
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0)

def predict(image: Image.Image) -> tuple[str, float]:
    """Run inference on a Pillow image and return (label, confidence)."""
    model = load_model()
    img_arr = preprocess_image(image)
    prediction = model.predict(img_arr)
    confidence = float(np.max(prediction))
    class_index = int(np.argmax(prediction))
    return CLASS_LABELS[class_index], confidence
