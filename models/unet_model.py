

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import os
import rasterio
import numpy as np
import cv2



IMG_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\1_CLOUD_FREE_DATASET\2_SENTINEL2\IMAGE_16_GRID"
MASK_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\3_TRAINING_MASKS\MASK_16_GRID"

IMG_SIZE = 128

def load_patches():
    images = []
    masks = []

    files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".tif")])

    for file in files:
        img_path = os.path.join(IMG_DIR, file)
        mask_path = os.path.join(MASK_DIR, file)

        # Load image
        with rasterio.open(img_path) as src:
            img = src.read()[:3]
            img = np.transpose(img, (1, 2, 0))

        img = img / np.max(img)

        # Load mask
        with rasterio.open(mask_path) as src:
            mask = src.read(1)

        # Convert to binary
        mask = (mask == 1).astype(np.float32)

        # Create patches
        h, w, _ = img.shape

        for i in range(0, h - IMG_SIZE, IMG_SIZE):
            for j in range(0, w - IMG_SIZE, IMG_SIZE):
                patch_img = img[i:i+IMG_SIZE, j:j+IMG_SIZE]
                patch_mask = mask[i:i+IMG_SIZE, j:j+IMG_SIZE]

                if patch_img.shape == (IMG_SIZE, IMG_SIZE, 3):

                    ratio = np.mean(patch_mask)

                    # ✅ Keep ALL deforestation patches
                    if ratio > 0.01:
                        images.append(patch_img)
                        masks.append(patch_mask)

                    # ✅ Keep SOME forest patches (balance)
                    elif ratio == 0 and np.random.rand() < 0.05:
                        images.append(patch_img)
                        masks.append(patch_mask)

    images = np.array(images)
    masks = np.array(masks)

    print("✅ Total patches:", len(images))
    print("✅ Final ratio:", np.mean(masks))
    print("✅ Mask values:", np.unique(masks))

    return images, masks



from tensorflow.keras import layers, models


import tensorflow as tf

def dice_loss(y_true, y_pred):
    smooth = 1e-6
    intersection = tf.reduce_sum(y_true * y_pred)
    return 1 - (2. * intersection + smooth) / (
        tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + smooth
    )

def combined_loss(y_true, y_pred):
    bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    
    dice = dice_loss(y_true, y_pred)
    return bce + dice

def build_unet():
    inputs = layers.Input((128, 128, 3))

    # Encoder
    c1 = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(32, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    c2 = layers.Conv2D(64, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(64, 3, activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D()(c2)

    # Bottleneck
    b1 = layers.Conv2D(128, 3, activation='relu', padding='same')(p2)

    # Decoder
    u1 = layers.UpSampling2D()(b1)
    u1 = layers.concatenate([u1, c2])
    c3 = layers.Conv2D(64, 3, activation='relu', padding='same')(u1)

    u2 = layers.UpSampling2D()(c3)
    u2 = layers.concatenate([u2, c1])
    c4 = layers.Conv2D(32, 3, activation='relu', padding='same')(u2)

    outputs = layers.Conv2D(1, 1, activation='sigmoid')(c4)

    model = models.Model(inputs, outputs)

    import tensorflow as tf

    def final_loss(y_true, y_pred):
        weight = 5.0

        # ✅ pixel-wise BCE (no reduction)
        bce = tf.keras.backend.binary_crossentropy(y_true, y_pred)

        # ✅ apply weighting
        weighted = bce * (y_true * weight + (1 - y_true))

        # ✅ dice loss
        smooth = 1e-6
        intersection = tf.reduce_sum(y_true * y_pred)
        dice = 1 - (2. * intersection + smooth) / (
            tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + smooth
        )

        return weighted + dice

    model.compile(
        optimizer='adam',
        loss=final_loss,
        metrics=['accuracy']
    )
    return model


