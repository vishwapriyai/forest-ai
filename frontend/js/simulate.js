let simulationMetadata = {
  thresholds: {},
  grids: [],
  zones: []
};

async function loadSimulationMetadata() {
  simulationMetadata = await getJson("/simulation-metadata");
  const select = document.getElementById("simulateZone");
  select.innerHTML = simulationMetadata.zones.map(zone => `<option value="${zone.zone_id}">${zone.name}</option>`).join("");
  applyThresholdLabels();
  syncZoneFromGrid();
  renderRiskGuide();
}

function applyThresholdLabels() {
  const t = simulationMetadata.thresholds;
  setText("temperatureLabel", `Temperature (threshold ${t.temperature} C)`);
  setText("smokeLabel", `Smoke (threshold ${t.smoke} ppm)`);
  setText("soundLabel", `Sound (threshold ${t.sound} dB)`);
  setText("motionLabel", `Motion (threshold ${t.motion})`);
  setText("solarLabel", `Solar Health (threshold ${t.solar_health} %)`);
  setText("droneChangeLabel", `Drone Change % (medium ${t.drone_medium_change_percent}%, high ${t.drone_high_change_percent}%)`);
}

function renderRiskGuide() {
  const t = simulationMetadata.thresholds;
  setText(
    "riskClassificationGuide",
    `Low risk is below score ${t.medium_risk_score}. Medium risk is from ${t.medium_risk_score} to below ${t.high_risk_score}. High risk is ${t.high_risk_score} and above.`
  );
}

function syncZoneFromGrid() {
  const gridId = document.getElementById("simulateGrid").value.trim().toUpperCase();
  const zoneSelect = document.getElementById("simulateZone");
  const matchedGrid = simulationMetadata.grids.find(grid => grid.grid_id.toUpperCase() === gridId);
  if (matchedGrid) {
    zoneSelect.value = matchedGrid.zone_id;
    setText("gridLookupNote", `Mapped automatically to ${matchedGrid.zone_id}.`);
    document.getElementById("simulateHotspot").checked = !!matchedGrid.hotspot_flag;
  } else {
    setText("gridLookupNote", "Grid not found in forest map. Zone stays on current selection.");
  }
}

function payloadFromForm() {
  return {
    grid_id: document.getElementById("simulateGrid").value || "SIM-GRID",
    zone_id: document.getElementById("simulateZone").value,
    hotspot_flag: document.getElementById("simulateHotspot").checked,
    reliability_score: Number(document.getElementById("simulateReliability").value),
    temperature: Number(document.getElementById("simulateTemperature").value),
    smoke: Number(document.getElementById("simulateSmoke").value),
    sound: Number(document.getElementById("simulateSound").value),
    motion: Number(document.getElementById("simulateMotion").value),
    solar_health: Number(document.getElementById("simulateSolar").value),
    drone_change_percent: Number(document.getElementById("simulateDroneChange").value)
  };
}

// function renderSimulationResult(result) {
//   setText("simulationRisk", result.risk);
//   setText("simulationScore", result.score);
//   setText("simulationExplanation", result.explanation);
//   setText("computedDroneChange", result.drone_change_percent ?? "-");
//   document.getElementById("triggeredList").innerHTML = result.triggered_sources.map(source => `<span class="badge red">${source}</span>`).join("") || `<span class="badge green">No triggers</span>`;
// }

function renderSimulationResult(result) {
  setText("simulationRisk", result.risk);
  setText("simulationScore", result.score);
  setText("simulationExplanation", result.explanation);
  setText("computedDroneChange", result.drone_change_percent ?? "-");
}

async function runSimulation() {
  syncZoneFromGrid();
  const payload = payloadFromForm();
  const result = await getJson("/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  renderSimulationResult(result);
}

async function runUploadSimulation() {
  syncZoneFromGrid();
  const formData = new FormData();
  formData.append("grid_id", document.getElementById("simulateGrid").value || "SIM-GRID");
  formData.append("zone_id", document.getElementById("simulateZone").value);
  formData.append("hotspot_flag", document.getElementById("simulateHotspot").checked ? "true" : "false");
  formData.append("reliability_score", document.getElementById("simulateReliability").value);
  formData.append("temperature", document.getElementById("simulateTemperature").value);
  formData.append("smoke", document.getElementById("simulateSmoke").value);
  formData.append("sound", document.getElementById("simulateSound").value);
  formData.append("motion", document.getElementById("simulateMotion").value);
  formData.append("solar_health", document.getElementById("simulateSolar").value);

  const yesterday = document.getElementById("uploadYesterday").files[0];
  const today = document.getElementById("uploadToday").files[0];
  if (!yesterday || !today) {
    setText("simulationExplanation", "Please upload both yesterday and today drone images.");
    return;
  }

  formData.append("yesterday_image", yesterday);
  formData.append("today_image", today);

  const response = await fetch(`${API_BASE}/simulate-upload`, {
    method: "POST",
    body: formData
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.detail || "Image simulation failed.");
  }
  renderSimulationResult(result);
}

document.getElementById("simulateForm").addEventListener("submit", event => {
  event.preventDefault();
  runSimulation().catch(error => {
    setText("simulationExplanation", error.message);
  });
});

document.getElementById("simulateUploadButton").addEventListener("click", event => {
  event.preventDefault();
  runUploadSimulation().catch(error => {
    setText("simulationExplanation", error.message);
  });
});

document.getElementById("simulateGrid").addEventListener("input", () => {
  syncZoneFromGrid();
});

loadSimulationMetadata().then(runSimulation).catch(error => {
  setText("simulationExplanation", error.message);
});
