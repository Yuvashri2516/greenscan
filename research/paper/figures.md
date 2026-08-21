# Recommended Paper Figures

This document details the minimum list of figures required to illustrate the GreenScan system architecture, processing pipeline, and experimental results in the research paper.

---

### Figure 1 — Overall System Architecture
- *Description:* Schematic flow diagram illustrating the integration between the React frontend, FastAPI backend gateway, TensorFlow inference engine, SQLite database, and the external decision support calculators (Soil Health, Dosage, Chatbot).
- *Purpose:* Illustrates the end-to-end software engineering architecture of the platform.

### Figure 2 — GreenScan Processing Pipeline
- *Description:* A step-by-step flowchart tracking an input leaf image as it undergoes contrast enhancement (CLAHE), HSV color masking, CNN classification forward pass, Grad-CAM backpropagation, GSA score calculation, and final recommendation generation.
- *Purpose:* Explains the algorithmic execution path.

### Figure 3 — EfficientNet-B0 Classification Workflow
- *Description:* Diagram of the EfficientNet-B0 network structure, showing the input layer ($224 \times 224 \times 3$), MBConv blocks, global average pooling, dense layers, dropout, and the final softmax probability classification output.
- *Purpose:* Illustrates the deep learning backbone structure.

### Figure 4 — Grad-CAM Explainability
- *Description:* Visual comparison showing the input leaf image, the final convolutional feature maps, computed gradients for the target class, and the resulting normalized Grad-CAM activation heatmap.
- *Purpose:* Explains how model attention maps are generated.

### Figure 5 — Leaf Segmentation and Activation Mask
- *Description:* Visual comparison of the segmentation steps: (a) raw input image, (b) HSV binary leaf mask, (c) isolated leaf contours, (d) Grad-CAM heatmap, (e) thresholded activation mask ($\tau = 0.60$), and (f) final GSA spatial attention overlay.
- *Purpose:* Visualizes how leaf contours are combined with Grad-CAM to isolate disease features.

### Figure 6 — GSA Health Score Pipeline
- *Description:* Block diagram illustrating GSA calculations: computing the attention-affected region percentage ($N_{\text{activated}} / N_{\text{leaf}}$), calculating mean activations, applying weighted formulas for healthy and diseased leaves, and mapping scores to severity tiers.
- *Purpose:* Illustrates the mathematical GSA scoring process.

### Figure 7 — Example Healthy Prediction
- *Description:* End-to-end visualization of a healthy tomato leaf prediction, showing the input image, leaf mask, low Grad-CAM activation, health score (e.g., 97), and the green "Healthy" severity label.
- *Purpose:* Provides a visual example of a healthy classification.

### Figure 8 — Example Early Blight Prediction
- *Description:* End-to-end visualization of an Early Blight infection, showing target-board concentric spots, Grad-CAM attention hotspots, the thresholded activation mask, and the orange "Moderate" severity label.
- *Purpose:* Illustrates GSA performance on Early Blight.

### Figure 9 — Example Late Blight Prediction
- *Description:* End-to-end visualization of a Late Blight infection, showing water-soaked lesions, corresponding Grad-CAM hotspots, and the orange "Moderate" severity label.
- *Purpose:* Illustrates GSA performance on Late Blight.

### Figure 10 — Frontend System Interface
- *Description:* Screenshot layout showing the Web UI dashboard, featuring the drag-and-drop upload panel, interactive Grad-CAM layer selectors, the PHS gauge, disease insights, and agronomic treatment options.
- *Purpose:* Displays the user-facing web dashboard.
