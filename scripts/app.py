# ==============================
# 🌿 GreenScan App
# ==============================

import streamlit as st
import numpy as np
from PIL import Image
from model_service import predict

# Model loading moved to model_service module

# Class labels
# Class labels are defined in model_service module

# Disease info (🔥 NEW FEATURE)
disease_info = {
    "tomato_Early blight": {
        "solution": "Use fungicide and remove infected leaves.",
        "confidence_tip": "Spreads in warm, humid conditions."
    },
    "tomato_Late blight": {
        "solution": "Apply copper-based fungicide immediately.",
        "confidence_tip": "Can destroy crops quickly."
    },
    "tomato_healthy": {
        "solution": "No action needed. Plant is healthy.",
        "confidence_tip": "Maintain proper watering and sunlight."
    }
}

# UI
st.set_page_config(page_title="GreenScan", layout="centered")
st.title("🌿 GreenScan - Smart Plant Doctor")

uploaded_file = st.file_uploader("Upload a leaf image", type=["jpg", "png", "jpeg"])

# Prediction function
# Prediction is handled by model_service.predict imported above

# Run app
if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    result, confidence = predict(image)

    # 🔥 Confidence score
    st.info(f"Confidence: {confidence*100:.2f}%")

    # 🔥 Smart output
    if "healthy" in result.lower():
        st.success(f"✅ {result}")
    else:
        st.error(f"⚠️ {result}")

    # 🔥 Solution display
    st.subheader("🩺 Recommendation")
    st.write(disease_info[result]["solution"])

    # 🔥 Extra info
    st.subheader("📌 Info")
    st.write(disease_info[result]["confidence_tip"])

    # 🔥 Download result
    st.download_button(
        "📥 Download Result",
        data=f"Prediction: {result}\nConfidence: {confidence*100:.2f}%",
        file_name="result.txt"
    )