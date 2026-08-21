import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os

# ==========================
# 1️⃣ Load Trained Model
# ==========================
model = tf.keras.models.load_model("greenscan_model.h5")

# ==========================
# 2️⃣ Automatically Get Class Names
# ==========================
dataset_path = "dataset"
class_labels = sorted(os.listdir(dataset_path))

print("Detected Classes:", class_labels)

# ==========================
# 3️⃣ Ask User for Image Name
# ==========================
img_path = input("\nEnter image filename (example: test.jpg): ")

if not os.path.exists(img_path):
    print("Error: Image not found. Make sure the image is inside project folder.")
    exit()

# ==========================
# 4️⃣ Preprocess Image
# ==========================
img = image.load_img(img_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# ==========================
# 5️⃣ Predict
# ==========================
prediction = model.predict(img_array)
predicted_class_index = np.argmax(prediction)
confidence = np.max(prediction)

predicted_class = class_labels[predicted_class_index]

# ==========================
# 6️⃣ Output Result
# ==========================
print("\nPrediction:", predicted_class)
print("Confidence: {:.2f}%".format(confidence * 100))