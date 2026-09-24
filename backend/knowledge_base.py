"""
knowledge_base.py - GreenScan 2.0 Phase 11: Structured Agricultural Knowledge Layer

Provides a curated, reference-grade agronomic knowledge store for GreenScan diseases.
Designed as a RAG-ready interface: retrieve_relevant_knowledge() uses keyword-based
retrieval now, and can be upgraded to vector/embedding retrieval without changing callers.

Safety principle:
    All treatment product information is sourced from the existing verified dosage.py
    static database. No information is invented or LLM-generated.

References used:
    - PlantVillage Disease Database (Penn State / CGIAR)
    - CABI Crop Protection Compendium
    - ICAR (Indian Council of Agricultural Research) guidelines
    - Cornell University Plant Disease Diagnostic Clinic
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("greenscan.knowledge_base")

# ─── Structured Knowledge Base ──────────────────────────────────────────────────
# Each entry maps a model class label to structured agronomic knowledge.
# This is separate from disease_db.py to allow independent extensibility.

KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {

    "tomato_Early blight": {
        "display_name": "Tomato Early Blight",
        "pathogen": "Alternaria solani (fungal pathogen)",
        "pathogen_type": "Fungus",
        "host_range": ["Tomato", "Potato", "Eggplant"],
        "symptoms": [
            "Dark brown circular spots with concentric rings (target-board / bullseye pattern)",
            "Yellow chlorotic halo surrounding lesions",
            "Lesions first appear on older, lower leaves",
            "Premature defoliation as infection progresses upward",
            "Dark sunken lesions may appear on stem, petiole, and fruit",
            "Severe infection causes significant yield reduction through defoliation",
        ],
        "favorable_conditions": {
            "temperature_range_c": (24, 29),
            "humidity_threshold_pct": 60,
            "leaf_wetness_hours": 6,
            "description": (
                "Warm temperatures (24-29 degrees C) combined with high relative humidity "
                "and extended leaf wetness periods (6+ hours) create ideal conditions for "
                "Alternaria solani spore germination and infection."
            ),
        },
        "environmental_risk_factors": {
            "high_risk": [
                "Temperature between 24-29 degrees C",
                "Relative humidity above 80%",
                "Prolonged leaf wetness (dew, rain, overhead irrigation)",
                "Nutrient-stressed plants (especially nitrogen deficiency)",
                "Crowded planting with poor air circulation",
            ],
            "moderate_risk": [
                "Temperature between 20-24 degrees C",
                "Relative humidity 60-80%",
                "Infected plant debris from previous season present in soil",
            ],
            "low_risk": [
                "Temperature below 18 degrees C or above 32 degrees C",
                "Low humidity and dry weather",
                "Well-spaced plants with good airflow",
            ],
        },
        "prevention": [
            "Use certified disease-free seeds and transplants from reputable sources",
            "Practice 2-3 year crop rotation with non-solanaceous crops",
            "Maintain adequate plant spacing (45-60 cm) to promote airflow",
            "Use drip irrigation to keep foliage dry; avoid overhead irrigation",
            "Mulch soil to prevent spore splash-up from infected debris",
            "Remove and destroy infected plant debris after harvest",
            "Maintain balanced soil nutrition (avoid excess nitrogen)",
            "Apply preventive copper-based fungicide before rainy season",
            "Monitor lower leaves weekly for early lesion development",
        ],
        "treatment_categories": [
            {
                "category": "Organic / Biological",
                "description": "Suitable for mild-to-moderate infections; prefer for early intervention.",
                "products": [
                    {"name": "Copper Oxychloride 50% WP", "rate": "3 g/litre", "interval_days": 7, "phi_days": 3},
                    {"name": "Neem Oil (Azadirachtin 1500 PPM)", "rate": "3-5 ml/litre", "interval_days": 7, "phi_days": 0},
                    {"name": "Trichoderma viride (biological fungicide)", "rate": "Soil drench per label", "interval_days": 14, "phi_days": 0},
                    {"name": "Baking Soda (Sodium Bicarbonate)", "rate": "1 tbsp/litre water", "interval_days": 7, "phi_days": 0, "note": "Preventive only; limited curative action"},
                ],
            },
            {
                "category": "Chemical (Conventional)",
                "description": "Use when infection is moderate to severe or organic options have been insufficient.",
                "products": [
                    {"name": "Mancozeb 75% WP", "rate": "2.5 g/litre", "interval_days": 7, "phi_days": 7},
                    {"name": "Chlorothalonil 75% WP", "rate": "2 g/litre", "interval_days": 7, "phi_days": 7},
                    {"name": "Azoxystrobin 23% SC", "rate": "1 ml/litre", "interval_days": 10, "phi_days": 14},
                    {"name": "Propiconazole 25% EC", "rate": "1 ml/litre", "interval_days": 14, "phi_days": 14},
                ],
            },
        ],
        "safety_information": [
            "Always wear protective gloves, mask, and goggles when mixing and applying fungicides.",
            "Spray during calm early morning or late evening hours to avoid drift and heat stress.",
            "Ensure full coverage of both upper and lower leaf surfaces.",
            "Observe the Pre-Harvest Interval (PHI) stated on the product label before harvesting.",
            "Do not apply during high wind or when rain is imminent.",
            "Store chemicals in original containers in a locked, well-ventilated location away from children.",
            "Never mix fungicides without checking label compatibility.",
            "Dispose of empty containers as per local agricultural waste regulations.",
        ],
        "monitoring_guidance": {
            "after_treatment_days": 7,
            "watch_for": [
                "No new lesions developing on upper leaves after 7 days",
                "Existing lesions not spreading significantly",
                "No new defoliation",
            ],
            "escalation_trigger": (
                "If new lesions continue spreading to upper leaves within 7 days "
                "despite organic treatment, switch to chemical fungicide."
            ),
        },
        "references": [
            "PlantVillage / CGIAR Disease Database - Alternaria solani",
            "CABI Crop Protection Compendium - Early Blight",
            "ICAR-IIHR Technical Bulletin: Tomato Disease Management",
            "Cornell Plant Disease Diagnostic Clinic",
        ],
    },

    "tomato_Late blight": {
        "display_name": "Tomato Late Blight",
        "pathogen": "Phytophthora infestans (oomycete / water mold)",
        "pathogen_type": "Oomycete",
        "host_range": ["Tomato", "Potato"],
        "symptoms": [
            "Water-soaked, pale green to dark brown-grey irregular lesions on leaves",
            "White cottony sporulation visible on leaf undersides in humid conditions",
            "Rapid blighting: entire leaf collapses within 2-4 days of infection",
            "Dark brown-black rot spreading to petioles, stems, and fruit",
            "Brown, greasy-looking lesions with white mold on fruit",
            "Distinctive musty odor from heavily infected tissue",
            "Whole plant can collapse within 3-7 days under favorable conditions",
        ],
        "favorable_conditions": {
            "temperature_range_c": (10, 22),
            "humidity_threshold_pct": 90,
            "leaf_wetness_hours": 10,
            "description": (
                "Cool temperatures (10-22 degrees C) with very high relative humidity "
                "above 90% and extended leaf wetness (10+ hours) are ideal for "
                "Phytophthora infestans sporulation and rapid spread."
            ),
        },
        "environmental_risk_factors": {
            "high_risk": [
                "Temperature between 10-22 degrees C with humidity above 90%",
                "Prolonged rainy or foggy periods",
                "Low-lying, poorly drained fields",
                "Nearby infected tomato or potato crops (wind-dispersed spores)",
                "High plant density with restricted airflow",
            ],
            "moderate_risk": [
                "Temperature 18-25 degrees C with humidity 75-90%",
                "Intermittent rainfall or heavy dew",
                "Volunteer tomato/potato plants present near field borders",
            ],
            "low_risk": [
                "Hot and dry conditions (above 28 degrees C with low humidity)",
                "Resistant varieties planted",
                "Good field drainage and adequate plant spacing",
            ],
        },
        "prevention": [
            "Plant resistant or tolerant varieties (Mountain Magic, Defiant PHR, Iron Lady)",
            "Avoid planting in low-lying, poorly drained areas",
            "Use drip irrigation to keep foliage dry",
            "Scout fields regularly, especially after rain or foggy periods",
            "Remove volunteer tomato and potato plants from field borders immediately",
            "Apply fungicide preventively before rainy season begins",
            "Maintain adequate plant spacing (60-75 cm) for airflow",
            "Avoid night-time overhead irrigation",
            "Destroy infected plant material by burning; do NOT compost",
        ],
        "treatment_categories": [
            {
                "category": "Organic / Biological",
                "description": "Use as preventive or very early intervention. Curative action is limited for late blight.",
                "products": [
                    {"name": "Copper Hydroxide (Kocide 2000)", "rate": "3 g/litre", "interval_days": 5, "phi_days": 3},
                    {"name": "Copper Oxychloride 50% WP", "rate": "3 g/litre", "interval_days": 7, "phi_days": 3},
                    {"name": "Bacillus subtilis (Serenade)", "rate": "Per label", "interval_days": 7, "phi_days": 0},
                ],
            },
            {
                "category": "Chemical (Conventional)",
                "description": "Required for moderate-to-severe infections. Act immediately upon detection.",
                "products": [
                    {"name": "Metalaxyl + Mancozeb (Ridomil Gold MZ)", "rate": "2.5 g/litre", "interval_days": 7, "phi_days": 7, "note": "Most effective systemic option"},
                    {"name": "Cymoxanil 8% + Mancozeb 64% WP", "rate": "2.5 g/litre", "interval_days": 7, "phi_days": 7},
                    {"name": "Dimethomorph 50% WP", "rate": "1 g/litre", "interval_days": 7, "phi_days": 14},
                    {"name": "Fluopicolide + Propamocarb (Infinito)", "rate": "1.6 ml/litre", "interval_days": 7, "phi_days": 3},
                ],
            },
        ],
        "safety_information": [
            "Late blight spreads VERY RAPIDLY. Begin treatment within 24-48 hours of detection.",
            "Always wear full PPE: gloves, mask, eye protection, and protective clothing.",
            "Remove and immediately destroy (burn) heavily infected plants to stop sporulation.",
            "Do NOT compost infected plant material; spores can survive and spread.",
            "Spray both upper and lower leaf surfaces for thorough coverage.",
            "Observe label PHI strictly before harvesting.",
            "Rotate between fungicide classes to prevent resistance development.",
            "Notify neighboring farmers if late blight is detected (spores travel by wind).",
        ],
        "monitoring_guidance": {
            "after_treatment_days": 3,
            "watch_for": [
                "Sporulation (white fuzzy growth) stopped on leaf undersides",
                "No new water-soaked lesions appearing",
                "Lesion margins drying out",
            ],
            "escalation_trigger": (
                "If spreading continues within 3-5 days despite copper treatment, "
                "immediately apply systemic chemical fungicide (Metalaxyl+Mancozeb) "
                "and consider removing severely infected plants."
            ),
        },
        "references": [
            "PlantVillage / CGIAR Disease Database - Phytophthora infestans",
            "CABI Crop Protection Compendium - Late Blight",
            "ICAR-IIHR Technical Bulletin: Tomato Disease Management",
            "American Phytopathological Society: Late Blight",
        ],
    },

    "tomato_healthy": {
        "display_name": "Healthy Tomato",
        "pathogen": None,
        "pathogen_type": None,
        "host_range": ["Tomato"],
        "symptoms": [
            "Deep green, firm, glossy leaves",
            "No spots, lesions, or discoloration",
            "Strong, upright stem structure",
            "Normal leaf texture and shape",
            "Active growth and flowering",
        ],
        "favorable_conditions": {
            "temperature_range_c": (20, 28),
            "humidity_threshold_pct": 65,
            "leaf_wetness_hours": 0,
            "description": "Healthy tomato plants thrive at 20-28 degrees C with moderate humidity and good airflow.",
        },
        "environmental_risk_factors": {
            "high_risk": [
                "Prolonged cool wet weather (risk of early/late blight onset)",
                "Hot humid weather combined with plant stress",
            ],
            "moderate_risk": [
                "Fluctuating temperatures causing growth stress",
                "Overwatering or poor drainage",
            ],
            "low_risk": ["Current conditions appear optimal for healthy growth"],
        },
        "prevention": [
            "Maintain current watering schedule (1-2 inches per week)",
            "Continue balanced NPK fertilization every 2 weeks",
            "Inspect lower leaves weekly for early disease signs",
            "Maintain plant spacing for air circulation",
            "Apply preventive neem oil spray monthly",
            "Practice crop rotation each season",
        ],
        "treatment_categories": [
            {
                "category": "Preventive Maintenance",
                "description": "No treatment required. Maintain preventive practices.",
                "products": [
                    {"name": "Neem Oil (preventive)", "rate": "2-3 ml/litre", "interval_days": 14, "phi_days": 0, "note": "Monthly preventive spray"},
                    {"name": "Copper spray (pre-rainy season)", "rate": "3 g/litre", "interval_days": 0, "phi_days": 3, "note": "Once before monsoon/rainy season"},
                ],
            }
        ],
        "safety_information": [
            "No curative treatment required.",
            "If using any preventive sprays, observe standard PPE practices.",
        ],
        "monitoring_guidance": {
            "after_treatment_days": 14,
            "watch_for": [
                "Any early brown or yellow spots on lower leaves",
                "Changes in leaf texture or color",
                "Signs of pest damage (holes, stippling)",
            ],
            "escalation_trigger": "If disease symptoms appear at next scan, re-run prediction for updated diagnosis.",
        },
        "references": [
            "ICAR-IIHR Technical Bulletin: Tomato Production Guidelines",
            "University of Florida IFAS: Tomato Production",
        ],
    },
}


# ─── Public API Functions ───────────────────────────────────────────────────────

def get_knowledge(disease_key: str) -> Dict[str, Any]:
    """
    Returns the full knowledge base entry for a disease key.
    Returns a default fallback dict if the key is not found.
    """
    entry = KNOWLEDGE_BASE.get(disease_key)
    if entry is None:
        logger.warning(f"[KnowledgeBase] No entry found for disease_key='{disease_key}'")
        return {
            "display_name": disease_key.replace("_", " ").title(),
            "pathogen": "Unknown",
            "pathogen_type": "Unknown",
            "symptoms": [],
            "favorable_conditions": {},
            "environmental_risk_factors": {},
            "prevention": [],
            "treatment_categories": [],
            "safety_information": ["Consult a qualified agricultural professional."],
            "monitoring_guidance": {},
            "references": [],
        }
    return entry


def get_environmental_risk_factors(
    disease_key: str,
    temp_c: Optional[float] = None,
    humidity_pct: Optional[float] = None,
) -> List[str]:
    """
    Returns a list of relevant environmental risk factor descriptions
    based on the current temperature and humidity readings.

    This is used to personalize recommendations based on farm weather context.
    """
    entry = KNOWLEDGE_BASE.get(disease_key)
    if entry is None:
        return []

    risk_factors_db = entry.get("environmental_risk_factors", {})
    favorable = entry.get("favorable_conditions", {})
    active_factors: List[str] = []

    if temp_c is not None and humidity_pct is not None:
        temp_min, temp_max = favorable.get("temperature_range_c", (0, 100))
        hum_threshold = favorable.get("humidity_threshold_pct", 100)

        if temp_min <= temp_c <= temp_max and humidity_pct >= hum_threshold * 0.85:
            active_factors.append(
                f"Current conditions (Temp: {temp_c}°C, Humidity: {humidity_pct}%) "
                f"are within the HIGH RISK range for {entry['display_name']}."
            )
            active_factors.extend(risk_factors_db.get("high_risk", []))
        elif temp_min - 3 <= temp_c <= temp_max + 3 and humidity_pct >= 60:
            active_factors.append(
                f"Current conditions (Temp: {temp_c}°C, Humidity: {humidity_pct}%) "
                f"are within MODERATE RISK range for {entry['display_name']}."
            )
            active_factors.extend(risk_factors_db.get("moderate_risk", []))
        else:
            active_factors.append(
                f"Current conditions (Temp: {temp_c}°C, Humidity: {humidity_pct}%) "
                f"are in the LOW RISK range for {entry['display_name']}."
            )
            active_factors.extend(risk_factors_db.get("low_risk", []))
    else:
        # No weather data — return general high-risk factors
        active_factors.extend(risk_factors_db.get("high_risk", []))

    return active_factors


def retrieve_relevant_knowledge(query: str, disease_key: str) -> List[Dict[str, Any]]:
    """
    RAG-ready interface: retrieves the most relevant knowledge snippets
    for a given query and disease context.

    Currently uses keyword-based matching. This function signature is designed
    to be upgraded to vector/embedding retrieval without changing callers.

    Args:
        query:       Natural language question from the farmer.
        disease_key: Target disease class label.

    Returns:
        List of relevant knowledge snippets as dicts with 'section' and 'content'.
    """
    entry = KNOWLEDGE_BASE.get(disease_key)
    if entry is None:
        return []

    query_lower = query.lower()
    results: List[Dict[str, Any]] = []

    # Symptom queries
    if any(w in query_lower for w in ["symptom", "sign", "look like", "spot", "lesion", "what is"]):
        results.append({"section": "Symptoms", "content": entry.get("symptoms", [])})

    # Prevention queries
    if any(w in query_lower for w in ["prevent", "avoid", "stop", "protect", "before"]):
        results.append({"section": "Prevention", "content": entry.get("prevention", [])})

    # Treatment queries
    if any(w in query_lower for w in ["treat", "spray", "cure", "medicine", "fungicide", "chemical", "organic", "apply"]):
        results.append({"section": "Treatment Options", "content": entry.get("treatment_categories", [])})

    # Safety queries
    if any(w in query_lower for w in ["safe", "ppe", "glove", "danger", "protect", "harvest", "phi", "interval"]):
        results.append({"section": "Safety Information", "content": entry.get("safety_information", [])})

    # Monitoring queries
    if any(w in query_lower for w in ["monitor", "check", "when", "next", "scan", "watch"]):
        results.append({"section": "Monitoring Guidance", "content": entry.get("monitoring_guidance", {})})

    # Environment queries
    if any(w in query_lower for w in ["weather", "humid", "temp", "rain", "condition", "risk"]):
        results.append({"section": "Favorable Conditions", "content": entry.get("favorable_conditions", {})})
        results.append({"section": "Environmental Risk Factors", "content": entry.get("environmental_risk_factors", {})})

    # General / fallback
    if not results:
        results.append({"section": "General Disease Info", "content": {
            "display_name": entry.get("display_name"),
            "pathogen": entry.get("pathogen"),
            "symptoms": entry.get("symptoms", [])[:3],
        }})

    return results


def get_all_disease_keys() -> List[str]:
    """Returns all disease keys currently in the knowledge base."""
    return list(KNOWLEDGE_BASE.keys())
