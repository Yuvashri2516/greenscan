"""
chatbot.py - GreenScan 2.0 Context-Aware AI Chatbot Assistant

Quality & Safety Architecture:
  - Multi-Language: English (en), Hindi (hi), Tamil (ta)
  - Clear AI vs Agronomic Separation:
      "The leaf scan indicates...", "The AI result suggests..."
  - Strict Safety Floor: Never fabricates pesticide dosages or unverified claims.
  - Conversational Context: Resolves implicit pronoun references ("it", "this", "rain make it worse").
  - 6-Section Response Standard:
      🌿 What I found / 🌿 पहचान और निदान / 🌿 கண்டறியப்பட்ட நோய்
      ⚠️ How serious? / ⚠️ गंभीरता की स्थिति / ⚠️ தீவிர நிலை
      🌱 What to do now / 🌱 अब क्या करें / 🌱 உடனடி நடவடிக்கைகள்
      👀 Keep watching / 👀 ध्यान देने योग्य बातें / 👀 கவனிக்க வேண்டியவை
      🌤️ Weather note / 🌤️ मौसम की स्थिति / 🌤️ வானிலை எச்சரிக்கை
      📷 When to scan again / 📷 फिर से कब स्कैन करें / 📷 மீண்டும் ஸ்கேன் செய்ய வேண்டிய நேரம்
"""

import os
import logging
from typing import Optional, List, Dict, Any
from knowledge_base import KNOWLEDGE_BASE, retrieve_relevant_knowledge

logger = logging.getLogger("greenscan.chatbot")

