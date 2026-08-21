# Experimental Setup

## Dataset

**Source:** PlantVillage dataset (publicly available from Kaggle: https://www.kaggle.com/datasets/emmarex/plantdisease)

| Class Label | Disease | Image Count |
|---|---|---|
| `tomato_Early blight` | *Alternaria solani* | 2,520 |
| `tomato_Late blight` | *Phytophthora infestans* | 2,555 |
| `tomato_healthy` | No disease | 2,450 |
| **Total** | | **7,525** |

**Train/Validation Split:** 80% / 20% stratified split using `ImageDataGenerator(validation_split=0.2)` from TensorFlow/Keras. Shuffle is disabled on the validation generator to ensure reproducible per-image evaluation.

**Validation Partition Sizes:**
- `tomato_Early blight`: 504 images
- `tomato_Late blight`: 511 images
- `tomato_healthy`: 490 images
- **Total validation images: 1,505**

**Image Properties:**
- Resolution standardized to 224 × 224 pixels
- Colour mode: RGB
- Pixel normalization: divide by 255.0 → [0.0, 1.0]

**Dataset Notes:** PlantVillage images are acquired under controlled laboratory conditions with uniform background. Performance under field conditions (variable lighting, outdoor backgrounds, motion blur) may differ and is partially addressed in robustness testing (Section: Robustness Experiments).

---

## Model Training Environment

| Parameter | Value |
|---|---|
| Framework | TensorFlow 2.x / Keras |
| Python Version | 3.10+ |
| Backbone | EfficientNetB0 (ImageNet pre-trained) |
| Optimizer | Adam |
| Loss | Categorical Crossentropy |
| Batch Size | 32 |
| Max Epochs | 10 |
| Early Stopping | patience=5, restore_best_weights=True |
| LR Reduction | factor=0.2, patience=3, min_lr=1e-6 |

**Hardware:** Not documented in current implementation. Training was completed on local workstation hardware. Specific GPU model, VRAM, and training duration are not available from the current record.

---

## Inference Environment

| Component | Value |
|---|---|
| Backend Framework | FastAPI (Python) |
| ASGI Server | Uvicorn |
| API Port | 8001 |
| OpenCV Version | Installed via `opencv-python-headless` |
| NumPy / Pillow | System versions (requirements.txt) |
| Frontend | React 19 + Vite 8 |
| Database | SQLite (scan history) |

**Inference Latency (Warm, measured on development hardware):**

| Sub-system | Latency |
|---|---|
| HSV Leaf Segmentation | ~0.15 s |
| CNN Forward Pass | ~0.45 s |
| Grad-CAM Backpropagation | ~0.48 s |
| GSA + Logging | ~0.11 s |
| **Total (Warm)** | **~1.19 s** |

First (cold) inference time: ~2.84 s (model load + JIT compilation).

---

## Classification Evaluation Protocol

The trained model was evaluated on the 1,505-image validation partition using the following protocol:

1. Each image was passed through the full preprocessing pipeline (quality check, CLAHE, bilateral filter, resize).
2. The enhanced image was classified using the model.
3. `sklearn.metrics` was used to compute accuracy, precision, recall, F1-score, and the confusion matrix against ground-truth labels.
4. Metrics are reported at macro-average (unweighted) and weighted-average levels.

---

## GSA Evaluation Protocol

GSA metrics were computed for 30 validation samples per disease class (n = 90 total) selected from the validation partition, covering:
- Mean attention-affected region percentage
- Mean Plant Health Score
- Severity tier distribution

Threshold sensitivity was evaluated across τ ∈ {0.40, 0.50, 0.60, 0.70, 0.80} over the same 90-sample subset.

---

## Robustness Testing Protocol

Nine imaging degradation conditions were tested (n = 30 samples per condition, 270 total):

| Condition | Degradation Applied |
|---|---|
| A. Normal | No degradation |
| B. Low Resolution | Downsampled to 32×32, then upsampled back |
| C. Slightly Blurred | Gaussian blur kernel (σ=2) |
| D. Dark | Brightness reduced by 60% |
| E. Overexposed | Brightness increased to near-saturation |
| F. Uneven Lighting | Simulated gradient illumination |
| H. Partial Leaf | Centre crop (75% of image) |
| I. Rotated | 30° rotation with border padding |
| K. Small Portion | Extreme centre crop (40% of image) |

---

## Expert Validation Setup

90 composite validation images were prepared (30 per class) via `backend/prepare_expert_annotation.py`. Each composite shows: original leaf, Grad-CAM heatmap overlay, activation mask, and GreenScan output.

The expert annotation CSV (`research/expert_annotation_task/gsa_expert_validation.csv`) contains columns:
- `image_id`, `predicted_disease`, `model_confidence`, `estimated_attention_affected_region`, `weighted_activation`, `green_scan_health_score`, `green_scan_severity`
- **Expert columns (to be filled):** `expert_disease`, `expert_severity`, `expert_comments`

**Status at time of writing:** Expert annotation columns are blank. Statistical agreement analysis (Cohen's Kappa, Spearman correlation) cannot be performed until expert labels are collected.
