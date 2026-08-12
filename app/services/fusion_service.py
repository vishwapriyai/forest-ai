def fuse_all(drone_level, sensor_risk):

    score_map = {
        "LOW": 1,
        "MEDIUM": 5,
        "HIGH": 9
    }

    sensor_map = {
        "SAFE": 1,
        "LOW RISK": 3,
        "MEDIUM RISK": 6,
        "HIGH RISK": 9
    }

    total = 0.7 * score_map.get(drone_level, 1) + \
            0.3 * sensor_map.get(sensor_risk, 1)

    if total > 7:
        return "HIGH RISK"
    elif total > 4:
        return "MEDIUM RISK"
    return "LOW RISK"