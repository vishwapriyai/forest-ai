from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from backend.core.config import DRONE_TODAY_DIR, DRONE_YESTERDAY_DIR, get_config
from backend.models.drone_task import DroneTaskModel
from backend.models.grid import GridModel
from models.change_detection_model import compare_images, get_drone_status
from models.location_map import IMAGE_LOCATION_MAP


def _available_images() -> list[str]:
    if not DRONE_TODAY_DIR.exists():
        return []
    return sorted(path.name for path in DRONE_TODAY_DIR.iterdir() if path.is_file())


def build_drone_schedule(grids: list[GridModel]) -> list[DroneTaskModel]:
    config = get_config()
    now = datetime.utcnow()
    images = _available_images()
    tasks: list[DroneTaskModel] = []

    for index, grid in enumerate(grids, start=1):
        scheduled_for = now - timedelta(hours=index % 7) if grid.hotspot_flag else now + timedelta(hours=index % 20)
        status = "completed" if grid.hotspot_flag and images else "scheduled"
        if status != "completed" and index % 9 == 0:
            status = "scanning"

        image_name = images[(index - 1) % len(images)] if images else None
        yesterday_image = str(DRONE_YESTERDAY_DIR / image_name) if image_name else None
        today_image = str(DRONE_TODAY_DIR / image_name) if image_name else None
        change_percent = 0.0
        risk_level = "LOW"
        last_scanned = None

        if image_name and Path(yesterday_image).exists() and Path(today_image).exists():
            change_ratio = compare_images(yesterday_image, today_image)
            change_percent = round(change_ratio * 100, 2)
            risk_level = get_drone_status(change_ratio)
        if status in {"completed", "scanning"} and image_name and Path(yesterday_image).exists() and Path(today_image).exists():
            last_scanned = now - timedelta(hours=index % 11)

        tasks.append(
            DroneTaskModel(
                task_id=f"DT-{index:04d}",
                drone_id=config.drone_ids[(index - 1) % len(config.drone_ids)],
                grid_id=grid.grid_id,
                zone_id=grid.zone_id,
                scheduled_for=scheduled_for,
                last_scanned_time=last_scanned,
                status=status,
                image_name=image_name,
                yesterday_image=yesterday_image,
                today_image=today_image,
                change_percent=change_percent,
                risk_level=risk_level,
            )
        )

    return tasks


def task_location(task: DroneTaskModel, grid_lookup: dict[str, GridModel]) -> tuple[float, float]:
    if task.image_name:
        loc = IMAGE_LOCATION_MAP.get(task.image_name) or IMAGE_LOCATION_MAP.get(task.image_name.replace(".png", ".jpg"))
        if loc:
            return loc["lat"], loc["lon"]
    grid = grid_lookup[task.grid_id]
    return grid.center_lat, grid.center_lon
