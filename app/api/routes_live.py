from fastapi import APIRouter
from app.services.geo_service import assign_sensors_to_grids
from app.services.sensor_service import evaluate_sensor, sensor_risk
from app.services.fusion_service import fuse_all
import random

router = APIRouter()

@router.get("/live-system")
def live_system():

    grids, sensors = assign_sensors_to_grids()

    alerts = []

    for s in sensors:
        triggered = evaluate_sensor(s)
        risk = sensor_risk(triggered)

        if risk != "SAFE":
            alerts.append({
                "sensor": s["id"],
                "grid": s["grid_id"],
                "zone": s["zone"],
                "risk": risk,
                "triggered": triggered,
                "health": s["health"]
            })

    drone_level = random.choice(["LOW", "MEDIUM", "HIGH"])

    final_risk = fuse_all(drone_level, "HIGH RISK" if alerts else "SAFE")

    return {
        "drone": drone_level,
        "alerts": alerts,
        "final_risk": final_risk,
        "total_sensors": len(sensors)
    }