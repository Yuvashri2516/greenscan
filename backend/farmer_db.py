"""
farmer_db.py - GreenScan 2.0 Phase 7: Farmer Profile CRUD Operations

Provides create, read, update, and query operations for farmer profiles
stored in the greenscan.db SQLite database (farmers table).

Design notes:
  - Farmer ID is generated as a UUID to avoid sequential guessing.
  - PIN is stored as a simple hash (SHA-256) for basic identity protection.
    This is NOT production-grade authentication. For a research prototype,
    it provides sufficient identity separation between farmers.
  - All functions are synchronous to match existing database.py patterns.
  - Data isolation: get_farmer_history returns ONLY that farmer's scans.
"""

import sqlite3
import json
import hashlib
import uuid
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger("greenscan.farmer_db")

DB_PATH = Path(__file__).parent / "greenscan.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_pin(pin: str) -> str:
    """SHA-256 hash of a PIN. Not production auth — research prototype only."""
    return hashlib.sha256(pin.strip().encode()).hexdigest()


# ─── CREATE ────────────────────────────────────────────────────────────────────

def create_farmer(profile: Dict[str, Any]) -> str:
    """
    Creates a new farmer profile in the database.

    Args:
        profile: dict with keys: name (required), contact, farm_name,
                 farm_location, farm_size, crop, tomato_variety, crop_stage,
                 irrigation_method, pin (optional, will be hashed).

    Returns:
        farmer_id (str): UUID string for the created farmer.

    Raises:
        ValueError: If 'name' is missing or empty.
    """
    name = (profile.get("name") or "").strip()
    if not name:
        raise ValueError("Farmer 'name' is required.")

    farmer_id = str(uuid.uuid4())
    pin_raw = profile.get("pin", "")
    pin_hash = _hash_pin(pin_raw) if pin_raw else None

    conn = _get_conn()
    try:
        conn.execute("""
            INSERT INTO farmers (
                farmer_id, name, contact, farm_name, farm_location,
                farm_size, crop, tomato_variety, crop_stage,
                irrigation_method, pin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            farmer_id,
            name,
            profile.get("contact"),
            profile.get("farm_name"),
            profile.get("farm_location"),
            profile.get("farm_size"),
            profile.get("crop", "Tomato"),
            profile.get("tomato_variety"),
            profile.get("crop_stage"),
            profile.get("irrigation_method"),
            pin_hash,
        ))
        conn.commit()
        logger.info(f"[FarmerDB] Created farmer '{name}' with ID {farmer_id}")
        return farmer_id
    finally:
        conn.close()


# ─── READ ──────────────────────────────────────────────────────────────────────

def get_farmer(farmer_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a farmer profile dict, or None if not found.
    The PIN hash is excluded from the returned dict.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM farmers WHERE farmer_id = ?", (farmer_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d.pop("pin", None)  # Never expose PIN hash
        return d
    finally:
        conn.close()


def list_farmers() -> List[Dict[str, Any]]:
    """Returns all farmer profiles (PIN excluded). For admin/debug use only."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM farmers ORDER BY created_at DESC"
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d.pop("pin", None)
            result.append(d)
        return result
    finally:
        conn.close()


# ─── UPDATE ────────────────────────────────────────────────────────────────────

def update_farmer(farmer_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Updates allowed fields on a farmer profile. Returns updated profile or None.

    Updatable fields: name, contact, farm_name, farm_location, farm_size,
                      crop, tomato_variety, crop_stage, irrigation_method, pin.
    """
    allowed = {
        "name", "contact", "farm_name", "farm_location", "farm_size",
        "crop", "tomato_variety", "crop_stage", "irrigation_method", "pin"
    }
    filtered = {k: v for k, v in updates.items() if k in allowed}
    if not filtered:
        return get_farmer(farmer_id)

    # Hash PIN if being updated
    if "pin" in filtered:
        raw_pin = filtered["pin"]
        filtered["pin"] = _hash_pin(raw_pin) if raw_pin else None

    filtered["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    set_clause = ", ".join(f"{k} = ?" for k in filtered.keys())
    values = list(filtered.values()) + [farmer_id]

    conn = _get_conn()
    try:
        conn.execute(
            f"UPDATE farmers SET {set_clause} WHERE farmer_id = ?",
            values
        )
        conn.commit()
        logger.info(f"[FarmerDB] Updated farmer {farmer_id}: {list(filtered.keys())}")
        return get_farmer(farmer_id)
    finally:
        conn.close()


# ─── AUTHENTICATION ────────────────────────────────────────────────────────────

def verify_farmer_pin(farmer_id: str, pin: str) -> bool:
    """
    Returns True if the provided PIN matches the stored hash for this farmer.
    Returns True if the farmer has no PIN set (open profile).
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT pin FROM farmers WHERE farmer_id = ?", (farmer_id,)
        ).fetchone()
        if row is None:
            return False
        stored_hash = row["pin"]
        if not stored_hash:
            return True  # No PIN set — open profile
        return _hash_pin(pin) == stored_hash
    finally:
        conn.close()


# ─── FARMER SCAN HISTORY ───────────────────────────────────────────────────────

def get_farmer_history(farmer_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Returns scan history records associated with a specific farmer.
    Data isolation: only returns records WHERE farmer_id = ?.
    """
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT * FROM scan_history
            WHERE farmer_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (farmer_id, limit)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            if item.get("recommendations_json"):
                try:
                    item["recommendations"] = json.loads(item["recommendations_json"])
                except Exception:
                    pass
            if item.get("environmental_context_json"):
                try:
                    item["environmental_context"] = json.loads(item["environmental_context_json"])
                except Exception:
                    pass
            result.append(item)
        return result
    finally:
        conn.close()


# ─── FARMER TRENDS ─────────────────────────────────────────────────────────────

def get_farmer_trends(farmer_id: str, limit: int = 20) -> Dict[str, Any]:
    """
    Computes health score and severity trends for a farmer's scan history.

    Returns:
        dict with:
            - health_scores: list of (date, score) tuples, newest first
            - severities: list of severity labels, newest first
            - dates: list of timestamp strings
            - disease_counts: dict of disease_name -> count
            - trend_direction: "improving" | "worsening" | "stable" | "insufficient_data"
            - avg_health_score: float
            - last_scan: dict or None
    """
    history = get_farmer_history(farmer_id, limit=limit)

    if not history:
        return {
            "health_scores": [],
            "severities": [],
            "dates": [],
            "disease_counts": {},
            "trend_direction": "insufficient_data",
            "avg_health_score": None,
            "last_scan": None,
            "scan_count": 0,
        }

    # Reverse to chronological order for trend calculation
    chron = list(reversed(history))

    health_scores = [item.get("plant_health_score", 0) for item in chron]
    severities = [item.get("severity_level", "Unknown") for item in chron]
    dates = [item.get("timestamp", "") for item in chron]
    disease_counts: Dict[str, int] = {}
    for item in chron:
        dn = item.get("display_name", "Unknown")
        disease_counts[dn] = disease_counts.get(dn, 0) + 1

    avg_health_score = round(sum(health_scores) / len(health_scores), 1) if health_scores else None

    # Trend: compare last 3 vs first 3 if enough data
    trend_direction = "stable"
    if len(health_scores) >= 4:
        half = len(health_scores) // 2
        older_avg = sum(health_scores[:half]) / half
        newer_avg = sum(health_scores[half:]) / (len(health_scores) - half)
        diff = newer_avg - older_avg
        if diff > 5:
            trend_direction = "improving"
        elif diff < -5:
            trend_direction = "worsening"
        else:
            trend_direction = "stable"
    elif len(health_scores) < 2:
        trend_direction = "insufficient_data"

    return {
        "health_scores": list(zip(dates, health_scores)),
        "severities": list(zip(dates, severities)),
        "dates": dates,
        "disease_counts": disease_counts,
        "trend_direction": trend_direction,
        "avg_health_score": avg_health_score,
        "last_scan": history[0] if history else None,
        "scan_count": len(history),
    }
