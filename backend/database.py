"""
database.py - GreenScan SQLite Database & Repository Layer
Persists scan history, disease catalogs, recommendations, and user logs.
"""

import sqlite3
import json
import os
import csv
import io
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent / "greenscan.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables for GreenScan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Scan History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            disease_name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            plant_health_score INTEGER NOT NULL,
            affected_area_pct REAL NOT NULL,
            weighted_activation REAL NOT NULL,
            severity_level TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            treatment_priority TEXT NOT NULL,
            traffic_light TEXT NOT NULL,
            leaf_pixels INTEGER NOT NULL,
            activated_pixels INTEGER NOT NULL,
            recommendations_json TEXT,
            research_metrics_json TEXT
        );
    """)

    # Alter table if it exists but lacks the new column (migration)
    try:
        cursor.execute("ALTER TABLE scan_history ADD COLUMN research_metrics_json TEXT;")
    except sqlite3.OperationalError:
        pass # Column already exists

    # 2. Disease Catalog Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disease_catalog (
            key TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            scientific_name TEXT,
            symptoms TEXT,
            causes TEXT,
            organic_treatment TEXT,
            chemical_treatment TEXT,
            preventive_measures TEXT,
            suitable_fertilizer TEXT,
            recovery_time TEXT
        );
    """)

    conn.commit()
    
    # Seed Disease Catalog if empty
    seed_disease_catalog(conn)
    conn.close()

def seed_disease_catalog(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM disease_catalog")
    if cursor.fetchone()[0] == 0:
        diseases = [
            (
                "tomato_healthy",
                "Tomato Healthy",
                "Solanum lycopersicum",
                "Vibrant green leaves, robust stem, clear vascular tissue, no spots or lesions.",
                "Optimal nutritional balance, proper soil drainage, clean environmental conditions.",
                "Maintain organic soil compost, neem oil foliar spray bi-weekly for prevention.",
                "No chemical treatment required.",
                "Ensure proper row spacing (45-60cm), crop rotation, drip irrigation at soil level.",
                "Balanced N-P-K (10-10-10) fertilizer during foliage growth, calcium nitrate during flowering.",
                "N/A (Plant is healthy)"
            ),
            (
                "tomato_Early blight",
                "Tomato Early Blight",
                "Alternaria solani",
                "Concentric ringed brown/black spots (target board pattern) on older lower leaves, leaf yellowing.",
                "Fungal pathogen Alternaria solani surviving in soil debris; favored by warm temperatures (24-29°C) and high humidity.",
                "Spray copper sulfate solution or Trichoderma harzianum; prune infected lower leaves.",
                "Apply Chlorothalonil or Mancozeb fungicide every 7-10 days.",
                "Rotate crops with non-solanaceous plants, mulch around base to prevent soil splash, avoid overhead watering.",
                "High Potassium (K) fertilizer to boost disease resistance; minimize excess nitrogen.",
                "10 to 14 days with active fungicidal management."
            ),
            (
                "tomato_Late blight",
                "Tomato Late Blight",
                "Phytophthora infestans",
                "Water-soaked dark lesions on leaves with white fuzzy fungal growth underneath in humid conditions, rapid wilting.",
                "Oomycete pathogen Phytophthora infestans spread by wind and rain; thrives in cool (15-22°C), wet weather.",
                "Baking soda solution (1 tbsp/gal water) with horticultural oil; immediate removal and destruction of heavily infected foliage.",
                "Systemic fungicides such as Metalaxyl, Dimethomorph, or Copper Hydroxide within 24-48 hours.",
                "Plant resistant cultivars (e.g., Defiant PHR), destroy volunteer tomato/potato plants, maintain rapid foliage drying.",
                "Potassium silicate spray to strengthen cell walls; avoid high nitrogen during wet spells.",
                "14 to 21 days; requires immediate containment to prevent total crop loss."
            )
        ]
        cursor.executemany("""
            INSERT INTO disease_catalog VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, diseases)
        conn.commit()

def save_scan_history(record: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scan_history (
            disease_name, display_name, confidence, plant_health_score,
            affected_area_pct, weighted_activation, severity_level, risk_level,
            treatment_priority, traffic_light, leaf_pixels, activated_pixels,
            recommendations_json, research_metrics_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["disease_name"],
        record["display_name"],
        record["confidence"],
        record["plant_health_score"],
        record["affected_area_pct"],
        record["weighted_activation"],
        record["severity_level"],
        record["risk_level"],
        record["treatment_priority"],
        record["traffic_light"],
        record["leaf_pixels"],
        record["activated_pixels"],
        json.dumps(record.get("recommendations", {})),
        json.dumps(record.get("research_metrics_json", {}))
    ))
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id

def get_recent_history(limit: int = 20) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM scan_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    history = []
    for r in rows:
        item = dict(r)
        if item.get("recommendations_json"):
            item["recommendations"] = json.loads(item["recommendations_json"])
        history.append(item)
    conn.close()
    return history

def get_disease_catalog() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM disease_catalog")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def export_history_csv() -> str:
    """Exports the scan_history table to a CSV formatted string for research validation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    if not rows:
        return ""
        
    writer = csv.writer(output)
    # Write headers
    writer.writerow(rows[0].keys())
    # Write data
    for row in rows:
        writer.writerow(row)
        
    return output.getvalue()

# Initialize DB when module loaded
init_db()
