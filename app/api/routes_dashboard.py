from fastapi import APIRouter
from app.utils.grid_generator import generate_grid

router = APIRouter()

@router.get("/dashboard-map")
def get_map():

    grids = generate_grid(
        lat_min=11.3,
        lat_max=11.6,
        lon_min=76.6,
        lon_max=76.9
    )

    return {
        "grids": grids,
        "hotspots": [g for g in grids if g["is_hotspot"]]
    }