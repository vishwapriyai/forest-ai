import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Paths
IMG_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\1_CLOUD_FREE_DATASET\2_SENTINEL2\IMAGE_16_GRID"
MASK_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\3_TRAINING_MASKS\MASK_16_GRID"

MODEL_PATH = "models/deforestation_model.h5"
IMG_SIZE = 128

# Load model
model = load_model(MODEL_PATH)

# Pick one image
img_files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".tif")])
file = img_files[0]

img_path = os.path.join(IMG_DIR, file)
mask_path = os.path.join(MASK_DIR, file)

# Load image
with rasterio.open(img_path) as src:
    img = src.read()[:3]
    img = np.transpose(img, (1, 2, 0))

# Normalize
img = (img - img.min()) / (img.max() - img.min())

# Resize
img_resized = np.resize(img, (IMG_SIZE, IMG_SIZE, 3))
input_img = np.expand_dims(img_resized, axis=0)

# Predict
pred = model.predict(input_img)[0]

# Threshold
pred_mask = (pred > 0.5).astype(np.float32)

# Load actual mask
with rasterio.open(mask_path) as src:
    true_mask = src.read(1)

true_mask = np.resize(true_mask, (IMG_SIZE, IMG_SIZE))

# Plot
plt.figure(figsize=(12,4))

plt.subplot(1,3,1)
plt.title("Satellite Image")
plt.imshow(img_resized)

plt.subplot(1,3,2)
plt.title("Predicted Mask")
plt.imshow(pred_mask, cmap='gray')

plt.subplot(1,3,3)
plt.title("Actual Mask")
plt.imshow(true_mask, cmap='gray')

plt.show()