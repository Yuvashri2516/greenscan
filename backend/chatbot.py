"""
chatbot.py - GreenScan Context-Aware AI Chatbot Assistant
Automatically integrates latest diagnosis, PHS, severity, and recommendations to answer farmer queries.
"""

import os
from typing import Optional, List

async def get_chat_response(
    message: str,
    language: str = "en",
    context: Optional[dict] = None,
    history: Optional[List[dict]] = None
) -> dict:
    """
    Generates intelligent advice for farmers.
    Utilizes current prediction context (Disease, Confidence, Severity, PHS, Recommendations).
    """
    msg_lower = message.lower().strip()
    
    # Extract prediction context if provided
    disease = context.get("display_name", "Tomato Plant") if context else "Tomato Plant"
    confidence = context.get("confidence", 0.0) if context else 0.0
    severity = context.get("severity_level", "Unknown") if context else "Unknown"
    phs = context.get("plant_health_score", 100) if context else 100
    recs = context.get("recommendations", {}) if context else {}
    
    # Intelligent response matching rules tailored for farmers
    if "organic" in msg_lower or "bio" in msg_lower or "natural" in msg_lower:
        org_treat = recs.get("organic_treatment", "Apply neem oil (5ml/L) or copper sulfate spray every 7 days.")
        response_text = f"🌱 **Organic Treatment for {disease}**:\n\n{org_treat}\n\n*Tip:* Apply organic sprays during early morning or late evening to prevent leaf scorching."
        
    elif "chemical" in msg_lower or "fungicide" in msg_lower or "medicine" in msg_lower or "spray" in msg_lower:
        chem_treat = recs.get("chemical_treatment", "Apply Chlorothalonil or Mancozeb fungicide according to label directions.")
        response_text = f"🧪 **Chemical Treatment Recommendation**:\n\nFor **{disease}** (Severity: {severity}), use:\n{chem_treat}\n\n⚠️ *Safety Warning:* Always wear protective equipment and observe harvest wait periods."

    elif "fertilizer" in msg_lower or "nitorgen" in msg_lower or "potassium" in msg_lower or "feed" in msg_lower:
        fert = recs.get("suitable_fertilizer", "Use balanced N-P-K (10-10-10) with added calcium to strengthen cell walls.")
        response_text = f"🌾 **Fertilizer Guidance**:\n\nRecommended fertilizer for your crop:\n{fert}"

    elif "severity" in msg_lower or "health" in msg_lower or "score" in msg_lower or "bad" in msg_lower:
        if context:
            priority = context.get('treatment_priority', 'Monitor regularly')
            response_text = f"📊 **Crop Health Summary**:\n\n- **Diagnosis**: {disease}\n- **Plant Health Score**: {phs}/100\n- **Severity Level**: {severity}\n- **AI Confidence**: {confidence}%\n\nPriority: {priority}"
        else:
            response_text = (
                "📊 **Crop Health Summary**:\n\n"
                "No active leaf scan context was found. Please upload or scan a tomato leaf image in the **Scan** tab "
                "to retrieve an AI-powered health score, diagnosis, and severity analysis!"
            )

    elif "cause" in msg_lower or "why" in msg_lower or "symptom" in msg_lower:
        causes = recs.get("causes", "Fungal/Oomycete infection favored by leaf wetness and high humidity.")
        symptoms = recs.get("symptoms", "Dark spots, target-board ring patterns, or water-soaked leaf lesions.")
        response_text = f"🔍 **Symptoms & Causes of {disease}**:\n\n**Symptoms:** {symptoms}\n\n**Root Causes:** {causes}"

    elif "prevent" in msg_lower or "avoid" in msg_lower or "stop" in msg_lower:
        prev = recs.get("preventive_measures", "Practice crop rotation, mulch soil to prevent fungal splash, and avoid overhead watering.")
        response_text = f"🛡️ **Preventive Action Plan**:\n\n{prev}"

    elif "recovery" in msg_lower or "time" in msg_lower or "how long" in msg_lower:
        rec_time = recs.get("recovery_time", "7 to 14 days with active treatment.")
        response_text = f"⏳ **Expected Recovery Time**:\n\nWith timely treatment, expected recovery for {disease} is **{rec_time}**."

    else:
        if context:
            response_text = (
                f"Hello! I am GreenScan AI. Based on your scan for **{disease}** (Plant Health Score: {phs}/100, Severity: {severity}):\n\n"
                f"I can help you with:\n"
                f"1. 🌿 **Organic Treatments**\n"
                f"2. 🧪 **Chemical Fungicides**\n"
                f"3. 🌾 **Fertilizer Advice**\n"
                f"4. 🛡️ **Preventive Measures**\n"
                f"5. ⏳ **Recovery Timelines**\n\n"
                f"Feel free to ask any specific question!"
            )
        else:
            response_text = (
                f"Hello! I am GreenScan AI, your tomato farming assistant. 🍅\n\n"
                f"I can help you understand tomato leaf diseases, suggest treatments, and provide farming tips. "
                f"You can also upload a leaf photo in the **Scan** tab to get an AI-powered diagnosis!\n\n"
                f"What would you like to ask me about?\n"
                f"- 🌿 **Organic Treatments**\n"
                f"- 🧪 **Chemical Fungicides**\n"
                f"- 🌾 **Fertilizers & Soil**\n"
                f"- 🛡️ **Preventive Measures**"
            )

    return {
        "reply": response_text,
        "disease_context": disease,
        "plant_health_score": phs,
        "severity": severity
    }
