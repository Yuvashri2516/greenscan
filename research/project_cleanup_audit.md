# GreenScan — Project Cleanup Audit

Generated: 2026-08-21  
Purpose: Identify which files/folders are safe to keep, ignore via .gitignore, or delete before public GitHub release.

---

## Root Directory

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `backend/` | Core Python API source | **KEEP** | Essential source code |
| `frontend/` | React web application | **KEEP** | Essential source code |
| `android/` | Kotlin Android app | **KEEP** | Source code (SDK testing blocked) |
| `model/` | Trained Keras model | **KEEP + NOTE** | 25.3 MB — fits GitHub; keep as-is |
| `dataset/` | Training image dataset | **GITIGNORE** | 7,525 large images; too large for GitHub. Link to Kaggle/PlantVillage instead |
| `research/` | Research outputs, drafts, validation data | **KEEP** | Scientific documentation |
| `scripts/` | Training, evaluation, utility scripts | **KEEP** | Reproducibility |
| `venv/` | Python virtual environment | **GITIGNORE** | Never commit — regenerated with `pip install` |
| `.vscode/` | VS Code IDE settings | **GITIGNORE** | IDE-specific, not project config |
| `scratch/` | Temp scratch files | **DELETE** | Temporary working files only |
| `requirements.txt` | Root-level pip requirements (duplicate) | **DELETE** | Backend has its own; root copy has only 2 lines |
| `package-lock.json` (root) | Root-level npm lockfile (wrong location) | **DELETE** | Frontend has its own; this root one is stale |
| `test_leaf.jpg` | Test image file at root | **KEEP** | Useful reference sample for README demos |
| `run_all.bat` | Launch script for both servers | **KEEP** | Useful developer convenience script |
| `cleanup_inventory.md` | Temporary internal notes | **DELETE** | Internal working notes, not publication material |
| `greenscan_complete_functional_test.md` | Internal QA notes | **KEEP → MOVE** | Move to `docs/` |
| `README.md` | Existing README (minimal) | **REPLACE** | Will be replaced with professional version |

---

## backend/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `main.py` | FastAPI application entry point | **KEEP** | Core source |
| `config.py` | Threshold and env config | **KEEP** | Core source |
| `database.py` | SQLite persistence layer | **KEEP** | Core source |
| `disease_db.py` | Disease information catalog | **KEEP** | Core source |
| `gsa_engine.py` | GSA severity calculation | **KEEP** | Core source |
| `gradcam_engine.py` | Grad-CAM computation | **KEEP** | Core source |
| `gradcam.py` | Alternative Grad-CAM helper | **KEEP** | Core source |
| `leaf_segmenter.py` | HSV leaf segmentation | **KEEP** | Core source |
| `image_enhancer.py` | Image quality enhancement | **KEEP** | Core source |
| `recommendation_engine.py` | Disease recommendations | **KEEP** | Core source |
| `chatbot.py` | AI Chatbot integration | **KEEP** | Core source |
| `progression.py` | Disease progression forecast | **KEEP** | Core source |
| `soil.py` | Soil health advisor | **KEEP** | Core source |
| `dosage.py` | Dosage calculator | **KEEP** | Core source |
| `weather.py` | Weather risk integration | **KEEP** | Core source |
| `tips.py` | Agricultural tips | **KEEP** | Core source |
| `severity.py` | Severity helper | **KEEP** | Core source |
| `stores.py` | Store locator | **KEEP** | Core source |
| `translations.py` | Multi-language support | **KEEP** | Core source |
| `analytics.py` | Analytics helper | **KEEP** | Core source |
| `research.py` | Research endpoint | **KEEP** | Core source |
| `evaluate_greenscan.py` | Validation evaluation script | **KEEP** | Research reproducibility |
| `evaluate_gsa_calibration.py` | GSA threshold calibration | **KEEP** | Research reproducibility |
| `evaluate_robustness.py` | Robustness testing script | **KEEP** | Research reproducibility |
| `prepare_expert_annotation.py` | Expert validation prep | **KEEP** | Research reproducibility |
| `validate_expert_csv.py` | CSV validation checker | **KEEP** | Research reproducibility |
| `analyze_expert_validation.py` | Expert result analysis | **KEEP** | Research reproducibility |
| `test_e2e.py` | End-to-end test script | **KEEP** | Testing |
| `requirements.txt` | Python dependencies | **KEEP** | Required for installation |
| `.env` | Live environment file | **GITIGNORE** | May contain secrets. Already safe (placeholder values) |
| `.env.example` | Template for env variables | **KEEP** | Should be committed |
| `greenscan.db` | SQLite database file | **GITIGNORE** | Runtime-generated; contains user scan data |
| `__pycache__/` | Python bytecode cache | **GITIGNORE + DELETE** | Auto-generated, never commit |
| `model/` (inside backend) | Duplicate/old model file (.h5, 219MB) | **GITIGNORE** | `backend/model/greenscan_model.h5` is 219 MB — too large, and the canonical model is already at `model/greenscan_model.keras` |
| `venv/` (inside backend) | Nested Python venv | **GITIGNORE** | Duplicate venv inside backend |
| `#/`, `a/`, `creates/`, `environment/`, `virtual/` | Broken/stale directories | **DELETE** | Appear to be temp virtual environment remnants with no source code |