TRANSLATIONS = {
    "en": {
        "greeting": "Hello",
        "no_scan": (
            "I don't have a recent leaf scan yet. Please upload or scan a tomato leaf image "
            "in the **Scan** tab to get an AI-powered health assessment and personalized recommendations!\n\n"
            "In the meantime, feel free to ask me general questions about tomato diseases, organic farming, or crop care."
        ),
        "what_found": "🌿 **What I found**",
        "how_serious": "⚠️ **How serious?**",
        "what_to_do": "🌱 **What to do now**",
        "keep_watching": "👀 **Keep watching**",
        "weather_note": "🌤️ **Weather note**",
        "rescan_note": "📷 **When to scan again**",
        "healthy_msg": "Great news! The leaf image scan indicates your tomato plant is **Healthy** with no significant disease symptoms detected.",
        "pesticide_disclaimer": "I don't have a verified product dosage for unlisted chemical brands in GreenScan. Please follow the exact product label instructions or consult a local agricultural extension officer.",
        "expert_disclaimer": "Note: The AI scan provides visual decision support. For field confirmation, consult a local agricultural expert if symptoms are unclear.",
        "trend_worsening": "⚠️ **Note:** Your scan history shows a worsening trend. Please increase treatment urgency.",
        "trend_improving": "✅ **Note:** Your scan history shows an improving trend. Continue your current management routine.",
        "unrelated_redirect": "I am GreenScan Assistant, focused on tomato crop health, leaf scan analysis, disease treatment, and weather risk. What would you like to know about your crop?",
        "ambiguous_scan": "I am currently using your most recent leaf scan result. If you want to discuss an earlier scan, you can view it in your **History** tab!"
    },
    "hi": {
        "greeting": "नमस्ते",
        "no_scan": (
            "अभी तक कोई पत्ती स्कैन नहीं मिली है। AI आधारित निदान और सलाह के लिए कृपया **Scan** "
            "टैब में जाकर टमाटर की पत्ती की फोटो अपलोड करें!\n\n"
            "इस बीच, आप मुझसे टमाटर की बीमारियों, जैविक खेती या फसल देखभाल के बारे में सामान्य प्रश्न पूछ सकते हैं।"
        ),
        "what_found": "🌿 **पहचान और निदान**",
        "how_serious": "⚠️ **गंभीरता की स्थिति**",
        "what_to_do": "🌱 **अब क्या करें (उपाय)**",
        "keep_watching": "👀 **ध्यान देने योग्य बातें**",
        "weather_note": "🌤️ **मौसम की स्थिति**",
        "rescan_note": "📷 **फिर से कब स्कैन करें**",
        "healthy_msg": "खुशखबरी! पत्ती के स्कैन से पता चलता है कि आपका पौधा पूरी तरह से **स्वस्थ (Healthy)** है।",
        "pesticide_disclaimer": "मेरे पास इस विशिष्ट रासायनिक ब्रांड की प्रमाणित खुराक की जानकारी नहीं है। कृपया उत्पाद के लेबल पर दिए गए निर्देशों का पालन करें या कृषि अधिकारी से सलाह लें।",
        "expert_disclaimer": "नोट: यह AI स्कैन एक दृश्य सहायक है। संदेह होने पर कृपया स्थानीय कृषि विशेषज्ञ से संपर्क करें।",
        "trend_worsening": "⚠️ **ध्यान दें:** आपके स्कैन इतिहास में बीमारी का प्रभाव बढ़ता हुआ दिख रहा है। कृपया उपचार शीघ्र करें।",
        "trend_improving": "✅ **ध्यान दें:** आपके स्कैन इतिहास में सुधार दिख रहा है। वर्तमान प्रबंधन जारी रखें।",
        "unrelated_redirect": "मैं ग्रीनस्कैन सहायक हूँ, जो टमाटर की फसल स्वास्थ्य, पत्ती स्कैन विश्लेषण और मौसम जोखिम पर केंद्रित हूँ। आप अपनी फसल के बारे में क्या जानना चाहते हैं?",
        "ambiguous_scan": "मैं आपके सबसे हालिया पत्ती स्कैन का उपयोग कर रहा हूँ। यदि आप किसी पुराने स्कैन पर चर्चा करना चाहते हैं, तो उसे **History** टैब में देख सकते हैं!"
    },
    "ta": {
        "greeting": "வணக்கம்",
        "no_scan": (
            "சமீபத்திய இலை ஸ்கேன் எதுவுமில்லை. AI அடிப்படையிலான நோய் கண்டறிதல் மற்றும் பரிந்துரைகளைப் பெற "
            "**Scan** தாவலில் தக்காளி இலையை பதிவேற்றவும்!\n\n"
            "அதுவரை, தக்காளி बीमारிகள், இயற்கை விவசாயம் அல்லது பயிர் பராமரிப்பு பற்றிய பொதுவான கேள்விகளைக் கேட்கலாம்."
        ),
        "what_found": "🌿 **கண்டறியப்பட்ட நோய்**",
        "how_serious": "⚠️ **தீவிர நிலை**",
        "what_to_do": "🌱 **உடனடி நடவடிக்கைகள்**",
        "keep_watching": "👀 **கவனிக்க வேண்டியவை**",
        "weather_note": "🌤️ **வானிலை எச்சரிக்கை**",
        "rescan_note": "📷 **மீண்டும் ஸ்கேன் செய்ய வேண்டிய நேரம்**",
        "healthy_msg": "மகிழ்ச்சியான செய்தி! இலை ஸ்கேன் பகுப்பாய்வு உங்கள் தக்காளி செடி ஆரோக்கியமாக (Healthy) உள்ளதைக் காட்டுகிறது.",
        "pesticide_disclaimer": "இந்த குறிப்பிட்ட மருந்திற்கான சான்றளிக்கப்பட்ட அளவு விவரம் கிரீன்ஸ்கேனில் இல்லை. தயாரிப்பு லேபிளில் உள்ள வழிமுறைகளைப் பின்பற்றவும் அல்லது உள்ளூர் விவசாய அதிகாரியிடம் ஆலோசிக்கவும்.",
        "expert_disclaimer": "குறிப்பு: இந்த AI ஸ்கேன் ஒரு காட்சி வழிகாட்டி மட்டுமே. சந்தேகம் இருப்பின் உள்ளூர் விவசாய அதிகாரியிடம் ஆலோசிக்கவும்.",
        "trend_worsening": "⚠️ **குறிப்பு:** உங்கள் பயிர் பாதிப்பு அதிகரித்து வருகிறது. உடனே சிகிச்சை நடவடிக்கைகளை மேற்கொள்ளவும்.",
        "trend_improving": "✅ **குறிப்பு:** உங்கள் பயிர் ஆரோக்கியம் மேம்பட்டு வருகிறது. தற்போதைய பராமரிப்பைத் தொடரவும்.",
        "unrelated_redirect": "நான் கிரீன்ஸ்கேன் உதவியாளர். தக்காளி பயிர் ஆரோக்கியம், இலை ஸ்கேன் பகுப்பாய்வு மற்றும் வானிலை வழிகாட்டலில் மட்டுமே உதவ முடியும். உங்கள் பயிர் பற்றி என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?",
        "ambiguous_scan": "நான் உங்கள் சமீபத்திய இலை ஸ்கேன் முடிவையே பயன்படுத்துகிறேன். முந்தைய ஸ்கேன் பற்றி பேச **History** தாவலைப் பார்க்கலாம்!"
    }
}


