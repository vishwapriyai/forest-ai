from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SensorHealth = Literal["GREEN", "ORANGE", "RED"]


class SensorNode(BaseModel):
    sensor_id: str
    label: str
    actual: float
    threshold: float
    triggered: bool
    unit: str
    status: str


class SensorClusterModel(BaseModel):
    cluster_id: str
    grid_id: str
    zone_id: str
    hotspot_flag: bool
    placement_km: int
    health: SensorHealth
    reliability_score: float
    last_ping: datetime
    nodes: list[SensorNode] = Field(default_factory=list)
