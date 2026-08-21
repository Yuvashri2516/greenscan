# GreenScan+ — Testing Documentation

This document describes the testing status of all major GreenScan+ system components.

> **Legend:**  
> ✅ PASS — Tested and verified working  
> ⚠️ PARTIAL — Partially tested; some gaps noted  
> ❌ FAIL — Known failure  
> 🔲 NOT TESTED — No test performed

---

## 1. Backend API Tests

### Health & Startup

| Test | Status | Notes |
|---|---|---|
| Backend starts without errors | ✅ PASS | `uvicorn backend.main:app --port 8001` |
| `GET /` returns project info | ✅ PASS | Returns version, status, disease list |
| `GET /health` returns model status | ✅ PASS | `model_loaded: true` when `.keras` file present |
| API docs available at `/docs` | ✅ PASS | Swagger UI renders correctly |

### Prediction Pipeline

| Test | Status | Notes |
|---|---|---|
| `POST /predict` accepts JPEG upload | ✅ PASS | Returns full prediction JSON |
| `POST /predict` accepts PNG upload | ✅ PASS | |
| Classification returns 3-class probabilities | ✅ PASS | tomato_healthy, Early Blight, Late Blight |
| Confidence score returned correctly | ✅ PASS | Range 0–100% |
| Grad-CAM heatmap base64 returned | ✅ PASS | `research_details.visuals.heatmap` |
| Leaf mask base64 returned | ✅ PASS | `research_details.visuals.leaf_mask` |
| GSA metrics returned | ✅ PASS | plant_health_score, severity_level, affected_area_pct |
| Disease info returned | ✅ PASS | Symptoms, causes, prevention, solutions |
| Recommendations returned | ✅ PASS | organic, chemical, preventive |
| Progression forecast returned | ✅ PASS | risk_level, 7-day spread projection |
| Scan saved to SQLite history | ✅ PASS | `backend/greenscan.db` updated |
| Blur detection rejects blurry images | ✅ PASS | Returns `is_reliable: false` with reason |
| Low confidence triggers safety warning | ✅ PASS | Below `MIN_CONFIDENCE_THRESHOLD` (0.65) |

### Supporting Endpoints

| Test | Status | Notes |
|---|---|---|
| `GET /history` returns recent scans | ✅ PASS | Default limit 20 |
| `GET /export-research` returns CSV | ✅ PASS | Downloadable scan export |
| `GET /disease` returns catalog | ✅ PASS | All 3 disease entries |
| `POST /chat` returns chatbot response | ✅ PASS | Falls back gracefully without API key |
| `GET /tips` returns agricultural tips | ✅ PASS | |
| `POST /dosage` returns dosage calculation | ✅ PASS | Organic and chemical outputs |
| `POST /soil-health` returns NPK analysis | ✅ PASS | Recommendations returned |
| `GET /weather` returns risk data | ⚠️ PARTIAL | Requires valid lat/lon and network access |

---

## 2. Frontend UI Tests

### Navigation

| Test | Status | Notes |
|---|---|---|
| Home page loads at `/` | ✅ PASS | |
| Scan page loads at `/scan?tab=scan` | ✅ PASS | |
| History page loads at `/history` | ✅ PASS | |
| Disease Information page loads | ✅ PASS | |
| Soil Advisor tab loads | ✅ PASS | |
| Dosage Calculator tab loads | ✅ PASS | |
| Chatbot panel opens | ✅ PASS | |
| Navigation links work correctly | ✅ PASS | |
| Mobile navigation menu works | ✅ PASS | |

### Scan Flow

| Test | Status | Notes |
|---|---|---|
| File upload (gallery picker) | ✅ PASS | |
| Drag-and-drop image upload | ✅ PASS | |
| Demo leaf scan | ✅ PASS | Base64 demo image loaded |
| Loading state displays correctly | ✅ PASS | Pulsing skeleton UI |
| Results render after prediction | ✅ PASS | Disease name, confidence, PHS |
| Grad-CAM heatmap displays | ✅ PASS | Canvas overlay |
| Disease info panel renders | ✅ PASS | |
| Recommendations panel renders | ✅ PASS | |
| Download Report button downloads HTML | ✅ PASS | Opens in browser by double-click |
| Error state shown for bad image | ✅ PASS | Error message displayed |

### History

| Test | Status | Notes |
|---|---|---|
| History list loads from API | ✅ PASS | |
| Empty state shows correct copy | ✅ PASS | "No scans yet" / "Your analyzed plants will appear here." |
| Skeleton loader during fetch | ✅ PASS | |
| Clicking history item reloads result | ✅ PASS | |

### Chatbot

| Test | Status | Notes |
|---|---|---|
| Chatbot opens from floating button | ✅ PASS | |
| Idle state shows "No active plant scan" | ✅ PASS | |
| Active disease context displayed | ✅ PASS | Disease name in context |
| Query submission works | ✅ PASS | |
| Response rendered in chat bubble | ✅ PASS | |

