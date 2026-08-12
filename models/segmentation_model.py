import os
import rasterio
import numpy as np

IMG_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\1_CLOUD_FREE_DATASET\2_SENTINEL2\IMAGE_16_GRID"
MASK_DIR = r"D:\Vish\AI_agent\Forest\sentinel_amazon forest\3_TRAINING_MASKS\MASK_16_GRID"

IMG_SIZE = 128


def load_data():
    images = []
    masks = []

    img_files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith(".tif")])

    for file in img_files:
        img_path = os.path.join(IMG_DIR, file)
        mask_path = os.path.join(MASK_DIR, file)

        # Read image
        with rasterio.open(img_path) as src:
            img = src.read()[:3]  # take first 3 bands
            img = np.transpose(img, (1, 2, 0))

        # Normalize
        img = (img - img.min()) / (img.max() - img.min())

        # Resize
        img = np.array(img)
        img = np.resize(img, (IMG_SIZE, IMG_SIZE, 3))

        # Read mask
        with rasterio.open(mask_path) as src:
            mask = src.read(1)

        mask = np.resize(mask, (IMG_SIZE, IMG_SIZE))
        mask = (mask > 0).astype(np.float32)

        images.append(img)
        masks.append(mask)

    return np.array(images), np.array(masks)

from tensorflow.keras import layers, models

def build_model():
    inputs = layers.Input((128, 128, 3))

    # Encoder
    c1 = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(32, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    c2 = layers.Conv2D(64, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(64, 3, activation='relu', padding='same')(c2)

    # Decoder
    u1 = layers.UpSampling2D()(c2)
    u1 = layers.concatenate([u1, c1])

    c3 = layers.Conv2D(32, 3, activation='relu', padding='same')(u1)

    outputs = layers.Conv2D(1, 1, activation='sigmoid')(c3)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model

def train():
    X, y = load_data()

    print("Data shape:", X.shape, y.shape)

    model = build_model()

    model.fit(X, y, epochs=20, batch_size=2)

    model.save("models/deforestation_model.h5")

    print("✅ Model trained and saved")

def weighted_loss(y_true, y_pred):
    return tf.keras.losses.binary_crossentropy(y_true, y_pred) * 2

if __name__ == "__main__":
    train()