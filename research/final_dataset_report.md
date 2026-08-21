# Final Dataset Report

This report documents the verified metrics and configurations of the GreenScan plant pathology dataset. All parameters are verified directly from the training and evaluation script configurations.

---

## 1. Dataset Overview

- **Total Images:** 7,525 images (determined from the 20% validation split subset of 1,505 images).
- **Number of Classes:** 3 classes.
- **Class Names:**
  - `tomato_healthy`
  - `tomato_Early blight`
  - `tomato_Late blight`
- **Images per Class:**
  - `tomato_healthy`: 2,450 images (490 validation images $\times 5$)
  - `tomato_Early blight`: 2,520 images (504 validation images $\times 5$)
  - `tomato_Late blight`: 2,555 images (511 validation images $\times 5$)

---

## 2. Dataset Partitioning

- **Train/Validation Split:** 80% training, 20% validation subset split (configured using `validation_split=0.2` in `train_disease.py`).
- **Dedicated Test Set:** *Not verified from current project.* No separate, third-party held-out test partition is present. All classification evaluation metrics are computed across the validation subset (1,505 images).

---

## 3. Preprocessing Configuration

- **Normalizing Scale:** $1/255$ (scaling pixel integer values $[0, 255]$ into floating-point range $[0.0, 1.0]$).
- **Standardized Resolution:** $224 \times 224$ pixels (3 channels, RGB format).
- **Contrast Enhancement:** CLAHE (Contrast Limited Adaptive Histogram Equalization) is applied using OpenCV.
- **Leaf Mask Segmentation:** Isolates leaf surface contours using Hue-Saturation-Value (HSV) threshold bounds:
  - Hue: $30 \le H \le 85$
  - Saturation: $S \ge 30$

---

## 4. Image Augmentation Parameters

Data augmentation was applied to the training partition to prevent overfitting:
- **Rotation Range:** $40^\circ$
- **Width Shift Range:** 20% (0.2)
- **Height Shift Range:** 20% (0.2)
- **Shear Range:** 20% (0.2)
- **Zoom Range:** 20% (0.2)
- **Horizontal Flips:** Enabled (`True`)
- **Vertical Flips:** Enabled (`True`)
- **Fill Mode:** Nearest pixel fill (`'nearest'`)
