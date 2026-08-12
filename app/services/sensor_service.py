import random

def generate_sensor_pack(sensor_id):
    sensor = {
        "id": f"S{sensor_id}",
        "temperature": random.randint(20, 50),
        "smoke": random.randint(0, 100),
        "sound": random.randint(30, 120),
        "motion": random.randint(0, 1),
        "health": check_health()
    }
    return sensor


def check_health():
    r = random.random()
    if r < 0.1:
        return "FAILED"
    elif r < 0.3:
        return "PARTIAL"
    return "ACTIVE"


def evaluate_sensor(sensor):
    triggered = []

    if sensor["temperature"] > 40:
        triggered.append("temp")

    if sensor["smoke"] > 70:
        triggered.append("smoke")

    if sensor["sound"] > 80:
        triggered.append("sound")

    if sensor["motion"] == 1:
        triggered.append("motion")

    return triggered


def sensor_risk(triggered):
    if len(triggered) >= 3:
        return "HIGH RISK"
    elif len(triggered) == 2:
        return "MEDIUM RISK"
    elif len(triggered) == 1:
        return "LOW RISK"
    return "SAFE"