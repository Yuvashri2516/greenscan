# GreenScan+

> AI-powered tomato leaf disease classification and plant health severity estimation system with explainable Grad-CAM visualization.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Overview

GreenScan+ is a full-stack agricultural decision support system built for real-world tomato crop disease management. Farmers and agronomists can photograph a tomato leaf, upload it to GreenScan+, and instantly receive:

- An AI-driven disease classification (Healthy / Early Blight / Late Blight)
- Explainable heatmap visualization (Grad-CAM) showing which regions influenced the prediction
- A relative Plant Health Score (0–100) derived from spatial attention analysis
- Targeted organic and chemical treatment recommendations
- Scan history tracking, soil diagnostics, dosage calculations, and an AI chatbot advisor

The system is designed for transparency. Severity estimates are clearly framed as **AI-attention-derived indicators**, not direct physical lesion measurements.

---

## Key Features

| Feature | Status |
|---|---|
| Tomato disease classification (3 classes) | ✅ Working |
| EfficientNet-B0 deep learning backbone | ✅ Working |
| Grad-CAM explainability heatmaps | ✅ Working |
| HSV-based leaf segmentation | ✅ Working |
| GreenScan Severity Analyzer (GSA) | ✅ Working |
| Plant Health Score (0–100) | ✅ Working |
| Disease information catalog | ✅ Working |
| Organic & chemical treatment recommendations | ✅ Working |
| Scan history with SQLite persistence | ✅ Working |
| AI Chatbot advisor | ✅ Working |
| Soil health advisor | ✅ Working |
| Dosage calculator | ✅ Working |
| Downloadable HTML diagnostic reports | ✅ Working |
| Disease progression forecast | ✅ Working |
| Responsive React web interface | ✅ Working |
| Android Kotlin application | ⚠️ Source complete; SDK testing environment blocked |

---

## Supported Diseases

GreenScan+ currently classifies three conditions in **tomato leaves only**:

| Class Label | Display Name | Type |
|---|---|---|
| `tomato_healthy` | Tomato Healthy | Baseline — no disease |
| `tomato_Early blight` | Tomato Early Blight | *Alternaria solani* fungal infection |
| `tomato_Late blight` | Tomato Late Blight | *Phytophthora infestans* oomycete infection |

> ⚠️ GreenScan+ is **not** validated for any other plant species or disease classes. Do not use it to diagnose pepper, potato, or other crops.

---

## System Architecture

```
User
 ↓
React Frontend (Vite)
 ↓
FastAPI Backend (Python)
 ↓
Image Quality Enhancement (OpenCV — CLAHE, blur detection, bilateral filter)
 ↓
Leaf Segmentation (HSV colour-space masking, contour extraction)
 ↓
EfficientNet-B0 Classification (TensorFlow/Keras)
 ↓
Grad-CAM Activation Matrix (backpropagation through final conv layer)
 ↓
GreenScan Severity Analyzer (GSA — spatial attention statistics)
 ↓
Disease DB / Recommendation Engine / Chatbot / Soil / Dosage
 ↓
SQLite Persistence
 ↓
JSON Response → Frontend Results UI
```

---

## Technology Stack

### Frontend
- **React 19** with React Router DOM
- **Vite 8** (dev server + build)
- **Framer Motion** (animations)
- **Lucide React** (icons)
- Vanilla CSS with CSS custom properties

### Backend
- **Python 3.10+**
- **FastAPI** + **Uvicorn** (ASGI server)
- **TensorFlow 2.x** / **Keras** (model inference)
- **OpenCV** (image processing, Grad-CAM, leaf segmentation)
- **NumPy**, **Pillow**, **SciPy**
- **SQLite** (scan history persistence)
- **python-dotenv** (environment configuration)

### Machine Learning
- **EfficientNet-B0** (fine-tuned classification backbone)
- **Grad-CAM** (Gradient-weighted Class Activation Mapping)
- Custom **GreenScan Severity Analyzer (GSA)** pipeline

### Android
- **Kotlin** + Android Jetpack architecture
- Retrofit for REST API communication
- CameraX for live capture

---

## Project Structure

