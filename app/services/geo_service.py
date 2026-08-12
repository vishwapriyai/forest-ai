from app.utils.grid_generator import generate_grid
from app.services.sensor_service import generate_sensor_pack

def assign_sensors_to_grids():
    grids = generate_grid(11.3, 11.6, 76.6, 76.9)

    sensors = []
    sensor_id = 1

    for g in grids:
        if g["is_hotspot"]:
            density = 1   # every 1km
        else:
            density = 5   # every 5km

        if g["grid_id"] % density == 0:
            sensor = generate_sensor_pack(sensor_id)

            sensor["grid_id"] = g["grid_id"]
            sensor["zone"] = g["zone"]

            sensors.append(sensor)
            sensor_id += 1

    return grids, sensors