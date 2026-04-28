from __future__ import annotations

from backend.core.config import get_config
from backend.models.sensor_cluster import SensorClusterModel


def _drone_score(change_percent: float) -> float:
    if change_percent >= 15:
        return 9.0
    if change_percent >= 5:
        return 5.0
    return 1.5


def _sensor_score(triggered_count: int) -> float:
    if triggered_count >= 3:
        return 9.0
    if triggered_count == 2:
        return 6.0
    if triggered_count == 1:
        return 3.0
    return 1.0


def calculate_risk(change_percent: float, cluster: SensorClusterModel, hotspot_flag: bool) -> tuple[str, float, list[str]]:
    config = get_config()
    triggered = [node.sensor_id for node in cluster.nodes if node.triggered]
    drone_component = _drone_score(change_percent)
    sensor_component = _sensor_score(len(triggered))
    reliability_component = max(cluster.reliability_score, 0.25) * 2.0
    hotspot_component = 1.5 if hotspot_flag else 0.5

    score = (0.45 * drone_component) + (0.35 * sensor_component) + reliability_component + hotspot_component
    if score >= config.thresholds.high_risk_score:
        label = "HIGH RISK"
    elif score >= config.thresholds.medium_risk_score:
        label = "MEDIUM RISK"
    else:
        label = "LOW RISK"
    return label, round(score, 2), triggered