```
Greenscan project/
│
├── backend/                    # FastAPI Python API
│   ├── main.py                 # Application entry point + all routes
│   ├── config.py               # Threshold & environment configuration
│   ├── gsa_engine.py           # GreenScan Severity Analyzer
│   ├── gradcam_engine.py       # Grad-CAM computation
│   ├── leaf_segmenter.py       # HSV leaf segmentation
│   ├── image_enhancer.py       # Quality enhancement pipeline
│   ├── disease_db.py           # Disease information catalog
│   ├── recommendation_engine.py
│   ├── chatbot.py
│   ├── database.py             # SQLite persistence
│   ├── dosage.py
│   ├── soil.py
│   ├── progression.py
│   ├── weather.py
│   ├── requirements.txt
│   ├── .env.example
│   └── [evaluation & research scripts]
│
├── frontend/                   # React + Vite web application
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page views
│   │   ├── api/                # API client
│   │   ├── hooks/              # Custom React hooks
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── android/                    # Kotlin Android application
│   ├── app/src/main/java/com/greenscan/
│   └── [Gradle build files]
│
├── model/
│   └── greenscan_model.keras   # Trained EfficientNet-B0 (25.3 MB)
│
├── dataset/                    # Training images (gitignored — see Dataset section)
│   ├── tomato_Early blight/    # 2,520 images
│   ├── tomato_Late blight/     # 2,555 images
│   └── tomato_healthy/         # 2,450 images
│
├── scripts/                    # Training, evaluation, utility scripts
│   ├── train_disease.py
│   ├── evaluate_robustness.py
│   ├── compile_final_results.py
│   └── [other utilities]
│
├── research/                   # Research documentation & results
│   ├── paper/                  # Paper section drafts
│   ├── final_results/          # Compiled metrics, CSVs, confusion matrix
│   ├── expert_annotation_task/ # Expert validation package
│   └── [status & reports]
│
├── docs/                       # Project documentation
│   ├── TESTING.md
│   └── screenshots/
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
└── run_all.bat                 # Windows convenience launcher
```

---

## Installation

### Prerequisites

