"""
gsa_engine.py - GreenScan Severity Analyzer (GSA) Novel Research Contribution Engine
IEEE / Scopus Quality Implementation

Translates internal Grad-CAM activation maps and OpenCV leaf segmentations
into reproducible, farmer-friendly decision support metrics and scientific research data.
"""

import numpy as np

# Configurable constants for GSA mathematical formulas
GRADCAM_THRESHOLD = 0.60
AREA_WEIGHT = 0.60
ACTIVATION_WEIGHT = 0.40

def run_gsa_pipeline(
    gradcam_matrix: np.ndarray,
    leaf_mask: np.ndarray,
    leaf_pixels: int,
    confidence: float,
    predicted_class: str,
) -> dict:
    """
    Executes the GreenScan Severity Analyzer (GSA) computational protocol.
    
    Args:
        gradcam_matrix: 2D float array (224x224) with values in [0.0, 1.0].
        leaf_mask: 2D binary array (224x224) where 1=leaf, 0=background.
        leaf_pixels: Total count of leaf pixels (N_leaf).
        confidence: Prediction confidence float in range [0.0, 1.0].
        predicted_class: Disease label string.
        
    Returns:
        Dictionary containing GSA statistical outputs, research metrics, and severity determinations.
    """
    # Guarantee shapes match
    if gradcam_matrix.shape != leaf_mask.shape:
        import cv2
        gradcam_matrix = cv2.resize(gradcam_matrix, (leaf_mask.shape[1], leaf_mask.shape[0]))
        
    # Isolate Grad-CAM intensities inside the leaf mask boundary
    leaf_gradcam_values = gradcam_matrix * leaf_mask
    
    # ─── STEP 1: Leaf Segmentation ───────────────────────────────────────────
    # N_leaf = Leaf Pixels
    n_leaf = int(leaf_pixels) if leaf_pixels > 0 else int(np.sum(leaf_mask))
    if n_leaf <= 0:
        n_leaf = gradcam_matrix.shape[0] * gradcam_matrix.shape[1]
        
    # ─── STEP 2: Grad-CAM Thresholding & Activated Pixels ─────────────────────
    activated_mask = (leaf_gradcam_values >= GRADCAM_THRESHOLD) & (leaf_mask == 1)
    n_activated = int(np.sum(activated_mask))
    
    # ─── STEP 3: Attention-Affected Region Percentage ────────────────────────
    # Call this "Estimated Attention-Affected Region" to avoid overclaiming.
    attention_affected_region_percent = (n_activated / n_leaf) * 100.0
    attention_affected_region_percent = float(np.clip(attention_affected_region_percent, 0.0, 100.0))
    
    # ─── STEP 4: Activation Analysis ─────────────────────────────────────────
    sum_intensities = float(np.sum(leaf_gradcam_values))
    mean_leaf_activation = sum_intensities / float(n_leaf)
    mean_leaf_activation = float(np.clip(mean_leaf_activation, 0.0, 1.0))
    
    if n_activated > 0:
        mean_activated_activation = float(np.sum(leaf_gradcam_values[activated_mask])) / float(n_activated)
    else:
        mean_activated_activation = 0.0
    mean_activated_activation = float(np.clip(mean_activated_activation, 0.0, 1.0))
    
    # Retain the old weighted_activation_score for legacy compatibility, but rename conceptually
    weighted_activation_score = mean_leaf_activation
    
    # ─── STEP 5: Plant Health Score (PHS) Calculation ───────────────────────
    # PHS scale: [0, 100]
    # Removed ML confidence from PHS formula to keep severity spatial-only.
    is_healthy = "healthy" in predicted_class.lower()
    
    if is_healthy:
        # Healthy plant - theoretically no attention on disease features
        phs = 100.0 - (mean_leaf_activation * 5.0)
    else:
        # Diseased plant reproducible formula balancing spatial extent and intensity
        # Initial research thresholds
        phs = 100.0 - (
            (AREA_WEIGHT * attention_affected_region_percent) +
            (ACTIVATION_WEIGHT * (mean_activated_activation * 100.0))
        )
        
    plant_health_score = int(round(np.clip(phs, 0, 100)))
    
    # ─── STEP 6: Severity & Risk Classification (Initial Research Thresholds) ─
    if plant_health_score >= 90 or is_healthy:
        severity_label = "Healthy"
        traffic_light = "🟢"
        traffic_code = "GREEN"
        risk_level = "None"
        treatment_priority = "No chemical intervention needed. Monitor crop health routinely."
    elif plant_health_score >= 70:
        severity_label = "Mild"
        traffic_light = "🟡"
        traffic_code = "YELLOW"
        risk_level = "Low"
        treatment_priority = "Apply organic bio-fungicide and adjust irrigation within 7 days."
    elif plant_health_score >= 40:
        severity_label = "Moderate"
        traffic_light = "🟠"
        traffic_code = "ORANGE"
        risk_level = "Medium"
        treatment_priority = "Apply targeted copper-based fungicide within 48 hours."
    else:
        severity_label = "Severe"
        traffic_light = "🔴"
        traffic_code = "RED"
        risk_level = "High / Critical"
        treatment_priority = "Isolate infected plants immediately and apply broad-spectrum systemic fungicide within 24 hours."

    return {
        # Research details (Detailed metrics)
        "leaf_pixels": n_leaf,
        "activated_pixels": n_activated,
        "attention_affected_region_percent": round(attention_affected_region_percent, 2),
        "mean_leaf_activation": round(mean_leaf_activation, 4),
        "mean_activated_activation": round(mean_activated_activation, 4),
        "threshold_used": GRADCAM_THRESHOLD,
        
        # Legacy mappings for backward compatibility
        "affected_area_pct": round(attention_affected_region_percent, 2),
        "weighted_activation_score": round(weighted_activation_score, 4),
        
        # Farmer Dashboard metrics
        "plant_health_score": plant_health_score,
        "severity_level": severity_label,
        "traffic_light": traffic_light,
        "traffic_code": traffic_code,
        "risk_level": risk_level,
        "treatment_priority": treatment_priority,
        
        # Internal Masks
        "_internal_activated_mask": activated_mask
    }

