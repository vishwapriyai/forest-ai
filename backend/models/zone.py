from __future__ import annotations

from pydantic import BaseModel, Field


class ZoneModel(BaseModel):
    zone_id: str
    name: str
    color: str
    grid_ids: list[str] = Field(default_factory=list)
    center_lat: float
    center_lon: float
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
