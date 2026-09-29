"""
gradcam_engine.py - GreenScan Grad-CAM Explainability Matrix Engine
Generates raw 2D normalized activation matrix A(x,y) internally.
The raw heatmap is NEVER exposed to the frontend/farmer directly.
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import logging
from typing import Optional, Tuple, Any

logger = logging.getLogger("greenscan.gradcam")

try:
    import tensorflow as tf
except ImportError:
    tf = None

# In-memory cache for Grad-CAM sub-models and layer names: {model_id: (grad_model, last_conv_layer_name)}
_grad_model_cache = {}

def get_or_build_grad_model(model) -> Optional[Tuple[Any, str]]:
    """
    Retrieves or constructs a cached Grad-CAM model wrapper for the provided tf.keras.Model.
    Avoids rebuilding the computational graph on every prediction request.
    """
    if tf is None or model is None:
        return None
        
    model_id = id(model)
    if model_id in _grad_model_cache:
        return _grad_model_cache[model_id]
        
    try:
        last_conv_layer_name = None
        for layer in reversed(model.layers):
            if isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.DepthwiseConv2D)):
                last_conv_layer_name = layer.name
                break
        
        if not last_conv_layer_name:
            for layer in model.layers:
                if "conv" in layer.name.lower() or "top_conv" in layer.name.lower():
                    last_conv_layer_name = layer.name
                    break

        if not last_conv_layer_name:
            last_conv_layer_name = model.layers[-1].name

        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(last_conv_layer_name).output, model.output]
        )
        _grad_model_cache[model_id] = (grad_model, last_conv_layer_name)
        logger.info(f"Initialized and cached Grad-CAM model with target layer: {last_conv_layer_name}")
        return _grad_model_cache[model_id]
    except Exception as e:
        logger.error(f"Failed to build Grad-CAM model: {e}")
        return None

def init_gradcam_engine(model):
    """Explicitly pre-warms the Grad-CAM engine at server startup."""
    cached = get_or_build_grad_model(model)
    if cached is not None and tf is not None:
        try:
            grad_model, _ = cached
            dummy_tensor = tf.zeros((1, 224, 224, 3), dtype=tf.float32)
            with tf.GradientTape() as tape:
                conv_out, preds = grad_model(dummy_tensor, training=False)
                loss = preds[:, 0]
            _ = tape.gradient(loss, conv_out)
            logger.info("Grad-CAM engine pre-warmed successfully.")
        except Exception as e:
            logger.warning(f"Grad-CAM engine pre-warming warning: {e}")

def get_gradcam_activation_matrix(model, img_array: np.ndarray, class_index: int) -> np.ndarray:
    """
    Computes normalized Grad-CAM activation map for the given target class.
    
    Args:
        model: Trained tf.keras.Model (e.g. EfficientNet-B0)
        img_array: Preprocessed image tensor of shape (1, 224, 224, 3)
        class_index: Target class index (0: Early Blight, 1: Late Blight, 2: Healthy)
        
    Returns:
        2D numpy array of shape (224, 224) with values in range [0.0, 1.0].
    """
    if tf is None or model is None:
        logger.warning("TensorFlow or model is unavailable. Returning synthetic activation matrix.")
        h, w = img_array.shape[1], img_array.shape[2]
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        xx, yy = np.meshgrid(x, y)
        d = np.sqrt(xx*xx + yy*yy)
        synthetic_matrix = np.exp(- (d**2) / 0.5)
        return (synthetic_matrix - synthetic_matrix.min()) / (synthetic_matrix.max() - synthetic_matrix.min() + 1e-8)

    try:
        cached = get_or_build_grad_model(model)
        if cached is None:
            raise RuntimeError("Unable to get or construct Grad-CAM model wrapper.")
            
        grad_model, _ = cached

        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_tensor, training=False)
            loss = predictions[:, class_index]

        # Compute gradients of top class w.r.t last conv layer
        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # Apply ReLU to retain positive activations and normalize to [0, 1]
        heatmap = tf.maximum(heatmap, 0)
        max_val = tf.math.reduce_max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val

        heatmap_np = heatmap.numpy()

        # Resize heatmap to match input image dimensions (224x224) using OpenCV
        import cv2
        target_h, target_w = img_array.shape[1], img_array.shape[2]
        heatmap_resized = cv2.resize(heatmap_np, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        
        # Ensure strict [0, 1] clipping
        heatmap_resized = np.clip(heatmap_resized, 0.0, 1.0)
        return heatmap_resized

    except Exception as e:
        logger.error("Grad-CAM generation error: %s", e)
        # Return fallback matrix in case of runtime layer extraction issue
        return np.full((224, 224), 0.2, dtype=np.float32)
