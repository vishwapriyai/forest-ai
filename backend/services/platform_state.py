from __future__ import annotations

import asyncio
from datetime import datetime

import cv2
import numpy as np

from backend.core.config import get_config
from backend.models.alert import AlertModel
from backend.models.drone_task import DroneTaskModel
from backend.models.grid import GridModel
from backend.models.sensor_cluster import SensorClusterModel
from backend.models.simulation import SimulationRequest, SimulationResponse
from backend.models.zone import ZoneModel
from backend.services.drone_service import build_drone_schedule, task_location
from backend.services.grid_service import build_zones, generate_grids
from backend.services.risk_service import calculate_risk
from backend.services.sensor_service import build_sensor_clusters


SENSOR_LABEL_ORDER = ["temperature", "motion", "smoke", "sound", "solar"]


class PlatformState:
    def __init__(self) -> None:
        self.drone_active = False
        self.live_cycle = 0
        self.grids: list[GridModel] = []
        self.zones: list[ZoneModel] = []
        self.sensor_clusters: list[SensorClusterModel] = []
        self.drone_tasks: list[DroneTaskModel] = []
        self.alerts: list[AlertModel] = []
        self.grid_lookup: dict[str, GridModel] = {}
        self.zone_lookup: dict[str, ZoneModel] = {}
        self.cluster_lookup: dict[str, SensorClusterModel] = {}
        self.task_lookup: dict[str, DroneTaskModel] = {}
        self.refresh()

    def refresh(self) -> None:
        self.live_cycle += 1
        self.grids = generate_grids()
        self.zones = build_zones(self.grids)
        self.sensor_clusters = build_sensor_clusters(self.grids)
        self.drone_tasks = build_drone_schedule(self.grids)
        self.grid_lookup = {grid.grid_id: grid for grid in self.grids}
        self.zone_lookup = {zone.zone_id: zone for zone in self.zones}
        self.cluster_lookup = {cluster.grid_id: cluster for cluster in self.sensor_clusters}
        self.task_lookup = {task.grid_id: task for task in self.drone_tasks}

        for task in self.drone_tasks:
            self.grid_lookup[task.grid_id].last_drone_scan_time = task.last_scanned_time
        self.alerts = self._build_alerts()

    def advance_live_feed(self, zone_id: str | None = None) -> dict:
        self.refresh()
        return self.get_live_payload(zone_id=zone_id)

    def _grid_number(self, grid_id: str) -> int:
        return int(grid_id.split("-")[1])

    def _visible_grids(self, zone_id: str | None = None) -> list[GridModel]:
        return [grid for grid in self.grids if not zone_id or grid.zone_id == zone_id]

    def _focus_grid_id(self, zone_id: str | None = None) -> str | None:
        visible = self._visible_grids(zone_id)
        if not visible:
            return None
        return visible[self.live_cycle % len(visible)].grid_id

    def _triggered_labels(self, grid_id: str) -> set[str]:
        grid_no = self._grid_number(grid_id)
        if (grid_no + self.live_cycle) % 4 != 0:
            return set()

        primary = SENSOR_LABEL_ORDER[(grid_no + self.live_cycle) % len(SENSOR_LABEL_ORDER)]
        triggered = {primary}
        if (grid_no + self.live_cycle) % 9 == 0:
            triggered.add(SENSOR_LABEL_ORDER[(grid_no + self.live_cycle + 2) % len(SENSOR_LABEL_ORDER)])
        return triggered

    def _sensor_nodes_for_cycle(self, cluster: SensorClusterModel, triggered_labels: set[str]) -> list:
        updated_nodes = []
        grid_no = self._grid_number(cluster.grid_id)
        for node in cluster.nodes:
            triggered = node.label in triggered_labels
            actual = node.actual
            status = "OK"
            variation_seed = (grid_no * 7) + self.live_cycle + sum(ord(char) for char in node.sensor_id)

            if node.label == "temperature":
                over = 2 + (variation_seed % 7)
                under = 4 + (variation_seed % 6)
                actual = node.threshold + over if triggered else max(node.threshold - under, 24 + (variation_seed % 3))
            elif node.label == "smoke":
                over = 6 + (variation_seed % 20)
                under = 12 + (variation_seed % 18)
                actual = node.threshold + over if triggered else max(node.threshold - under, 8 + (variation_seed % 5))
            elif node.label == "sound":
                over = 5 + (variation_seed % 18)
                under = 10 + (variation_seed % 20)
                actual = node.threshold + over if triggered else max(node.threshold - under, 30 + (variation_seed % 8))
            elif node.label == "motion":
                actual = 1.0 if triggered else float((variation_seed % 2) * 0.0)
            elif node.label == "solar":
                drop = 2 + (variation_seed % 9)
                gain = 18 + (variation_seed % 10)
                actual = node.threshold - drop if triggered else node.threshold + gain

            if node.label == "solar":
                status = "WARN" if triggered else "OK"
            else:
                status = "ALERT" if triggered else "OK"

            updated_nodes.append(
                node.model_copy(
                    update={
                        "actual": round(actual, 2),
                        "triggered": triggered,
                        "status": status,
                    }
                )
            )
        return updated_nodes

    def _live_cluster(self, grid_id: str) -> SensorClusterModel:
        cluster = self.cluster_lookup[grid_id]
        triggered_labels = self._triggered_labels(grid_id)
        nodes = self._sensor_nodes_for_cycle(cluster, triggered_labels)
        triggered_count = sum(1 for node in nodes if node.triggered)
        health = "ORANGE" if triggered_count else "GREEN"
        reliability = 0.72 if triggered_count else 0.95
        return cluster.model_copy(
            update={
                "nodes": nodes,
                "health": health,
                "reliability_score": reliability,
                "last_ping": datetime.utcnow(),
            }
        )

    def _live_task(self, grid_id: str) -> DroneTaskModel:
        task = self.task_lookup[grid_id]
        if not self.drone_active:
            return task.model_copy(
                update={
                    "status": "scheduled",
                    "change_percent": 0.0,
                    "risk_level": "LOW RISK",
                }
            )

        change_percent = round(max(task.change_percent, 0.0), 2)
        risk_level = self._drone_risk_label(change_percent)
        return task.model_copy(
            update={
                "status": "scanning" if (self.live_cycle % 2 == 0) else "completed",
                "change_percent": change_percent,
                "risk_level": risk_level,
                "last_scanned_time": datetime.utcnow(),
            }
        )

    def _score_percentage(self, score: float) -> float:
        return round(max(0.0, min(score, 1.0)) * 100.0, 2)

    def _node_value(self, cluster: SensorClusterModel, label: str, default: float = 0.0) -> float:
        for node in cluster.nodes:
            if node.label == label:
                return float(node.actual)
        return default

    def _sound_score(self, sound_value: float, sound_threshold_high: float) -> float:
        medium = sound_threshold_high * 0.8
        low = sound_threshold_high * 0.6
        if sound_value >= sound_threshold_high:
            return 1.0
        if sound_value >= medium:
            return 0.7
        if sound_value >= low:
            return 0.4
        return 0.1

    def _motion_score(self, motion_value: float) -> float:
        return 1.0 if motion_value >= 1.0 else 0.1

    def _smoke_score(self, smoke_value: float, smoke_min: float = 0.0, smoke_max: float = 100.0) -> float:
        if smoke_max <= smoke_min:
            return 0.1
        normalized = (smoke_value - smoke_min) / (smoke_max - smoke_min)
        return round(max(0.0, min(normalized, 1.0)), 3)

    def _temperature_score(self, temp_value: float, temp_high: float) -> float:
        medium = temp_high * 0.85
        if temp_value >= temp_high:
            return 1.0
        if temp_value >= medium:
            return 0.6
        return 0.2

    def _sensor_location_score(self, cluster: SensorClusterModel) -> float:
        sound_value = self._node_value(cluster, "sound")
        motion_value = self._node_value(cluster, "motion")
        smoke_value = self._node_value(cluster, "smoke")
        temperature_value = self._node_value(cluster, "temperature")

        sound_score = self._sound_score(sound_value, 80.0)
        motion_score = self._motion_score(motion_value)
        smoke_score = self._smoke_score(smoke_value, 0.0, 100.0)
        temperature_score = self._temperature_score(temperature_value, 40.0)

        sensor_score = (
            (0.35 * sound_score)
            + (0.35 * motion_score)
            + (0.15 * smoke_score)
            + (0.15 * temperature_score)
        )
        return round(max(0.0, min(sensor_score, 1.0)), 4)

    def _aggregate_sensor_score(self, clusters: list[SensorClusterModel]) -> float:
        if not clusters:
            return 0.0
        location_scores = [self._sensor_location_score(cluster) for cluster in clusters]
        s_avg = sum(location_scores) / len(location_scores)
        n_active = sum(1 for score in location_scores if score >= 0.5)
        consistency_boost = 0.25 * (n_active / len(location_scores))
        return round(min(s_avg + consistency_boost, 1.0), 4)

    def _sensor_risk_level(self, sensor_score: float) -> str:
        if sensor_score >= 0.7:
            return "HIGH"
        if sensor_score >= 0.4:
            return "MEDIUM"
        return "LOW"

    def _drone_risk_label(self, change_percent: float) -> str:
        thresholds = get_config().thresholds
        if change_percent >= thresholds.drone_high_change * 100:
            return "HIGH RISK"
        if change_percent >= thresholds.drone_medium_change * 100:
            return "MEDIUM RISK"
        return "LOW RISK"

    def _drone_risk_level(self, change_ratio: float) -> str:
        return self._drone_risk_label(change_ratio * 100.0)

    def _final_risk_label(self, final_risk: float) -> str:
        if final_risk >= 0.7:
            return "HIGH RISK"
        if final_risk >= 0.4:
            return "MEDIUM RISK"
        return "LOW RISK"

    def _overall_live_risk(
        self,
        visible_clusters: list[SensorClusterModel],
        focus_task: DroneTaskModel | None,
    ) -> tuple[str, float, str, float, str, float]:
        sensor_score = self._aggregate_sensor_score(visible_clusters)
        sensor_level = self._sensor_risk_level(sensor_score)
        drone_score = 0.0
        drone_level = "SAFE"
        if self.drone_active and focus_task:
            drone_score = round(max(0.0, min(focus_task.change_percent / 100.0, 1.0)), 4)
            drone_level = self._drone_risk_level(drone_score)
        if self.drone_active:
            thresholds = get_config().thresholds
            if drone_score >= thresholds.drone_high_change:
                final_risk = 1.0
            elif drone_score >= thresholds.drone_medium_change:
                final_risk = 0.6
            else:
                final_risk = 0.2
        else:
            final_risk = sensor_score
        return self._final_risk_label(final_risk), final_risk, sensor_level, sensor_score, drone_level, drone_score

    def _sensor_summary(self, zone_id: str | None = None) -> list[dict]:
        visible_grids = self._visible_grids(zone_id)
        summary_map: dict[str, dict] = {}

        for label in SENSOR_LABEL_ORDER:
            summary_map[label] = {
                "label": label,
                "threshold": 0.0,
                "unit": "",
                "total_sensors": 0,
                "triggered_count": 0,
                "risk_percentage": 0.0,
                "triggered_sensors": [],
                "risk_zones": [],
            }

        for grid in visible_grids:
            cluster = self._live_cluster(grid.grid_id)
            task = self._live_task(grid.grid_id)
            local_sensor_score = self._sensor_location_score(cluster)
            drone_ratio = round(max(0.0, min(task.change_percent / 100.0, 1.0)), 4) if self.drone_active else 0.0
            if self.drone_active:
                thresholds = get_config().thresholds
                if drone_ratio >= thresholds.drone_high_change:
                    local_final_risk = 1.0
                elif drone_ratio >= thresholds.drone_medium_change:
                    local_final_risk = 0.6
                else:
                    local_final_risk = 0.2
            else:
                local_final_risk = local_sensor_score
            score_percentage = self._score_percentage(local_final_risk)

            for node in cluster.nodes:
                entry = summary_map[node.label]
                entry["threshold"] = node.threshold
                entry["unit"] = node.unit
                entry["total_sensors"] += 1

                if node.triggered:
                    entry["triggered_count"] += 1
                    triggered_item = {
                        "sensor_id": node.sensor_id,
                        "actual": node.actual,
                        "unit": node.unit,
                        "grid_id": grid.grid_id,
                        "zone_id": grid.zone_id,
                    }
                    entry["triggered_sensors"].append(triggered_item)
                    if score_percentage > 50:
                        entry["risk_zones"].append(
                            {
                                "grid_id": grid.grid_id,
                                "zone_id": grid.zone_id,
                                "score_percentage": score_percentage,
                                "sensor_id": node.sensor_id,
                            }
                        )

        result = []
        for label in SENSOR_LABEL_ORDER:
            entry = summary_map[label]
            if entry["total_sensors"]:
                entry["risk_percentage"] = round((entry["triggered_count"] / entry["total_sensors"]) * 100, 2)
            result.append(entry)
        return result

    def _sensor_thresholds(self) -> dict[str, dict[str, float | str]]:
        return {
            "temperature": {"threshold": 40.0, "unit": "C"},
            "motion": {"threshold": 1.0, "unit": "binary"},
            "smoke": {"threshold": 70.0, "unit": "ppm"},
            "sound": {"threshold": 80.0, "unit": "dB"},
        }

    def _sensor_table_rows(self, zone_id: str | None = None) -> list[dict]:
        rows: list[dict] = []
        for grid in self._visible_grids(zone_id):
            cluster = self._live_cluster(grid.grid_id)
            local_sensor_score = self._sensor_location_score(cluster)
            row = {
                "grid_id": grid.grid_id,
                "zone_id": grid.zone_id,
                "temperature": "-",
                "motion": "-",
                "smoke": "-",
                "sound": "-",
                "risk": self._final_risk_label(local_sensor_score),
                "risk_percentage": self._score_percentage(local_sensor_score),
            }

            for node in cluster.nodes:
                if node.label not in {"temperature", "motion", "smoke", "sound"}:
                    continue
                row[node.label] = f"{node.actual} {node.unit}"

            rows.append(row)

        risk_order = {"HIGH RISK": 0, "MEDIUM RISK": 1, "LOW RISK": 2}
        rows.sort(key=lambda row: (risk_order.get(row["risk"], 9), -row["risk_percentage"], row["grid_id"]))
        return rows

    def _build_alerts(self) -> list[AlertModel]:
        alerts: list[AlertModel] = []
        for grid in self.grids:
            cluster = self._live_cluster(grid.grid_id)
            task = self._live_task(grid.grid_id)
            local_sensor_score = self._sensor_location_score(cluster)
            local_sensor_level = self._sensor_risk_level(local_sensor_score)
            drone_score = round(max(0.0, min(task.change_percent / 100.0, 1.0)), 4) if self.drone_active else 0.0
            drone_level = self._drone_risk_level(drone_score)
            if self.drone_active:
                thresholds = get_config().thresholds
                if drone_score >= thresholds.drone_high_change:
                    final_risk = 1.0
                elif drone_score >= thresholds.drone_medium_change:
                    final_risk = 0.6
                else:
                    final_risk = 0.2
            else:
                final_risk = local_sensor_score
            risk = self._final_risk_label(final_risk)
            score_percentage = self._score_percentage(final_risk)
            triggered = [node.sensor_id for node in cluster.nodes if node.triggered]
            if final_risk < 0.4:
                continue

            lat, lon = task_location(task, self.grid_lookup)
            source_items = triggered if triggered else (["drone-change"] if self.drone_active else ["sensor"])
            alerts.append(
                AlertModel(
                    alert_id=f"ALT-{len(alerts) + 1:04d}",
                    timestamp=datetime.utcnow(),
                    zone_id=grid.zone_id,
                    grid_id=grid.grid_id,
                    source="drone" if self.drone_active else "sensor",
                    source_label=", ".join(source_items),
                    message=f"{risk} ({score_percentage:.0f}%) in {grid.grid_id}, {grid.zone_id}. Drone image comparison change={task.change_percent:.2f}% and status={drone_level}." if self.drone_active else f"{risk} ({score_percentage:.0f}%) in {grid.grid_id}, {grid.zone_id}. Sensor={local_sensor_level} ({self._score_percentage(local_sensor_score):.0f}%). Area is under risk.",
                    risk=risk,
                    lat=lat,
                    lon=lon,
                    image=task.image_name if self.drone_active else None,
                )
            )
        return alerts

    def toggle_drone(self, state: bool) -> bool:
        self.drone_active = state
        self.alerts = self._build_alerts()
        return self.drone_active

    def get_live_payload(self, zone_id: str | None = None) -> dict:
        focus_grid_id = self._focus_grid_id(zone_id)
        focus_grid = self.grid_lookup.get(focus_grid_id) if focus_grid_id else None
        focus_cluster = self._live_cluster(focus_grid_id) if focus_grid_id else None
        focus_task = self._live_task(focus_grid_id) if focus_grid_id else None
        visible_grids = self._visible_grids(zone_id)
        visible_clusters = [self._live_cluster(grid.grid_id) for grid in visible_grids]

        risk = "LOW RISK"
        score = 0.0
        triggered: list[str] = []
        sensor_risk_level = "LOW"
        sensor_risk_percentage = 0.0
        drone_risk_level = "SAFE"
        if focus_task and focus_cluster and focus_grid:
            risk, score, sensor_risk_level, sensor_risk_percentage, drone_risk_level, drone_score = self._overall_live_risk(visible_clusters, focus_task)
            triggered = [node.sensor_id for node in focus_cluster.nodes if node.triggered]

        visible_alerts = [alert for alert in self.alerts if not zone_id or alert.zone_id == zone_id]
        if focus_grid and focus_task and risk in {"HIGH RISK", "MEDIUM RISK"}:
            focus_alert_exists = any(alert.grid_id == focus_grid.grid_id for alert in visible_alerts)
            if not focus_alert_exists:
                lat, lon = task_location(focus_task, self.grid_lookup)
                focus_source_items = triggered if triggered else (["drone-change"] if self.drone_active else ["sensor"])
                visible_alerts.insert(
                    0,
                    AlertModel(
                        alert_id="ALT-FOCUS",
                        timestamp=datetime.utcnow(),
                        zone_id=focus_grid.zone_id,
                        grid_id=focus_grid.grid_id,
                        source="drone" if self.drone_active else "sensor",
                        source_label=", ".join(focus_source_items),
                        message=f"{risk} ({self._score_percentage(score):.0f}%) in {focus_grid.grid_id}, {focus_grid.zone_id}. Drone image comparison change={focus_task.change_percent:.2f}% and current live focus area is under risk." if self.drone_active else f"{risk} ({self._score_percentage(score):.0f}%) in {focus_grid.grid_id}, {focus_grid.zone_id}. Current live focus area is under risk.",
                        risk=risk,
                        lat=lat,
                        lon=lon,
                        image=focus_task.image_name if self.drone_active else None,
                    ).model_dump()
                )

        return {
            "mode": "DRONE_ACTIVE" if self.drone_active else "SENSOR_ACTIVE",
            "zone_id": zone_id,
            "refresh_seconds": 60,
            "cycle_id": self.live_cycle,
            "analysis_source": "drone-only image comparison" if self.drone_active else "sensor-only analysis",
            "drone": focus_task.model_dump() if focus_task else None,
            "sensor_cluster": focus_cluster.model_dump() if focus_cluster else None,
            "sensor_summary": self._sensor_summary(zone_id),
            "sensor_thresholds": self._sensor_thresholds(),
            "sensor_table": self._sensor_table_rows(zone_id),
            "image_pair": {
                "yesterday": f"/data/raw/drone/21-04-26/{focus_task.image_name}" if self.drone_active and focus_task and focus_task.image_name else None,
                "today": f"/data/raw/drone/22-04-26/{focus_task.image_name}" if self.drone_active and focus_task and focus_task.image_name else None,
                "image_name": focus_task.image_name if self.drone_active and focus_task else None,
                "change_percent": focus_task.change_percent if self.drone_active and focus_task else 0.0,
                "risk_level": self._drone_risk_label(focus_task.change_percent) if self.drone_active and focus_task else "LOW RISK",
            },
            "risk": risk,
            "score": score,
            "score_percentage": self._score_percentage(score),
            "sensor_risk_level": sensor_risk_level,
            "sensor_risk_percentage": self._score_percentage(sensor_risk_percentage),
            "drone_risk_level": drone_risk_level,
            "drone_thresholds": {
                "medium_change_percent": get_config().thresholds.drone_medium_change * 100,
                "high_change_percent": get_config().thresholds.drone_high_change * 100,
            },
            "triggered_sources": triggered,
            "alerts": [alert if isinstance(alert, dict) else alert.model_dump() for alert in visible_alerts[:20]],
            "zones": [zone.model_dump() for zone in self.zones],
            "summary": {
                "grid_count": len(self.grids),
                "hotspot_count": sum(1 for grid in self.grids if grid.hotspot_flag),
                "sensor_count": len(self.sensor_clusters),
                "drone_count": len({task.drone_id for task in self.drone_tasks}),
            },
        }

    def get_dashboard_payload(self) -> dict:
        return {
            "forest_name": "Sathyamangalam Tiger Reserve Forest",
            "grids": [grid.model_dump() for grid in self.grids],
            "zones": [zone.model_dump() for zone in self.zones],
            "hotspots": [grid.model_dump() for grid in self.grids if grid.hotspot_flag],
            "sensor_clusters": [cluster.model_dump() for cluster in self.sensor_clusters],
            "drone_tasks": [task.model_dump() for task in self.drone_tasks],
        }

    def simulate(self, payload: SimulationRequest) -> SimulationResponse:
        from backend.models.sensor_cluster import SensorClusterModel, SensorNode

        cluster = SensorClusterModel(
            cluster_id="SIM",
            grid_id=payload.grid_id or "SIM-GRID",
            zone_id=payload.zone_id or "SIM-ZONE",
            hotspot_flag=payload.hotspot_flag,
            placement_km=1 if payload.hotspot_flag else 5,
            health="GREEN" if payload.reliability_score >= 0.8 else "ORANGE" if payload.reliability_score >= 0.4 else "RED",
            reliability_score=payload.reliability_score,
            last_ping=datetime.utcnow(),
            nodes=[
                SensorNode(sensor_id="temp1", label="temperature", actual=payload.temperature, threshold=40.0, triggered=payload.temperature >= 40.0, unit="C", status="ALERT" if payload.temperature >= 40.0 else "OK"),
                SensorNode(sensor_id="mov1", label="motion", actual=payload.motion, threshold=1.0, triggered=payload.motion >= 1.0, unit="binary", status="ALERT" if payload.motion >= 1.0 else "OK"),
                SensorNode(sensor_id="sm1", label="smoke", actual=payload.smoke, threshold=70.0, triggered=payload.smoke >= 70.0, unit="ppm", status="ALERT" if payload.smoke >= 70.0 else "OK"),
                SensorNode(sensor_id="so1", label="sound", actual=payload.sound, threshold=80.0, triggered=payload.sound >= 80.0, unit="dB", status="ALERT" if payload.sound >= 80.0 else "OK"),
                SensorNode(sensor_id="solar1", label="solar", actual=payload.solar_health, threshold=55.0, triggered=payload.solar_health < 55.0, unit="%", status="WARN" if payload.solar_health < 55.0 else "OK"),
            ],
        )
        risk, score, triggered = calculate_risk(payload.drone_change_percent, cluster, payload.hotspot_flag)
        explanation = f"Risk {risk} from drone change {payload.drone_change_percent:.1f}% with {len(triggered)} triggered sensor channels and reliability {payload.reliability_score:.2f}."
        return SimulationResponse(
            risk=risk,
            score=score,
            triggered_sources=triggered,
            explanation=explanation,
            drone_change_percent=payload.drone_change_percent,
        )

    def simulate_with_uploaded_images(
        self,
        payload: SimulationRequest,
        yesterday_bytes: bytes,
        today_bytes: bytes,
    ) -> SimulationResponse:
        yesterday = cv2.imdecode(np.frombuffer(yesterday_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        today = cv2.imdecode(np.frombuffer(today_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if yesterday is None or today is None:
            raise ValueError("Unable to read one or both uploaded images.")

        yesterday = cv2.resize(yesterday, (256, 256))
        today = cv2.resize(today, (256, 256))
        gray_yesterday = cv2.cvtColor(yesterday, cv2.COLOR_BGR2GRAY)
        gray_today = cv2.cvtColor(today, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_yesterday, gray_today)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        change_percent = round((float(np.sum(thresh > 0)) / float(256 * 256)) * 100, 2)

        payload_with_change = payload.model_copy(update={"drone_change_percent": change_percent})
        result = self.simulate(payload_with_change)
        return result.model_copy(
            update={
                "explanation": f"{result.explanation} Uploaded drone images produced a computed vegetation change of {change_percent:.2f}%.",
                "drone_change_percent": change_percent,
            }
        )


platform_state = PlatformState()


async def refresh_loop() -> None:
    while True:
        await asyncio.sleep(60)
        platform_state.refresh()
