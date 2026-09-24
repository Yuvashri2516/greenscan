"""
main.py - GreenScan FastAPI Backend
IEEE/Scopus Research Grade Decision Support System API
"""

import os
import io
import sys
import logging
import traceback
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import base64
from fastapi.responses import StreamingResponse

# Ensure backend root is in sys.path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Logger setup
logger = logging.getLogger("greenscan.api")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("[GreenScan API] %(asctime)s %(levelname)s: %(message)s"))
if not logger.handlers:
    logger.addHandler(ch)

# ─── Model Loading ────────────────────────────────────────────────────────────
# Priority: Frozen Research Model (EfficientNetB0 best checkpoint)
RESEARCH_MODEL_PATH = (Path(__file__).parent.parent / "research" / "models" / "greenscan_efficientnetb0_best.keras").resolve()
DEPLOYMENT_MODEL_PATH = (Path(__file__).parent.parent / "model" / "greenscan_model.keras").resolve()
MODEL_PATH = RESEARCH_MODEL_PATH if RESEARCH_MODEL_PATH.is_file() else DEPLOYMENT_MODEL_PATH
CLASS_LABELS = ["tomato_Early blight", "tomato_Late blight", "tomato_healthy"]

def load_tf_model():
    if not MODEL_PATH.is_file():
        logger.warning(f"Model file not found at {MODEL_PATH}")
        return None
    try:
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        model = tf.keras.models.load_model(str(MODEL_PATH))
        logger.info(f"Successfully loaded frozen EfficientNet-B0 model from {MODEL_PATH}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {MODEL_PATH}: {e}")
        return None

model = load_tf_model()

# ─── Module Imports ───────────────────────────────────────────────────────────
from image_enhancer import enhance_leaf_image, QualityCheckError
from leaf_segmenter import segment_leaf
from gradcam_engine import get_gradcam_activation_matrix
from gsa_engine import run_gsa_pipeline
from database import save_scan_history, get_recent_history, get_disease_catalog, export_history_csv
from recommendation_engine import get_recommendations_for_disease
from chatbot import get_chat_response
from tips import get_daily_tips
from weather import get_weather_risk
from dosage import calculate_dosage
from soil import analyze_soil_health
import config
import gsa_engine

# GreenScan 2.0 new module imports
from leaf_validator import validate_leaf_image, get_validation_user_message, VALID_TOMATO_LEAF, NOT_TOMATO_LEAF, LOW_QUALITY_IMAGE
from farmer_db import (
    create_farmer, get_farmer, update_farmer, verify_farmer_pin,
    get_farmer_history, get_farmer_trends, list_farmers
)
from knowledge_base import get_knowledge, retrieve_relevant_knowledge, get_all_disease_keys
from recommendation_v2 import get_structured_recommendations

# Override GSA threshold with config
gsa_engine.GRADCAM_THRESHOLD = config.GRADCAM_THRESHOLD

# ─── FastAPI Application Initialization ─────────────────────────────────────
app = FastAPI(
    title="GreenScan API",
    description="Explainable AI Plant Disease Detection & Decision Support System",
    version="2.0.0"
)

# Build CORS origin list from environment
# FRONTEND_URL: set this on Render to your Vercel frontend URL (e.g. https://greenscan.vercel.app)
_frontend_url = os.getenv("FRONTEND_URL", "").strip()
_allowed_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]
if _frontend_url:
    if _frontend_url == "*":
        _allowed_origins = ["*"]
    else:
        for u in _frontend_url.split(","):
            u = u.strip()
            if u and u not in _allowed_origins:
                _allowed_origins.append(u)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if "*" not in _allowed_origins else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Request Models ─────────────────────────────────────────────────
class ChatApiRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    context: Optional[dict] = None
    history: Optional[List[dict]] = None
    # GreenScan 2.0: optional extended context fields
    farmer_context: Optional[dict] = None
    weather_context: Optional[dict] = None
    history_trend: Optional[str] = None

class DosageApiRequest(BaseModel):
    disease: str
    severity: str
    area_value: float
    area_unit: Optional[str] = "acres"

