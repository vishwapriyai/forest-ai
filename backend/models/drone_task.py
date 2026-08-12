from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


DroneStatus = Literal["scheduled", "scanning", "completed"]


class DroneTaskModel(BaseModel):
    task_id: str
    drone_id: str
    grid_id: str
    zone_id: str
    scheduled_for: datetime
    last_scanned_time: datetime | None = None
    status: DroneStatus
    image_name: str | None = None
    yesterday_image: str | None = None
    today_image: str | None = None
    change_percent: float = 0.0
    risk_level: str = "LOW"