- **Python 3.10+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org)
- **Git** — [git-scm.com](https://git-scm.com)

### 1. Clone the Repository

```powershell
git clone https://github.com/your-username/greenscan.git
cd "greenscan"
```

### 2. Backend Setup

```powershell
# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r backend/requirements.txt

# Also install TensorFlow (required for model inference)
pip install tensorflow
```

### 3. Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

**Backend:**
```powershell
Copy-Item backend\.env.example backend\.env
```
Edit `backend/.env`:
```env
OPENROUTER_API_KEY=your_openrouter_key_here   # Optional: for AI chatbot
FRONTEND_URL=http://localhost:5173
```

**Frontend:**
```powershell
Copy-Item frontend\.env.example frontend\.env
```
Edit `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

---

## Running the Application

### Start Backend

```powershell
# From project root, with venv activated
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8001
```

Backend runs at: **http://127.0.0.1:8001**  
API documentation: **http://127.0.0.1:8001/docs**

> If port 8001 is occupied, change to `--port 8002` and update `frontend/.env` accordingly.

### Start Frontend

```powershell
cd frontend
npm run dev
```

Frontend runs at: **http://127.0.0.1:5173**

### Quick Start (Windows — both servers)

```powershell
.\run_all.bat
```

---

## Dataset

The training dataset is **not included** in this repository due to its size (~2 GB, 7,525 images).

**Download from Kaggle:**
> [PlantVillage Dataset — Tomato Classes](https://www.kaggle.com/datasets/emmarex/plantdisease)

After downloading, place images in:
```
dataset/
├── tomato_Early blight/   ← paste Early_Blight images here
├── tomato_Late blight/    ← paste Late_Blight images here
└── tomato_healthy/        ← paste Tomato_healthy images here
```

The trained model (`model/greenscan_model.keras`) is included in the repository and does **not** require re-training.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API health and project info |
| `GET` | `/health` | Model load status |
| `POST` | `/predict` | Upload leaf image → full diagnosis |
| `GET` | `/history` | Retrieve recent scan history |
| `GET` | `/export-research` | Export scan history as CSV |
| `GET` | `/disease` | Disease catalog (optional `?name=` filter) |
| `POST` | `/chat` | AI chatbot query |
| `GET` | `/tips` | Agricultural tips |
| `GET` | `/weather` | Weather risk (requires `?lat=&lon=`) |
| `POST` | `/dosage` | Fungicide dosage calculation |
| `POST` | `/soil-health` | Soil NPK health analysis |

Full interactive API docs available at `/docs` (Swagger UI) when the backend is running.

---

## Machine Learning Model

### Architecture
- **Base:** EfficientNet-B0 (ImageNet pre-trained, fine-tuned on PlantVillage tomato subset)
- **Input:** 224 × 224 × 3 RGB images (normalized to [0, 1])
- **Output:** 3-class softmax probability vector
- **Training:** Adam optimizer, categorical crossentropy, 10 epochs, batch size 32

### Classification Performance (Validation Set — 1,505 images)

| Metric | Score |
|---|---|
| Overall Accuracy | **91.76%** |
| Macro Precision | 91.95% |
| Macro Recall | 91.83% |
| Macro F1-Score | 91.68% |

### Grad-CAM Explainability
Gradient-weighted Class Activation Mapping (Grad-CAM) generates a spatial attention heatmap indicating which pixel regions most influenced the model's classification. This heatmap is overlaid on the leaf image for user interpretation.

---

## Severity Estimation (GSA)

The **GreenScan Severity Analyzer (GSA)** converts the Grad-CAM activation matrix into a relative **Plant Health Score (PHS)** on a 0–100 scale.

### How It Works

1. Apply activation threshold τ = 0.60 to the Grad-CAM matrix
2. Count activated pixels within the leaf mask (HSV segmented)
3. Compute attention-affected region %
4. Calculate mean activation intensity within activated regions
5. Apply weighted formula:

**Diseased leaf:**
```
PHS = 100 − (0.60 × affected_region% + 0.40 × mean_activation × 100)
```

**Healthy leaf:**
```
PHS = 100 − (mean_leaf_activation × 5.0)
```

### Severity Tiers

| PHS Range | Severity | Treatment Priority |
|---|---|---|
| 80–100 | Healthy | None |
| 60–79 | Mild | Monitor |
| 40–59 | Moderate | Treat Soon |
| 0–39 | Severe | Urgent |

> ⚠️ **Scientific Disclaimer:** PHS is an AI-attention-derived relative indicator based on Grad-CAM spatial gradients, not a direct measurement of physical lesion area or biological infection severity. It should not be treated as a clinical measurement without expert validation.

---

## Research Validation

### Classification Validation
Evaluated on a held-out 20% validation split (1,505 images), achieving **91.76% overall accuracy**.

### GSA Validation
Threshold sensitivity analysis performed across τ ∈ {0.40, 0.50, 0.60, 0.70, 0.80}.  
Default τ = 0.60 selected based on empirical severity class distribution.

### Expert Validation
An expert annotation campaign has been prepared (90 composite images + structured CSV).  
**Status: PENDING** — Expert pathologist annotations have not yet been completed.  
Agreement metrics (Spearman correlation, Cohen's Kappa) cannot be reported until expert labels are collected.

### Pixel-Level Validation
No pixel-level lesion ground-truth segmentation masks exist in the dataset.  
**Intersection over Union (IoU) is not calculated.**

Full details: [`research/final_results/final_validation_report.md`](research/final_results/final_validation_report.md)

---

## Robustness Testing

Model performance was evaluated under 9 real-world degradation conditions (30 samples each):

| Condition | Accuracy |
|---|---|
| Normal | 93.33% |
| Overexposed | 96.67% |
| Uneven Lighting | 86.67% |
| Partial Leaf | 86.67% |
| Rotated | 80.00% |
| Small Portion | 80.00% |
| Dark Illumination | 73.33% |
| Low Resolution | 66.67% |
| Slightly Blurred | 46.67% |

The model is robust to brightness variation but susceptible to heavy blur and low-resolution compression.

---

## Limitations

1. **Disease scope is limited:** Only 3 tomato classes are supported. Other plants and diseases are not classified.
2. **Grad-CAM is attention, not segmentation:** Heatmaps show model focus regions, not physical lesion boundaries.
3. **Severity is a relative indicator:** PHS does not correlate directly with biological infection severity without expert validation.
4. **Expert validation pending:** Disease/severity agreement with agricultural pathologists has not been completed.
5. **No pixel-level masks:** IoU validation is not available for this dataset.
6. **Blur sensitivity:** Model accuracy drops to ~46% under out-of-focus conditions — users should ensure sharp images.
7. **Android status:** Kotlin source code is complete; testing requires an Android SDK environment and device/emulator.
8. **Single-class per image:** The system classifies one condition per image — multi-infection detection is not supported.
9. **Chatbot responses depend on OpenRouter API:** Without an API key, chatbot falls back to a rule-based mode.

---

## Screenshots

> Screenshots of the live application are available in [`docs/screenshots/`](docs/screenshots/).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup, branch workflow, and pull request expectations.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Citation

If you use GreenScan+ in academic work, please cite:

```
GreenScan+: Explainable Deep Learning for Tomato Disease Classification and 
Severity Estimation using Grad-CAM and EfficientNet-B0.
[Authors], [Year].
```

---

## Acknowledgements

- [PlantVillage Dataset](https://plantvillage.psu.edu/) — Training data source
- [TensorFlow / Keras](https://tensorflow.org) — Model training and inference
- [OpenCV](https://opencv.org) — Image processing pipeline
- [FastAPI](https://fastapi.tiangolo.com) — Backend API framework
- [React](https://react.dev) — Frontend framework
