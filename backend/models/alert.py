from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertModel(BaseModel):
    alert_id: str
    timestamp: datetime
    zone_id: str
    grid_id: str
    source: str
    source_label: str
    message: str
    risk: str
    lat: float
    lon: float
    image: str | None = None
