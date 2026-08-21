from typing import Dict, Any

def analyze_soil_health(
    ph: float = 6.5,
    nitrogen: float = 140.0,    # mg/kg (ppm)
    phosphorus: float = 45.0,   # mg/kg (ppm)
    potassium: float = 210.0,   # mg/kg (ppm)
    moisture: float = 45.0,     # %
    soil_type: str = "Loam"
) -> Dict[str, Any]:
    """
    Evaluates soil NPK levels, pH balance, and moisture to provide 
    soil health diagnostics, deficiency warnings, and organic amendments.
    """
    deficiencies = []
    recommendations = []
    score = 100

    # 1. pH Analysis (Ideal range for tomatoes/solanaceous crops: 6.0 - 6.8)
    if ph < 5.8:
        score -= 20
        ph_status = "Strongly Acidic"
        deficiencies.append("Calcium and Magnesium availability suppressed due to low pH.")
        recommendations.append("Apply Agricultural Lime (Calcium Carbonate) at 500g/m² to elevate soil pH.")
    elif ph > 7.5:
        score -= 20
        ph_status = "Alkaline / Basic"
        deficiencies.append("Iron, Manganese, and Zinc micronutrients bound in soil.")
        recommendations.append("Apply Agricultural Sulfur or elemental sulfur at 300g/m² to reduce soil pH.")
    else:
        ph_status = "Optimal Neutral (6.0 - 6.8)"

    # 2. Nitrogen (N) (Ideal range: 120 - 200 ppm)
    if nitrogen < 100:
        score -= 20
        n_status = "Deficient (Low)"
        deficiencies.append("Nitrogen deficiency: Causes pale green foliage, chlorosis, and stunted leaf growth.")
        recommendations.append("Apply Bio-fertilizer (Azotobacter / Vermicompost) or Neem cake meal.")
    elif nitrogen > 250:
        score -= 15
        n_status = "Excessive (High)"
        deficiencies.append("Excess Nitrogen: Causes lush foliage susceptible to fungal blights and delayed fruit set.")
        recommendations.append("Reduce nitrogenous fertilizers and flush soil with clean irrigation.")
    else:
        n_status = "Optimal"

    # 3. Phosphorus (P) (Ideal range: 30 - 60 ppm)
    if phosphorus < 25:
        score -= 15
        p_status = "Deficient (Low)"
        deficiencies.append("Phosphorus deficiency: Leads to purplish leaves and poor root establishment.")
        recommendations.append("Incorporate Bone Meal or Rock Phosphate into root zone soil.")
    else:
        p_status = "Optimal"

    # 4. Potassium (K) (Ideal range: 150 - 300 ppm)
    if potassium < 140:
        score -= 15
        k_status = "Deficient (Low)"
        deficiencies.append("Potassium deficiency: Causes marginal leaf scorching and poor disease resistance.")
        recommendations.append("Apply Wood Ash or Organic Potash (Sulfate of Potash).")
    else:
        k_status = "Optimal"

    # 5. Moisture %
    if moisture < 30:
        moisture_status = "Low (Under-irrigated)"
        recommendations.append("Increase drip irrigation frequency and apply straw mulch to retain moisture.")
    elif moisture > 70:
        moisture_status = "Saturated (High root rot risk)"
        recommendations.append("Improve field drainage channels immediately to prevent Phytophthora root rot.")
    else:
        moisture_status = "Optimal (35% - 60%)"

    score = max(score, 10)

    # Health Rating Grade
    if score >= 85:
        rating = "Excellent Soil Health"
        badge_color = "#22c55e"
    elif score >= 65:
        rating = "Good (Minor Adjustments Required)"
        badge_color = "#eab308"
    else:
        rating = "Needs Remediation"
        badge_color = "#ef4444"

    return {
        "overall_score": score,
        "rating": rating,
        "badge_color": badge_color,
        "parameters": {
            "ph": {"value": ph, "status": ph_status},
            "nitrogen_ppm": {"value": nitrogen, "status": n_status},
            "phosphorus_ppm": {"value": phosphorus, "status": p_status},
            "potassium_ppm": {"value": potassium, "status": k_status},
            "moisture_pct": {"value": moisture, "status": moisture_status},
            "soil_type": soil_type
        },
        "deficiencies": deficiencies,
        "organic_amendments": recommendations,
        "suitable_crops": [
            "Tomatoes", "Capsicum / Peppers", "Eggplant (Brinjal)", "Legumes / Beans"
        ] if score >= 60 else ["Legumes / Beans (Nitrogen-fixing crops for soil recovery)"]
    }
