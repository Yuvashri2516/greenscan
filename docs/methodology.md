# GreenScan — Research Methodology

## 1. Problem Definition

GreenScan addresses automated foliar disease identification and health assessment in tomato crops (*Solanum lycopersicum*). The classification task is defined over three primary diagnostic categories:
1. **Tomato Early Blight** (*Alternaria solani*) — fungal pathogen causing dark, necrotic concentric-ring foliar lesions.
2. **Tomato Late Blight** (*Phytophthora infestans*) — oomycete pathogen causing rapidly spreading, water-soaked, irregular necrotic foliar blights.
3. **Tomato Healthy** — asymptomatic foliar tissue exhibiting normal physiological coloration and venation.

The central research challenge identified in preliminary diagnostic studies was **inter-disease confusion between Early Blight and Late Blight**, which accounted for more than 80% of all baseline classification errors due to visual similarities between late-stage necrotic lesions.

---

## 2. Dataset Preparation & Leakage Prevention

To ensure scientific validity and prevent overly optimistic generalization claims, the raw dataset underwent an extensive audit:
1. **Cryptographic Duplicate Audit**: Applied SHA-256 hash detection to identify exact duplicate files across the repository. Eleven duplicate files were flagged and excluded from all model partitions.
2. **Physical Leaf Identification**: Analysis of image filenames and masked counterparts indicated that multiple photographs frequently originated from the same physical leaf specimen under varying lighting, background masking, and orientations.
3. **Group Disjoint Partitioning**: Images were clustered by `physical_leaf_id` ($3,328$ clusters). All splits were performed at the physical leaf cluster level rather than the image level to guarantee **zero subject leakage** between training, validation, and testing cohorts.

---

## 3. Group-Stratified Data Splitting Protocol

The dataset was partitioned using a **70% / 15% / 15%** group-stratified protocol:
- **Training Partition**: $3,588$ images ($2,314$ physical leaf groups)
- **Validation Partition**: $766$ images ($503$ physical leaf groups)
- **Held-Out Test Partition**: $770$ images ($511$ physical leaf groups)

Group disjointness was strictly maintained: no physical leaf group or image appears in more than one partition.

---

## 4. Online Data Augmentation

Data augmentation was applied exclusively during training to enhance invariance against geometric and photometric variations:
- Random rotation: $\pm 40^\circ$
- Horizontal and vertical shifts: $\pm 20\%$
- Shear transformation: $\pm 20\%$
- Random zoom: $[0.8, 1.2]$
- Horizontal and vertical flips: enabled
- Validation and testing pipelines remained strictly unaugmented.

---

## 5. Baseline Architecture (MobileNetV2)

The baseline model utilized a transfer learning setup:
- **Backbone**: MobileNetV2 (ImageNet pretrained weights, fully frozen backbone).
- **Classification Head**: `GlobalAveragePooling2D` $\rightarrow$ `Dense(128, ReLU)` $\rightarrow$ `Dropout(0.5)` $\rightarrow$ `Dense(3, Softmax)`.
- **Training Config**: Adam optimizer ($\text{initial lr} = 0.001$), Categorical Cross-Entropy, batch size 32, max 15 epochs, ReduceLROnPlateau (factor 0.2, patience 3), EarlyStopping (patience 5).
- **Baseline Validation Performance**: Accuracy $90.60\%$, Macro F1 $90.89\%$, Early Blight Recall $83.33\%$, Early $\leftrightarrow$ Late Errors: $57$.

---

## 6. Experimental Interventions (Controlled Studies)

Four single-variable experiments were conducted on the validation cohort ($N = 766$) to resolve Early $\leftrightarrow$ Late Blight confusion:

### Experiment 1: Partial MobileNetV2 Fine-Tuning
- **Hypothesis**: Allowing the top convolutional layers of MobileNetV2 to adapt to plant pathology features would improve lesion feature separation.
- **Intervention**: Unfroze top 29 layers of MobileNetV2 with low learning rate ($\text{lr} = 10^{-5}$).
- **Outcome**: Validation accuracy $90.86\%$, Macro F1 $90.86\%$, Early Blight recall dropped to $80.83\%$. **Result: Not Sufficient**.

### Experiment 2: Class-Weighted Training
- **Hypothesis**: Applying inverse class frequency weighting ($1.057, 0.671, 1.774$) would compensate for the $1.58 : 1$ Late-to-Early class imbalance.
- **Intervention**: Applied balanced class weights during categorical cross-entropy optimization.
- **Outcome**: Validation accuracy $89.95\%$, Macro F1 $90.46\%$, Early $\leftrightarrow$ Late errors increased to $64$. **Result: Not Sufficient** (shifts decision threshold without enhancing feature separability).

### Experiment 3: Higher-Resolution Training (384×384)
- **Hypothesis**: Increasing spatial input resolution from $224 \times 224$ to $384 \times 384$ would preserve high-frequency concentric ring textural detail.
- **Intervention**: Input resolution scaled to $384 \times 384$, batch size adjusted to 16.
- **Outcome**: Validation accuracy $89.82\%$, Macro F1 $90.29\%$, Early $\leftrightarrow$ Late errors increased to $63$. **Result: Not Sufficient**.

### Experiment 4: EfficientNetB0 Feature Extractor
- **Hypothesis**: Squeeze-and-excitation channel attention modules within EfficientNetB0's MBConv blocks would adaptively recalibrate feature responses to distinguish concentric rings from diffuse necrosis.
- **Intervention**: Replaced frozen MobileNetV2 backbone with frozen EfficientNetB0 backbone ($224 \times 224$).
- **Outcome**: Validation accuracy **$93.08\%$** ($+2.48\%$), Macro F1 **$93.18\%$** ($+2.30\%$), Early Blight recall **$89.17\%$** ($+5.83\%$), Early $\leftrightarrow$ Late errors **$39$** (down by $31.6\%$). **Result: Strong, balanced improvement**.

---

## 7. Model Selection Protocol

Model selection was conducted strictly on the validation partition prior to accessing the held-out test partition. EfficientNetB0 (Checkpoint Epoch 15) was selected as the final model candidate based on superior validation Macro F1, Early Blight recall, and inter-disease error reduction.

---

## 8. Final Held-Out Test Protocol

The held-out test partition ($N = 770$ images, $511$ physical leaf groups) was accessed **strictly once**:
- **Test Integrity**: Zero subject leakage confirmed; unaugmented images; pre-selected frozen checkpoint evaluated without retraining, fine-tuning, or threshold modification.
- **Final Test Performance**:
  - Accuracy: **$91.95\%$** ($708 / 770$ correct)
  - Macro F1-Score: **$92.46\%$**
  - Early Blight Recall: **$88.48\%$** (F1: **$88.84\%$**)
  - Late Blight Recall: **$91.36\%$** (F1: **$92.21\%$**)
  - Healthy Recall: **$99.31\%$** (F1: **$96.32\%$**)
  - Early $\leftrightarrow$ Late Errors: **$51$** (Reduced from $53$ in baseline test).
