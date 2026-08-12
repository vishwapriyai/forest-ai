from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from backend.core.config import get_config
from backend.models.simulation import SimulationRequest
from backend.services.platform_state import platform_state


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/grids")
def get_grids() -> list[dict]:
    return [grid.model_dump() for grid in platform_state.grids]


@router.get("/zones")
def get_zones() -> list[dict]:
    return [zone.model_dump() for zone in platform_state.zones]


@router.get("/hotspots")
def get_hotspots() -> list[dict]:
    return [grid.model_dump() for grid in platform_state.grids if grid.hotspot_flag]


@router.get("/sensor-status")
def get_sensor_status() -> list[dict]:
    return [cluster.model_dump() for cluster in platform_state.sensor_clusters]


@router.get("/drone-schedule")
def get_drone_schedule() -> list[dict]:
    return [task.model_dump() for task in platform_state.drone_tasks]


@router.get("/dashboard-data")
def get_dashboard_data() -> dict:
    return platform_state.get_dashboard_payload()


@router.get("/simulation-metadata")
def get_simulation_metadata() -> dict:
    config = get_config()
    return {
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


@router.get("/live-data")
def get_live_data(zone_id: str | None = Query(default=None)) -> dict:
    return platform_state.get_live_payload(zone_id=zone_id)


@router.post("/live-feed/refresh")
def refresh_live_feed(zone_id: str | None = Query(default=None)) -> dict:
    return platform_state.advance_live_feed(zone_id=zone_id)


@router.get("/live-feed/status")
def live_feed_status(zone_id: str | None = Query(default=None)) -> dict:
    return platform_state.get_live_payload(zone_id=zone_id)


@router.post("/simulate")
def simulate(payload: SimulationRequest) -> dict:
    return platform_state.simulate(payload).model_dump()


@router.post("/simulate-upload")
async def simulate_upload(
    zone_id: str = Form(...),
    grid_id: str = Form("SIM-GRID-UPLOAD"),
    hotspot_flag: bool = Form(False),
    reliability_score: float = Form(1.0),
    temperature: float = Form(30.0),
    smoke: float = Form(20.0),
    sound: float = Form(35.0),
    motion: float = Form(0.0),
    solar_health: float = Form(90.0),
    yesterday_image: UploadFile = File(...),
    today_image: UploadFile = File(...),
) -> dict:
    try:
        payload = SimulationRequest(
            grid_id=grid_id,
            zone_id=zone_id,
            hotspot_flag=hotspot_flag,
            reliability_score=reliability_score,
            temperature=temperature,
            smoke=smoke,
            sound=sound,
            motion=motion,
            solar_health=solar_health,
        )
        result = platform_state.simulate_with_uploaded_images(
            payload,
            await yesterday_image.read(),
            await today_image.read(),
        )
        return result.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/alerts")
def get_alerts() -> list[dict]:
    return [alert.model_dump() for alert in platform_state.alerts]


@router.post("/toggle-drone")
def toggle_drone(state: bool) -> dict:
    return {"drone_active": platform_state.toggle_drone(state)}


@router.get("/analyze-live")
def analyze_live() -> dict:
    payload = platform_state.get_live_payload()
    task = payload["drone"]
    cluster = payload["sensor_cluster"]
    return {
        "mode": payload["mode"],
        "drone": {
            "image": task["image_name"] if task else None,
            "change": round((task["change_percent"] if task else 0.0) / 100, 3),
            "level": task["risk_level"] if task else "LOW",
        },
        "sensor": {
            "sound": next((node["actual"] for node in cluster["nodes"] if node["label"] == "sound"), 0) if cluster else 0,
            "vibration": next((node["actual"] for node in cluster["nodes"] if node["label"] == "motion"), 0) if cluster else 0,
            "event": "logging_activity" if payload["triggered_sources"] else "normal",
        },
        "risk": payload["risk"],
        "alert": payload["alerts"][0]["message"] if payload["alerts"] else "Safe",
    }


@router.get("/dashboard-map")
def dashboard_map() -> dict:
    grids = []
    for grid in platform_state.grids:
        grids.append(
            {
                "grid_id": grid.grid_id,
                "lat_min": grid.lat_min,
                "lat_max": grid.lat_max,
                "lon_min": grid.lon_min,
                "lon_max": grid.lon_max,
                "zone": grid.zone_id,
                "is_hotspot": grid.hotspot_flag,
            }
        )
    return {"grids": grids, "hotspots": [grid for grid in grids if grid["is_hotspot"]]}


@router.get("/live-system")
def live_system() -> dict:
    alerts = []
    for alert in platform_state.alerts:
        alerts.append(
            {
                "sensor": alert.source_label,
                "grid": alert.grid_id,
                "zone": alert.zone_id,
                "risk": alert.risk,
                "triggered": alert.source_label.split(", "),
                "health": platform_state.cluster_lookup[alert.grid_id].health,
            }
        )

    scanning_task = next((task for task in platform_state.drone_tasks if task.status in {"scanning", "completed"}), None)
    return {
        "drone": scanning_task.risk_level if scanning_task else "LOW",
        "alerts": alerts,
        "final_risk": alerts[0]["risk"] if alerts else "LOW RISK",
        "total_sensors": len(platform_state.sensor_clusters),
    }
