# ==============================
# 🌿 GreenScan+ Model Training & Evaluation
# ==============================

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

# ==============================
# 1. Dataset Path
# ==============================
dataset_path = r"C:\Greenscan project\dataset"

# ==============================
# 2. Data Preprocessing & Augmentation
# ==============================
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest'
)

train_data = datagen.flow_from_directory(
    dataset_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_data = datagen.flow_from_directory(
    dataset_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation',
    shuffle=False # Crucial for confusion matrix
)

class_indices = train_data.class_indices
labels = list(class_indices.keys())
with open("class_labels.json", "w") as f:
    json.dump(class_indices, f)

# ==============================
# 3. Model Factory
# ==============================
def build_model(arch="mobilenet"):
    if arch == "resnet50":
        base = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    elif arch == "efficientnet":
        base = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    else:
        base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    base.trainable = False
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(len(labels), activation='softmax')(x)
    return Model(inputs=base.input, outputs=predictions)

model = build_model("mobilenet")

# ==============================
# 4. Training
# ==============================
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)

print("\n--- Training Starting ---")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=[early_stop, reduce_lr]
)

# ==============================
# 5. Evaluation & Metrics Export
# ==============================
print("\n--- Generating Research Metrics ---")

# Save history
with open("training_history.json", "w") as f:
    # Convert float32 to float for JSON
    clean_history = {k: [float(x) for x in v] for k, v in history.history.items()}
    json.dump(clean_history, f)

# Predictions for validation set
Y_pred = model.predict(val_data)
y_pred = np.argmax(Y_pred, axis=1)

# Confusion Matrix
cm = confusion_matrix(val_data.classes, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap='Greens')
plt.title('Confusion Matrix - GreenScan+')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.savefig('confusion_matrix.png')

# Classification Report
report = classification_report(val_data.classes, y_pred, target_names=labels, output_dict=True)
with open("classification_report.json", "w") as f:
    json.dump(report, f)

# Save Model
model.save(r"C:\Greenscan project\model\greenscan_model.keras")
print("\nDone! All metrics and model saved.")
