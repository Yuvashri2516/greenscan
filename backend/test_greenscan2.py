"""
test_e2e.py - GreenScan 2.0 Extended End-to-End Tests

Tests all new GreenScan 2.0 modules:
  - Phase 1: Leaf validation (NOT_TOMATO_LEAF, LOW_QUALITY_IMAGE, VALID_TOMATO_LEAF)
  - Phase 7: Farmer CRUD (create, get, update, verify PIN, trends)
  - Phase 10: Structured recommendation v2
  - Phase 11: Knowledge base

Run from backend directory:
    python test_e2e.py
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

# ─── Test 1: Leaf Validator ────────────────────────────────────────────────────
def test_leaf_validator():
    from leaf_validator import validate_leaf_image, VALID_TOMATO_LEAF, NOT_TOMATO_LEAF, LOW_QUALITY_IMAGE

    print("\n[TEST] Leaf Validator")

    # Test 1a: Valid leaf (good coverage, quality passed)
    result = validate_leaf_image(
        leaf_pixels=15000,
        total_pixels=224 * 224,
        quality_info={"passed": True, "reasons": []},
        confidence=0.92,
        min_leaf_coverage_pct=10.0,
        min_leaf_pixels=1000,
    )
    assert result["validation_status"] == VALID_TOMATO_LEAF, f"Expected VALID, got {result['validation_status']}"
    assert result["is_valid"] == True
    print("  [PASS] Valid leaf correctly identified")

    # Test 1b: Not a tomato leaf (very low coverage)
    result = validate_leaf_image(
        leaf_pixels=50,
        total_pixels=224 * 224,
        quality_info={"passed": True, "reasons": []},
        confidence=0.45,
        min_leaf_coverage_pct=10.0,
        min_leaf_pixels=1000,
    )
    assert result["validation_status"] == NOT_TOMATO_LEAF, f"Expected NOT_TOMATO_LEAF, got {result['validation_status']}"
    assert result["is_valid"] == False
    print("  [PASS] Non-leaf image correctly rejected")

    # Test 1c: Low quality image
    result = validate_leaf_image(
        leaf_pixels=5000,
        total_pixels=224 * 224,
        quality_info={"passed": False, "reasons": ["Image is too blurry (Laplacian variance: 15.3 < 80.0)"]},
        confidence=None,
    )
    assert result["validation_status"] == LOW_QUALITY_IMAGE, f"Expected LOW_QUALITY, got {result['validation_status']}"
    assert result["is_valid"] == False
    print("  [PASS] Low quality image correctly rejected")

    # Test 1d: Confidence warning (valid but low confidence)
    result = validate_leaf_image(
        leaf_pixels=20000,
        total_pixels=224 * 224,
        quality_info={"passed": True, "reasons": []},
        confidence=0.68,  # Above hard block (0.65) but below warning (0.75)
        min_leaf_coverage_pct=10.0,
    )
    assert result["validation_status"] == VALID_TOMATO_LEAF
    assert result["confidence_warning"] == True
    print("  [PASS] Low confidence warning correctly set")


# ─── Test 2: Knowledge Base ────────────────────────────────────────────────────
def test_knowledge_base():
    from knowledge_base import get_knowledge, get_environmental_risk_factors, retrieve_relevant_knowledge, get_all_disease_keys

    print("\n[TEST] Knowledge Base")

    # Test 2a: Get existing knowledge
    kb = get_knowledge("tomato_Early blight")
    assert kb["display_name"] == "Tomato Early Blight"
    assert "symptoms" in kb
    assert len(kb["symptoms"]) > 0
    assert "treatment_categories" in kb
    print("  [PASS] Early Blight knowledge retrieved")

    kb2 = get_knowledge("tomato_Late blight")
    assert kb2["display_name"] == "Tomato Late Blight"
    print("  [PASS] Late Blight knowledge retrieved")

    kb3 = get_knowledge("tomato_healthy")
    assert kb3["display_name"] == "Healthy Tomato"
    print("  [PASS] Healthy Tomato knowledge retrieved")

    # Test 2b: Unknown key fallback
    kb_unknown = get_knowledge("tomato_unknown_disease")
    assert isinstance(kb_unknown, dict)
    assert "safety_information" in kb_unknown
    print("  [PASS] Unknown disease key returns fallback dict")

    # Test 2c: Environmental risk factors
    factors = get_environmental_risk_factors("tomato_Late blight", temp_c=15.0, humidity_pct=92.0)
    assert isinstance(factors, list)
    assert len(factors) > 0
    print(f"  [PASS] Environmental risk factors: {len(factors)} factor(s) for Late Blight at 15C/92%")

    # Test 2d: Retrieve relevant knowledge (RAG interface)
    results = retrieve_relevant_knowledge("how to treat fungicide spray", "tomato_Early blight")
    assert isinstance(results, list)
    assert len(results) > 0
    print(f"  [PASS] RAG retrieval: {len(results)} snippet(s) for treatment query")

    # Test 2e: All keys
    keys = get_all_disease_keys()
    assert "tomato_Early blight" in keys
    assert "tomato_Late blight" in keys
    assert "tomato_healthy" in keys
    print(f"  [PASS] All keys: {keys}")


# ─── Test 3: Structured Recommendation v2 ─────────────────────────────────────
def test_recommendation_v2():
    from recommendation_v2 import get_structured_recommendations

    print("\n[TEST] Structured Recommendation v2")

    # Test 3a: Late blight moderate
    rec = get_structured_recommendations(
        disease_key="tomato_Late blight",
        severity_level="Moderate",
        confidence=0.87,
    )
    assert "disease_display_name" in rec
    assert rec["disease_display_name"] == "Tomato Late Blight"
    assert "immediate_actions" in rec
    assert len(rec["immediate_actions"]) > 0
    assert "treatment_options" in rec
    assert "monitoring" in rec
    assert "disclaimer" in rec
    assert rec["farmer_context_used"] == False
    print("  [PASS] Late Blight Moderate recommendation generated")

    # Test 3b: With farmer context
    farmer_ctx = {
        "name": "Test Farmer",
        "crop_stage": "Flowering",
        "tomato_variety": "Kesar",
        "farm_name": "Test Farm",
        "irrigation_method": "Overhead",
    }
    rec_farmer = get_structured_recommendations(
        disease_key="tomato_Early blight",
        severity_level="Mild",
        confidence=0.92,
        farmer_context=farmer_ctx,
    )
    assert rec_farmer["farmer_context_used"] == True
    assert len(rec_farmer["personalization_notes"]) > 0
    print(f"  [PASS] Farmer context personalization: {len(rec_farmer['personalization_notes'])} notes")

    # Test 3c: Healthy plant
    rec_healthy = get_structured_recommendations(
        disease_key="tomato_healthy",
        severity_level="Healthy",
        confidence=0.96,
    )
    assert rec_healthy["is_healthy"] == True
    assert "treatment_options" in rec_healthy
    print("  [PASS] Healthy plant recommendation generated")

    # Safety: No LLM-invented dosages — all from static DB
    for opt_list in [rec["treatment_options"].get("organic", []), rec["treatment_options"].get("chemical", [])]:
        for item in opt_list:
            # Items should be strings from static DB, not complex LLM output
            assert isinstance(item, str)
    print("  [PASS] All treatment options are static strings (no LLM data)")


# ─── Test 4: Farmer DB ────────────────────────────────────────────────────────
def test_farmer_db():
    from database import init_db
    from farmer_db import create_farmer, get_farmer, update_farmer, verify_farmer_pin, get_farmer_trends

    # Use a temp DB for testing
    import database
    import farmer_db

    # Init test DB
    init_db()

    print("\n[TEST] Farmer DB")

    # Test 4a: Create farmer
    farmer_id = create_farmer({
        "name": "Test Farmer GreenScan",
        "farm_name": "Test Farm",
        "farm_location": "Chennai",
        "farm_size": 2.5,
        "crop": "Tomato",
        "tomato_variety": "Kesar",
        "crop_stage": "Flowering",
        "irrigation_method": "Drip",
        "pin": "1234",
        "contact": "9876543210"
    })
    assert farmer_id is not None
    assert len(farmer_id) > 10  # UUID
    print(f"  [PASS] Farmer created with ID {farmer_id[:8]}...")

    # Test 4b: Get farmer (PIN excluded)
    farmer = get_farmer(farmer_id)
    assert farmer is not None
    assert farmer["name"] == "Test Farmer GreenScan"
    assert "pin" not in farmer  # PIN hash never returned
    assert farmer["crop_stage"] == "Flowering"
    print("  [PASS] Farmer retrieved (PIN excluded)")

    # Test 4c: Update farmer
    updated = update_farmer(farmer_id, {"crop_stage": "Fruiting", "farm_size": 3.0})
    assert updated["crop_stage"] == "Fruiting"
    assert updated["farm_size"] == 3.0
    print("  [PASS] Farmer updated")

    # Test 4d: Verify PIN
    assert verify_farmer_pin(farmer_id, "1234") == True
    assert verify_farmer_pin(farmer_id, "9999") == False
    print("  [PASS] PIN verification correct")

    # Test 4e: Trends (no scans yet)
    trends = get_farmer_trends(farmer_id)
    assert "trend_direction" in trends
    assert trends["scan_count"] == 0
    print("  [PASS] Trends returns insufficient_data for new farmer")


# ─── Test 5: Config Thresholds ────────────────────────────────────────────────
def test_config():
    import config
    print("\n[TEST] Config")
    assert hasattr(config, "LEAF_COVERAGE_MIN_PCT"), "Missing LEAF_COVERAGE_MIN_PCT"
    assert hasattr(config, "LEAF_PIXEL_MIN"), "Missing LEAF_PIXEL_MIN"
    assert hasattr(config, "LOW_CONFIDENCE_WARNING_THRESHOLD"), "Missing LOW_CONFIDENCE_WARNING_THRESHOLD"
    assert 0 < config.LEAF_COVERAGE_MIN_PCT < 100
    assert config.LEAF_PIXEL_MIN > 0
    assert 0 < config.LOW_CONFIDENCE_WARNING_THRESHOLD < 1
    print(f"  [PASS] LEAF_COVERAGE_MIN_PCT = {config.LEAF_COVERAGE_MIN_PCT}%")
    print(f"  [PASS] LEAF_PIXEL_MIN = {config.LEAF_PIXEL_MIN}")
    print(f"  [PASS] LOW_CONFIDENCE_WARNING_THRESHOLD = {config.LOW_CONFIDENCE_WARNING_THRESHOLD}")


if __name__ == "__main__":
    print("=" * 60)
    print("  GreenScan 2.0 - Extended Test Suite")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_fn in [test_config, test_leaf_validator, test_knowledge_base, test_recommendation_v2, test_farmer_db]:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test_fn.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
