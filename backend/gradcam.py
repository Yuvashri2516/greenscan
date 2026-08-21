import numpy as np
# Attempt to import TensorFlow; if unavailable, disable Grad-CAM functionality
try:
    import tensorflow as tf
except ImportError:
    tf = None  # Grad-CAM will be disabled
import cv2
import base64
from io import BytesIO
from PIL import Image

def generate_gradcam(model, img_array, class_index):
    """
    Generates Grad-CAM heatmap for a given image and class.
    Returns base64 encoded PNG.
    """
    if tf is None:
        # TensorFlow not available; return None to indicate Grad-CAM disabled
        print("[Grad-CAM] TensorFlow not installed; skipping Grad-CAM generation.")
        return None
    try:
        # 1. Find the last convolutional layer
        last_conv_layer_name = None
        for layer in reversed(model.layers):
            if isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.DepthwiseConv2D)):
                last_conv_layer_name = layer.name
                break
        
        if not last_conv_layer_name:
            # Fallback for some architectures if the above fails
            for layer in model.layers:
                if "conv" in layer.name.lower():
                    last_conv_layer_name = layer.name

        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
        )

        # 2. Compute gradients
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)
            class_channel = preds[:, class_index]

        grads = tape.gradient(class_channel, last_conv_layer_output)

        # 3. Pool gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # 4. Multiply each channel by "how important it is" for the class
        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # 5. Normalize heatmap
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        heatmap = heatmap.numpy()

        # 6. Resize and overlay
        # Load original image for overlay
        # We assume img_array is (1, 224, 224, 3) and normalized to [0, 1]
        img = (img_array[0] * 255).astype(np.uint8)
        
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        superimposed_img = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
        
        # 7. Convert to Base64
        _, buffer = cv2.imencode('.png', superimposed_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"[Grad-CAM] Error: {e}")
        return None
