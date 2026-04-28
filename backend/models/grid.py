from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GridModel(BaseModel):
    grid_id: str
    zone_id: str
    hotspot_flag: bool
    last_drone_scan_time: datetime | None = None
    sensor_density: str
    center_lat: float
    center_lon: float
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    scan_frequency_days: int = Field(default=5)
