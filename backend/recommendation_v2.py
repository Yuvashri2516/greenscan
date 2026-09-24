"""
recommendation_v2.py - GreenScan 2.0 Phase 10: Farmer-Specific Recommendation Engine

Generates structured, context-aware, farmer-personalized recommendations.
Extends (does NOT replace) the original recommendation_engine.py.

Key principles:
  - The original recommendations key is preserved in /predict for backward compat.
  - This module adds a new structured_recommendation key to the API response.
  - ALL chemical product data is sourced from the verified static dosage.py DB.
  - No LLM is used. No dosages, concentrations, or PHI values are invented.
  - Environmental context and farmer context personalize the text, not the data.

Inputs:
  - disease_key:      Model class label (e.g., "tomato_Late blight")
  - severity_level:   GSA severity label (Healthy / Mild / Moderate / Severe)
  - confidence:       Model confidence float in [0.0, 1.0]
  - weather_context:  Dict from weather.py (temperature_c, humidity_pct, disease_risk, etc.)
  - farmer_context:   Dict from farmer_db.py (crop_stage, tomato_variety, irrigation_method, etc.)
  - history_trend:    String: "improving" | "worsening" | "stable" | "insufficient_data"

Output:
  Structured dict with sections: immediate_actions, prevention, treatment_options,
  environmental_actions, monitoring, safety_information, personalization_notes.
"""

import logging
from typing import Optional, Dict, Any, List

from knowledge_base import get_knowledge, get_environmental_risk_factors
from disease_db import get_disease_info

logger = logging.getLogger("greenscan.recommendation_v2")

# ─── Severity → urgency mapping ──────────────────────────────────────────────
_URGENCY = {
    "Healthy": {"priority": "None", "window": "Monitor routinely", "next_scan_days": 14},
    "Mild":    {"priority": "Low",  "window": "Apply within 7 days", "next_scan_days": 7},
    "Moderate":{"priority": "Medium","window": "Apply within 48 hours", "next_scan_days": 5},
    "Severe":  {"priority": "High", "window": "Apply within 24 hours", "next_scan_days": 3},
}

_CROP_STAGE_NOTES = {
    "Seedling":    "During seedling stage, avoid high-concentration chemical sprays; prefer organic options.",
    "Vegetative":  "Vegetative stage: full fungicide applications can be used. Ensure adequate coverage.",
    "Flowering":   "During flowering, apply sprays in the evening to avoid bee/pollinator harm.",
    "Fruiting":    "During fruiting: strictly observe Pre-Harvest Interval (PHI) before harvesting.",
    "Harvest":     "At harvest stage: only zero-PHI organic options are advisable. Consult an expert.",
}

_IRRIGATION_NOTES = {
    "Overhead":  "Overhead irrigation increases leaf wetness; switch to drip irrigation to reduce fungal spread.",
    "Sprinkler": "Sprinkler irrigation increases leaf wetness duration; consider converting to drip irrigation.",
    "Drip":      "Drip irrigation is optimal for disease management as it keeps foliage dry.",
    "Flood":     "Flood irrigation increases soil-splash spread of spores; use mulch and reduce frequency.",
    "Rainfed":   "Rainfed farming: scout more frequently after rain events for early disease detection.",
}


