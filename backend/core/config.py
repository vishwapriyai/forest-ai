from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
THRESHOLDS_FILE = BACKEND_DIR / "data" / "thresholds.json"
DRONE_YESTERDAY_DIR = DATA_DIR / "raw" / "drone" / "21-04-26"
DRONE_TODAY_DIR = DATA_DIR / "raw" / "drone" / "22-04-26"


class RiskThresholds(BaseModel):
    temperature: float = 40.0
    smoke: float = 70.0
    sound: float = 80.0
    motion: float = 1.0
    drone_medium_change: float = 0.05
    drone_high_change: float = 0.15
    high_risk_score: float = 7.0
    medium_risk_score: float = 4.0


class ForestConfig(BaseModel):
    forest_name: str = "Mudumalai Forest Reserve"
    forest_bounds: dict[str, float] = Field(
        default_factory=lambda: {
            "lat_min": 11.30,
            "lat_max": 11.84,
            "lon_min": 76.60,
            "lon_max": 77.28,
        }
    )
    grid_size_km: int = 3
    zone_count: int = 6
    hotspot_grid_ids: list[str] = Field(
        default_factory=lambda: [
            "G-0010",
            "G-0011",
            "G-0012",
            "G-0043",
            "G-0044",
            "G-0075",
            "G-0076",
            "G-0108",
            "G-0139",
        ]
    )
    drone_ids: list[str] = Field(default_factory=lambda: ["DR-01", "DR-02", "DR-03", "DR-04"])
    thresholds: RiskThresholds = Field(default_factory=RiskThresholds)


@lru_cache(maxsize=1)
def get_config() -> ForestConfig:
    if THRESHOLDS_FILE.exists():
        payload: dict[str, Any] = json.loads(THRESHOLDS_FILE.read_text(encoding="utf-8"))
        thresholds = RiskThresholds(**payload.get("thresholds", {}))
        config = ForestConfig(**{k: v for k, v in payload.items() if k != "thresholds"})
        return config.model_copy(update={"thresholds": thresholds})
    return ForestConfig()
