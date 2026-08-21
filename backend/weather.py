import httpx
from typing import Dict, Any

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

async def get_weather_risk(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches real-time weather data from Open-Meteo API for given lat/lon
    and computes a fungal/bacterial plant disease risk score.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m,temperature_2m,precipitation_probability",
        "forecast_days": 1
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()

        current = data.get("current_weather", {})
        temp = current.get("temperature", 24.0)
        windspeed = current.get("windspeed", 10.0)

        # Extract hourly humidity and rain prob averages
        hourly = data.get("hourly", {})
        humidities = hourly.get("relativehumidity_2m", [70])
        rain_probs = hourly.get("precipitation_probability", [20])

        avg_humidity = sum(humidities[:12]) / max(len(humidities[:12]), 1)
        max_rain_prob = max(rain_probs[:12]) if rain_probs else 0

        # Calculate Disease Risk Index
        risk_score = 0
        risk_factors = []

        if avg_humidity > 80:
            risk_score += 40
            risk_factors.append("High relative humidity (>80%) creates ideal spore germination environment.")
        elif avg_humidity > 65:
            risk_score += 20
            risk_factors.append("Moderate humidity level detected.")

        if 18 <= temp <= 26:
            risk_score += 35
            risk_factors.append("Optimal temperature range (18°C-26°C) for fungal blights.")
        elif temp > 26:
            risk_score += 15
            risk_factors.append("Warm temperatures present.")

        if max_rain_prob > 50:
            risk_score += 25
            risk_factors.append(f"High rain probability ({max_rain_prob}%) accelerates foliar disease spread.")

        # Determine level
        if risk_score >= 75:
            risk_level = "Critical"
            warning_color = "#ef4444"
        elif risk_score >= 50:
            risk_level = "High"
            warning_color = "#f97316"
        elif risk_score >= 30:
            risk_level = "Moderate"
            warning_color = "#eab308"
        else:
            risk_level = "Low"
            warning_color = "#22c55e"

        return {
            "status": "success",
            "temperature_c": temp,
            "humidity_pct": round(avg_humidity, 1),
            "windspeed_kmh": windspeed,
            "rain_probability_pct": max_rain_prob,
            "disease_risk": {
                "score": risk_score,
                "level": risk_level,
                "color": warning_color,
                "target_pathogens": ["Late Blight (P. infestans)", "Early Blight (A. solani)", "Powdery Mildew"],
                "recommendation": (
                    "Apply protective copper fungicide immediately before expected rain." 
                    if risk_score >= 60 else 
                    "Monitor leaves closely for dark spots and ensure proper row spacing for airflow."
                ),
                "risk_factors": risk_factors
            }
        }

    except Exception as e:
        print(f"[Weather API Error] {e}")
        # Fallback graceful response
        return {
            "status": "fallback",
            "temperature_c": 25.0,
            "humidity_pct": 72.0,
            "windspeed_kmh": 12.0,
            "rain_probability_pct": 30,
            "disease_risk": {
                "score": 45,
                "level": "Moderate",
                "color": "#eab308",
                "target_pathogens": ["Early Blight", "Leaf Spot"],
                "recommendation": "Maintain optimal field ventilation and inspect leaves daily.",
                "risk_factors": ["Standard seasonal humidity baseline used (Network offline or location unavailable)."]
            }
        }
