import pandas as pd
import numpy as np

from models.sensor_model import compute_sensor_score
from models.fusion_model import compute_final_risk

# simulate inputs
satellite_score = 0.7
drone_score = 0.6

df = pd.read_csv("data/raw/sensor/sensor_data.csv")
df = compute_sensor_score(df)

sensor_score = df["sensor_score"].mean()

final_risk = compute_final_risk(
    satellite_score,
    drone_score,
    sensor_score
)

print("🚨 FINAL RISK SCORE:", final_risk)

if final_risk > 0.6:
    print("🔥 ALERT: Illegal logging detected!")