# backend/translations.py

TRANSLATIONS = {
    "en": {
        "severity": "Severity",
        "stage": "Stage",
        "mild": "Mild",
        "moderate": "Moderate",
        "severe": "Severe",
        "risk_level": "Risk Level",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "critical": "Critical",
        "treatment_plan": "Treatment Plan",
        "organic": "Organic",
        "chemical": "Chemical",
        "prevention": "Prevention",
        "prediction_confidence": "Prediction Confidence"
    },
    "hi": {
        "severity": "गंभीरता",
        "stage": "चरण",
        "mild": "हल्का",
        "moderate": "मध्यम",
        "severe": "गंभीर",
        "risk_level": "जोखिम स्तर",
        "high": "उच्च",
        "medium": "मध्यम",
        "low": "कम",
        "critical": "अत्यधिक गंभीर",
        "treatment_plan": "उपचार योजना",
        "organic": "जैविक",
        "chemical": "रासायनिक",
        "prevention": "रोकथाम",
        "prediction_confidence": "भविष्यवाणी का भरोसा"
    },
    "ta": {
        "severity": "தீவிரத்தன்மை",
        "stage": "நிலை",
        "mild": "மிதமான",
        "moderate": "நடுத்தர",
        "severe": "தீவிர",
        "risk_level": "ஆபத்து நிலை",
        "high": "அதிகம்",
        "medium": "நடுத்தரம்",
        "low": "குறைவு",
        "critical": "மிகவும் ஆபத்தானது",
        "treatment_plan": "சிகிச்சை திட்டம்",
        "organic": "இயற்கை வழி",
        "chemical": "வேதியியல் வழி",
        "prevention": "தடுப்பு முறைகள்",
        "prediction_confidence": "கணிப்பு உறுதி"
    }
}

def get_text(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
