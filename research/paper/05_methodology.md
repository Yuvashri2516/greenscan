# Methodology

## Overview

The GreenScan+ pipeline transforms a raw tomato leaf photograph into a disease classification, spatial attention visualization, relative health score, and treatment recommendation through a six-stage processing chain:

```
Raw Input Image
      ↓
1. Image Quality Assurance & Enhancement (OpenCV)
      ↓
2. Leaf Foreground Segmentation (HSV + Otsu)
      ↓
3. Disease Classification (EfficientNet-B0)
      ↓
4. Grad-CAM Activation Matrix (Gradient Backpropagation)
      ↓
5. GreenScan Severity Analyzer — GSA (Spatial Attention Statistics)
      ↓
6. Plant Health Score + Severity Tier + Recommendations
```

---

## Stage 1: Image Quality Assurance and Enhancement

**Module:** `backend/image_enhancer.py`

Before any inference, the raw image undergoes quality inspection and enhancement:

### 1.1 Blur Detection
Sharpness is estimated using the Laplacian variance operator:

```
LapVar = Var(∇²I)
```

where `∇²I` is the Laplacian of the grayscale image. Images with `LapVar < 80.0` (configurable via `BLUR_THRESHOLD`) are flagged as unreliable and trigger a safety warning in the API response.

### 1.2 Brightness Validation
Mean pixel brightness is computed over the grayscale channel:

```
B_mean = (1/N) Σ I_gray(x,y)
```

Images with `B_mean < 30.0` (too dark) or `B_mean > 230.0` (overexposed) are flagged.

### 1.3 CLAHE Contrast Enhancement
Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to the L channel in LAB colour space with `clipLimit=2.0` and `tileGridSize=(8,8)` to normalize local luminance variation.

### 1.4 Bilateral Filtering
A bilateral filter (`d=7, σ_color=50, σ_space=50`) reduces noise while preserving lesion boundary edges.

### 1.5 Resizing
The enhanced image is resized to 224×224 pixels using INTER_AREA interpolation for inference compatibility.

---

## Stage 2: Leaf Foreground Segmentation

**Module:** `backend/leaf_segmenter.py`

The leaf segmentation step isolates the leaf foreground from the image background, producing a binary mask `M(x,y) ∈ {0,1}` where 1 denotes leaf pixels.

> **Important:** This is a colour-space heuristic segmentation, **not** deep semantic segmentation. It does not label individual lesion regions — it distinguishes leaf tissue from non-leaf background.

### 2.1 HSV Dual-Range Masking
The image is converted to HSV colour space. Two colour ranges capture the full spectral range of tomato leaf tissue:

- **Green vegetation:** H ∈ [25, 95], S ∈ [25, 255], V ∈ [25, 255]
- **Necrotic brown/yellow:** H ∈ [5, 25], S ∈ [30, 255], V ∈ [20, 220]

The masks are combined via bitwise OR.

### 2.2 Otsu Thresholding
An Otsu-adaptive binary threshold on the blurred grayscale channel provides a complementary mask that captures additional leaf texture not well-characterized by colour alone. The two masks are combined via bitwise OR.

### 2.3 Morphological Cleanup
Morphological close (elliptical kernel 7×7) fills internal mask holes. Morphological open (elliptical kernel 3×3) removes small noise regions.

### 2.4 Largest Contour Selection
The largest external contour is identified using `cv2.findContours`, and only the largest contour is filled as the final leaf mask. This prevents fragmented background segments from being included.

### 2.5 Fallback Safety
If the resulting mask contains fewer than 100 pixels (e.g., extreme background crops), the entire image is used as the fallback leaf mask.

**Output:** Binary mask `M` (224×224) and leaf pixel count `N_leaf = Σ M(x,y)`.

---

## Stage 3: Disease Classification (EfficientNet-B0)

**Module:** `backend/main.py`, `model/greenscan_model.keras`

### 3.1 Architecture
The classification backbone is EfficientNet-B0, a compound-scaled CNN pre-trained on ImageNet with a custom classification head:

```
EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224,224,3))
    → GlobalAveragePooling2D
    → Dense(128, activation='relu')
    → Dropout(0.5)
    → Dense(3, activation='softmax')
```

### 3.2 Input Preprocessing
Images are normalized to `[0.0, 1.0]` by dividing pixel values by 255.0. No additional channel-level normalization is applied in the inference path.

### 3.3 Training Configuration (from `scripts/train_disease.py`)

| Parameter | Value |
|---|---|
| Optimizer | Adam |
| Loss Function | Categorical Crossentropy |
| Batch Size | 32 |
| Target Image Size | 224 × 224 |
| Maximum Epochs | 10 |
| Early Stopping | patience=5, monitor=val_loss |
| LR Reduction | factor=0.2, patience=3, min_lr=1e-6 |
| Validation Split | 20% (stratified by directory) |

> **Note:** The training script supports MobileNetV2, ResNet50, and EfficientNetB0 as selectable architectures. The deployed model (`greenscan_model.keras`) was trained with EfficientNetB0. The default in the script factory is `mobilenet`; EfficientNet is selected by passing `arch="efficientnet"`.

### 3.4 Data Augmentation (Training Only)

| Augmentation | Parameter |
|---|---|
| Rotation | ±40° |
| Width shift | ±20% |
| Height shift | ±20% |
| Shear | 20% |
| Zoom | 20% |
| Horizontal flip | Enabled |
| Vertical flip | Enabled |
| Fill mode | Nearest |

