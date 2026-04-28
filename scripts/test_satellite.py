import numpy as np
import matplotlib.pyplot as plt
from models.satellite_model import load_band, compute_ndvi

# load your files
red = load_band("data/raw/satellite/0_red.tif")
nir = load_band("data/raw/satellite/0_nir.tif")

# compute NDVI
ndvi = compute_ndvi(red, nir)

# visualize
plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar()
plt.title("NDVI Map")
plt.show()