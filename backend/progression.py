import random

def predict_progression(disease_label: str, severity_pct: float, spread_rate: str) -> dict:
    """
    Heuristic-based disease progression forecasting.
    Predicts risk level and 7-day spread forecast.
    """
    
    # Base spread factors
    spread_factors = {
        "Very Fast": 1.5,
        "Fast": 1.3,
        "Moderate": 1.1,
        "Slow": 1.05,
        "N/A": 0
    }
    
    factor = spread_factors.get(spread_rate, 1.0)
    
    # Healthy plants have 0 risk
    if "healthy" in disease_label.lower():
        return {
            "risk_score": 0,
            "warning_level": "Low",
            "forecast_7d": [0] * 7,
            "days_to_severe": -1
        }

    # Generate 7-day forecast
    forecast = []
    current = severity_pct
    for day in range(7):
        # Add some random variation (weather/environment simulation)
        daily_growth = (factor * (1 + random.uniform(-0.05, 0.1)))
        current = min(100, current * daily_growth)
        forecast.append(round(current, 2))

    # Calculate risk score (0-100)
    # Based on current severity and spread potential
    risk_score = min(100, (severity_pct * 0.6) + (factor * 20))
    
    if risk_score > 80:
        warning = "Critical"
    elif risk_score > 50:
        warning = "High"
    elif risk_score > 25:
        warning = "Medium"
    else:
        warning = "Low"

    # Estimate days until it becomes "Severe" (e.g., > 50%)
    days_to_severe = -1
    if severity_pct < 50:
        temp_sev = severity_pct
        for d in range(1, 30):
            temp_sev *= factor
            if temp_sev >= 50:
                days_to_severe = d
                break

    return {
        "risk_score": round(risk_score, 1),
        "warning_level": warning,
        "forecast_7d": forecast,
        "days_to_severe": days_to_severe
    }