### 3.5 Classification Output
The model produces a 3-element softmax probability vector `P = [p_early, p_late, p_healthy]`. The predicted class is `argmax(P)` and confidence is `max(P) × 100%`.

---

## Stage 4: Grad-CAM Activation Matrix

**Module:** `backend/gradcam_engine.py`

Gradient-weighted Class Activation Mapping (Grad-CAM) generates a spatial attention map `A(x,y) ∈ [0,1]` indicating which image regions most influenced the predicted class.

### 4.1 Feature Extraction
A sub-model is constructed that outputs both the final convolutional layer activations `F^k(x,y)` and the final classification logits. The last `Conv2D` or `DepthwiseConv2D` layer is automatically identified by iterating reversed model layers.

### 4.2 Gradient Computation
Using TensorFlow's `GradientTape`, gradients of the target class score `y^c` with respect to the feature map activations are computed:

```
∂y^c / ∂F^k(x,y)
```

### 4.3 Importance Weights (Global Average Pooling)
Channel importance weights are obtained by globally average-pooling the gradients over the spatial dimensions:

```
α^c_k = (1/Z) Σ_x Σ_y  (∂y^c / ∂F^k(x,y))
```

### 4.4 Weighted Activation Map
The Grad-CAM heatmap is produced by computing the ReLU-rectified linear combination of activations weighted by their importance:

```
L^c_GradCAM(x,y) = ReLU( Σ_k  α^c_k · F^k(x,y) )
```

### 4.5 Normalization and Resizing
The heatmap is normalized to `[0,1]` by dividing by its maximum value (if non-zero), then bilinearly resized to 224×224 pixels using `cv2.INTER_LINEAR`.

### 4.6 Scientific Clarification
> Grad-CAM represents the model's **attention** — the spatial gradient signal that influenced the classification decision. It does **not** represent a direct segmentation of disease lesions. High activation in a region indicates that the model found that region discriminative for the predicted class; it does not confirm that physical lesion tissue occupies that precise area.

---

## Stage 5: GreenScan Severity Analyzer (GSA)

**Module:** `backend/gsa_engine.py`

The GSA converts the Grad-CAM activation matrix and the leaf segmentation mask into quantitative health metrics.

### 5.1 Leaf-Constrained Activation
Grad-CAM values outside the leaf mask are zeroed:

```
G_leaf(x,y) = A(x,y) · M(x,y)
```

### 5.2 Activation Thresholding
A binary activated mask is produced by applying threshold τ:

```
B_τ(x,y) = 1  if G_leaf(x,y) ≥ τ  and  M(x,y) = 1
           0  otherwise
```

Default: **τ = 0.60** (configurable via `GRADCAM_THRESHOLD`).

### 5.3 Attention-Affected Region Percentage

```
R_τ = (N_activated / N_leaf) × 100%

where N_activated = Σ B_τ(x,y)
      N_leaf      = Σ M(x,y)
```

This metric estimates the proportion of the leaf area over which the model's attention exceeds the threshold. It is labelled as "Estimated Attention-Affected Region" to distinguish it from a direct lesion measurement.

### 5.4 Mean Activation Statistics

```
μ_leaf     = (Σ G_leaf(x,y)) / N_leaf              [mean over all leaf pixels]
μ_activated = (Σ G_leaf(x,y) · B_τ(x,y)) / N_activated  [mean over activated pixels only]
```

### 5.5 Plant Health Score (PHS)

**Diseased leaves:**
```
PHS = 100 − (w_area × R_τ + w_act × μ_activated × 100)

where w_area = 0.60  (AREA_WEIGHT)
      w_act  = 0.40  (ACTIVATION_WEIGHT)
PHS = clip(round(PHS), 0, 100)
```

**Healthy leaves:**
```
PHS = 100 − (μ_leaf × 5.0)
PHS = clip(round(PHS), 0, 100)
```

The healthy branch uses only mean leaf activation rather than the diseased formula, reflecting that healthy-class Grad-CAM activations represent general leaf-texture attention rather than disease-feature discrimination.

### 5.6 Severity Tier Classification

| PHS Range | Severity Label | Traffic Code | Risk Level |
|---|---|---|---|
| ≥ 90 (or healthy class) | Healthy | GREEN | None |
| 70 – 89 | Mild | YELLOW | Low |
| 40 – 69 | Moderate | ORANGE | Medium |
| < 40 | Severe | RED | High / Critical |

---

## Stage 6: Recommendation Engine

**Module:** `backend/recommendation_engine.py`, `backend/disease_db.py`

Disease-specific treatment recommendations are retrieved from the static knowledge base (`DISEASE_DB`) keyed by predicted class label. Recommendations cover:
- Preventive cultural practices
- Organic biological controls
- Chemical fungicide options with dosage guidance

In low-reliability cases (blurry images, confidence < 0.65), the recommendation engine returns a safety warning and image quality improvement guidance instead of treatment advice.

---

## Supporting Components

| Component | Module | Function |
|---|---|---|
| Progression Forecast | `progression.py` | 7-day disease spread projection |
| Soil Health Advisor | `soil.py` | NPK-based soil diagnostic |
| Dosage Calculator | `dosage.py` | Fungicide volume calculation |
| AI Chatbot | `chatbot.py` | Contextual advisory (OpenRouter API) |
| Scan History | `database.py` | SQLite persistence |
| Web API | `main.py` | FastAPI REST gateway |
| Web Frontend | `frontend/src/` | React + Vite SPA |
