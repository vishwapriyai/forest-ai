import rasterio
import numpy as np

def load_band(path):
    with rasterio.open(path) as src:
        return src.read(1).astype(float)

def compute_ndvi(red, nir):
    return (nir - red) / (nir + red + 1e-6)

def detect_change(ndvi1, ndvi2):
    diff = ndvi2 - ndvi1
    loss = diff < -0.2
    return diff, loss

def compute_satellite_score(diff):
    return np.clip(-diff, 0, 1)