import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import cv2
from tensorflow.keras.models import load_model
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

IMG_PATH = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\1_CLOUD_FREE_DATASET\2_SENTINEL2\IMAGE_16_GRID\RASTER_0.tif"
MASK_PATH = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\3_TRAINING_MASKS\MASK_16_GRID\RASTER_0.tif"

from models.unet_model import dice_loss, combined_loss

model = load_model(
    "models/unet_deforestation.h5",
    custom_objects={
        "dice_loss": dice_loss,
        "combined_loss": combined_loss
    }
)

# 🔹 Load image
with rasterio.open(IMG_PATH) as src:
    img = src.read()[:3]
    img = np.transpose(img, (1, 2, 0))

img = img / np.max(img)

# 🔹 Resize
img_resized = cv2.resize(img, (128, 128))
input_img = np.expand_dims(img_resized, axis=0)

# 🔹 Predict
pred = model.predict(input_img)[0]
print("Prediction min:", np.min(pred))
print("Prediction max:", np.max(pred))
print("Prediction mean:", np.mean(pred))
pred_mask = (pred > 0.1).astype(np.float32)

# 🔹 Load true mask
with rasterio.open(MASK_PATH) as src:
    true_mask = src.read(1)

# Convert mask same as training
true_mask = (true_mask == 1).astype(np.float32)
true_mask = cv2.resize(true_mask, (128, 128))


plt.figure(figsize=(5,4))
plt.title("Raw Prediction Heatmap")
plt.imshow(pred, cmap='jet')
plt.colorbar()
plt.show()


# 🔹 Plot
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