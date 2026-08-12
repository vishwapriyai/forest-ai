import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

IMG_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\1_CLOUD_FREE_DATASET\2_SENTINEL2\IMAGE_16_GRID"
MASK_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\3_TRAINING_MASKS\MASK_16_GRID"

img_files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".tif")])
mask_files = sorted([f for f in os.listdir(MASK_DIR) if f.endswith(".tif")])

print("Images:", len(img_files))
print("Masks:", len(mask_files))

# Load one pair
img_path = os.path.join(IMG_DIR, img_files[0])
mask_path = os.path.join(MASK_DIR, mask_files[0])

# ✅ Read satellite image properly
with rasterio.open(img_path) as src:
    img = src.read()  # shape: (bands, H, W)

# Convert to RGB (use first 3 bands)
img = np.transpose(img[:3], (1, 2, 0))

# Normalize for display
img = (img - img.min()) / (img.max() - img.min())

# Read mask
with rasterio.open(mask_path) as src:
    mask = src.read(1)

# Plot
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.title("Satellite Image")
plt.imshow(img)

plt.subplot(1,2,2)
plt.title("Mask (Deforestation)")
plt.imshow(mask, cmap='gray')

plt.show()