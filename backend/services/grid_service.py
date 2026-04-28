from __future__ import annotations

from collections import defaultdict
from math import ceil, cos, radians

from backend.core.config import get_config
from backend.models.grid import GridModel
from backend.models.zone import ZoneModel


ZONE_COLORS = ["#1f6f78", "#4a7c59", "#c06c2b", "#8c4f7d", "#2e5bff", "#7a8f32"]


def _km_to_lat(km: float) -> float:
    return km / 111.0


def _km_to_lon(km: float, latitude: float) -> float:
    return km / (111.320 * max(cos(radians(latitude)), 0.2))


def generate_grids() -> list[GridModel]:
    config = get_config()
    bounds = config.forest_bounds
    lat_step = _km_to_lat(config.grid_size_km)
    raw_cells: list[dict] = []
    lat = bounds["lat_min"]
    row_index = 0

    while lat < bounds["lat_max"]:
        lon_step = _km_to_lon(config.grid_size_km, lat + (lat_step / 2))
        lon = bounds["lon_min"]
        col_index = 0
        while lon < bounds["lon_max"]:
            raw_cells.append(
                {
                    "row": row_index,
                    "col": col_index,
                    "center_lat": round(lat + (lat_step / 2), 6),
                    "center_lon": round(lon + (lon_step / 2), 6),
                    "lat_min": round(lat, 6),
                    "lat_max": round(min(lat + lat_step, bounds["lat_max"]), 6),
                    "lon_min": round(lon, 6),
                    "lon_max": round(min(lon + lon_step, bounds["lon_max"]), 6),
                }
            )
            col_index += 1
            lon += lon_step
        row_index += 1
        lat += lat_step

    if not raw_cells:
        return []

    total_rows = max(cell["row"] for cell in raw_cells) + 1
    total_cols = max(cell["col"] for cell in raw_cells) + 1
    zone_rows = 2 if config.zone_count >= 2 else 1
    zone_cols = ceil(config.zone_count / zone_rows)
    row_band = max(1, ceil(total_rows / zone_rows))
    col_band = max(1, ceil(total_cols / zone_cols))

    grids: list[GridModel] = []
    for grid_index, cell in enumerate(raw_cells, start=1):
        zone_row = min(cell["row"] // row_band, zone_rows - 1)
        zone_col = min(cell["col"] // col_band, zone_cols - 1)
        zone_no = min((zone_row * zone_cols) + zone_col + 1, config.zone_count)
        grid_id = f"G-{grid_index:04d}"
        hotspot_flag = grid_id in config.hotspot_grid_ids
        grids.append(
            GridModel(
                grid_id=grid_id,
                zone_id=f"ZONE-{zone_no}",
                hotspot_flag=hotspot_flag,
                last_drone_scan_time=None,
                sensor_density="1km" if hotspot_flag else "5km",
                center_lat=cell["center_lat"],
                center_lon=cell["center_lon"],
                lat_min=cell["lat_min"],
                lat_max=cell["lat_max"],
                lon_min=cell["lon_min"],
                lon_max=cell["lon_max"],
                scan_frequency_days=1 if hotspot_flag else 5,
            )
        )
    return grids


def build_zones(grids: list[GridModel]) -> list[ZoneModel]:
    grouped: dict[str, list[GridModel]] = defaultdict(list)
    for grid in grids:
        grouped[grid.zone_id].append(grid)

    zones: list[ZoneModel] = []
    for index, zone_id in enumerate(sorted(grouped)):
        zone_grids = grouped[zone_id]
        zones.append(
            ZoneModel(
                zone_id=zone_id,
                name=zone_id.replace("-", " ").title(),
                color=ZONE_COLORS[index % len(ZONE_COLORS)],
                grid_ids=[grid.grid_id for grid in zone_grids],
                center_lat=round(sum(grid.center_lat for grid in zone_grids) / len(zone_grids), 6),
                center_lon=round(sum(grid.center_lon for grid in zone_grids) / len(zone_grids), 6),
                lat_min=min(grid.lat_min for grid in zone_grids),
                lat_max=max(grid.lat_max for grid in zone_grids),
                lon_min=min(grid.lon_min for grid in zone_grids),
                lon_max=max(grid.lon_max for grid in zone_grids),
            )
        )
    return zones
