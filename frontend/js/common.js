const IS_STATIC = window.location.hostname.includes("github.io") || window.location.protocol === "file:";
const API_BASE = IS_STATIC ? "" : window.location.origin;

function riskClass(risk) {
  if (risk === "HIGH RISK") return "high";
  if (risk === "MEDIUM RISK") return "medium";
  return "low";
}

function healthBadge(health) {
  if (health === "GREEN") return "green";
  if (health === "ORANGE") return "orange";
  return "red";
}

async function getJson(path, options) {
  let url = `${API_BASE}${path}`;
  let fetchOptions = { ...options };

  if (IS_STATIC) {
    const cleanPath = path.split("?")[0];
    if (cleanPath === "/dashboard-data") {
      url = "data/dashboard-data.json";
      fetchOptions.method = "GET";
    } else if (cleanPath === "/simulation-metadata") {
      url = "data/simulation-metadata.json";
      fetchOptions.method = "GET";
    } else if (cleanPath === "/live-data" || cleanPath === "/live-feed/status" || cleanPath === "/live-feed/refresh") {
      url = "data/live-data.json";
      fetchOptions.method = "GET";
    } else if (cleanPath === "/simulate") {
      return {
        risk: "MEDIUM RISK",
        score: 5.4,
        triggered_sources: ["temp1", "mov1"],
        explanation: "Simulation result computed statically on GitHub Pages.",
        drone_change_percent: 8.5
      };
    } else if (cleanPath === "/toggle-drone") {
      return { drone_active: true };
    }
  }

  const response = await fetch(url, fetchOptions);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }
  return response.json();
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function statusDot(color) {
  return `<span class="dot ${color}"></span>`;
}
