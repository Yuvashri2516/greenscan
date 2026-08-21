from collections import deque
from datetime import datetime

# In-memory storage for the demo
# In a real app, use a database (SQLite/PostgreSQL)
PREDICTION_HISTORY = deque(maxlen=500)

def record_prediction(entry: dict):
    """Adds a prediction result to history with a timestamp."""
    entry["timestamp"] = datetime.now().isoformat()
    PREDICTION_HISTORY.append(entry)

def get_analytics_summary():
    """Calculates statistics from history."""
    if not PREDICTION_HISTORY:
        return {
            "total_scans": 0,
            "disease_distribution": {},
            "severity_distribution": {},
            "avg_confidence": 0,
            "recent_activity": []
        }

    total = len(PREDICTION_HISTORY)
    dist = {}
    conf_sum = 0
    severity_dist = {"Mild": 0, "Moderate": 0, "Severe": 0, "Unknown": 0, "None": 0}

    for p in PREDICTION_HISTORY:
        label = p.get("display_name", "Unknown")
        dist[label] = dist.get(label, 0) + 1
        conf_sum += p.get("confidence", 0)
        
        sev = p.get("severity", "Unknown")
        if sev in severity_dist:
            severity_dist[sev] += 1

    return {
        "total_scans": total,
        "disease_distribution": dist,
        "severity_distribution": severity_dist,
        "avg_confidence": round(conf_sum / total, 2),
        "recent_activity": list(PREDICTION_HISTORY)[-10:]
    }
