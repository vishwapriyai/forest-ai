let dashboardMap;
let zoneRects = [];
let gridRects = [];
let sensorMarkers = [];
let droneMarkers = [];
let currentDashboardPayload;
let dashboardForestBounds;
const DEFAULT_GRID_PAN_OFFSET = [-289, 184];

function ensureDashboardMap(center) {
  if (!dashboardMap) {
    dashboardMap = L.map("dashboardMap").setView(center, 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(dashboardMap);
  }
}

function clearDashboardLayers() {
  [...zoneRects, ...gridRects, ...sensorMarkers, ...droneMarkers].forEach(layer => dashboardMap.removeLayer(layer));
  zoneRects = [];
  gridRects = [];
  sensorMarkers = [];
  droneMarkers = [];
}

function buildForestBounds(grids) {
  if (!grids.length) return null;
  return L.latLngBounds(
    grids.flatMap(grid => [
      [grid.lat_min, grid.lon_min],
      [grid.lat_max, grid.lon_max]
    ])
  );
}

function zoneColor(zoneId) {
  const num = Number(zoneId.split("-")[1] || "1");
  return getComputedStyle(document.documentElement).getPropertyValue(`--zone-${num}`).trim() || "#4a7c59";
}

function renderSummary(payload) {
  currentDashboardPayload = payload;
  setText("forestName", payload.forest_name);
  setText("gridCount", payload.grids.length);
  setText("zoneCount", payload.zones.length);
  setText("hotspotCount", payload.hotspots.length);
  setText("sensorCount", payload.sensor_clusters.length);
  setText("droneCount", new Set(payload.drone_tasks.map(task => task.drone_id)).size);

  const zoneList = document.getElementById("zoneList");
  zoneList.innerHTML = payload.zones.map(zone => `
    <div class="list-item">
      <strong>${zone.name}</strong>
      <div class="small">${zone.grid_ids.length} grids</div>
      <div class="small">${zone.lat_min.toFixed(3)}, ${zone.lon_min.toFixed(3)} to ${zone.lat_max.toFixed(3)}, ${zone.lon_max.toFixed(3)}</div>
      <button class="secondary" onclick="zoomToZone('${zone.zone_id}')">Zoom to ${zone.zone_id}</button>
    </div>
  `).join("");

  const hotspotList = document.getElementById("hotspotList");
  hotspotList.innerHTML = payload.hotspots.map(grid => `
    <div class="list-item">
      <strong>${grid.grid_id}</strong>
      <div class="small">${grid.zone_id} | scan every ${grid.scan_frequency_days} day(s)</div>
      <div class="small">Sensor density ${grid.sensor_density}</div>
    </div>
  `).join("");
}

function fitDashboardToGrid() {
  if (!dashboardMap || !dashboardForestBounds) return;
  dashboardMap.fitBounds(dashboardForestBounds, {
    padding: [56, 56]
  });
  dashboardMap.panBy(DEFAULT_GRID_PAN_OFFSET, { animate: false });
}

function drawMap(payload) {
  const center = [payload.zones[0]?.center_lat || 11.45, payload.zones[0]?.center_lon || 76.8];
  ensureDashboardMap(center);
  clearDashboardLayers();
  dashboardForestBounds = buildForestBounds(payload.grids);

  payload.zones.forEach(zone => {
    const rect = L.rectangle(
      [[zone.lat_min, zone.lon_min], [zone.lat_max, zone.lon_max]],
      {
        color: zoneColor(zone.zone_id),
        weight: 3,
        fillOpacity: 0.14,
        dashArray: "6 5"
      }
    ).addTo(dashboardMap).bindPopup(`${zone.name}<br>${zone.grid_ids.length} grids`);
    zoneRects.push(rect);
  });

  payload.grids.forEach(grid => {
    const rect = L.rectangle(
      [[grid.lat_min, grid.lon_min], [grid.lat_max, grid.lon_max]],
      {
        color: grid.hotspot_flag ? "#bf2f2f" : zoneColor(grid.zone_id),
        weight: grid.hotspot_flag ? 1.8 : 1,
        fillColor: grid.hotspot_flag ? "#d62828" : zoneColor(grid.zone_id),
        fillOpacity: grid.hotspot_flag ? 0.72 : 0.09
      }
    ).addTo(dashboardMap).bindTooltip(`${grid.grid_id} | ${grid.zone_id}${grid.hotspot_flag ? " | hotspot" : ""}`);
    gridRects.push(rect);
  });

  payload.sensor_clusters.forEach(cluster => {
    const grid = payload.grids.find(item => item.grid_id === cluster.grid_id);
    if (!grid) return;
    const marker = L.circleMarker([grid.center_lat, grid.center_lon], {
      radius: 6,
      color: cluster.health === "GREEN" ? "#37a36b" : cluster.health === "ORANGE" ? "#d18a2a" : "#bf4b3d",
      fillOpacity: 0.9
    }).addTo(dashboardMap).bindPopup(`${cluster.cluster_id}<br>${cluster.health}<br>${cluster.grid_id}`);
    sensorMarkers.push(marker);
  });

  payload.drone_tasks.filter(task => task.status === "completed" || task.status === "scanning").forEach(task => {
    const grid = payload.grids.find(item => item.grid_id === task.grid_id);
    if (!grid) return;
    const marker = L.marker([grid.center_lat, grid.center_lon], {
      icon: L.divIcon({
        className: "",
        html: `<div style="width:18px;height:18px;border-radius:50%;background:${task.status === "completed" ? "#2c7be5" : "#37a36b"};border:2px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.18)"></div>`,
        iconSize: [18, 18]
      })
    }).addTo(dashboardMap).bindPopup(`${task.drone_id}<br>${task.grid_id}<br>${task.status}`);
    droneMarkers.push(marker);
  });

  fitDashboardToGrid();

  requestAnimationFrame(() => {
    dashboardMap.invalidateSize();
    fitDashboardToGrid();
  });

  setTimeout(() => {
    dashboardMap.invalidateSize();
    fitDashboardToGrid();
  }, 180);
}

window.zoomToZone = async function zoomToZone(zoneId) {
  const payload = currentDashboardPayload || await getJson("/dashboard-data");
  const zone = payload.zones.find(item => item.zone_id === zoneId);
  if (!zone || !dashboardMap) return;
  dashboardMap.fitBounds([[zone.lat_min, zone.lon_min], [zone.lat_max, zone.lon_max]], { padding: [30, 30] });
};

async function initDashboard() {
  const payload = await getJson("/dashboard-data");
  renderSummary(payload);
  drawMap(payload);

  window.addEventListener("resize", () => {
    if (!dashboardMap) return;
    dashboardMap.invalidateSize();
    fitDashboardToGrid();
  });
}

initDashboard().catch(error => {
  setText("forestName", `Unable to load dashboard: ${error.message}`);
});
