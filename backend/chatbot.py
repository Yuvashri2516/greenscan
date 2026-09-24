"""
chatbot.py - GreenScan 2.0 Context-Aware AI Chatbot Assistant

GreenScan 2.0 extensions:
  - farmer_context:  Optional farmer profile dict (name, crop_stage, tomato_variety, etc.)
  - weather_context: Optional weather dict (temperature_c, humidity_pct, disease_risk, etc.)
  - history_trend:   Optional trend string ("improving" | "worsening" | "stable")

All existing keyword-matching logic is preserved. New context enriches responses
without breaking backward compatibility with any existing callers.
"""

import os
from typing import Optional, List
from knowledge_base import retrieve_relevant_knowledge


async def get_chat_response(
    message: str,
    language: str = "en",
    context: Optional[dict] = None,
    history: Optional[List[dict]] = None,
    farmer_context: Optional[dict] = None,
    weather_context: Optional[dict] = None,
    history_trend: Optional[str] = None,
) -> dict:
    """
    Generates intelligent advice for farmers.
    Utilizes current prediction context (Disease, Confidence, Severity, PHS, Recommendations)
    plus optional farmer profile and weather context for personalized responses.

    Args (existing, unchanged):
        message:          Farmer's question.
        language:         Language code ("en", "hi", "ta"). Default "en".
        context:          Prediction result dict from /predict.
        history:          Chat history list.

    Args (new in GreenScan 2.0):
        farmer_context:   Farmer profile dict from farmer_db.get_farmer().
        weather_context:  Weather dict from weather.get_weather_risk().
        history_trend:    Trend direction from farmer_db.get_farmer_trends().
    """
    msg_lower = message.lower().strip()

    # ─── Extract prediction context (existing logic, unchanged) ───────────────
    disease = context.get("display_name", "Tomato Plant") if context else "Tomato Plant"
    disease_key = context.get("disease_name", "") if context else ""
    confidence = context.get("confidence", 0.0) if context else 0.0
    severity = context.get("severity_level", "Unknown") if context else "Unknown"
    phs = context.get("plant_health_score", 100) if context else 100
    recs = context.get("recommendations", {}) if context else {}

    # ─── Extract farmer context (new, graceful fallback if absent) ────────────
    farmer_name = ""
    crop_stage = ""
    tomato_variety = ""
    farm_name = ""
    if farmer_context:
        farmer_name = farmer_context.get("name", "")
        crop_stage = farmer_context.get("crop_stage", "")
        tomato_variety = farmer_context.get("tomato_variety", "")
        farm_name = farmer_context.get("farm_name", "")

    # ─── Extract weather context (new, graceful fallback if absent) ───────────
    weather_summary = ""
    if weather_context:
        temp = weather_context.get("temperature_c", "")
        humidity = weather_context.get("humidity_pct", "")
        risk = weather_context.get("disease_risk", {}).get("level", "")
        if temp and humidity:
            weather_summary = f"Current conditions: {temp}°C, {humidity}% humidity, Disease Risk: {risk}."

    # ─── Build personalized greeting prefix ───────────────────────────────────
    greeting = f"Hello{', ' + farmer_name if farmer_name else ''}! "
    scan_context_line = ""
    if context:
        scan_context_line = (
            f"Based on your latest scan — **{disease}** "
            f"(Severity: {severity}, Health Score: {phs}/100)"
        )
        if tomato_variety:
            scan_context_line += f" for your **{tomato_variety}** variety"
        if crop_stage:
            scan_context_line += f" at **{crop_stage}** stage"
        if weather_summary:
            scan_context_line += f" — {weather_summary}"
        scan_context_line += ":\n\n"

    # ─── Trend annotation ─────────────────────────────────────────────────────
    trend_note = ""
    if history_trend == "worsening":
        trend_note = "\n\n⚠️ **Note:** Your scan history shows a worsening trend. Please increase treatment urgency."
    elif history_trend == "improving":
        trend_note = "\n\n✅ **Note:** Your scan history shows an improving trend. Continue current treatment."

    # ─── Keyword-based response matching (all original logic preserved) ────────
    if "organic" in msg_lower or "bio" in msg_lower or "natural" in msg_lower:
        org_treat = recs.get("organic_treatment", "Apply neem oil (5ml/L) or copper sulfate spray every 7 days.")
        # Try to enrich from knowledge base if disease key available
        if disease_key:
            kb_snippets = retrieve_relevant_knowledge("organic treatment", disease_key)
            if kb_snippets:
                kb_content = kb_snippets[0].get("content", [])
                if isinstance(kb_content, list) and kb_content:
                    org_products = [
                        f"• {p.get('name', '')} @ {p.get('rate', '')} every {p.get('interval_days', 7)} days"
                        for p in kb_content if isinstance(p, dict) and p.get("name")
                    ]
                    if org_products:
                        org_treat = "\n".join(org_products)
        response_text = (
            f"🌱 **Organic Treatment for {disease}:**\n\n"
            f"{scan_context_line}"
            f"{org_treat}\n\n"
            f"*Tip:* Apply organic sprays during early morning or late evening to prevent leaf scorching."
            f"{trend_note}"
        )

    elif "chemical" in msg_lower or "fungicide" in msg_lower or "medicine" in msg_lower or "spray" in msg_lower:
        chem_treat = recs.get("chemical_treatment", "Apply Chlorothalonil or Mancozeb fungicide according to label directions.")
        stage_note = f"\n\n📋 **Crop Stage Note ({crop_stage}):** {_crop_stage_note(crop_stage)}" if crop_stage else ""
        response_text = (
            f"🧪 **Chemical Treatment Recommendation:**\n\n"
            f"{scan_context_line}"
            f"For **{disease}** (Severity: {severity}):\n{chem_treat}\n\n"
            f"⚠️ *Safety Warning:* Always wear protective equipment (gloves, mask, goggles) "
            f"and observe the Pre-Harvest Interval (PHI) on the product label."
            f"{stage_note}"
            f"{trend_note}"
        )

    elif "fertilizer" in msg_lower or "nitrogen" in msg_lower or "potassium" in msg_lower or "feed" in msg_lower:
        fert = recs.get("suitable_fertilizer", "Use balanced N-P-K (10-10-10) with added calcium to strengthen cell walls.")
        response_text = (
            f"🌾 **Fertilizer Guidance:**\n\n"
            f"{scan_context_line}"
            f"Recommended fertilizer for your crop:\n{fert}"
        )

    elif "severity" in msg_lower or "health" in msg_lower or "score" in msg_lower or "bad" in msg_lower:
        if context:
            priority = context.get('treatment_priority', 'Monitor regularly')
            weather_line = f"\n- **Weather Risk:** {weather_summary}" if weather_summary else ""
            trend_line = f"\n- **Trend:** {history_trend.title()}" if history_trend and history_trend != "unknown" else ""
            response_text = (
                f"📊 **Crop Health Summary:**\n\n"
                f"- **Diagnosis:** {disease}\n"
                f"- **Plant Health Score:** {phs}/100\n"
                f"- **Severity Level:** {severity}\n"
                f"- **AI Confidence:** {confidence}%"
                f"{weather_line}"
                f"{trend_line}\n\n"
                f"**Priority Action:** {priority}"
                f"{trend_note}"
            )
        else:
            response_text = (
                "📊 **Crop Health Summary:**\n\n"
                "No active leaf scan context was found. Please upload or scan a tomato leaf image in the **Scan** tab "
                "to retrieve an AI-powered health score, diagnosis, and severity analysis!"
            )

    elif "cause" in msg_lower or "why" in msg_lower or "symptom" in msg_lower:
        causes = recs.get("causes", "Fungal/Oomycete infection favored by leaf wetness and high humidity.")
        symptoms = recs.get("symptoms", "Dark spots, target-board ring patterns, or water-soaked leaf lesions.")
        weather_line = f"\n\n🌡️ **Current Conditions:** {weather_summary}" if weather_summary else ""
        response_text = (
            f"🔍 **Symptoms & Causes of {disease}:**\n\n"
            f"**Symptoms:** {symptoms}\n\n"
            f"**Root Causes:** {causes}"
            f"{weather_line}"
        )

    elif "prevent" in msg_lower or "avoid" in msg_lower or "stop" in msg_lower:
        prev = recs.get("preventive_measures", "Practice crop rotation, mulch soil to prevent fungal splash, and avoid overhead watering.")
        response_text = (
            f"🛡️ **Preventive Action Plan:**\n\n"
            f"{scan_context_line}"
            f"{prev}"
        )

    elif "recovery" in msg_lower or "how long" in msg_lower:
        rec_time = recs.get("recovery_time", "7 to 14 days with active treatment.")
        response_text = (
            f"⏳ **Expected Recovery Time:**\n\n"
            f"With timely treatment, expected recovery for {disease} is **{rec_time}**."
            f"{trend_note}"
        )

    elif "weather" in msg_lower or "rain" in msg_lower or "humid" in msg_lower or "temperature" in msg_lower:
        if weather_summary:
            risk_factors = weather_context.get("disease_risk", {}).get("risk_factors", []) if weather_context else []
            rf_lines = "\n".join(f"• {r}" for r in risk_factors[:3]) if risk_factors else ""
            response_text = (
                f"🌤️ **Weather & Disease Risk:**\n\n"
                f"{weather_summary}\n"
                f"{rf_lines}\n\n"
                f"Monitor your crop closely and apply preventive fungicide before rain events."
            )
        else:
            response_text = (
                "🌤️ **Weather Information:**\n\n"
                "No live weather data is currently available. "
                "Visit the **Weather & Risk Radar** tab in the Scan section to check current conditions."
            )

    elif "trend" in msg_lower or "history" in msg_lower or "previous" in msg_lower:
        if history_trend and history_trend != "unknown":
            trend_icon = "✅" if history_trend == "improving" else ("⚠️" if history_trend == "worsening" else "➡️")
            response_text = (
                f"📈 **Your Crop Health Trend:**\n\n"
                f"{trend_icon} Your scan history shows a **{history_trend.upper()}** trend.\n\n"
                f"{'Continue current treatment protocol.' if history_trend == 'improving' else 'Consider escalating treatment or consulting an agricultural expert.' if history_trend == 'worsening' else 'Maintain current management practices and monitor regularly.'}"
            )
        else:
            response_text = (
                "📈 **Crop Health Trend:**\n\n"
                "Scan more times to build a trend analysis. "
                "After 4+ scans, GreenScan will show you whether your crop health is improving, worsening, or stable."
            )

    else:
        # Default / general response
        if context:
            variety_line = f" ({tomato_variety} variety)" if tomato_variety else ""
            stage_line = f" at {crop_stage} stage" if crop_stage else ""
            response_text = (
                f"{greeting}I am GreenScan AI. Based on your scan for **{disease}**{variety_line}{stage_line} "
                f"(Plant Health Score: {phs}/100, Severity: {severity}):\n\n"
                f"I can help you with:\n"
                f"1. 🌿 **Organic Treatments**\n"
                f"2. 🧪 **Chemical Fungicides**\n"
                f"3. 🌾 **Fertilizer Advice**\n"
                f"4. 🛡️ **Preventive Measures**\n"
                f"5. ⏳ **Recovery Timelines**\n"
                f"6. 🌤️ **Weather Risk**\n"
                f"7. 📈 **Health Trend**\n\n"
                f"Feel free to ask any specific question!"
                f"{trend_note}"
            )
        else:
            response_text = (
                f"{greeting}I am GreenScan AI, your tomato farming assistant. 🍅\n\n"
                f"I can help you understand tomato leaf diseases, suggest treatments, and provide farming tips. "
                f"You can also upload a leaf photo in the **Scan** tab to get an AI-powered diagnosis!\n\n"
                f"What would you like to ask me about?\n"
                f"- 🌿 **Organic Treatments**\n"
                f"- 🧪 **Chemical Fungicides**\n"
                f"- 🌾 **Fertilizers & Soil**\n"
                f"- 🛡️ **Preventive Measures**\n"
                f"- 🌤️ **Weather Risk**"
            )

    return {
        "reply": response_text,
        "disease_context": disease,
        "plant_health_score": phs,
        "severity": severity,
        "farmer_context_used": farmer_context is not None,
        "weather_context_used": weather_context is not None,
    }


def _crop_stage_note(crop_stage: str) -> str:
    """Returns a crop-stage-specific treatment note."""
    notes = {
        "Seedling":   "During seedling stage, avoid high-concentration chemical sprays; prefer organic options.",
        "Vegetative": "Vegetative stage: full fungicide applications can be used.",
        "Flowering":  "During flowering, apply sprays in the evening to avoid harming pollinators.",
        "Fruiting":   "During fruiting: strictly observe the Pre-Harvest Interval (PHI) before harvesting.",
        "Harvest":    "At harvest stage: only zero-PHI organic options are advisable. Consult an expert.",
    }
    return notes.get(crop_stage, "")
