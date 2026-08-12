from __future__ import annotations

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    grid_id: str | None = None
    zone_id: str | None = None
    hotspot_flag: bool = False
    reliability_score: float = Field(default=1.0, ge=0.0, le=1.0)
    temperature: float = 30.0
    smoke: float = 20.0
    sound: float = 35.0
    motion: float = 0.0
    solar_health: float = 90.0
    drone_change_percent: float = 0.0


class SimulationResponse(BaseModel):
    risk: str
    score: float
    triggered_sources: list[str]
    explanation: str
    drone_change_percent: float | None = None