---

## frontend/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `src/` | React application source | **KEEP** | Core source |
| `public/` | Static assets | **KEEP** | Required |
| `index.html` | HTML entry point | **KEEP** | Required |
| `package.json` | NPM configuration | **KEEP** | Required |
| `package-lock.json` | NPM lockfile | **KEEP** | Should be committed for reproducible installs |
| `vite.config.js` | Vite build configuration | **KEEP** | Required |
| `.env` | Frontend env (VITE_API_BASE_URL) | **GITIGNORE** | Developer-local API URL |
| `.env.example` | Frontend env template | **KEEP** | Should be committed |
| `node_modules/` | NPM packages | **GITIGNORE** | Auto-installed; never commit |
| `dist/` | Production build output | **GITIGNORE** | Generated artifact |

---

## android/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `app/` | Android application source | **KEEP** | Source code |
| `build.gradle.kts` | Gradle build config | **KEEP** | Required |
| `settings.gradle.kts` | Gradle settings | **KEEP** | Required |
| `gradle.properties` | Gradle properties | **KEEP** | Required |
| `gradlew` / `gradlew.bat` | Gradle wrapper scripts | **KEEP** | Required for builds |
| `gradle/` | Gradle wrapper files | **KEEP** | Required |
| `local.properties` | SDK path (machine-specific) | **GITIGNORE** | Contains local SDK path — differs per machine |
| `.gradle/` | Gradle build cache | **GITIGNORE** | Auto-generated build cache |

---

## model/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `greenscan_model.keras` | **Canonical trained model (25.3 MB)** | **KEEP** | Fits GitHub's 100 MB limit; essential for reproducibility |

> ⚠️ `backend/model/greenscan_model.h5` is 219 MB — this exceeds GitHub's 100 MB file limit. It must be excluded via `.gitignore`. The `.keras` version at `model/greenscan_model.keras` is the canonical model to use.

---

## dataset/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `tomato_Early blight/` | 2,520 training images | **GITIGNORE** | Too large for GitHub; source is PlantVillage on Kaggle |
| `tomato_Late blight/` | 2,555 training images | **GITIGNORE** | Same |
| `tomato_healthy/` | 2,450 training images | **GITIGNORE** | Same |

---

## research/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `paper/` | Paper section drafts | **KEEP** | Research documentation |
| `final_results/` | Compiled CSV tables, confusion matrix | **KEEP** | Research outputs |
| `expert_annotation_task/` | Expert validation CSVs and composite images | **KEEP** | Validation package |
| `gsa_research_examples/` | GSA visual examples | **KEEP** | Research figures |
| `gsa_visualizations/` | GSA heatmap outputs | **KEEP** | Research figures |
| `research_examples/` | Example scan outputs | **KEEP** | Research figures |
| `reports/` | Report files | **KEEP** | Research documentation |
| `results/` | Experiment result files | **KEEP** | Research outputs |
| `FINAL_RESEARCH_STATUS.md` | Readiness dashboard | **KEEP** | Documentation |
| `RESEARCH_PAPER_STATUS.md` | Paper status tracker | **KEEP** | Documentation |
| `final_dataset_report.md` | Dataset documentation | **KEEP** | Documentation |
| `expert_validation_instructions.md` | Expert workflow guide | **KEEP** | Documentation |
| `expert_validation_report.md` | Validation status report | **KEEP** | Documentation |

---

## scripts/

| File / Folder | Purpose | Action | Reason |
|---|---|---|---|
| `train_disease.py` | Model training script | **KEEP** | Reproducibility |
| `predict_disease.py` | Prediction utility | **KEEP** | Reproducibility |
| `evaluate_greenscan.py` (duplicate ref) | Already in backend | **KEEP** | Used independently |
| `compile_final_results.py` | Results compilation | **KEEP** | Research pipeline |
| `balance_dataset.py` | Dataset balancing | **KEEP** | Training utility |
| `balance_dataset_v2.py` | Dataset balancing v2 | **KEEP** | Training utility |
| `model_service.py` | Model service wrapper | **KEEP** | Utility |
| `app.py` | App runner script | **KEEP** | Convenience launcher |

---

## Large File Summary

| File | Size | Action |
|---|---|---|
| `venv/` (root) | ~1+ GB (TensorFlow etc.) | **GITIGNORE** |
| `backend/venv/` | ~500 MB | **GITIGNORE** |
| `backend/model/greenscan_model.h5` | **219 MB** | **GITIGNORE** (exceeds GitHub 100MB limit) |
| `frontend/node_modules/` | ~200 MB | **GITIGNORE** |
| `dataset/` | ~2+ GB | **GITIGNORE** |
| `model/greenscan_model.keras` | **25.3 MB** | **KEEP** (under 100MB limit) |

---

## Security Summary

- No real API keys found in source code ✅
- `backend/.env` contains only placeholder value `your_openrouter_key_here` ✅  
- `frontend/.env` contains only local URL `http://127.0.0.1:8001` ✅
- `android/local.properties` contains a machine-specific SDK path — must be gitignored ✅
