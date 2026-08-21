from typing import Dict, Any

DOSAGE_DATABASE = {
    "tomato_Early blight": {
        "chemical_active": "Mancozeb 75% WP / Chlorothalonil",
        "chemical_rate_per_acre": 600, # grams
        "organic_active": "Neem Oil 10,000 PPM + Copper Hydroxide",
        "organic_rate_per_acre": 500, # mL
        "water_volume_per_acre": 200, # Liters
        "phi_days": 7, # Pre-Harvest Interval
        "spray_interval_days": 10
    },
    "tomato_Late blight": {
        "chemical_active": "Cymoxanil 8% + Mancozeb 64% WP or Metalaxyl",
        "chemical_rate_per_acre": 750, # grams
        "organic_active": "Bordeaux Mixture (1%) / Copper Oxychloride",
        "organic_rate_per_acre": 800, # grams
        "water_volume_per_acre": 220, # Liters
        "phi_days": 14,
        "spray_interval_days": 7
    },
    "tomato_healthy": {
        "chemical_active": "N/A (Preventative Bio-fungicide: Trichoderma viride)",
        "chemical_rate_per_acre": 0,
        "organic_active": "Neem Oil spray 3000 PPM",
        "organic_rate_per_acre": 250,
        "water_volume_per_acre": 150,
        "phi_days": 0,
        "spray_interval_days": 14
    }
}

def calculate_dosage(disease: str, severity: str, area_value: float, area_unit: str = "acres") -> Dict[str, Any]:
    """
    Calculates exact chemical and organic treatment dosage and spray parameters.
    """
    # Convert area to acres
    unit_lower = area_unit.lower()
    if unit_lower in ["ha", "hectare", "hectares"]:
        acres = area_value * 2.47105
    elif unit_lower in ["sqm", "sq_m", "square_meters", "m2"]:
        acres = area_value / 4046.86
    else:
        acres = area_value  # default acres

    acres = max(round(acres, 3), 0.01)

    # Fetch disease parameters or fallback
    info = DOSAGE_DATABASE.get(disease, DOSAGE_DATABASE["tomato_Early blight"])

    # Multiplier based on severity
    severity_lower = severity.lower()
    if severity_lower == "severe":
        multiplier = 1.25
        urgency = "HIGH - Apply spray within 24 hours"
    elif severity_lower == "moderate":
        multiplier = 1.0
        urgency = "MEDIUM - Apply spray within 48 hours"
    else:
        multiplier = 0.75
        urgency = "PREVENTATIVE - Apply during morning/evening hours"

    chemical_total_g = round(info["chemical_rate_per_acre"] * acres * multiplier, 1)
    organic_total = round(info["organic_rate_per_acre"] * acres * multiplier, 1)
    water_total_l = round(info["water_volume_per_acre"] * acres, 1)

    # Dilution concentration (grams or mL per Liter of water)
    chemical_per_liter = round(chemical_total_g / max(water_total_l, 1), 2)
    organic_per_liter = round(organic_total / max(water_total_l, 1), 2)

    return {
        "disease": disease,
        "severity": severity,
        "area_acres": acres,
        "original_area": f"{area_value} {area_unit}",
        "urgency": urgency,
        "chemical_treatment": {
            "active_ingredient": info["chemical_active"],
            "total_quantity": f"{chemical_total_g} g",
            "concentration": f"{chemical_per_liter} g per Liter of water"
        },
        "organic_treatment": {
            "active_ingredient": info["organic_active"],
            "total_quantity": f"{organic_total} mL/g",
            "concentration": f"{organic_per_liter} mL/g per Liter of water"
        },
        "spray_specifications": {
            "total_water_required_liters": water_total_l,
            "pre_harvest_interval_days": info["phi_days"],
            "next_application_in_days": info["spray_interval_days"],
            "safety_instructions": [
                "Wear protective gloves, mask, and goggles while mixing.",
                "Spray during calm early morning or late evening hours to avoid high wind drift.",
                "Ensure full coverage of both top and underside of leaves.",
                f"Respect the {info['phi_days']}-day Pre-Harvest Interval (PHI) before picking fruit."
            ]
        }
    }