def get_structured_recommendations(
    disease_key: str,
    severity_level: str,
    confidence: float,
    weather_context: Optional[Dict[str, Any]] = None,
    farmer_context: Optional[Dict[str, Any]] = None,
    history_trend: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates structured, personalized recommendations for a disease diagnosis.

    Returns a structured dict. All product data is from verified static sources.
    """
    kb = get_knowledge(disease_key)
    disease_info = get_disease_info(disease_key)
    urgency = _URGENCY.get(severity_level, _URGENCY["Moderate"])
    is_healthy = disease_key == "tomato_healthy"

    # ─── 1. Immediate Actions ─────────────────────────────────────────────────
    immediate_actions: List[str] = []

    if is_healthy:
        immediate_actions = [
            "Continue current crop management practices.",
            "Monitor lower leaves weekly for early disease signs.",
            "Maintain regular irrigation and fertilization schedule.",
        ]
    elif severity_level == "Mild":
        immediate_actions = [
            "Prune and remove visibly infected lower leaves.",
            "Apply an organic copper-based or neem oil spray.",
            "Improve airflow: ensure adequate plant spacing.",
            "Switch to drip irrigation if using overhead watering.",
        ]
    elif severity_level == "Moderate":
        immediate_actions = [
            f"Treat within 48 hours — do not delay.",
            "Remove and destroy all visibly infected plant material.",
            "Apply targeted fungicide (see Treatment Options below).",
            "Increase field scouting frequency to every 2-3 days.",
            "Avoid any overhead irrigation until symptoms stabilize.",
        ]
    elif severity_level == "Severe":
        immediate_actions = [
            f"URGENT: Isolate affected plants immediately to prevent spread.",
            "Apply broad-spectrum systemic fungicide within 24 hours.",
            "Remove and BURN (not compost) heavily infected plant material.",
            "Alert neighboring farmers — many fungal pathogens spread by wind.",
            "Contact your nearest agricultural extension officer for support.",
        ]

    # Trend modifier
    if history_trend == "worsening" and not is_healthy:
        immediate_actions.insert(0, "⚠️ Your scan history shows a worsening trend. Escalate treatment urgency.")
    elif history_trend == "improving":
        immediate_actions.insert(0, "✅ Trend is improving. Continue current treatment and monitor closely.")

    # ─── 2. Prevention ────────────────────────────────────────────────────────
    prevention = kb.get("prevention", disease_info.get("prevention", []))

    # ─── 3. Treatment Options ─────────────────────────────────────────────────
    treatment_categories = kb.get("treatment_categories", [])
    treatment_options: Dict[str, Any] = {"organic": [], "chemical": [], "note": ""}

    if is_healthy:
        treatment_options["note"] = "No treatment required. Plant is healthy."
        treatment_options["organic"] = ["Apply monthly preventive neem oil spray (2-3 ml/litre)."]
        treatment_options["chemical"] = ["No chemical treatment required."]
    else:
        for cat in treatment_categories:
            category_name = cat.get("category", "").lower()
            products = cat.get("products", [])
            product_lines = []
            for p in products:
                line = f"{p['name']} @ {p['rate']}"
                if p.get("interval_days"):
                    line += f" every {p['interval_days']} days"
                if p.get("phi_days", 0) > 0:
                    line += f" (PHI: {p['phi_days']} days before harvest)"
                if p.get("note"):
                    line += f" — {p['note']}"
                product_lines.append(line)

            if "organic" in category_name or "biological" in category_name:
                treatment_options["organic"] = product_lines
            elif "chemical" in category_name or "conventional" in category_name:
                treatment_options["chemical"] = product_lines

        # Confidence-based note
        if confidence < 0.75:
            treatment_options["note"] = (
                f"Note: Model confidence is {confidence*100:.1f}%, which is below the recommended threshold. "
                "Consider capturing a clearer image before applying any treatment. "
                "When in doubt, consult a qualified agricultural professional."
            )

    # ─── 4. Environmental Actions ─────────────────────────────────────────────
    environmental_actions: List[str] = []
    weather_context_used = False

    if weather_context and not is_healthy:
        weather_context_used = True
        temp = weather_context.get("temperature_c")
        humidity = weather_context.get("humidity_pct")
        rain_prob = weather_context.get("rain_probability_pct", 0)
        risk_level = weather_context.get("disease_risk", {}).get("level", "Unknown")

        env_factors = get_environmental_risk_factors(disease_key, temp, humidity)
        if env_factors:
            environmental_actions.extend(env_factors[:3])  # top 3 relevant factors

        if risk_level in ("High", "Critical"):
            environmental_actions.append(
                f"Current weather risk is {risk_level} "
                f"(Temp: {temp}°C, Humidity: {humidity}%). "
                "Apply fungicide BEFORE expected rain to prevent spore spread."
            )
        elif rain_prob and rain_prob > 50:
            environmental_actions.append(
                f"Rain probability is {rain_prob}%. Apply fungicide preventively before rainfall."
            )
        else:
            environmental_actions.append(
                f"Current conditions (Temp: {temp}°C, Humidity: {humidity}%). "
                "Monitor disease progression and scout field frequently."
            )

    # ─── 5. Monitoring ────────────────────────────────────────────────────────
    monitoring_kb = kb.get("monitoring_guidance", {})
    next_scan_days = urgency["next_scan_days"]
    watch_for = monitoring_kb.get("watch_for", [])
    escalation_trigger = monitoring_kb.get("escalation_trigger", "")

    monitoring = {
        "next_scan_days": next_scan_days,
        "next_scan_recommendation": f"Perform next scan in {next_scan_days} days.",
        "watch_for": watch_for,
        "escalation_trigger": escalation_trigger,
    }

    # ─── 6. Safety Information ────────────────────────────────────────────────
    safety_information = kb.get("safety_information", [])

    # ─── 7. Farmer-Specific Personalization ───────────────────────────────────
    personalization_notes: List[str] = []
    farmer_context_used = False

    if farmer_context:
        farmer_context_used = True
        crop_stage = farmer_context.get("crop_stage", "")
        irrigation = farmer_context.get("irrigation_method", "")
        variety = farmer_context.get("tomato_variety", "")
        farm_name = farmer_context.get("farm_name", "")

        if farm_name:
            personalization_notes.append(f"Recommendation tailored for: {farm_name}")

        if variety:
            personalization_notes.append(
                f"Variety: {variety}. Check if this variety has known resistance to {kb.get('display_name', 'this disease')}."
            )

        if crop_stage and crop_stage in _CROP_STAGE_NOTES:
            personalization_notes.append(f"Crop Stage ({crop_stage}): {_CROP_STAGE_NOTES[crop_stage]}")

        if irrigation and irrigation in _IRRIGATION_NOTES:
            personalization_notes.append(f"Irrigation ({irrigation}): {_IRRIGATION_NOTES[irrigation]}")

    # ─── Assemble Final Response ───────────────────────────────────────────────
    return {
        "disease_display_name": kb.get("display_name", disease_key),
        "disease_key": disease_key,
        "severity": severity_level,
        "confidence_pct": round(confidence * 100, 1),
        "urgency": urgency["priority"],
        "treatment_window": urgency["window"],
        "is_healthy": is_healthy,
        "immediate_actions": immediate_actions,
        "prevention": prevention,
        "treatment_options": treatment_options,
        "environmental_actions": environmental_actions,
        "monitoring": monitoring,
        "safety_information": safety_information,
        "personalization_notes": personalization_notes,
        "history_trend": history_trend or "unknown",
        "farmer_context_used": farmer_context_used,
        "weather_context_used": weather_context_used,
        "disclaimer": (
            "This recommendation is generated by an AI decision-support system and is "
            "intended as a decision-aid only. Always verify product labels and consult a "
            "qualified agricultural professional before applying any chemical treatment."
        ),
    }
