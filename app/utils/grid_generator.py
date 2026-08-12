import math

def generate_grid(lat_min, lat_max, lon_min, lon_max, step_km=3):
    grids = []
    grid_id = 1

    lat_step = step_km / 111  # approx conversion
    lon_step = step_km / 111

    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            grids.append({
                "grid_id": grid_id,
                "lat_min": lat,
                "lat_max": lat + lat_step,
                "lon_min": lon,
                "lon_max": lon + lon_step,
                "zone": f"Zone-{(grid_id % 3) + 1}",
                "is_hotspot": grid_id in [7,8,9]
            })
            grid_id += 1
            lon += lon_step
        lat += lat_step

    return grids