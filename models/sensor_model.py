import numpy as np

def detect_sensor_event(sound, vibration):

    # thresholds (POC)
    if sound > 70 and vibration > 5:
        return "logging_activity"

    elif sound > 50:
        return "movement"

    else:
        return "normal"