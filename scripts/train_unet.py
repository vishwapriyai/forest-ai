import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.unet_model import load_patches, build_unet

def train():
    print("🚀 Training started...")

    X, y = load_patches()

    print("Data:", X.shape, y.shape)

    model = build_unet()

    model.fit(X, y, epochs=30, batch_size=4)

    model.save("models/unet_deforestation.h5")

    print("✅ Model trained and saved!")

if __name__ == "__main__":
    train()