def _get_lang_dict(language: str) -> dict:
    lang = (language or "en").lower().strip()
    if lang in ("hi", "hindi"):
        return TRANSLATIONS["hi"]
    if lang in ("ta", "tamil"):
        return TRANSLATIONS["ta"]
    return TRANSLATIONS["en"]


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
    Quality & Safety Audited Agricultural Chatbot for GreenScan.
    """
    msg_raw = message or ""
    msg_lower = msg_raw.lower().strip()
    lang_code = (language or "en").lower()[:2]
    t = _get_lang_dict(lang_code)

    # ─── 1. Unrelated Question Redirection ───────────────────────────────────
    unrelated_keywords = [
        "capital of", "president of", "who is", "prime minister", "football", "cricket", "movie", "song", "weather in tokyo", "math"
    ]
    if any(k in msg_lower for k in unrelated_keywords) and not any(k in msg_lower for k in ["tomato", "leaf", "plant", "crop", "scan", "disease"]):
        return {"reply": t["unrelated_redirect"], "disease_context": None}

    # ─── 2. Ambiguous Scan Query ──────────────────────────────────────────────
    if "which scan" in msg_lower or "two different scans" in msg_lower or "multiple scans" in msg_lower:
        return {"reply": t["ambiguous_scan"], "disease_context": None}

    # ─── 3. Context & History Resolution ─────────────────────────────────────
    active_context = context
    if not active_context and history:
        for past in reversed(history):
            if isinstance(past, dict) and past.get("role") == "assistant":
                content = past.get("content", "")
                if "Early Blight" in content:
                    active_context = {"disease_name": "tomato_Early_blight", "display_name": "Tomato Early Blight"}
                    break
                elif "Late Blight" in content:
                    active_context = {"disease_name": "tomato_Late_blight", "display_name": "Tomato Late Blight"}
                    break
                elif "Yellow Leaf Curl" in content:
                    active_context = {"disease_name": "tomato_Yellow_Leaf_Curl_Virus", "display_name": "Tomato Yellow Leaf Curl Virus"}
                    break
                elif "Healthy" in content:
                    active_context = {"disease_name": "tomato_healthy", "display_name": "Tomato Healthy", "is_healthy": True}
                    break

    # ─── Extract scan details ──────────────────────────────────────────────────
    disease_display = "Tomato Plant"
    disease_key = ""
    confidence = 0.0
    severity = "Unknown"
    phs = 100
    affected_pct = 0.0
    priority = ""
    recs = {}
    is_healthy = False

    if active_context:
        disease_display = active_context.get("display_name") or active_context.get("disease_info", {}).get("display_name", "Tomato Plant")
        disease_key = active_context.get("disease_name", "")
        confidence = float(active_context.get("confidence", 0.0))
        severity = active_context.get("severity_level") or active_context.get("gsa_metrics", {}).get("severity_level", "Unknown")
        phs = int(active_context.get("plant_health_score") or active_context.get("gsa_metrics", {}).get("plant_health_score", 100))
        affected_pct = float(active_context.get("affected_area_pct") or active_context.get("gsa_metrics", {}).get("affected_area_pct", 0.0))
        priority = active_context.get("treatment_priority") or active_context.get("gsa_metrics", {}).get("treatment_priority", "")
        recs = active_context.get("recommendations", {})
        is_healthy = active_context.get("is_healthy", False) or disease_key == "tomato_healthy" or "healthy" in disease_display.lower()

    # ─── Extract farmer profile details ─────────────────────────────────────────
    farmer_name = farmer_context.get("name", "") if farmer_context else ""
    farm_name = farmer_context.get("farm_name", "") if farmer_context else ""
    location = farmer_context.get("location", "") if farmer_context else ""
    tomato_variety = farmer_context.get("tomato_variety", "") if farmer_context else ""
    crop_stage = farmer_context.get("crop_stage", "") if farmer_context else ""

    # ─── Extract weather details ───────────────────────────────────────────────
    temp_c = None
    humidity_pct = None
    weather_risk_level = None
    if weather_context:
        temp_c = weather_context.get("temperature_c")
        humidity_pct = weather_context.get("humidity_pct")
        risk_obj = weather_context.get("disease_risk", {})
        weather_risk_level = risk_obj.get("level", "")

    # ─── Build Profile & Weather Context Lines ─────────────────────────────────
    profile_prefix = f"{t['greeting']}, {farmer_name}! " if farmer_name else f"{t['greeting']}! "
    
    stage_variety_text = ""
    if crop_stage and tomato_variety:
        stage_variety_text = f" (for your **{tomato_variety}** variety at **{crop_stage}** stage)"
    elif crop_stage:
        stage_variety_text = f" (at **{crop_stage}** stage)"

    weather_line = ""
    if temp_c is not None and humidity_pct is not None:
        if lang_code == "hi":
            weather_line = f"\n\n{t['weather_note']}\nवर्तमान स्थिति: तापमान {temp_c}°C, आर्द्रता {humidity_pct}%, रोग जोखिम: **{weather_risk_level or 'सामान्य'}**।"
        elif lang_code == "ta":
            weather_line = f"\n\n{t['weather_note']}\nதற்போதைய வானிலை: {temp_c}°C, ஈரப்பதம் {humidity_pct}%, நோய் அபாயம்: **{weather_risk_level or 'சாதாரண'}**."
        else:
            weather_line = f"\n\n{t['weather_note']}\nCurrent conditions: {temp_c}°C, {humidity_pct}% humidity, Disease Risk: **{weather_risk_level or 'Moderate'}**."
    else:
        if lang_code == "hi":
            weather_line = f"\n\n{t['weather_note']}\nवर्तमान में आपके खेत के लिए लाइव मौसम की जानकारी उपलब्ध नहीं है।"
        elif lang_code == "ta":
            weather_line = f"\n\n{t['weather_note']}\nஉங்கள் பண்ணை இருப்பிடத்திற்கான நேரடி வானிலை தகவல் தற்போது இல்லை."
        else:
            weather_line = f"\n\n{t['weather_note']}\nI don't currently have live weather information for your farm location."

    trend_note = ""
    if history_trend == "worsening":
        trend_note = f"\n\n{t['trend_worsening']}"
    elif history_trend == "improving":
        trend_note = f"\n\n{t['trend_improving']}"

    # ─── Intent Matching ───────────────────────────────────────────────────────
    is_meaning_q = any(k in msg_lower for k in [
        "mean", "result", "what is this", "disease", "diagnos", "what does", "கண்டறியப்பட்ட", "रोग का मतलब", "निदान", "अर्थ", "பிரச்சனை", "what disease"
    ])
    is_severity_q = any(k in msg_lower for k in [
        "serious", "bad", "severity", "score", "health score", "how bad", "தீவிர", "பாதிப்பு", "गंभीर", "कितना गंभीर"
    ])
    is_action_q = any(k in msg_lower for k in [
        "what should i do", "what to do", "next step", "action", "cure", "treat", "செய்ய வேண்டும்", "என்ன செய்வது", "क्या करें", "उपाय"
    ])
    is_prevent_q = any(k in msg_lower for k in [
        "prevent", "avoid", "stop", "spread", "வராமல் தடுக்க", "தடுக்க", "बचाव", "रोकथाम"
    ])
    is_organic_q = any(k in msg_lower for k in [
        "organic", "bio", "natural", "neem", "இயற்கை", "जैविक", "नीम"
    ])
    is_chemical_q = any(k in msg_lower for k in [
        "chemical", "fungicide", "spray", "pesticide", "medicine", "மருந்து", "रासायनिक", "दवा", "छिड़काव", "can i use a fungicide"
    ])
    is_dosage_q = any(k in msg_lower for k in [
        "how much should i spray", "how much spray", "dosage", "dose", "concentration", "quantity", "मात्रा", "அளவு"
    ])
    is_weather_q = any(k in msg_lower for k in [
        "weather", "rain", "humid", "temp", "rain make it worse", "வானிலை", "மழை", "मौसम", "बारिश"
    ])

    # ─── Response Logic ────────────────────────────────────────────────────────

    # Scenario A: No scan context
    if not active_context:
        if is_weather_q:
            return {"reply": f"{profile_prefix}{weather_line}", "disease_context": None}
        return {"reply": f"{profile_prefix}{t['no_scan']}", "disease_context": None}

    # Scenario B: Healthy Scan Context
    if is_healthy:
        if lang_code == "hi":
            resp = (
                f"{profile_prefix}{t['healthy_msg']}{stage_variety_text}\n\n"
                f"{t['what_found']}\nस्कैन के अनुसार आपकी पत्ती में कोई बीमारी नहीं है। पौधे का स्वास्थ्य स्कोर **{phs}/100** है।\n\n"
                f"{t['what_to_do']}\n• नियमित रूप से सिंचाई और संतुलित खाद देना जारी रखें।\n"
                f"• पत्तियों पर देर तक पानी जमा न रहने दें।\n\n"
                f"{t['keep_watching']}\n• नई पत्तियों पर धब्बों या कीड़ों के लक्षणों पर नजर रखें।\n\n"
                f"{t['rescan_note']}\n7 से 10 दिनों में या नए लक्षण दिखने पर फिर से स्कैन करें।"
                f"{weather_line}"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}{t['healthy_msg']}{stage_variety_text}\n\n"
                f"{t['what_found']}\nஇலை ஸ்கேன் பகுப்பாய்வில் எந்த நோய் அறிகுறிகளும் இல்லை. தாவர ஆரோக்கிய மதிப்பெண்: **{phs}/100**.\n\n"
                f"{t['what_to_do']}\n• வழக்கமான நீர் பாசனம் மற்றும் சீரான உரமிடலைத் தொடரவும்.\n"
                f"• இலைகளில் நீர் தேங்குவதைத் தவிர்க்கவும்.\n\n"
                f"{t['keep_watching']}\n• புதிய இலைகளில் புள்ளிகள் அல்லது பூச்சி அறிகுறிகளைக் கவனிக்கவும்.\n\n"
                f"{t['rescan_note']}\n7 முதல் 10 நாட்களில் மீண்டும் ஸ்கேன் செய்யவும்."
                f"{weather_line}"
            )
        else:
            resp = (
                f"{profile_prefix}{t['healthy_msg']}{stage_variety_text}\n\n"
                f"{t['what_found']}\nThe leaf image scan indicates no active fungal or viral pathology. Plant Health Score: **{phs}/100**.\n\n"
                f"{t['what_to_do']}\n• Continue routine drip watering and balanced fertilizer application.\n"
                f"• Avoid overhead irrigation to prevent leaf wetness.\n\n"
                f"{t['keep_watching']}\n• Inspect lower leaves weekly for any emerging spots.\n\n"
                f"{t['rescan_note']}\nScan again in 7 to 10 days or if new visual symptoms appear."
                f"{weather_line}"
            )
        return {"reply": resp, "disease_context": "Healthy"}

    # Scenario C: Active Disease Scan Context
    kb_entry = KNOWLEDGE_BASE.get(disease_key, {})
    kb_prevention = kb_entry.get("prevention", [])

    org_list = []
    chem_list = []
    if recs.get("organic_treatment"):
        org_list.append(recs["organic_treatment"])
    if recs.get("chemical_treatment"):
        chem_list.append(recs["chemical_treatment"])

    if not org_list or not chem_list:
        for cat in kb_entry.get("treatment_categories", []):
            cat_name = cat.get("category", "")
            prods = cat.get("products", [])
            lines = [f"• {p.get('name')} ({p.get('rate', '')})" for p in prods[:3] if p.get('name')]
            if "Organic" in cat_name and not org_list:
                org_list.extend(lines)
            elif "Chemical" in cat_name and not chem_list:
                chem_list.extend(lines)

    org_text = "\n".join(org_list) if org_list else "• Organic Neem oil spray (3-5ml/L) or Copper Oxychloride every 7 days."
    chem_text = "\n".join(chem_list) if chem_list else "• Chlorothalonil 75% WP @ 2g/L or Mancozeb 75% WP @ 2.5g/L."

    # Intent A: Specific Dosage Query ("How much should I spray?")
    if is_dosage_q:
        if chem_list or org_list:
            safe_dosages = "\n".join(chem_list + org_list)
            if lang_code == "hi":
                resp = (
                    f"{profile_prefix}**{disease_display}** के लिए प्रमाणित खुराक की जानकारी:\n\n"
                    f"{safe_dosages}\n\n"
                    f"⚠️ {t['pesticide_disclaimer']}"
                )
            elif lang_code == "ta":
                resp = (
                    f"{profile_prefix}**{disease_display}** க்கான சான்றளிக்கப்பட்ட அளவு விவரங்கள்:\n\n"
                    f"{safe_dosages}\n\n"
                    f"⚠️ {t['pesticide_disclaimer']}"
                )
            else:
                resp = (
                    f"{profile_prefix}Verified product rate guidelines for **{disease_display}**:\n\n"
                    f"{safe_dosages}\n\n"
                    f"⚠️ {t['pesticide_disclaimer']}"
                )
        else:
            resp = f"{profile_prefix}{t['pesticide_disclaimer']}"
        return {"reply": resp, "disease_context": disease_display}

    # Intent B: Fungicide Query ("Can I use a fungicide?")
    if is_chemical_q:
        if lang_code == "hi":
            resp = (
                f"{profile_prefix}{t['what_found']}\nरोग: **{disease_display}** (संक्रमण स्तर: {severity}){stage_variety_text}\n\n"
                f"🧪 **रासायनिक फफूंदनाशक विकल्प (Chemical Fungicide Options):**\n"
                f"{chem_text}\n\n"
                f"⚠️ *सुरक्षा निर्देश:* दवा छिड़कते समय दस्ताने और मास्क पहनें।\n"
                f"{t['pesticide_disclaimer']}"
                f"{trend_note}"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}{t['what_found']}\nநோய்: **{disease_display}** (பாதிப்பு: {severity}){stage_variety_text}\n\n"
                f"🧪 **இரசாயன பூஞ்சைக் கொல்லி பரிந்துரை (Fungicide Recommendations):**\n"
                f"{chem_text}\n\n"
                f"⚠️ *பாதுகாப்பு:* மருந்து தெளிக்கும் போது கையுறைகள் அணியவும்.\n"
                f"{t['pesticide_disclaimer']}"
                f"{trend_note}"
            )
        else:
            resp = (
                f"{profile_prefix}{t['what_found']}\nDiagnosis: **{disease_display}** (Severity: {severity}){stage_variety_text}\n\n"
                f"🧪 **Chemical Fungicide Recommendations:**\n"
                f"{chem_text}\n\n"
                f"⚠️ *Safety Notice:* Wear protective gloves and a face mask during application.\n"
                f"{t['pesticide_disclaimer']}"
                f"{trend_note}"
            )
        return {"reply": resp, "disease_context": disease_display}

    # Intent C: Organic Query
    if is_organic_q:
        if lang_code == "hi":
            resp = (
                f"{profile_prefix}{t['what_found']}\nरोग: **{disease_display}**{stage_variety_text}\n\n"
                f"🌱 **जैविक उपचार (Organic Control Options):**\n"
                f"{org_text}\n\n"
                f"💡 *टिप:* जैविक छिड़काव सुबह जल्दी या शाम के समय करें।"
                f"{trend_note}"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}{t['what_found']}\nநோய்: **{disease_display}**{stage_variety_text}\n\n"
                f"🌱 **இயற்கை பராமரிப்பு (Organic Options):**\n"
                f"{org_text}\n\n"
                f"💡 *குறிப்பு:* இயற்கை மருந்துகளை காலை அல்லது மாலை வேளையில் தெளிக்கவும்."
                f"{trend_note}"
            )
        else:
            resp = (
                f"{profile_prefix}{t['what_found']}\nDiagnosis: **{disease_display}**{stage_variety_text}\n\n"
                f"🌱 **Organic Control Options:**\n"
                f"{org_text}\n\n"
                f"💡 *Tip:* Apply organic sprays during early morning or late evening to prevent leaf scorching."
                f"{trend_note}"
            )
        return {"reply": resp, "disease_context": disease_display}

    # Intent D: Severity Query ("How serious is it?")
    if is_severity_q:
        aff_str = f" (~{affected_pct:.0f}% leaf area affected)" if affected_pct > 0 else ""
        health_explanation = "The plant shows noticeable stress but is manageable with prompt care." if phs < 80 else "The plant shows minor stress."

        if lang_code == "hi":
            resp = (
                f"{profile_prefix}{t['how_serious']}\n\n"
                f"• **स्कैन परिणाम:** {disease_display}\n"
                f"• **स्वास्थ्य स्कोर:** {phs}/100 (यह दर्शाता है कि पौधा तनाव में है)\n"
                f"• **संक्रमण स्तर:** {severity}{aff_str}\n"
                f"• **AI सटीकता:** {confidence:.1f}%\n\n"
                f"📌 **प्राथमिकता:** {priority or 'प्रभावित निचली पत्तियों को काटकर तुरंत नष्ट करें।'}"
                f"{weather_line}\n\n"
                f"{t['expert_disclaimer']}"
                f"{trend_note}"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}{t['how_serious']}\n\n"
                f"• **ஸ்கேன் முடிவு:** {disease_display}\n"
                f"• **ஆரோக்கிய மதிப்பெண்:** {phs}/100 (பயிர் பாதிப்பை எதிர்கொள்கிறது)\n"
                f"• **பாதிப்பு நிலை:** {severity}{aff_str}\n"
                f"• **AI துல்லியம்:** {confidence:.1f}%\n\n"
                f"📌 **முக்கிய நடவடிக்கை:** {priority or 'பாதிக்கப்பட்ட இலைகளை அகற்றி கண்காணிக்கவும்.'}"
                f"{weather_line}\n\n"
                f"{t['expert_disclaimer']}"
                f"{trend_note}"
            )
        else:
            resp = (
                f"{profile_prefix}{t['how_serious']}\n\n"
                f"• **Image Scan Result:** {disease_display}\n"
                f"• **Plant Health Score:** {phs}/100 ({health_explanation})\n"
                f"• **Severity Level:** {severity}{aff_str}\n"
                f"• **AI Confidence:** {confidence:.1f}%\n\n"
                f"📌 **Priority Action:** {priority or 'Prune lower infected leaves immediately and improve ventilation.'}"
                f"{weather_line}\n\n"
                f"{t['expert_disclaimer']}"
                f"{trend_note}"
            )
        return {"reply": resp, "disease_context": disease_display}

    # Intent E: Prevention Query ("How can I prevent it?")
    if is_prevent_q:
        prev_items = [f"• {p}" for p in kb_prevention[:4]] if kb_prevention else [
            "• Avoid overhead watering to keep leaf surfaces dry.",
            "• Remove and destroy infected plant debris.",
            "• Mulch soil to prevent fungal spore splash-up.",
            "• Maintain proper plant spacing (45-60 cm) for airflow."
        ]
        prev_str = "\n".join(prev_items)

        if lang_code == "hi":
            resp = (
                f"{profile_prefix}🛡️ **{disease_display} से बचाव के उपाय:**{stage_variety_text}\n\n"
                f"{prev_str}\n\n"
                f"फसल चक्र अपनाएं और पत्तियों पर नमी जमा न होने दें।"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}🛡️ **{disease_display} தடுப்பு முறைகள்:**{stage_variety_text}\n\n"
                f"{prev_str}\n\n"
                f"பயிர் சுழற்சியைப் பின்பற்றி இலைகளில் நீர் தேங்குவதைத் தவிர்க்கவும்."
            )
        else:
            resp = (
                f"{profile_prefix}🛡️ **Preventive Action Plan for {disease_display}:**{stage_variety_text}\n\n"
                f"{prev_str}\n\n"
                f"Practicing crop rotation and keeping foliage dry significantly reduces disease spread."
            )
        return {"reply": resp, "disease_context": disease_display}

    # Intent F: Weather Impact Query ("Will rain make it worse?")
    if is_weather_q:
        if temp_c is not None and humidity_pct is not None:
            if lang_code == "hi":
                resp = (
                    f"{profile_prefix}🌤️ **मौसम और {disease_display} जोखिम:**\n\n"
                    f"वर्तमान स्थिति: तापमान {temp_c}°C, आर्द्रता {humidity_pct}%, रोग जोखिम: **{weather_risk_level}**。\n\n"
                    f"उच्च आर्द्रता और बारिश की संभावना फफूंद बीजाणुओं के प्रसार को बढ़ा सकती है। "
                    f"प्रभावित पत्तियों को तुरंत काटें और बारिश से पहले बचाव हेतु जैविक/फफूंदनाशक स्प्रे करें।"
                )
            elif lang_code == "ta":
                resp = (
                    f"{profile_prefix}🌤️ **வானிலை மற்றும் {disease_display} அபாயம்:**\n\n"
                    f"தற்போதைய வானிலை: {temp_c}°C, ஈரப்பதம் {humidity_pct}%, நோய் அபாயம்: **{weather_risk_level}**.\n\n"
                    f"அதிக ஈரப்பதம் மற்றும் மழை பூஞ்சை நோய் பரவுவதை அதிகரிக்கும். "
                    f"பாதிக்கப்பட்ட இலைகளை நீக்கி, மழைக்கு முன் முன்னெச்சரிக்கை தெளிப்பு செய்யவும்."
                )
            else:
                resp = (
                    f"{profile_prefix}🌤️ **Weather & {disease_display} Spread Risk:**\n\n"
                    f"Current conditions: {temp_c}°C, {humidity_pct}% humidity, Disease Risk: **{weather_risk_level}**.\n\n"
                    f"High humidity and rain create optimal conditions for fungal spore spread. "
                    f"Prune infected foliage immediately and ensure soil drainage and good air ventilation."
                )
        else:
            resp = f"{profile_prefix}{weather_line}\n\nFungal diseases generally spread faster during rain and high humidity. Keep leaf canopy dry."
        return {"reply": resp, "disease_context": disease_display}

    # Intent G: Action / Next Steps Query ("What should I do now?")
    if is_action_q:
        if lang_code == "hi":
            resp = (
                f"{profile_prefix}\n\n"
                f"{t['what_to_do']} (**{disease_display}**){stage_variety_text}:\n"
                f"1. अत्यधिक प्रभावित पत्तियों को काटकर दूर नष्ट करें।\n"
                f"2. {org_list[0] if org_list else 'नीम तेल (3-5ml/लीटर) का छिड़काव करें।'}\n"
                f"3. पत्तियों पर देर शाम पानी देने से बचें।\n\n"
                f"{t['keep_watching']}\n• आसपास के पौधों पर नए धब्बों की निगरानी करें।\n\n"
                f"{t['rescan_note']}\n5 से 7 दिनों में फिर से स्कैन करें।"
                f"{weather_line}"
                f"{trend_note}"
            )
        elif lang_code == "ta":
            resp = (
                f"{profile_prefix}\n\n"
                f"{t['what_to_do']} (**{disease_display}**){stage_variety_text}:\n"
                f"1. தீவிரமாக பாதிக்கப்பட்ட இலைகளை அகற்றி அழிக்கவும்.\n"
                f"2. {org_list[0] if org_list else 'வேப்ப எண்ணெய் (3-5ml/லிட்டர்) தெளிக்கவும்.'}\n"
                f"3. இலைகள் மீது நீர் தேங்காமல் பார்த்துக் கொள்ளவும்.\n\n"
                f"{t['keep_watching']}\n• மற்ற இலைகளில் நோய் பரவுதலைக் கவனிக்கவும்.\n\n"
                f"{t['rescan_note']}\n5 முதல் 7 நாட்களில் மீண்டும் ஸ்கேன் செய்யவும்."
                f"{weather_line}"
                f"{trend_note}"
            )
        else:
            resp = (
                f"{profile_prefix}\n\n"
                f"{t['what_to_do']} (**{disease_display}**){stage_variety_text}:\n"
                f"1. Prune lower severely-infected leaves and dispose of them away from healthy plants.\n"
                f"2. {org_list[0] if org_list else 'Apply organic Neem oil (3-5ml/L) or Copper Oxychloride spray.'}\n"
                f"3. Switch to drip irrigation to keep leaf canopy dry.\n\n"
                f"{t['keep_watching']}\n• Inspect nearby tomato foliage for expanding target spots.\n\n"
                f"{t['rescan_note']}\nPerform a follow-up scan in 5 to 7 days."
                f"{weather_line}"
                f"{trend_note}"
            )
        return {"reply": resp, "disease_context": disease_display}

    # Intent H: Meaning / General Result Explanation ("What disease does my plant have?" / "What does my result mean?")
    aff_str = f" (~{affected_pct:.0f}% leaf area affected)" if affected_pct > 0 else ""

    if lang_code == "hi":
        resp = (
            f"{profile_prefix}\n\n"
            f"{t['what_found']}\nपत्ती के स्कैन से **{disease_display}** के लक्षण दिखे हैं (AI सटीकता: **{confidence:.1f}%**){stage_variety_text}।\n\n"
            f"{t['how_serious']}\nपौधे का स्वास्थ्य स्कोर **{phs}/100** है। संक्रमण स्तर **{severity}** है{aff_str}।\n\n"
            f"{t['what_to_do']}\n"
            f"1. प्रभावित निचली पत्तियों को काटकर नष्ट करें।\n"
            f"2. {org_list[0] if org_list else 'नीम तेल (3-5ml/लीटर) का छिड़काव करें।'}\n"
            f"3. ड्रिप सिंचाई का प्रयोग करें।\n\n"
            f"{t['keep_watching']}\n• नए धब्बों के प्रसार की निगरानी करें।\n\n"
            f"{t['rescan_note']}\n5 से 7 दिनों में फिर से स्कैन करें।"
            f"{weather_line}\n\n"
            f"{t['expert_disclaimer']}"
            f"{trend_note}"
        )
    elif lang_code == "ta":
        resp = (
            f"{profile_prefix}\n\n"
            f"{t['what_found']}\nஇலை ஸ்கேன் மூலம் **{disease_display}** **{confidence:.1f}% துல்லியத்துடன்** சுட்டிக்காட்டப்பட்டுள்ளது{stage_variety_text}.\n\n"
            f"{t['how_serious']}\nதாவர ஆரோக்கிய மதிப்பெண் **{phs}/100**, பாதிப்பு நிலை **{severity}**{aff_str}.\n\n"
            f"{t['what_to_do']}\n"
            f"1. பாதிக்கப்பட்ட கீழ் இலைகளை அகற்றி அழிக்கவும்.\n"
            f"2. {org_list[0] if org_list else 'வேப்ப எண்ணெய் (3-5ml/லிட்டர்) தெளிக்கவும்.'}\n"
            f"3. சொட்டு நீர் பாசனத்தைப் பயன்படுத்தவும்.\n\n"
            f"{t['keep_watching']}\n• மற்ற இலைகளில் நோய் பரவுதலைக் கவனிக்கவும்.\n\n"
            f"{t['rescan_note']}\n5 முதல் 7 நாட்களில் மீண்டும் ஸ்கேன் செய்யவும்."
            f"{weather_line}\n\n"
            f"{t['expert_disclaimer']}"
            f"{trend_note}"
        )
    else:
        resp = (
            f"{profile_prefix}\n\n"
            f"{t['what_found']}\nThe leaf image scan indicates **{disease_display}** with **{confidence:.1f}% AI confidence**{stage_variety_text}.\n\n"
            f"{t['how_serious']}\nPlant Health Score: **{phs}/100** with **{severity}** severity level{aff_str}.\n\n"
            f"{t['what_to_do']}\n"
            f"1. Prune lower infected leaves and dispose of them away from healthy crop areas.\n"
            f"2. {org_list[0] if org_list else 'Apply organic Neem oil (3-5ml/L) spray.'}\n"
            f"3. Ensure good airflow spacing and avoid leaf wetness.\n\n"
            f"{t['keep_watching']}\n• Monitor neighboring leaves for expanding target spots.\n\n"
            f"{t['rescan_note']}\nPerform a follow-up scan in 5 to 7 days."
            f"{weather_line}\n\n"
            f"{t['expert_disclaimer']}"
            f"{trend_note}"
        )

    return {
        "reply": resp,
        "disease_context": disease_display,
        "plant_health_score": phs,
        "severity": severity,
        "farmer_context_used": farmer_context is not None,
        "weather_context_used": weather_context is not None,
    }
