const API_BASE = window.location.origin;

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
  const response = await fetch(`${API_BASE}${path}`, options);
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
