# Experiments

This section documents the experimental configuration, dataset, image preprocessing, and training hyper-parameters used to compile the GreenScan classification model.

---

## 1. Dataset Characteristics

The model was evaluated using a 20% validation subset containing 1,505 images. This validation set was extracted from the master dataset directory, which contains:
- **`tomato_healthy`:** 490 validation images (representing a total of 2,450 images)
- **`tomato_Early blight`:** 504 validation images (representing a total of 2,520 images)
- **`tomato_Late blight`:** 511 validation images (representing a total of 2,555 images)
- **Total Dataset Size:** 7,525 images.

---

## 2. Image Preprocessing and Augmentation

Data augmentation was applied to the training subset to improve generalization and robustness under field conditions:
- **Rescaling Factor:** $1/255$ (normalizes pixel values to $[0.0, 1.0]$)
- **Image Target Dimensions:** $224 \times 224$ pixels
- **Validation Split:** 20% (split seed kept consistent using Keras flow generators)
- **Rotation Range:** $40^\circ$
- **Width Shift Range:** 20% (0.2)
- **Height Shift Range:** 20% (0.2)
- **Shear Intensity Range:** 20% (0.2)
- **Zoom Range:** 20% (0.2)
- **Horizontal Flips:** Enabled (`True`)
- **Vertical Flips:** Enabled (`True`)
- **Fill Mode:** Nearest pixel fill (`'nearest'`)

---

## 3. Training Configuration

The model factory and training loop were executed under the following hyper-parameters:
- **Backbone Architecture:** MobileNetV2 (standard model compiled and saved in `train_disease.py`), with EfficientNet-B0 supported as a compound-scaled CNN backbone candidate.
- **Batch Size:** 32 (validation batch size is 32 during training evaluation, and evaluated with batch size 1 during Grad-CAM analysis pipeline checks)
- **Loss Function:** Categorical Crossentropy (for multi-class classification)
- **Optimizer:** Adam
- **Initial Epoch Limit:** 10 epochs
- **Callbacks:**
  - **Early Stopping:** Monitored `val_loss` with a patience of 5 epochs (restoring the weights from the best epoch).
  - **Reduce Learning Rate on Plateau (ReduceLROnPlateau):** Monitored `val_loss` with a factor of 0.2, a patience of 3 epochs, and a minimum learning rate threshold of $1 \times 10^{-6}$.
