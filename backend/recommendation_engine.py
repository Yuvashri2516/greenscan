"""
recommendation_engine.py - GreenScan Recommendation Engine
Provides comprehensive agronomic treatment protocols based on disease diagnosis and GSA severity.
"""

from database import get_disease_catalog

def split_treatment_field(text: str) -> list:
    if not text:
        return []
    if ";" in text:
        return [x.strip() for x in text.split(";") if x.strip()]
    if "," in text and len(text.split(",")) > 1:
        parts = [x.strip() for x in text.split(",") if x.strip()]
        if all(len(p) < 100 for p in parts):
            return parts
    return [text.strip()]

def get_recommendations_for_disease(disease_key: str, severity_level: str = "Moderate") -> dict:
    """
    Retrieves symptoms, causes, organic treatment, chemical treatment,
    preventive measures, suitable fertilizer, and recovery time.
    """
    catalog = get_disease_catalog()
    disease_info = next((d for d in catalog if d["key"].lower() == disease_key.lower()), None)
    
    if not disease_info:
        # Fallback to healthy if key unmatched
        disease_info = catalog[0]
        
    org_plan = split_treatment_field(disease_info["organic_treatment"])
    chem_plan = split_treatment_field(disease_info["chemical_treatment"])
    prev_plan = split_treatment_field(disease_info["preventive_measures"])
        
    return {
        "disease_key": disease_info["key"],
        "display_name": disease_info["display_name"],
        "scientific_name": disease_info["scientific_name"],
        "symptoms": disease_info["symptoms"],
        "causes": disease_info["causes"],
        "organic_treatment": disease_info["organic_treatment"],
        "chemical_treatment": disease_info["chemical_treatment"],
        "preventive_measures": disease_info["preventive_measures"],
        "suitable_fertilizer": disease_info["suitable_fertilizer"],
        "recovery_time": disease_info["recovery_time"],
        "severity_context": severity_level,
        "organic_plan": org_plan,
        "chemical_plan": chem_plan,
        "prevention_plan": prev_plan
    }

