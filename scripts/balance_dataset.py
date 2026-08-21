import os
import random
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

# Paths and parameters
dataset_path = 'dataset'
class_to_augment = 'tomato_healthy'
output_dir = os.path.join(dataset_path, class_to_augment)
num_images_to_generate = 1614  # Match the count of the next smallest class

# Create an ImageDataGenerator for augmentation
data_gen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Get all images in the class directory
image_files = [f for f in os.listdir(output_dir) if f.endswith(('jpg', 'jpeg', 'png'))]

# Generate new images
images_generated = 0
while images_generated < num_images_to_generate:
    img_file = random.choice(image_files)
    img_path = os.path.join(output_dir, img_file)

    # Load and preprocess the image
    img = load_img(img_path)
    img_array = img_to_array(img)
    img_array = img_array.reshape((1,) + img_array.shape)

    # Generate augmented images
    for batch in data_gen.flow(img_array, batch_size=1, save_to_dir=output_dir, save_prefix='aug', save_format='jpeg'):
        images_generated += 1
        if images_generated >= num_images_to_generate:
            break

print(f"Generated {images_generated} new images for class '{class_to_augment}'.")