import json
import sys
from pathlib import Path
from fastapi.encoders import jsonable_encoder

# Add backend directory to sys.path so we can import services
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.platform_state import platform_state
from backend.core.config import get_config

def export_static_json():
    frontend_data_dir = ROOT / "frontend" / "data"
    frontend_data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export dashboard-data.json
    dashboard_payload = jsonable_encoder(platform_state.get_dashboard_payload())
    dashboard_path = frontend_data_dir / "dashboard-data.json"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f)
    print(f"Exported static data -> {dashboard_path.name}")

    # 2. Export live-data.json
    live_payload = jsonable_encoder(platform_state.get_live_payload())
    live_path = frontend_data_dir / "live-data.json"
    with open(live_path, "w", encoding="utf-8") as f:
        json.dump(live_payload, f)
    print(f"Exported static data -> {live_path.name}")

    # 3. Export simulation-metadata.json
    config = get_config()
    sim_metadata = {
        "thresholds": {
            "temperature": config.thresholds.temperature,
            "smoke": config.thresholds.smoke,
            "sound": config.thresholds.sound,
            "motion": config.thresholds.motion,
            "solar_health": 55.0,
            "drone_medium_change_percent": config.thresholds.drone_medium_change * 100,
            "drone_high_change_percent": config.thresholds.drone_high_change * 100,
            "medium_risk_score": config.thresholds.medium_risk_score,
            "high_risk_score": config.thresholds.high_risk_score,
        },
        "grids": [grid.model_dump() for grid in platform_state.grids],
        "zones": [zone.model_dump() for zone in platform_state.zones],
    }
    sim_metadata_payload = jsonable_encoder(sim_metadata)
    sim_metadata_path = frontend_data_dir / "simulation-metadata.json"
    with open(sim_metadata_path, "w", encoding="utf-8") as f:
        json.dump(sim_metadata_payload, f)
    print(f"Exported static data -> {sim_metadata_path.name}")

if __name__ == "__main__":
    export_static_json()
