import os
import cv2
import numpy as np
import random
from glob import glob

def augment_image(img_path, output_path):
    img = cv2.imread(img_path)
    if img is None: return

    # 1. Flip
    if random.random() > 0.5: img = cv2.flip(img, 1)
    
    # 2. Brightness/Contrast
    alpha = 1.0 + random.uniform(-0.2, 0.2) # Contrast
    beta = random.randint(-20, 20)           # Brightness
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    # 3. Blur (simulating camera shake)
    if random.random() > 0.7:
        img = cv2.GaussianBlur(img, (3, 3), 0)

    cv2.imwrite(output_path, img)

def balance_dataset(data_dir):
    classes = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    counts = {c: len(glob(os.path.join(data_dir, c, "*"))) for c in classes}
    max_count = max(counts.values())
    
    print(f"Dataset Stats: {counts}")
    
    for cls in classes:
        cls_path = os.path.join(data_dir, cls)
        files = glob(os.path.join(cls_path, "*"))
        current_count = len(files)
        
        if current_count < max_count:
            needed = max_count - current_count
            print(f"Augmenting {cls}: adding {needed} images...")
            for i in range(needed):
                src = random.choice(files)
                ext = os.path.splitext(src)[1]
                dst = os.path.join(cls_path, f"aug_{i}{ext}")
                augment_image(src, dst)

if __name__ == "__main__":
    balance_dataset(r"C:\Greenscan project\dataset")
    print("Dataset balancing and augmentation complete!")
