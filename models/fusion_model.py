def fuse_decision(drone_level, sensor_event, drone_active):

    # SENSOR SCORE
    if sensor_event == "logging_activity":
        sensor_score = 8
    elif sensor_event == "movement":
        sensor_score = 4
    else:
        sensor_score = 1

    # DRONE SCORE
    drone_score = {
        "LOW": 1,
        "MEDIUM": 4,
        "HIGH": 8
    }.get(drone_level, 0)

    # FINAL LOGIC
    if drone_active:
        risk_value = 0.9 * drone_score + 0.1 * sensor_score
    else:
        risk_value = sensor_score

    # 🔥 CONVERT TO TEXT
    if risk_value >= 6:
        return "HIGH RISK"
    elif risk_value >= 3:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"


def generate_alert(risk_text):

    if risk_text == "HIGH RISK":
        return "🚨 Illegal Logging Detected"
    elif risk_text == "MEDIUM RISK":
        return "⚠️ Suspicious Activity"
    else:
        return "✅ Safe"