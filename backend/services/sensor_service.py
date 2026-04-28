from __future__ import annotations

from datetime import datetime, timedelta

from backend.core.config import get_config
from backend.models.grid import GridModel
from backend.models.sensor_cluster import SensorClusterModel, SensorNode


def _node(sensor_id: str, label: str, actual: float, threshold: float, unit: str) -> SensorNode:
    triggered = actual >= threshold if label != "solar" else actual < threshold
    if triggered:
        status = "ALERT"
    elif label == "solar" and actual < threshold + 15:
        status = "WARN"
    elif actual >= threshold * 0.85:
        status = "WARN"
    else:
        status = "OK"
    return SensorNode(
        sensor_id=sensor_id,
        label=label,
        actual=round(actual, 2),
        threshold=threshold,
        triggered=triggered,
        unit=unit,
        status=status,
    )


def _cluster_health(nodes: list[SensorNode]) -> tuple[str, float]:
    failing = sum(1 for node in nodes if node.status == "ALERT")
    warning = sum(1 for node in nodes if node.status == "WARN")
    if failing >= len(nodes) - 1:
        return "RED", 0.25
    if failing or warning >= 2:
        return "ORANGE", 0.65
    return "GREEN", 0.95


def _pattern(index: int, hotspot: bool) -> dict[str, float]:
    if hotspot:
        return {
            "temperature": 31 + (index % 7) * 2.4,
            "sound": 44 + (index % 5) * 10.0,
            "motion": 1.0 if index % 3 == 0 else 0.0,
            "smoke": 18 + (index % 6) * 12.0,
            "solar": 92 - (index % 4) * 8.0,
        }
    return {
        "temperature": 27 + (index % 6) * 1.8,
        "sound": 28 + (index % 4) * 8.0,
        "motion": 1.0 if index % 11 == 0 else 0.0,
        "smoke": 10 + (index % 5) * 8.0,
        "solar": 95 - (index % 5) * 5.0,
    }


def build_sensor_clusters(grids: list[GridModel]) -> list[SensorClusterModel]:
    config = get_config()
    clusters: list[SensorClusterModel] = []

    for index, grid in enumerate(grids, start=1):
        base = _pattern(index, grid.hotspot_flag)
        nodes = [
            _node(f"temp{index}", "temperature", base["temperature"], config.thresholds.temperature, "C"),
            _node(f"mov{index}", "motion", base["motion"], config.thresholds.motion, "binary"),
            _node(f"sm{index}", "smoke", base["smoke"], config.thresholds.smoke, "ppm"),
            _node(f"so{index}", "sound", base["sound"], config.thresholds.sound, "dB"),
            _node(f"solar{index}", "solar", base["solar"], 55.0, "%"),
        ]
        health, reliability = _cluster_health(nodes)
        clusters.append(
            SensorClusterModel(
                cluster_id=f"S{index}",
                grid_id=grid.grid_id,
                zone_id=grid.zone_id,
                hotspot_flag=grid.hotspot_flag,
                placement_km=1 if grid.hotspot_flag else 5,
                health=health,
                reliability_score=reliability,
                last_ping=datetime.utcnow() - timedelta(minutes=index % 17),
                nodes=nodes,
            )
        )
    return clusters


def evaluate_cluster(cluster: SensorClusterModel) -> list[str]:
    return [node.sensor_id for node in cluster.nodes if node.triggered]
