"""
disease_db.py – GreenScan Disease Knowledge Base
Maps each model class label to rich agronomic information.
"""

DISEASE_DB = {
    "tomato_Early blight": {
        "display_name": "Tomato Early Blight",
        "is_healthy": False,
        "description": (
            "Early blight is a common fungal disease of tomatoes caused by "
            "Alternaria solani. It typically appears as dark brown spots with "
            "concentric rings (target-board pattern) on older, lower leaves first, "
            "then spreads upward. Severely infected leaves turn yellow and drop off."
        ),
        "causes": [
            "Fungal pathogen: Alternaria solani",
            "Warm temperatures (24–29°C) combined with high humidity",
            "Infected plant debris left in soil",
            "Overhead irrigation that keeps leaves wet",
            "Nutrient-deficient plants (especially nitrogen)",
            "Crowded planting with poor air circulation",
        ],
        "symptoms": [
            "Dark brown circular spots with concentric rings",
            "Yellow halo around lesions",
            "Lesions first appear on older lower leaves",
            "Premature defoliation",
            "Dark sunken lesions may appear on stem and fruit",
        ],
        "prevention": [
            "Use certified disease-free seeds and transplants",
            "Practice 2–3 year crop rotation",
            "Ensure adequate spacing for air circulation",
            "Avoid overhead irrigation; use drip irrigation",
            "Mulch soil to prevent spore splash-up",
            "Remove and destroy infected plant debris after harvest",
            "Maintain balanced soil nutrition",
        ],
        "organic_solutions": [
            "Apply copper-based fungicides (Copper Oxychloride 50% WP)",
            "Neem oil spray (3–5 ml/litre) every 7–10 days",
            "Trichoderma viride biological fungicide soil drench",
            "Baking soda spray (1 tbsp per litre water) as preventive",
            "Garlic extract spray as natural antifungal",
        ],
        "chemical_solutions": [
            "Mancozeb 75% WP @ 2.5 g/litre – spray every 7 days",
            "Chlorothalonil 75% WP @ 2 g/litre",
            "Azoxystrobin 23% SC @ 1 ml/litre",
            "Propiconazole 25% EC @ 1 ml/litre",
            "Hexaconazole 5% SC @ 2 ml/litre",
        ],
        "severity": "Moderate",
        "spread_rate": "Moderate",
    },

    "tomato_Late blight": {
        "display_name": "Tomato Late Blight",
        "is_healthy": False,
        "description": (
            "Late blight is a highly destructive disease caused by the oomycete "
            "Phytophthora infestans — the same pathogen responsible for the Irish "
            "Potato Famine. It can destroy an entire crop within days under cool, "
            "wet conditions. Water-soaked greenish-grey lesions appear on leaves "
            "and spread rapidly to stems and fruits."
        ),
        "causes": [
            "Oomycete pathogen: Phytophthora infestans",
            "Cool temperatures (10–20°C) with high humidity (>90%)",
            "Prolonged leaf wetness from rain or dew",
            "Infected seed tubers or transplants",
            "Wind-dispersed sporangia from nearby infected fields",
            "Poor drainage and waterlogged soils",
        ],
        "symptoms": [
            "Water-soaked, irregularly shaped grey-green lesions",
            "White fuzzy sporulation on leaf undersides in humid conditions",
            "Dark brown-black rot spreading to stems and petioles",
            "Brown greasy lesions on fruit",
            "Rapid blighting — whole plant can collapse in 3–5 days",
        ],
        "prevention": [
            "Plant resistant varieties (e.g., Mountain Magic, Defiant)",
            "Avoid planting in low-lying, poorly drained areas",
            "Use drip irrigation to keep foliage dry",
            "Scout fields regularly, especially after rain",
            "Remove volunteer tomato/potato plants from field borders",
            "Apply fungicides preventively before rainy season",
        ],
        "organic_solutions": [
            "Copper hydroxide (Kocide) spray @ 3 g/litre every 5–7 days",
            "Copper Oxychloride 50% WP @ 3 g/litre",
            "Compost tea spray to boost plant immunity",
            "Bacillus subtilis (Serenade) bio-fungicide",
            "Remove and destroy infected plants immediately — do NOT compost",
        ],
        "chemical_solutions": [
            "Metalaxyl + Mancozeb (Ridomil Gold) @ 2.5 g/litre – most effective",
            "Cymoxanil 8% + Mancozeb 64% WP @ 2.5 g/litre",
            "Dimethomorph 50% WP @ 1 g/litre",
            "Fluopicolide + Propamocarb (Infinito) @ 1.6 ml/litre",
            "Fenamidone + Mancozeb @ 3 g/litre",
        ],
        "severity": "High",
        "spread_rate": "Very Fast",
    },

    "tomato_healthy": {
        "display_name": "Healthy Tomato",
        "is_healthy": True,
        "description": (
            "Great news! Your tomato plant appears to be perfectly healthy. "
            "The leaves show no signs of disease, pest damage, or nutrient deficiency. "
            "Continue your current care routine to maintain plant health throughout the season."
        ),
        "causes": [],
        "symptoms": [
            "Deep green, firm leaves",
            "No spots, lesions, or discoloration",
            "Strong stem structure",
            "Normal leaf texture and shape",
        ],
        "prevention": [
            "Continue regular watering — 1–2 inches per week",
            "Fertilize every 2 weeks with balanced NPK fertilizer",
            "Monitor for early signs of pests or disease weekly",
            "Maintain proper spacing for air circulation",
            "Keep soil consistently moist but not waterlogged",
        ],
        "organic_solutions": [
            "Apply compost or vermicompost for soil enrichment",
            "Use neem oil spray monthly as preventive measure",
            "Mulch around plant base to retain moisture and suppress weeds",
        ],
        "chemical_solutions": [
            "No treatment needed",
            "Consider preventive copper spray before rainy season",
        ],
        "severity": "None",
        "spread_rate": "N/A",
    },
}


def get_disease_info(class_label: str) -> dict:
    """Return disease info dict for a given model class label."""
    info = DISEASE_DB.get(class_label)
    if info is None:
        return {
            "display_name": class_label.replace("_", " ").title(),
            "is_healthy": False,
            "description": "Disease information not available in the database.",
            "causes": [],
            "symptoms": [],
            "prevention": [],
            "organic_solutions": [],
            "chemical_solutions": [],
            "severity": "Unknown",
            "spread_rate": "Unknown",
        }
    return info
