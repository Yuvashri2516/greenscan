# GreenScan Experiment 1: Partial MobileNetV2 Fine-Tuning Validation Report

## 1. Executive Summary & Protocol

This report documents **Experiment 1** of the GreenScan research pipeline: **Partial Fine-Tuning of the MobileNetV2 backbone**.

### Experimental Controls:
- **Partition Evaluated**: Strictly the **Validation Split** ($N = 766$ images).
- **Held-Out Test Set**: Never accessed, loaded, or evaluated in this experiment.
- **Model Architecture**: MobileNetV2 base with top 29 layers unfrozen (layers 125..153) + GlobalAveragePooling2D + Dense(128, ReLU) + Dropout(0.5) + Dense(3, Softmax).
- **Optimization**: Adam ($	ext{lr} = 10^{-5}$), batch size $32$, categorical crossentropy, max $15$ epochs with early stopping.
- **Augmentation**: Applied only during training; validation used raw images with $1/255$ rescaling.

---

## 2. Model Parameters & Training Dynamics

- **Trainable Parameters**: 1,675,075
- **Frozen / Non-trainable Parameters**: 747,264
- **Total Parameters**: 2,422,339
- **Best Epoch**: **Epoch 12** (out of 15 trained)
- **Best Training Loss**: `0.2601` | **Best Training Accuracy**: `89.66%`
- **Best Validation Loss**: `0.2244` | **Best Validation Accuracy**: `90.86%`

---

## 3. Validation Performance Comparison

| Metric | Frozen Baseline (Val) | Fine-Tuned (Val) | Delta (Change) |
| :--- | :---: | :---: | :---: |
| **Validation Accuracy** | **90.60%** | **90.86%** | `+0.26%` |
| **Validation Macro F1** | **90.89%** | **90.86%** | `-0.03%` |
| **Early Blight Recall** | **83.33%** | **80.83%** | `-2.50%` |
| **Late Blight Recall** | **92.41%** | **95.03%** | `+2.62%` |
| **Early $\rightarrow$ Late Errors** | **33** | **37** | `+4` |
| **Late $\rightarrow$ Early Errors** | **24** | **15** | `-9` |

---

## 4. Per-Class Validation Breakdown

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **tomato_Early blight** | **92.82%** | **80.83%** | **86.41%** | 240 |
| **tomato_Late blight** | **89.63%** | **95.03%** | **92.25%** | 382 |
| **tomato_healthy** | **91.45%** | **96.53%** | **93.92%** | 144 |

---

## 5. Validation Confusion Matrix

```
                          PREDICTED
                 Early Blight   Late Blight   Healthy    Total (True)
TRUE
Early Blight         194            37            9          240
Late Blight          15             363           4          382
Healthy              0              5             139        144
Total (Predicted)    209            405           152        766
```

---

## 6. Overfitting & Stability Assessment

- **Overfitting Analysis**: Mild (validation metrics improved modestly, minimal divergence).
- **Outcome Assessment**: **MODEST IMPROVEMENT**
- **Decision Rule**: PROCEED TO HELD-OUT TEST (MARGINAL)

---

## Artifact Manifest
- `research/models/greenscan_finetuned_best.keras`
- `research/results/finetuning_history.csv`
- `research/results/finetuning_summary.json`
- `research/results/finetuning_validation_metrics.json`
- `research/results/finetuning_validation_report.md`
- `research/results/finetuning_confusion_matrix.png`
