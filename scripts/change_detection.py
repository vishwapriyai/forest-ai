import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from models.satellite_model import load_band, compute_ndvi, detect_change

# Load BEFORE (0)
red1 = load_band("data/raw/satellite/0_red.tif")
nir1 = load_band("data/raw/satellite/0_nir.tif")

# Load AFTER (1) → ⚠️ make sure you have nir also
# red2 = load_band("data/raw/satellite/1_red.tif")
# nir2 = load_band("data/raw/satellite/1_nir.tif")

# NDVI
ndvi1 = compute_ndvi(red1, nir1)
# ndvi2 = compute_ndvi(red2, nir2)

# Change detection
# diff, loss = detect_change(ndvi1, ndvi2)
diff, loss = detect_change(ndvi1)

# Plot
plt.figure(figsize=(10,6))

plt.subplot(1,2,1)
plt.title("NDVI Change")
plt.imshow(diff, cmap='RdYlGn')
plt.colorbar()

plt.subplot(1,2,2)
plt.title("Detected Loss")
plt.imshow(loss, cmap='Reds')

plt.show()