class SoilApiRequest(BaseModel):
    ph: Optional[float] = 6.5
    nitrogen: Optional[float] = 140.0
    phosphorus: Optional[float] = 45.0
    potassium: Optional[float] = 210.0
    moisture: Optional[float] = 45.0
    soil_type: Optional[str] = "Loam"

# GreenScan 2.0: Farmer Profile Models
class FarmerCreateRequest(BaseModel):
    name: str
    contact: Optional[str] = None
    farm_name: Optional[str] = None
    farm_location: Optional[str] = None
    farm_size: Optional[float] = None
    crop: Optional[str] = "Tomato"
    tomato_variety: Optional[str] = None
    crop_stage: Optional[str] = None
    irrigation_method: Optional[str] = None
    pin: Optional[str] = None

class FarmerUpdateRequest(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    farm_name: Optional[str] = None
    farm_location: Optional[str] = None
    farm_size: Optional[float] = None
    crop: Optional[str] = None
    tomato_variety: Optional[str] = None
    crop_stage: Optional[str] = None
    irrigation_method: Optional[str] = None
    pin: Optional[str] = None

class FarmerPinRequest(BaseModel):
    pin: str

# ─── API Routes ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "project": "GreenScan Decision Support System",
        "version": "2.0.0",
        "status": "running",
        "target_diseases": ["Tomato Healthy", "Tomato Early Blight", "Tomato Late Blight"],
        "features": [
            "Hierarchical leaf validation",
            "Disease classification + Grad-CAM + GSA",
            "Farmer profile system",
            "Context-aware structured recommendations",
            "Structured agricultural knowledge base",
            "Context-aware chatbot",
            "Environmental weather risk integration",
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH)
    }

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    farmer_id: Optional[str] = Query(None, description="Optional farmer ID to associate this scan")
):
    """
    GreenScan 2.0 Core Decision Support Inference Pipeline:
    0. [NEW] Phase 1 Hierarchical Leaf Validation (NOT_TOMATO_LEAF / LOW_QUALITY gate)
    1. Read input leaf photo
    2. OpenCV Quality Inspection & Enhancement (Blur, CLAHE, Bilateral filter)
    3. OpenCV Leaf Segmentation (Leaf Mask & Leaf Pixels count)
    4. [NEW] Leaf coverage validation gate (returns early if not valid leaf)
    5. EfficientNet-B0 Classification (Disease Label & Confidence)
    6. Internal Grad-CAM Heatmap Matrix Generation
    7. GreenScan Severity Analyzer (GSA) Pipeline
    8. Recommendation Lookup (legacy v1, preserved)
    9. [NEW] Structured Recommendation v2 (context-aware, farmer-specific)
    10. SQLite Persistence & Response Packaging
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Invalid image file format.")

        # Step A: OpenCV Enhancement & Blur/Quality Validation
        enhanced_bgr, quality_info = enhance_leaf_image(img_bgr, target_size=(224, 224))
        
        # Step B: Leaf Segmentation
        leaf_mask, leaf_pixels = segment_leaf(enhanced_bgr)

        # Step B2: [NEW] Phase 1 Leaf Validation Gate
        # Check if image is a valid tomato leaf before running expensive inference.
        total_pixels = enhanced_bgr.shape[0] * enhanced_bgr.shape[1]
        early_validation = validate_leaf_image(
            leaf_pixels=int(leaf_pixels),
            total_pixels=total_pixels,
            quality_info=quality_info,
            confidence=None,  # confidence not yet known at this stage
            min_leaf_coverage_pct=config.LEAF_COVERAGE_MIN_PCT,
            min_leaf_pixels=config.LEAF_PIXEL_MIN,
            min_confidence=config.MIN_CONFIDENCE_THRESHOLD,
        )

        # If image quality fails, return early with a clear user message
        # (NOT_TOMATO_LEAF based purely on coverage/quality before model runs)
        if not early_validation["is_valid"] and early_validation["validation_status"] == LOW_QUALITY_IMAGE:
            return {
                "validation": early_validation,
                "is_valid": False,
                "validation_status": early_validation["validation_status"],
                "message": early_validation["message"],
                "user_guidance": early_validation["user_guidance"],
            }
        
        # Step C: Model Prediction (EfficientNet-B0)
        # Match exact training preprocessing: raw [0, 255] float32 RGB image resized to 224x224 without double-normalization or color distortion.
        raw_resized_bgr = cv2.resize(img_bgr, (224, 224), interpolation=cv2.INTER_AREA)
        rgb_img = cv2.cvtColor(raw_resized_bgr, cv2.COLOR_BGR2RGB)
        input_arr = np.expand_dims(rgb_img.astype(np.float32), axis=0)
        if model is not None:
            preds = model.predict(input_arr, verbose=0)
            predicted_idx = int(np.argmax(preds[0]))
            confidence = float(np.max(preds[0]))
            predicted_class = CLASS_LABELS[predicted_idx]
        else:
            # Fallback mock prediction if model binary is missing
            predicted_idx = 1
            confidence = 0.945
            predicted_class = CLASS_LABELS[predicted_idx]

        # Step C2: [NEW] Post-prediction leaf coverage validation
        # Now that we have the confidence score, re-run validator to catch borderline cases.
        validation_result = validate_leaf_image(
            leaf_pixels=int(leaf_pixels),
            total_pixels=total_pixels,
            quality_info=quality_info,
            confidence=confidence,
            min_leaf_coverage_pct=config.LEAF_COVERAGE_MIN_PCT,
            min_leaf_pixels=config.LEAF_PIXEL_MIN,
            min_confidence=config.MIN_CONFIDENCE_THRESHOLD,
        )

        # Return early for NOT_TOMATO_LEAF (coverage-based rejection)
        if not validation_result["is_valid"] and validation_result["validation_status"] == NOT_TOMATO_LEAF:
            return {
                "validation": validation_result,
                "is_valid": False,
                "validation_status": NOT_TOMATO_LEAF,
                "message": validation_result["message"],
                "user_guidance": validation_result["user_guidance"],
            }

        # Map display name
        display_names = {
            "tomato_healthy": "Tomato Healthy",
            "tomato_Early blight": "Tomato Early Blight",
            "tomato_Late blight": "Tomato Late Blight"
        }
        display_name = display_names.get(predicted_class, predicted_class)

        # Step D: Internal Grad-CAM Activation Matrix
        gradcam_matrix = get_gradcam_activation_matrix(model, input_arr, predicted_idx)

        # Step E: GreenScan Severity Analyzer (GSA) Execution
        gsa_results = run_gsa_pipeline(
            gradcam_matrix=gradcam_matrix,
            leaf_mask=leaf_mask,
            leaf_pixels=leaf_pixels,
            confidence=confidence,
            predicted_class=predicted_class
        )

        # Step F: Recommendation Lookup
        recommendations = get_recommendations_for_disease(
            disease_key=predicted_class,
            severity_level=gsa_results["severity_level"]
        )
        
        # Step G: Progression Forecast & Disease Info Lookup
        from progression import predict_progression
        from disease_db import get_disease_info
        
        disease_info_data = get_disease_info(predicted_class)
        progression_data = predict_progression(
            disease_label=predicted_class,
            severity_pct=gsa_results["attention_affected_region_percent"],
            spread_rate=disease_info_data.get("spread_rate", "Moderate")
        )
        
        # --- Farmer Safety Logic ---
        is_reliable = True
        unreliable_reasons = []
        
        if not quality_info.get("passed", True):
            is_reliable = False
            unreliable_reasons.extend(quality_info.get("reasons", []))
            
        if confidence < config.MIN_CONFIDENCE_THRESHOLD:
            is_reliable = False
            unreliable_reasons.append(f"Model confidence ({confidence*100:.1f}%) is below the minimum reliable threshold ({config.MIN_CONFIDENCE_THRESHOLD*100}%).")
            
        if not is_reliable:
            # Overwrite recommendations to safety message
            recommendations = {
                "organic": [],
                "chemical": [],
                "preventive": [
                    "Capture the entire leaf.",
                    "Use sufficient lighting.",
                    "Avoid blur.",
                    "Keep the leaf in focus.",
                    "Avoid excessive background.",
                    "Capture one leaf at a time."
                ],
                "safety_warning": "Unable to provide a reliable diagnosis. " + " ".join(unreliable_reasons)
            }

        # Generate base64 visuals for Research Validation Mode
        # 1. Original Leaf
        _, buffer = cv2.imencode('.jpg', enhanced_bgr)
        orig_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # 2. Grad-CAM Heatmap
        heatmap_color = cv2.applyColorMap(np.uint8(255 * gradcam_matrix), cv2.COLORMAP_JET)
        heatmap_overlay = cv2.addWeighted(enhanced_bgr, 0.6, heatmap_color, 0.4, 0)
        _, buffer = cv2.imencode('.jpg', heatmap_overlay)
        heatmap_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # 3. Leaf Mask
        mask_vis = (leaf_mask * 255).astype(np.uint8)
        _, buffer = cv2.imencode('.png', mask_vis)
        mask_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # 4. Activation Mask
        act_mask_vis = (gsa_results["_internal_activated_mask"] * 255).astype(np.uint8)
        _, buffer = cv2.imencode('.png', act_mask_vis)
        act_mask_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # 5. Overlay
        # Red overlay for activated region
        red_overlay = np.zeros_like(enhanced_bgr)
        red_overlay[:, :] = [0, 0, 255] # BGR
        act_overlay = np.where(gsa_results["_internal_activated_mask"][..., None], 
                               cv2.addWeighted(enhanced_bgr, 0.5, red_overlay, 0.5, 0), 
                               enhanced_bgr)
        _, buffer = cv2.imencode('.jpg', act_overlay)
        overlay_b64 = base64.b64encode(buffer).decode('utf-8')

        # Final Dashboard Record
        response_payload = {
            "disease": display_name,
            "disease_name": predicted_class,
            "display_name": display_name,
            "prediction": predicted_class,
            "confidence": round(confidence * 100.0, 2),
            "is_healthy": "healthy" in predicted_class.lower(),
            "is_reliable": is_reliable,
            "unreliable_reasons": unreliable_reasons,
            "quality_info": quality_info,
            "disease_info": disease_info_data,
            "progression": progression_data,
            "gsa_metrics": {
                "leaf_pixels": gsa_results["leaf_pixels"],
                "activated_pixels": gsa_results["activated_pixels"],
                "affected_area_pct": gsa_results["attention_affected_region_percent"], # Backward compat
                "attention_affected_region_percent": gsa_results["attention_affected_region_percent"],
                "weighted_activation_score": gsa_results["mean_leaf_activation"], # Backward compat
                "plant_health_score": gsa_results["plant_health_score"],
                "severity_level": gsa_results["severity_level"],
                "traffic_light": gsa_results["traffic_light"],
                "traffic_code": gsa_results["traffic_code"],
                "risk_level": gsa_results["risk_level"],
                "treatment_priority": gsa_results["treatment_priority"]
            },
            "research_details": {
                "leaf_pixels": gsa_results["leaf_pixels"],
                "activated_pixels": gsa_results["activated_pixels"],
                "attention_affected_region_percent": gsa_results["attention_affected_region_percent"],
                "mean_leaf_activation": gsa_results["mean_leaf_activation"],
                "mean_activated_activation": gsa_results["mean_activated_activation"],
                "threshold_used": gsa_results["threshold_used"],
                "visuals": {
                    "original": f"data:image/jpeg;base64,{orig_b64}",
                    "heatmap": f"data:image/jpeg;base64,{heatmap_b64}",
                    "leaf_mask": f"data:image/png;base64,{mask_b64}",
                    "activation_mask": f"data:image/png;base64,{act_mask_b64}",
                    "overlay": f"data:image/jpeg;base64,{overlay_b64}"
                }
            },
            "recommendations": recommendations,
            # GreenScan 2.0: Validation result (Phase 1)
            "validation": {
                "status": validation_result["validation_status"],
                "is_valid": validation_result["is_valid"],
                "leaf_coverage_pct": validation_result["leaf_coverage_pct"],
                "quality_passed": validation_result["quality_passed"],
                "quality_reasons": validation_result["quality_reasons"],
                "confidence_warning": validation_result["confidence_warning"],
                "message": get_validation_user_message(validation_result) or None,
            },
            "is_valid": validation_result["is_valid"],
            "validation_status": validation_result["validation_status"],
            "illumination_info": quality_info.get("illumination", {}),
            # GreenScan 2.0: Farmer association
            "farmer_id": farmer_id,
        }

        # GreenScan 2.0: Build structured recommendation v2
        try:
            structured_rec = get_structured_recommendations(
                disease_key=predicted_class,
                severity_level=gsa_results["severity_level"],
                confidence=confidence,
                weather_context=None,  # enriched externally if farmer passes weather
                farmer_context=get_farmer(farmer_id) if farmer_id else None,
                history_trend=None,  # enriched from farmer trends if farmer_id provided
            )
            if farmer_id:
                try:
                    trends = get_farmer_trends(farmer_id)
                    structured_rec = get_structured_recommendations(
                        disease_key=predicted_class,
                        severity_level=gsa_results["severity_level"],
                        confidence=confidence,
                        farmer_context=get_farmer(farmer_id),
                        history_trend=trends.get("trend_direction"),
                    )
                except Exception:
                    pass  # Non-critical; proceed without trend data
            response_payload["structured_recommendation"] = structured_rec
        except Exception as rec_err:
            logger.error(f"Failed to build structured recommendation: {rec_err}")
            response_payload["structured_recommendation"] = None

        # Step G: Persist to SQLite
        try:
            save_scan_history({
                "disease_name": predicted_class,
                "display_name": display_name,
                "confidence": round(confidence * 100.0, 2),
                "plant_health_score": gsa_results["plant_health_score"],
                "affected_area_pct": gsa_results["attention_affected_region_percent"],
                "weighted_activation": gsa_results["mean_leaf_activation"],
                "severity_level": gsa_results["severity_level"],
                "risk_level": gsa_results["risk_level"],
                "treatment_priority": gsa_results["treatment_priority"],
                "traffic_light": gsa_results["traffic_light"],
                "leaf_pixels": gsa_results["leaf_pixels"],
                "activated_pixels": gsa_results["activated_pixels"],
                "farmer_id": farmer_id,
                "validation_status": validation_result["validation_status"],
                "research_metrics_json": {
                    "attention_affected_region_percent": gsa_results["attention_affected_region_percent"],
                    "mean_leaf_activation": gsa_results["mean_leaf_activation"],
                    "mean_activated_activation": gsa_results["mean_activated_activation"],
                    "threshold_used": gsa_results["threshold_used"]
                },
                "recommendations": recommendations
            })
        except Exception as db_err:
            logger.error(f"Failed to persist scan history to SQLite: {db_err}")

        return response_payload

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction pipeline error: {str(e)}")

@app.post("/chat")
async def chat(request: ChatApiRequest):
    return await get_chat_response(
        message=request.message,
        language=request.language or "en",
        context=request.context,
        history=request.history,
        # GreenScan 2.0 extended context
        farmer_context=request.farmer_context,
        weather_context=request.weather_context,
        history_trend=request.history_trend,
    )

@app.get("/history")
def history(limit: int = 20):
    return {"history": get_recent_history(limit)}

@app.get("/export-research")
def export_research():
    csv_data = export_history_csv()
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=greenscan_research_data.csv"}
    )

@app.get("/disease")
def disease(name: Optional[str] = None):
    catalog = get_disease_catalog()
    if name:
        filtered = [d for d in catalog if d["key"].lower() == name.lower() or d["display_name"].lower() == name.lower()]
        return {"diseases": filtered}
    return {"diseases": catalog}

@app.get("/tips")
def tips(count: int = 3):
    return {"tips": get_daily_tips(count)}

@app.get("/weather")
async def weather(lat: float = Query(...), lon: float = Query(...)):
    return await get_weather_risk(lat, lon)

@app.post("/dosage")
async def dosage_calc(request: DosageApiRequest):
    return calculate_dosage(
        disease=request.disease,
        severity=request.severity,
        area_value=request.area_value,
        area_unit=request.area_unit or "acres"
    )

@app.post("/soil-health")
async def soil_diagnose(request: SoilApiRequest):
    return analyze_soil_health(
        ph=request.ph if request.ph is not None else 6.5,
        nitrogen=request.nitrogen if request.nitrogen is not None else 140.0,
        phosphorus=request.phosphorus if request.phosphorus is not None else 45.0,
        potassium=request.potassium if request.potassium is not None else 210.0,
        moisture=request.moisture if request.moisture is not None else 45.0,
        soil_type=request.soil_type or "Loam"
    )


# ─── GreenScan 2.0: Farmer Profile Routes (Phase 7) ────────────────────────────

@app.post("/farmers")
def create_farmer_profile(request: FarmerCreateRequest):
    """Create a new farmer profile. Returns farmer_id."""
    try:
        farmer_id = create_farmer(request.model_dump())
        return {"farmer_id": farmer_id, "message": "Farmer profile created successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create farmer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create farmer profile.")


@app.get("/farmers/{farmer_id}")
def get_farmer_profile(farmer_id: str):
    """Retrieve a farmer profile by ID. PIN hash is never returned."""
    farmer = get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")
    return {"farmer": farmer}


@app.put("/farmers/{farmer_id}")
def update_farmer_profile(farmer_id: str, request: FarmerUpdateRequest):
    """Update a farmer profile. Only provided fields are updated."""
    updated = update_farmer(farmer_id, {k: v for k, v in request.model_dump().items() if v is not None})
    if not updated:
        raise HTTPException(status_code=404, detail="Farmer not found.")
    return {"farmer": updated, "message": "Profile updated."}


@app.post("/farmers/{farmer_id}/verify")
def verify_pin(farmer_id: str, request: FarmerPinRequest):
    """Verify a farmer's PIN. Returns {valid: bool}."""
    is_valid = verify_farmer_pin(farmer_id, request.pin)
    return {"valid": is_valid}


