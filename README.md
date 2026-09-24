# GreenScan — Decision Support System for Tomato Leaf Disease Diagnosis

> Explainable deep learning and computer vision framework for tomato foliar disease identification and health assessment.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-FF6F00?logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 1. Project Overview

GreenScan is a full-stack agricultural decision support system engineered for tomato (*Solanum lycopersicum*) foliar pathology. It combines deep convolutional feature extraction with post-hoc explainability (Grad-CAM), disease management recommendations, and an interactive agronomic dashboard.

### Core Capabilities:
- **Diagnostic Classification**: Tri-class identification covering Tomato Healthy, Early Blight (*Alternaria solani*), and Late Blight (*Phytophthora infestans*).
- **Post-Hoc Explainability**: Gradient-Weighted Class Activation Mapping (Grad-CAM) highlighting salient visual feature regions.
- **Agronomic Action Guidance**: Context-aware organic, chemical, and cultural disease management recommendations.
- **Full-Stack Implementation**: FastAPI backend paired with a high-performance React (Vite) user interface.

---

## 2. Research Benchmark & Final Model

Following controlled research experiments and rigorous group-stratified data splitting, the final verified model is **EfficientNetB0** (frozen ImageNet backbone).

### Verified Held-Out Test Performance ($N = 770$ Images | $511$ Physical Leaf Groups):
- **Overall Accuracy**: **91.95%** ($708 / 770$ correct)
- **Macro Precision**: **91.93%**
- **Macro Recall**: **93.05%**
- **Macro F1-Score**: **92.46%**
- **Weighted F1-Score**: **91.92%**

| Class | Support ($N$) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **`tomato_Early blight`** | 243 | **89.21%** | **88.48%** | **88.84%** |
| **`tomato_Late blight`** | 382 | **93.07%** | **91.36%** | **92.21%** |
| **`tomato_healthy`** | 145 | **93.51%** | **99.31%** | **96.32%** |

---

## 3. Project Structure

```text
C:\Greenscan project
├── backend/                  # FastAPI backend application
│   ├── main.py               # API endpoints & route handlers
│   ├── model_service.py      # Core inference & Grad-CAM engine
│   ├── disease_db.py         # Pathology knowledge base & treatment logic
│   └── ...
├── frontend/                 # React 19 + Vite web interface
│   ├── src/                  # React components, pages, state
│   ├── package.json          # Frontend dependencies
│   └── ...
├── android/                  # Android mobile application source
├── dataset/                  # Curated dataset partitions
├── evaluation/               # Audited splits & dataset manifests
│   ├── clean_split_manifest.csv
│   └── clean_split_summary.json
├── research/                 # Research models, results & frozen benchmarks
│   ├── models/               # Frozen model checkpoints (.keras)
│   ├── results/              # Experiment metrics, predictions, CSVs, reports
│   ├── FINAL_MODEL_FREEZE.md # Official research freeze record
│   └── final_model_metadata.json
├── scripts/                  # Reproducible training & evaluation pipelines
│   ├── train_efficientnetb0.py
│   ├── evaluate_efficientnetb0_test.py
│   └── ...
├── docs/                     # Comprehensive scientific documentation
│   ├── methodology.md        # Research methodology & design
│   ├── reproducibility.md    # Environment & step-by-step reproduction
│   ├── experiment_comparison.md # Controlled experiment matrices
│   ├── error_analysis.md     # In-depth test misclassification study
│   └── limitations.md        # Operational boundaries & cautions
├── requirements.txt          # Python runtime dependencies
└── README.md                 # Project documentation
```

---

## 4. Quick Start: Running Locally

### 4.1 Backend Setup (FastAPI)
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# Start backend server
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Backend API will be accessible at `http://127.0.0.1:8000` (Swagger docs at `/docs`).

### 4.2 Frontend Setup (React / Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start development server
npm run dev
```
Frontend web interface will be accessible at `http://localhost:5173`.

---

## 5. Research Reproduction

To reproduce the data partitioning, training, and one-pass test evaluation:

```bash
# 1. Generate clean, group-disjoint splits
python evaluation/create_clean_split.py

# 2. Train the final EfficientNetB0 model
python scripts/train_efficientnetb0.py

# 3. Run the final held-out test evaluation
python scripts/evaluate_efficientnetb0_test.py
```

For complete technical specifications, see [`docs/reproducibility.md`](file:///c:/Greenscan%20project/docs/reproducibility.md).

---

## 6. Research Documentation Suite

- **[Methodology Guide](file:///c:/Greenscan%20project/docs/methodology.md)**: Details problem definition, group-stratified sampling, data augmentation, and experimental procedures.
- **[Experiment Comparison](file:///c:/Greenscan%20project/docs/experiment_comparison.md)**: Controlled benchmark matrix comparing Experiments 1–4 against baseline.
- **[Error Analysis & Interpretability](file:///c:/Greenscan%20project/docs/error_analysis.md)**: Analysis of the 62 test misclassifications, Early $\leftrightarrow$ Late confusion, and Grad-CAM explanations.
- **[Research Limitations](file:///c:/Greenscan%20project/docs/limitations.md)**: Detailed examination of crop scope, environmental domain shift, and operational constraints.
- **[Final Research Summary](file:///c:/Greenscan%20project/research/FINAL_RESEARCH_SUMMARY.md)**: High-level executive summary of project findings.

---

## 7. Operational Scope & Limitations

1. **Tomato Crop Scope**: The model is validated specifically on tomato leaves (*Solanum lycopersicum*) and should not be used on other crops.
2. **Tri-Class Diagnostic Domain**: GreenScan evaluates Tomato Healthy, Early Blight, and Late Blight. It does not diagnose other conditions (e.g., *Septoria*, bacterial spot, viruses).
3. **Decision-Support Heuristic**: Predictions are designed to serve as an assistive decision-support aid. They do not replace formal laboratory phytopathological assays or in-person agronomic inspections.
4. **Uncalibrated Confidence**: Softmax output values reflect relative model logits and should not be interpreted as calibrated biological probabilities.