### Soil Advisor

| Test | Status | Notes |
|---|---|---|
| NPK input sliders work | ✅ PASS | |
| Submit triggers `/soil-health` API | ✅ PASS | |
| Results display NPK analysis | ✅ PASS | |
| Skeleton state during load | ✅ PASS | |

### Dosage Calculator

| Test | Status | Notes |
|---|---|---|
| Disease and severity selection | ✅ PASS | |
| Area input and unit selection | ✅ PASS | |
| Calculate button triggers `/dosage` | ✅ PASS | |
| Organic and chemical doses displayed | ✅ PASS | |
| Skeleton state during load | ✅ PASS | |

---

## 3. Machine Learning Tests

| Test | Status | Notes |
|---|---|---|
| Model loads from `model/greenscan_model.keras` | ✅ PASS | |
| 3-class classification inference runs | ✅ PASS | |
| Tomato Healthy correctly classified | ✅ PASS | Validation accuracy 98.88% |
| Tomato Early Blight correctly classified | ✅ PASS | Validation accuracy 89.29% |
| Tomato Late Blight correctly classified | ✅ PASS | Validation accuracy 87.08% |
| Overall validation accuracy | ✅ PASS | **91.76%** on 1,505 images |
| Confidence correctly normalized to % | ✅ PASS | |
| Warm inference time | ✅ PASS | ~1.19 seconds average |

---

## 4. GSA Engine Tests

| Test | Status | Notes |
|---|---|---|
| Grad-CAM activation matrix produced | ✅ PASS | |
| HSV leaf mask produced | ✅ PASS | |
| Activated pixels count calculated | ✅ PASS | |
| Attention-affected region % calculated | ✅ PASS | |
| Mean activated activation calculated | ✅ PASS | |
| PHS formula applied correctly | ✅ PASS | Healthy: 100 − (mean × 5), Diseased: weighted |
| Severity tiers assigned correctly | ✅ PASS | Healthy ≥ 80, Mild 60–79, Moderate 40–59, Severe < 40 |
| Threshold τ = 0.60 applied | ✅ PASS | |
| Traffic light colour assigned | ✅ PASS | |

---

## 5. Error Handling Tests

| Test | Status | Notes |
|---|---|---|
| Non-image file rejected | ✅ PASS | Returns 400 error |
| Invalid file format rejected | ✅ PASS | |
| Blurry image triggers warning | ✅ PASS | is_reliable = false |
| Low confidence triggers warning | ✅ PASS | |
| Backend down: frontend shows error | ✅ PASS | Error boundary displayed |
| Empty chatbot query handled | ✅ PASS | |

---

## 6. Performance Tests

| Test | Status | Notes |
|---|---|---|
| Cold inference time | ✅ PASS | ~2.84 seconds (first load) |
| Warm inference time | ✅ PASS | ~1.19 seconds average |
| Frontend production build | ✅ PASS | `npm run build` succeeds — 530.74 kB bundle |
| Frontend dev server starts | ✅ PASS | `npm run dev` — no errors |

---

## 7. Android Tests

| Test | Status | Notes |
|---|---|---|
| Kotlin source code compiles | 🔲 NOT TESTED | No Android SDK/emulator available in this environment |
| API integration (Retrofit) | 🔲 NOT TESTED | Requires device or emulator |
| Camera capture | 🔲 NOT TESTED | Requires physical device |
| Result display | 🔲 NOT TESTED | |

> ⚠️ Android Kotlin source code is complete and reviewed. Build testing requires an Android SDK environment with a connected device or configured emulator.

---

## 8. Research Script Tests

| Script | Status | Notes |
|---|---|---|
| `backend/evaluate_greenscan.py` | ✅ PASS | 91.76% accuracy confirmed |
| `backend/evaluate_robustness.py` | ✅ PASS | 9 conditions × 30 samples verified |
| `backend/evaluate_gsa_calibration.py` | ✅ PASS | Threshold sweep τ ∈ [0.40–0.80] |
| `scripts/compile_final_results.py` | ✅ PASS | CSV tables and confusion matrix produced |
| `backend/validate_expert_csv.py` | ✅ PASS | 90/90 mapping verified; annotations pending |
| `backend/analyze_expert_validation.py` | ⚠️ PARTIAL | Correctly reports PENDING status; no stats yet |
| `scripts/train_disease.py` | ✅ PASS | Training pipeline functional |

---

## Summary

| Component | Status |
|---|---|
| Backend API | ✅ PASS |
| Frontend UI | ✅ PASS |
| ML Classification | ✅ PASS |
| GSA Engine | ✅ PASS |
| Error Handling | ✅ PASS |
| Performance | ✅ PASS |
| Android | 🔲 NOT TESTED |
| Expert Validation | ⚠️ PENDING |
| Pixel-Level IoU | ❌ NOT AVAILABLE |