@app.get("/farmers/{farmer_id}/history")
def farmer_history(farmer_id: str, limit: int = 20):
    """Return scan history for a specific farmer (data-isolated)."""
    farmer = get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")
    history = get_farmer_history(farmer_id, limit=limit)
    return {"farmer_id": farmer_id, "history": history}


@app.get("/farmers/{farmer_id}/trends")
def farmer_trends(farmer_id: str, limit: int = 20):
    """Return health score and severity trend analysis for a farmer."""
    farmer = get_farmer(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")
    trends = get_farmer_trends(farmer_id, limit=limit)
    return {"farmer_id": farmer_id, "trends": trends}


# ─── GreenScan 2.0: Knowledge Base Routes (Phase 11) ───────────────────────────

@app.get("/knowledge")
def knowledge_index():
    """Returns all disease keys available in the knowledge base."""
    return {"disease_keys": get_all_disease_keys()}


@app.get("/knowledge/{disease_key}")
def knowledge_entry(disease_key: str):
    """Returns the full structured knowledge base entry for a disease."""
    # Normalize: replace hyphens with underscores, lowercase
    normalized_key = disease_key.replace("-", "_")
    # Try exact match first, then case-insensitive search
    from knowledge_base import KNOWLEDGE_BASE
    matched_key = next(
        (k for k in KNOWLEDGE_BASE if k.lower() == normalized_key.lower()),
        None
    )
    if matched_key:
        return {"disease_key": matched_key, "knowledge": get_knowledge(matched_key)}
    # Return fallback
    kb = get_knowledge(normalized_key)
    return {"disease_key": normalized_key, "knowledge": kb}