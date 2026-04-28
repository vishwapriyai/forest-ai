import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

OUTPUT_DIR = "data/raw/sensor/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_realistic_sensor_data(samples=300):
    data = []

    start_time = datetime(2023, 1, 1, 6, 0, 0)

    for i in range(samples):

        timestamp = start_time + timedelta(minutes=i*5)

        # 📍 Fixed forest location (Mudumalai area)
        lat = 11.5 + np.random.uniform(-0.01, 0.01)
        lon = 76.7 + np.random.uniform(-0.01, 0.01)

        event = np.random.choice(
            ["normal", "cutting", "vehicle"],
            p=[0.6, 0.25, 0.15]
        )

        if event == "normal":
            sound = np.random.randint(30, 50)
            vibration = 0
            motion = 0

        elif event == "cutting":
            sound = np.random.randint(85, 120)   # chainsaw
            vibration = 1
            motion = 1

        elif event == "vehicle":
            sound = np.random.randint(60, 85)
            vibration = 0
            motion = 1

        temperature = np.random.randint(20, 35)
        humidity = np.random.randint(40, 90)

        data.append([
            timestamp, lat, lon,
            sound, vibration, motion,
            temperature, humidity,
            event
        ])

    df = pd.DataFrame(data, columns=[
        "timestamp",
        "latitude",
        "longitude",
        "sound_db",
        "vibration",
        "motion",
        "temperature",
        "humidity",
        "label"
    ])

    df.to_csv(os.path.join(OUTPUT_DIR, "sensor_data.csv"), index=False)

    print("✅ Realistic sensor data generated!")


if __name__ == "__main__":
    generate_realistic_sensor_data()