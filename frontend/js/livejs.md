let livePollTimer;
let lastLiveCycleId = null;
let latestSensorRows = [];
let latestSensorThresholds = {};

function renderZoneOptions(zones) {
  const select = document.getElementById("zoneSelector");
  const currentValue = select.value;
  select.innerHTML = `<option value="">All zones</option>` + zones.map(zone => `<option value="${zone.zone_id}">${zone.name}</option>`).join("");
  if (currentValue) {
    select.value = currentValue;
  }
}

function renderSensorTable(sensorRows, sensorThresholds) {
  const tableWrap = document.getElementById("sensorCards");
  const thresholdNote = document.getElementById("sensorThresholdNote");
  const riskFilter = document.getElementById("sensorRiskFilter")?.value || "ALL";
  const thresholds = sensorThresholds || {};

  latestSensorRows = sensorRows || [];
  latestSensorThresholds = thresholds;

  thresholdNote.textContent = [
    `Temperature threshold: ${thresholds.temperature?.threshold ?? "-"} ${thresholds.temperature?.unit ?? ""}`,
    `Motion threshold: ${thresholds.motion?.threshold ?? "-"} ${thresholds.motion?.unit ?? ""}`,
    `Smoke threshold: ${thresholds.smoke?.threshold ?? "-"} ${thresholds.smoke?.unit ?? ""}`,
    `Sound threshold: ${thresholds.sound?.threshold ?? "-"} ${thresholds.sound?.unit ?? ""}`
  ].join(" | ");

  const filteredRows = latestSensorRows.filter(row => riskFilter === "ALL" || row.risk === riskFilter);

  if (!filteredRows.length) {
    tableWrap.innerHTML = `<div class="list-item">No sensor rows available.</div>`;
    return;
  }

  tableWrap.innerHTML = `
    <div class="sensor-table-wrap">
      <table class="sensor-table">
        <thead>
          <tr>
            <th>Grid</th>
            <th>Zone</th>
            <th>Temperature</th>
            <th>Motion</th>
            <th>Smoke</th>
            <th>Sound</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          ${filteredRows.map(row => `
            <tr>
              <td>${row.grid_id}</td>
              <td>${row.zone_id}</td>
              <td>${row.temperature}</td>
              <td>${row.motion == 1 || row.motion === true || String(row.motion).toLowerCase() === "true" ? "Yes" : "No"}</td>
              <td>${row.smoke}</td>
              <td>${row.sound}</td>
              <td><span class="table-risk ${riskClass(row.risk)}">${row.risk} (${row.risk_percentage}%)</span></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function buildZoneFeedFromSensorSummary(sensorSummary) {
  const items = [];
  (sensorSummary || []).forEach(sensorType => {
    (sensorType.risk_zones || []).forEach(zoneRisk => {
      items.push({
        risk: zoneRisk.score_percentage >= 70 ? "HIGH RISK" : "MEDIUM RISK",
        grid_id: zoneRisk.grid_id,
        zone_id: zoneRisk.zone_id,
        source: sensorType.label,
        source_label: `${zoneRisk.sensor_id} | ${sensorType.label}`,
        message: `${zoneRisk.grid_id}, ${zoneRisk.zone_id} is under risk from ${sensorType.label} with overall score ${zoneRisk.score_percentage}%`
      });
    });
  });
  return items;
}

function pulseLiveChanges() {
  [
    "liveMode",
    "liveRisk",
    "liveAlerts",
    "liveRefreshNote",
    "analysisModeNote",
    "comparisonLabel",
    "zoneAlerts",
    "alertsFeed",
    "sensorCards",
    "droneTask",
    "droneGrid",
    "droneChange",
    "clusterHealth",
    "clusterReliability"
  ].forEach(id => {
    const node = document.getElementById(id);
    if (!node) return;
    node.classList.remove("live-blink");
    void node.offsetWidth;
    node.classList.add("live-blink");
  });
}

function renderLive(payload) {
  const isNewCycle = payload.cycle_id != null && payload.cycle_id !== lastLiveCycleId;
  lastLiveCycleId = payload.cycle_id ?? lastLiveCycleId;

  setText("liveMode", payload.mode);
  setText("liveRisk", payload.risk || "LOW RISK");
  setText("liveScore", payload.score_percentage != null ? `${payload.score_percentage}%` : payload.score);
  setText("liveAlerts", payload.alerts.length);
  setText("liveSensors", payload.summary.sensor_count);
  setText("liveSensorsCopy", payload.summary.sensor_count);
  setText("liveDrones", payload.summary.drone_count);
  setText("liveRefreshNote", `Live feed refreshes every ${payload.refresh_seconds / 60} minute for sensor and drone data.`);
  setText("analysisModeNote", payload.analysis_source);

  if (document.getElementById("zoneSelector").options.length <= 1) {
    renderZoneOptions(payload.zones);
  }

  const drone = payload.drone;
  const imagePair = payload.image_pair;

  if (drone) {
    setText("droneGrid", `${drone.grid_id} | ${drone.zone_id}`);
    setText("droneTask", payload.mode === "DRONE_ACTIVE" ? `${drone.drone_id} | ${drone.status}` : "Drone offline | sensor mode");
    setText("droneChange", payload.mode === "DRONE_ACTIVE" ? `${drone.change_percent.toFixed(2)}%` : "0.00%");
    setText("droneSchedule", formatDate(drone.scheduled_for));
    setText("clusterHealth", payload.sensor_cluster?.health || "-");
    setText("clusterReliability", payload.sensor_cluster?.reliability_score || "-");
  }

  // if (payload.mode === "DRONE_ACTIVE" && imagePair && imagePair.yesterday && imagePair.today) {
  //   document.getElementById("yesterdayImage").src = `${API_BASE}${imagePair.yesterday}`;
  //   document.getElementById("todayImage").src = `${API_BASE}${imagePair.today}`;
  //   setText("comparisonLabel", `${imagePair.image_name} | same grid comparison | change ${imagePair.change_percent.toFixed(2)}%`);
  // } else {
  //   document.getElementById("yesterdayImage").removeAttribute("src");
  //   document.getElementById("todayImage").removeAttribute("src");
  //   setText("comparisonLabel", "Sensor-only mode is active. Launch the drone to compare yesterday and today images for this same grid.");
  // }
  if (payload.mode === "DRONE_ACTIVE" && imagePair && imagePair.yesterday && imagePair.today) {
    document.getElementById("yesterdayImage").src = `${API_BASE}${imagePair.yesterday}`;
    document.getElementById("todayImage").src = `${API_BASE}${imagePair.today}`;
    document.getElementById("yesterdayPlaceholder").classList.add("hidden");
    document.getElementById("todayPlaceholder").classList.add("hidden");
    setText("comparisonLabel", `${imagePair.image_name} | same grid comparison | change ${imagePair.change_percent.toFixed(2)}%`);
  } else {
    document.getElementById("yesterdayImage").removeAttribute("src");
    document.getElementById("todayImage").removeAttribute("src");
    document.getElementById("yesterdayPlaceholder").classList.remove("hidden");
    document.getElementById("todayPlaceholder").classList.remove("hidden");
    setText("comparisonLabel", "Sensor-only mode is active. Launch the drone to compare yesterday and today images for this same grid.");
  }

  renderSensorTable(payload.sensor_table, payload.sensor_thresholds);


  if (payload.mode === "DRONE_ACTIVE" && imagePair && imagePair.yesterday && imagePair.today) {
    document.getElementById("yesterdayImage").src = `${API_BASE}${imagePair.yesterday}`;
    document.getElementById("todayImage").src = `${API_BASE}${imagePair.today}`;
    document.getElementById("yesterdayPlaceholder").classList.add("hidden");
    document.getElementById("todayPlaceholder").classList.add("hidden");
    setText("comparisonLabel", `${imagePair.image_name} | same grid comparison | change ${imagePair.change_percent.toFixed(2)}%`);

    const changePercent = imagePair.change_percent ?? 0;
    const isHighRisk = changePercent >= 15;
    const droneRiskEl = document.getElementById("droneRiskBanner");
    droneRiskEl.className = `drone-risk-banner ${isHighRisk ? "drone-risk-high" : "drone-risk-safe"}`;
    droneRiskEl.innerHTML = `
      <div class="drone-risk-icon">${isHighRisk ? "⚠" : "✓"}</div>
      <div class="drone-risk-body">
        <span class="drone-risk-label">Drone Image Analysis</span>
        <span class="drone-risk-value">${isHighRisk ? "HIGH RISK" : "SAFE"}</span>
        <span class="drone-risk-detail">${changePercent.toFixed(2)}% canopy change detected between yesterday and today</span>
      </div>
    `;
    droneRiskEl.style.display = "flex";
  } else {
    document.getElementById("yesterdayImage").removeAttribute("src");
    document.getElementById("todayImage").removeAttribute("src");
    document.getElementById("yesterdayPlaceholder").classList.remove("hidden");
    document.getElementById("todayPlaceholder").classList.remove("hidden");
    setText("comparisonLabel", "Sensor-only mode is active. Launch the drone to compare yesterday and today images for this same grid.");
    document.getElementById("droneRiskBanner").style.display = "none";
  }
  // const zoneFeedItems = payload.alerts.length ? payload.alerts.slice(0, 6) : buildZoneFeedFromSensorSummary(payload.sensor_summary).slice(0, 6);
  // const alertPanel = document.getElementById("zoneAlerts");
  // alertPanel.innerHTML = zoneFeedItems.map(alert => `
  //   <div class="alert-card ${riskClass(alert.risk)}">
  //     <strong>${alert.grid_id} | ${alert.risk}</strong>
  //     <div class="alert-meta">
  //       <span>${String(alert.source).toUpperCase()}</span>
  //       <span>${alert.timestamp ? formatDate(alert.timestamp) : "Live summary"}</span>
  //     </div>
  //     <div class="small">Source: ${alert.source_label}</div>
  //     <div>${alert.message}</div>
  //   </div>
  // `).join("") || `<div class="list-item">No active alerts in this zone right now.</div>`;

  const feed = document.getElementById("alertsFeed");
  feed.innerHTML = payload.alerts.map(alert => `
    <div class="alert-card ${riskClass(alert.risk)}">
      <strong>${alert.risk}</strong>
      <div class="alert-meta">
        <span>${alert.zone_id}</span>
        <span>${alert.grid_id}</span>
      </div>
      <div class="small">${alert.source_label}</div>
      <div>${alert.message}</div>
    </div>
  `).join("") || `<div class="list-item">No alerts crossed the 50% overall risk threshold in this cycle.</div>`;

  if (isNewCycle) {
    pulseLiveChanges();
  }
}

async function fetchLiveSnapshot(zoneId = "") {
  const suffix = zoneId ? `?zone_id=${encodeURIComponent(zoneId)}` : "";
  try {
    return await getJson(`/live-feed/status${suffix}`);
  } catch (error) {
    console.warn("Falling back to /live-data:", error.message);
    return getJson(`/live-data${suffix}`);
  }
}

async function refreshLiveFeed(zoneId = "") {
  const suffix = zoneId ? `?zone_id=${encodeURIComponent(zoneId)}` : "";
  try {
    return await getJson(`/live-feed/refresh${suffix}`, { method: "POST" });
  } catch (error) {
    console.warn("Falling back to /live-data refresh path:", error.message);
    return getJson(`/live-data${suffix}`);
  }
}

async function loadLive(zoneId = "") {
  const payload = await fetchLiveSnapshot(zoneId);
  renderLive(payload);
}

async function toggleDrone(state) {
  await getJson(`/toggle-drone?state=${state}`, { method: "POST" });
  const payload = await refreshLiveFeed(document.getElementById("zoneSelector").value);
  renderLive(payload);
}

function startLivePolling() {
  if (livePollTimer) {
    clearInterval(livePollTimer);
  }
  livePollTimer = setInterval(async () => {
    const zoneValue = document.getElementById("zoneSelector").value;
    try {
      const payload = await refreshLiveFeed(zoneValue);
      renderLive(payload);
    } catch (error) {
      console.warn("Live refresh failed:", error.message);
      setText("analysisModeNote", "Live refresh failed. Retrying on next cycle.");
    }
  }, 60000);
}

document.getElementById("zoneSelector").addEventListener("change", async event => {
  try {
    const payload = await fetchLiveSnapshot(event.target.value);
    renderLive(payload);
  } catch (error) {
    console.warn("Zone change load failed:", error.message);
  }
});

document.getElementById("sensorRiskFilter").addEventListener("change", () => {
  renderSensorTable(latestSensorRows, latestSensorThresholds);
});

document.getElementById("launchDrone").addEventListener("click", () => toggleDrone(true).catch(console.error));
document.getElementById("recallDrone").addEventListener("click", () => toggleDrone(false).catch(console.error));

loadLive().then(() => {
  startLivePolling();
}).catch(error => {
  console.warn("Initial live load failed:", error.message);
  setText("liveRisk", "-");
  setText("analysisModeNote", "Unable to load live feed right now. Please retry.");
});
