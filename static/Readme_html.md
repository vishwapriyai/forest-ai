<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ForestAI — Sentinel System</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0f0a;
    --bg2: #0e150e;
    --panel: rgba(15, 24, 15, 0.85);
    --border: rgba(74, 222, 128, 0.15);
    --green: #4ade80;
    --green2: #22c55e;
    --green-dim: rgba(74, 222, 128, 0.08);
    --amber: #fbbf24;
    --red: #f87171;
    --text: #e2f5e2;
    --muted: #6b8f6b;
    --mono: 'Space Mono', monospace;
    --display: 'Syne', sans-serif;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: var(--mono);
    overflow: hidden;
  }

  body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none; opacity: .5;
  }

  body::after {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
      linear-gradient(var(--border) 1px, transparent 1px),
      linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
  }

  .shell {
    position: relative; z-index: 1;
    display: grid;
    grid-template-columns: 240px 1fr 340px;
    grid-template-rows: 64px 1fr;
    height: 100vh;
    gap: 0;
  }

  /* ── TOPBAR ── */
  .topbar {
    grid-column: 1 / -1;
    display: flex; align-items: center; gap: 24px;
    padding: 0 28px;
    background: rgba(10,15,10,0.96);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(12px);
  }

  .logo {
    font-family: var(--display);
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--green);
    display: flex; align-items: center; gap: 10px;
  }

  .logo-icon {
    width: 32px; height: 32px;
    background: var(--green);
    clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%);
    animation: pulse-glow 3s ease-in-out infinite;
  }

  @keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); }
    50% { box-shadow: 0 0 20px 6px rgba(74,222,128,0.35); }
  }

  .topbar-stat {
    display: flex; align-items: center; gap: 8px;
    font-size: 11px; color: var(--muted);
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--green-dim);
    transition: opacity 0.3s;
  }

  .topbar-stat span { color: var(--green); font-weight: 700; font-size: 12px; }

  .live-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green);
    animation: blink 1.2s ease infinite;
    flex-shrink: 0;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
  }

  .topbar-time { margin-left: auto; font-size: 12px; color: var(--muted); letter-spacing: 2px; }

  /* ── SIDEBAR LEFT ── */
  .sidebar-left {
    background: var(--panel);
    border-right: 1px solid var(--border);
    padding: 20px 16px;
    display: flex; flex-direction: column; gap: 12px;
    backdrop-filter: blur(8px);
    overflow-y: auto;
  }

  .section-label {
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 4px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }

  .drone-status {
    background: var(--green-dim);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    text-align: center;
  }

  .drone-icon {
    font-size: 36px;
    animation: hover-drone 3s ease-in-out infinite;
    display: block;
  }

  @keyframes hover-drone {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }

  .mode-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    background: rgba(74,222,128,0.15);
    color: var(--green);
    border: 1px solid rgba(74,222,128,0.3);
    margin-top: 8px;
    text-align: center;
    width: 100%;
    transition: all 0.3s;
  }

  .mode-badge.offline {
    background: rgba(248,113,113,0.1);
    color: var(--red);
    border-color: rgba(248,113,113,0.3);
  }

  .ctrl-btn {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 5px;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }

  .btn-start {
    background: linear-gradient(135deg, #166534, #15803d);
    color: #dcfce7;
    border: 1px solid #22c55e;
  }

  .btn-start:hover {
    background: linear-gradient(135deg, #15803d, #16a34a);
    box-shadow: 0 0 20px rgba(74,222,128,0.3);
    transform: translateY(-1px);
  }

  .btn-stop {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    color: #fee2e2;
    border: 1px solid #f87171;
  }

  .btn-stop:hover {
    background: linear-gradient(135deg, #991b1b, #b91c1c);
    box-shadow: 0 0 20px rgba(248,113,113,0.3);
    transform: translateY(-1px);
  }

  .metric-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
  }

  .metric-label { color: var(--muted); }
  .metric-val { color: var(--green); font-weight: 700; }

  /* ── MAIN ── */
  .main {
    padding: 20px;
    overflow-y: auto;
    display: flex; flex-direction: column; gap: 20px;
  }

  /* ── DRONE PANEL (visible when drone ON) ── */
  .drone-panel { display: flex; flex-direction: column; gap: 20px; }
  .drone-panel.hidden { display: none; }

  /* ── SENSOR PANEL (visible when drone OFF) ── */
  .sensor-only-panel { display: flex; flex-direction: column; gap: 20px; }
  .sensor-only-panel.hidden { display: none; }

  .compare-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .img-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    transition: border-color 0.3s;
  }

  .img-card:hover { border-color: var(--green); }

  .img-card-header {
    padding: 10px 14px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
  }

  .img-card-header .date-chip {
    background: var(--green-dim);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 2px 8px;
    color: var(--green);
    font-size: 10px;
  }

  .img-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }

  .img-placeholder {
    width: 100%;
    height: 200px;
    background: repeating-linear-gradient(
      45deg,
      rgba(74,222,128,0.03),
      rgba(74,222,128,0.03) 10px,
      transparent 10px,
      transparent 20px
    );
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 8px;
    color: var(--muted);
    font-size: 11px;
  }

  .img-placeholder .ph-icon { font-size: 32px; opacity: 0.3; }

  .change-bar {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
  }

  .change-bar-title {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .reading-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }

  .reading-card {
    background: var(--green-dim);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px;
    text-align: center;
    transition: all 0.3s;
  }

  .reading-card:hover { border-color: var(--green); background: rgba(74,222,128,0.12); }

  .reading-card .r-label { font-size: 9px; letter-spacing: 2px; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; }
  .reading-card .r-value { font-family: var(--display); font-size: 22px; font-weight: 800; color: var(--green); }
  .reading-card .r-unit { font-size: 10px; color: var(--muted); margin-top: 2px; }

  /* ── SENSOR CARDS ── */
  .sensor-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

  .sensor-card {
    background: var(--green-dim);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    transition: all 0.3s;
  }

  .sensor-card .s-label { font-size: 9px; letter-spacing: 2px; color: var(--muted); margin-bottom: 8px; text-transform: uppercase; }
  .sensor-card .s-value { font-family: var(--display); font-size: 26px; font-weight: 800; color: var(--green); }
  .sensor-card .s-sub { font-size: 10px; color: var(--muted); margin-top: 4px; }

  .sensor-card.warn .s-value { color: var(--amber); }
  .sensor-card.warn { border-color: rgba(251,191,36,0.3); background: rgba(251,191,36,0.06); }
  .sensor-card.danger .s-value { color: var(--red); }
  .sensor-card.danger { border-color: rgba(248,113,113,0.3); background: rgba(248,113,113,0.06); animation: danger-pulse 2s ease-in-out infinite; }

  /* ── RISK BANNER ── */
  .risk-banner {
    border-radius: 8px;
    padding: 14px 18px;
    display: flex; align-items: center; gap: 14px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    border: 1px solid;
    transition: all 0.4s;
  }

  .risk-banner.low { background: rgba(74,222,128,0.08); border-color: rgba(74,222,128,0.3); color: var(--green); }
  .risk-banner.medium { background: rgba(251,191,36,0.08); border-color: rgba(251,191,36,0.3); color: var(--amber); }
  .risk-banner.high { background: rgba(248,113,113,0.08); border-color: rgba(248,113,113,0.3); color: var(--red); animation: danger-pulse 2s ease-in-out infinite; }

  @keyframes danger-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0); }
    50% { box-shadow: 0 0 20px 4px rgba(248,113,113,0.2); }
  }

  .risk-icon { font-size: 24px; flex-shrink: 0; }
  .risk-text { flex: 1; }
  .risk-text h3 { font-family: var(--display); font-size: 15px; font-weight: 800; }
  .risk-text p { font-size: 11px; font-weight: 400; opacity: 0.85; margin-top: 3px; }

  /* ── SOURCE TAG ── */
  .source-tag {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 9px; letter-spacing: 1.5px; font-weight: 700;
    padding: 3px 8px; border-radius: 3px;
    flex-shrink: 0;
  }

  .source-tag.drone { background: rgba(74,222,128,0.12); color: var(--green); border: 1px solid rgba(74,222,128,0.3); }
  .source-tag.sensor { background: rgba(251,191,36,0.1); color: var(--amber); border: 1px solid rgba(251,191,36,0.3); }

  /* ── OFFLINE NOTICE ── */
  .offline-notice {
    background: rgba(248,113,113,0.06);
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: 8px;
    padding: 14px 18px;
    display: flex; align-items: center; gap: 12px;
    font-size: 11px;
    color: var(--red);
    letter-spacing: 1px;
    line-height: 1.6;
  }

  .offline-notice .oi-icon { font-size: 20px; flex-shrink: 0; }

  /* ── SENSOR NOTE ── */
  .sensor-note {
    background: rgba(251,191,36,0.06);
    border: 1px solid rgba(251,191,36,0.18);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 10px;
    color: var(--amber);
    letter-spacing: 1px;
    line-height: 1.7;
  }

  /* ── SIDEBAR RIGHT ── */
  .sidebar-right {
    background: var(--panel);
    border-left: 1px solid var(--border);
    padding: 20px 14px;
    display: flex; flex-direction: column; gap: 14px;
    overflow-y: auto;
    backdrop-filter: blur(8px);
  }

  .filter-row { display: flex; gap: 6px; flex-wrap: wrap; }

  .filter-btn {
    padding: 4px 10px;
    border-radius: 20px;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 1px;
    font-weight: 700;
    cursor: pointer;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    transition: all 0.2s;
  }

  .filter-btn.active, .filter-btn:hover { background: var(--green-dim); color: var(--green); border-color: rgba(74,222,128,0.4); }
  .filter-btn.f-high.active { background: rgba(248,113,113,0.1); color: var(--red); border-color: rgba(248,113,113,0.4); }
  .filter-btn.f-medium.active { background: rgba(251,191,36,0.1); color: var(--amber); border-color: rgba(251,191,36,0.4); }

  .alert-feed { display: flex; flex-direction: column; gap: 8px; }

  .alert-item {
    background: var(--green-dim);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 10px;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
  }

  .alert-item::before {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
  }

  .alert-item.high::before { background: var(--red); }
  .alert-item.medium::before { background: var(--amber); }
  .alert-item.low::before { background: var(--green); }

  .alert-item:hover { transform: translateX(3px); border-color: rgba(74,222,128,0.3); }

  .alert-item .a-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }

  .a-risk { font-size: 9px; font-weight: 700; letter-spacing: 1px; border-radius: 3px; padding: 2px 6px; }
  .a-risk.high { background: rgba(248,113,113,0.15); color: var(--red); }
  .a-risk.medium { background: rgba(251,191,36,0.15); color: var(--amber); }
  .a-risk.low { background: rgba(74,222,128,0.15); color: var(--green); }

  .a-date { color: var(--muted); font-size: 9px; }
  .a-coords { color: var(--muted); font-size: 9px; margin-bottom: 3px; }
  .a-msg { color: var(--text); line-height: 1.5; }

  .empty-feed { text-align: center; padding: 30px 10px; color: var(--muted); font-size: 11px; }

  /* ── SCROLLBAR ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
  * { scrollbar-width: thin; scrollbar-color: var(--border) transparent; }

  /* ── SCAN LINE ── */
  .scanline {
    position: fixed; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(74,222,128,0.4), transparent);
    animation: scan 6s linear infinite;
    pointer-events: none; z-index: 9999;
  }

  @keyframes scan {
    0% { top: 0; opacity: 1; }
    95% { opacity: 1; }
    100% { top: 100vh; opacity: 0; }
  }

  /* ── FADE IN ── */
  .fade-in { animation: fadeUp 0.5s ease both; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>

<div class="scanline"></div>

<div class="shell">

  <!-- ── TOPBAR ── -->
  <header class="topbar">
    <div class="logo">
      <div class="logo-icon"></div>
      ForestAI
    </div>
    <div class="topbar-stat">
      <div class="live-dot"></div>
      STATUS <span id="topStatus">ACTIVE</span>
    </div>
    <div class="topbar-stat" id="topDroneStat">
      🛸 DRONE <span id="topDrone">—</span>
    </div>
    <div class="topbar-stat">
      📡 SENSOR <span id="topSensor">—</span>
    </div>
    <div class="topbar-stat">
      ⚠️ ALERTS <span id="topAlerts">0</span>
    </div>
    <div class="topbar-time" id="clockDisplay">—</div>
  </header>

  <!-- ── SIDEBAR LEFT ── -->
  <aside class="sidebar-left">

    <div class="section-label">Drone Control</div>

    <div class="drone-status">
      <span class="drone-icon">🚁</span>
      <div class="mode-badge" id="modeDisplay">INITIALIZING…</div>
    </div>

    <button class="ctrl-btn btn-start" onclick="toggleDrone(true)">▶ LAUNCH DRONE</button>
    <button class="ctrl-btn btn-stop" onclick="toggleDrone(false)">■ RECALL DRONE</button>

    <!-- Drone metrics: visible when drone is ON -->
    <div id="droneMetricsBlock">
      <div class="section-label" style="margin-top:8px">Drone Metrics</div>
      <div class="metric-row">
        <span class="metric-label">Altitude</span>
        <span class="metric-val" id="metricAlt">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Coverage</span>
        <span class="metric-val" id="metricCov">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Battery</span>
        <span class="metric-val" id="metricBat">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Signal</span>
        <span class="metric-val" id="metricSig">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Zone</span>
        <span class="metric-val" id="metricZone">—</span>
      </div>
    </div>

    <!-- Sensor metrics: visible when drone is OFF -->
    <div id="sensorMetricsBlock" style="display:none;">
      <div class="section-label" style="margin-top:8px">Sensor Metrics</div>
      <div class="metric-row">
        <span class="metric-label">Smoke</span>
        <span class="metric-val" id="smSmokeVal">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Heat</span>
        <span class="metric-val" id="smHeatVal">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Humidity</span>
        <span class="metric-val" id="smHumVal">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Motion</span>
        <span class="metric-val" id="smMotionVal">—</span>
      </div>
      <div class="metric-row">
        <span class="metric-label">Last Ping</span>
        <span class="metric-val" id="smLastPing">—</span>
      </div>
    </div>

  </aside>

  <!-- ── MAIN ── -->
  <main class="main">

    <!-- ══ DRONE ON: Aerial data panel ══ -->
    <div class="drone-panel" id="dronePanel">

      <!-- Image comparison -->
      <div class="compare-grid fade-in">
        <div class="img-card">
          <div class="img-card-header">
            📅 Yesterday
            <span class="date-chip" id="dateYest">21-04-26</span>
          </div>
          <div id="yesterdayWrap">
            <div class="img-placeholder">
              <span class="ph-icon">🛸</span>
              Awaiting feed…
            </div>
          </div>
        </div>
        <div class="img-card">
          <div class="img-card-header">
            📅 Today
            <span class="date-chip" id="dateToday">22-04-26</span>
          </div>
          <div id="todayWrap">
            <div class="img-placeholder">
              <span class="ph-icon">🛸</span>
              Awaiting feed…
            </div>
          </div>
        </div>
      </div>

      <!-- Drone risk banner -->
      <div class="risk-banner low fade-in" id="droneRiskBanner">
        <span class="risk-icon">🟢</span>
        <div class="risk-text">
          <h3 id="droneRiskLevel">SCANNING…</h3>
          <p id="droneRiskDetail">Initializing AI analysis pipeline</p>
        </div>
        <span class="source-tag drone">🛸 DRONE DATA</span>
      </div>

      <!-- Drone sensor readings -->
      <div class="change-bar fade-in">
        <div class="change-bar-title">🔬 Drone Sensor Readings</div>
        <div class="reading-grid">
          <div class="reading-card">
            <div class="r-label">Drone Level</div>
            <div class="r-value" id="rDroneLevel">—</div>
            <div class="r-unit">altitude index</div>
          </div>
          <div class="reading-card">
            <div class="r-label">Drone Sensor</div>
            <div class="r-value" id="rDroneSensorEvt" style="font-size:14px">—</div>
            <div class="r-unit">latest trigger</div>
          </div>
          <div class="reading-card">
            <div class="r-label">Risk Score</div>
            <div class="r-value" id="rDroneRiskScore">—</div>
            <div class="r-unit">threat index</div>
          </div>
        </div>
      </div>

    </div>
    <!-- ══ END DRONE PANEL ══ -->

    <!-- ══ DRONE OFF: Sensor-only panel ══ -->
    <div class="sensor-only-panel hidden" id="sensorPanel">

      <!-- Offline notice -->
      <div class="offline-notice fade-in">
        <span class="oi-icon">🚫</span>
        <div>
          <strong>DRONE OFFLINE</strong> — Displaying ground sensor data only.
          Launch the drone to enable aerial image comparison and canopy analysis.
        </div>
      </div>

      <!-- Sensor risk banner -->
      <div class="risk-banner low fade-in" id="sensorRiskBanner">
        <span class="risk-icon">🟢</span>
        <div class="risk-text">
          <h3 id="sensorRiskLevel">SENSOR READING</h3>
          <p id="sensorRiskDetail">Ground sensors nominal — no anomalies detected</p>
        </div>
        <span class="source-tag sensor">📡 SENSOR ONLY</span>
      </div>

      <!-- Ground sensor cards -->
      <div class="change-bar fade-in">
        <div class="change-bar-title">📡 Ground Sensor Data</div>
        <div class="sensor-grid">
          <div class="sensor-card" id="scSmoke">
            <div class="s-label">Smoke Detector</div>
            <div class="s-value" id="scSmokeVal">CLEAR</div>
            <div class="s-sub" id="scSmokeSub">No smoke detected</div>
          </div>
          <div class="sensor-card" id="scHeat">
            <div class="s-label">Heat Index</div>
            <div class="s-value" id="scHeatVal">32°C</div>
            <div class="s-sub" id="scHeatSub">Normal range</div>
          </div>
          <div class="sensor-card" id="scHumidity">
            <div class="s-label">Humidity</div>
            <div class="s-value" id="scHumVal">68%</div>
            <div class="s-sub" id="scHumSub">Adequate moisture</div>
          </div>
          <div class="sensor-card" id="scMotion">
            <div class="s-label">Motion / Vibration</div>
            <div class="s-value" id="scMotionVal">NONE</div>
            <div class="s-sub" id="scMotionSub">No activity</div>
          </div>
        </div>
      </div>

      <!-- Sensor-only disclaimer -->
      <div class="sensor-note fade-in">
        ⚠️ NOTE — Sensor-only mode provides limited risk assessment.
        Aerial image comparison and canopy analysis are unavailable while the drone is offline.
        Risk scores are based on ground-level triggers only.
      </div>

    </div>
    <!-- ══ END SENSOR PANEL ══ -->

  </main>

  <!-- ── SIDEBAR RIGHT ── -->
  <aside class="sidebar-right">

    <div class="section-label">Alert Feed</div>

    <div class="filter-row">
      <button class="filter-btn active" data-filter="ALL" onclick="setFilter(this)">ALL</button>
      <button class="filter-btn f-high" data-filter="HIGH RISK" onclick="setFilter(this)">HIGH</button>
      <button class="filter-btn f-medium" data-filter="MEDIUM RISK" onclick="setFilter(this)">MED</button>
      <button class="filter-btn" data-filter="LOW RISK" onclick="setFilter(this)">LOW</button>
    </div>

    <div class="alert-feed" id="alertFeed">
      <div class="empty-feed">
        <div style="font-size:28px;margin-bottom:8px">📡</div>
        No alerts yet.<br>System scanning…
      </div>
    </div>

  </aside>

</div>

<script>
  /* ═══════════════════════════════════════════
     STATE
  ═══════════════════════════════════════════ */
  let currentFilter = "ALL";
  let allAlerts = [];
  let droneActive = false;
  let demoTick = 0;

  /* ═══════════════════════════════════════════
     CLOCK
  ═══════════════════════════════════════════ */
  function updateClock() {
    document.getElementById("clockDisplay").textContent =
      new Date().toLocaleTimeString("en-GB", { hour12: false }) + " UTC";
  }
  updateClock();
  setInterval(updateClock, 1000);

  /* ═══════════════════════════════════════════
     HELPERS
  ═══════════════════════════════════════════ */
  function riskClass(risk) {
    if (risk === "HIGH RISK")    return "high";
    if (risk === "MEDIUM RISK")  return "medium";
    return "low";
  }

  function riskIcon(risk) {
    if (risk === "HIGH RISK")    return "🔴";
    if (risk === "MEDIUM RISK")  return "🟡";
    return "🟢";
  }

  /* ═══════════════════════════════════════════
     PANEL SWITCHER
     — Drone ON  → show drone panel, drone sidebar metrics, topbar drone stat
     — Drone OFF → show sensor panel, sensor sidebar metrics, dim topbar drone stat
  ═══════════════════════════════════════════ */
  function applyDroneState(active) {
    const dronePanel     = document.getElementById("dronePanel");
    const sensorPanel    = document.getElementById("sensorPanel");
    const droneMetrics   = document.getElementById("droneMetricsBlock");
    const sensorMetrics  = document.getElementById("sensorMetricsBlock");
    const modeBadge      = document.getElementById("modeDisplay");
    const topDroneStat   = document.getElementById("topDroneStat");

    if (active) {
      dronePanel.classList.remove("hidden");
      sensorPanel.classList.add("hidden");
      droneMetrics.style.display  = "";
      sensorMetrics.style.display = "none";
      topDroneStat.style.opacity  = "1";
      modeBadge.classList.remove("offline");
    } else {
      dronePanel.classList.add("hidden");
      sensorPanel.classList.remove("hidden");
      droneMetrics.style.display  = "none";
      sensorMetrics.style.display = "";
      topDroneStat.style.opacity  = "0.35";
      document.getElementById("topDrone").textContent = "—";
      modeBadge.textContent = "RECALLED";
      modeBadge.classList.add("offline");
    }
  }

  /* ═══════════════════════════════════════════
     ALERT FEED
  ═══════════════════════════════════════════ */
  function setFilter(btn) {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    renderAlerts();
  }

  function renderAlerts() {
    const feed = document.getElementById("alertFeed");
    const filtered = currentFilter === "ALL"
      ? allAlerts
      : allAlerts.filter(a => a.risk === currentFilter);

    if (filtered.length === 0) {
      feed.innerHTML = `<div class="empty-feed"><div style="font-size:28px;margin-bottom:8px">📡</div>No alerts match this filter.</div>`;
      return;
    }

    feed.innerHTML = filtered.map(row => `
      <div class="alert-item ${riskClass(row.risk)}">
        <div class="a-head">
          <span class="a-risk ${riskClass(row.risk)}">${row.risk}</span>
          <span class="a-date">${row.date}</span>
        </div>
        <div class="a-coords">📍 ${row.lat}, ${row.lon} &nbsp;|&nbsp; 🖼 ${row.image}</div>
        <div class="a-msg">${row.alert}</div>
      </div>
    `).join("");
  }

  async function loadAlerts() {
    try {
      const res = await fetch("http://127.0.0.1:8000/alerts");
      allAlerts = await res.json();
      renderAlerts();
      document.getElementById("topAlerts").textContent = allAlerts.length;
    } catch (e) { /* demo mode — alerts injected by injectDroneDemoData */ }
  }

  /* ═══════════════════════════════════════════
     TOGGLE DRONE
  ═══════════════════════════════════════════ */
  async function toggleDrone(state) {
    droneActive = state;
    applyDroneState(state);

    if (!state) {
      // Clear aerial feeds
      document.getElementById("yesterdayWrap").innerHTML =
        `<div class="img-placeholder"><span class="ph-icon">🛸</span>Awaiting feed…</div>`;
      document.getElementById("todayWrap").innerHTML =
        `<div class="img-placeholder"><span class="ph-icon">🛸</span>Awaiting feed…</div>`;
      // Immediately populate sensor data
      injectSensorDemoData();
    }

    try {
      await fetch(`http://127.0.0.1:8000/toggle-drone?state=${state}`, { method: "POST" });
    } catch (e) { /* offline demo */ }
  }

  /* ═══════════════════════════════════════════
     DEMO DATA POOLS
  ═══════════════════════════════════════════ */
  const demoRisks      = ["LOW RISK", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "LOW RISK"];
  const demoDroneSensors = ["NONE", "SMOKE DETECTED", "HEAT SPIKE", "NONE", "MOTION"];

  const demoAlerts = [
    { date:"22-04-26 09:14", image:"img_004.jpg", lat:"12.4521", lon:"79.1234", risk:"HIGH RISK",   alert:"Significant canopy loss detected. Possible wildfire spread." },
    { date:"22-04-26 07:02", image:"img_002.jpg", lat:"12.4388", lon:"79.1102", risk:"MEDIUM RISK", alert:"Heat signature above threshold. Monitor closely." },
    { date:"21-04-26 22:48", image:"img_009.jpg", lat:"12.4290", lon:"79.0991", risk:"LOW RISK",    alert:"Minor vegetation change. No immediate action required." },
    { date:"21-04-26 18:30", image:"img_001.jpg", lat:"12.4411", lon:"79.1300", risk:"HIGH RISK",   alert:"Large-scale deforestation event detected." },
  ];

  // Sensor-only states cycle through low → medium → high
  const sensorPool = [
    {
      smoke:"CLEAR", heat:"31°C", hum:"72%", motion:"NONE",
      smokeSub:"No smoke detected", heatSub:"Normal range",
      humSub:"Adequate moisture", motionSub:"No activity",
      smokeClass:"", heatClass:"", humClass:"", motionClass:"",
      risk:"LOW RISK"
    },
    {
      smoke:"TRACE", heat:"38°C", hum:"55%", motion:"LOW",
      smokeSub:"Trace levels — monitoring", heatSub:"Above normal",
      humSub:"Below optimal", motionSub:"Low-level detected",
      smokeClass:"warn", heatClass:"warn", humClass:"", motionClass:"",
      risk:"MEDIUM RISK"
    },
    {
      smoke:"DETECTED", heat:"47°C", hum:"38%", motion:"ACTIVE",
      smokeSub:"Active smoke — alert!", heatSub:"Critical heat spike",
      humSub:"Critically low", motionSub:"High activity",
      smokeClass:"danger", heatClass:"danger", humClass:"warn", motionClass:"warn",
      risk:"HIGH RISK"
    },
  ];

  /* ═══════════════════════════════════════════
     INJECT SENSOR-ONLY DEMO DATA
     (used when drone is OFF)
  ═══════════════════════════════════════════ */
  function injectSensorDemoData() {
    const pool = sensorPool[demoTick % sensorPool.length];

    // Left sidebar sensor metrics
    document.getElementById("smSmokeVal").textContent  = pool.smoke;
    document.getElementById("smHeatVal").textContent   = pool.heat;
    document.getElementById("smHumVal").textContent    = pool.hum;
    document.getElementById("smMotionVal").textContent = pool.motion;
    document.getElementById("smLastPing").textContent  = new Date().toLocaleTimeString("en-GB", { hour12: false });

    // Sensor cards
    document.getElementById("scSmokeVal").textContent  = pool.smoke;
    document.getElementById("scHeatVal").textContent   = pool.heat;
    document.getElementById("scHumVal").textContent    = pool.hum;
    document.getElementById("scMotionVal").textContent = pool.motion;
    document.getElementById("scSmokeSub").textContent  = pool.smokeSub;
    document.getElementById("scHeatSub").textContent   = pool.heatSub;
    document.getElementById("scHumSub").textContent    = pool.humSub;
    document.getElementById("scMotionSub").textContent = pool.motionSub;

    document.getElementById("scSmoke").className    = "sensor-card" + (pool.smokeClass  ? " " + pool.smokeClass  : "");
    document.getElementById("scHeat").className     = "sensor-card" + (pool.heatClass   ? " " + pool.heatClass   : "");
    document.getElementById("scHumidity").className = "sensor-card" + (pool.humClass    ? " " + pool.humClass    : "");
    document.getElementById("scMotion").className   = "sensor-card" + (pool.motionClass ? " " + pool.motionClass : "");

    // Sensor risk banner
    const risk = pool.risk;
    const banner = document.getElementById("sensorRiskBanner");
    banner.className = "risk-banner " + riskClass(risk) + " fade-in";
    banner.querySelector(".risk-icon").textContent = riskIcon(risk);
    document.getElementById("sensorRiskLevel").textContent = risk + " (SENSOR)";
    document.getElementById("sensorRiskDetail").textContent =
      risk === "HIGH RISK"   ? "Critical sensor thresholds breached — smoke and heat anomalies detected." :
      risk === "MEDIUM RISK" ? "Elevated ground readings. Deploy drone for aerial confirmation." :
                               "Ground sensors nominal. No immediate threat detected.";

    // Topbar sensor
    document.getElementById("topSensor").textContent = pool.smoke !== "CLEAR" ? pool.smoke : "CLEAR";
  }

  /* ═══════════════════════════════════════════
     INJECT DRONE DEMO DATA
     (used when drone is ON and API is offline)
  ═══════════════════════════════════════════ */
  function injectDroneDemoData() {
    const risk   = demoRisks[demoTick % demoRisks.length];
    const sensor = demoDroneSensors[demoTick % demoDroneSensors.length];

    // Mode badge & topbar
    document.getElementById("modeDisplay").textContent = "AUTO PATROL";
    document.getElementById("modeDisplay").classList.remove("offline");
    document.getElementById("topDrone").textContent  = "LVL 3";
    document.getElementById("topSensor").textContent = sensor || "CLEAR";

    // Left sidebar drone metrics
    document.getElementById("metricAlt").textContent  = (80 + Math.round(Math.random() * 20)) + "m";
    document.getElementById("metricCov").textContent  = (42 + Math.round(Math.random() * 10)) + "%";
    document.getElementById("metricBat").textContent  = (70 + Math.round(Math.random() * 20)) + "%";
    document.getElementById("metricSig").textContent  = ["STRONG","GOOD","MODERATE"][Math.floor(Math.random() * 3)];
    document.getElementById("metricZone").textContent = "SECTOR-" + (Math.floor(Math.random() * 5) + 1);

    // Drone readings panel
    document.getElementById("rDroneLevel").textContent    = "3";
    document.getElementById("rDroneSensorEvt").textContent = sensor || "NONE";
    document.getElementById("rDroneRiskScore").textContent =
      risk === "HIGH RISK" ? "8.4" : risk === "MEDIUM RISK" ? "4.7" : "1.2";

    // Drone risk banner
    const banner = document.getElementById("droneRiskBanner");
    banner.className = "risk-banner " + riskClass(risk) + " fade-in";
    banner.querySelector(".risk-icon").textContent = riskIcon(risk);
    document.getElementById("droneRiskLevel").textContent  = risk;
    document.getElementById("droneRiskDetail").textContent =
      risk === "HIGH RISK"   ? "Immediate intervention recommended — anomalies detected across multiple sensors." :
      risk === "MEDIUM RISK" ? "Elevated activity detected. Maintain surveillance on this sector." :
                               "All systems nominal. Forest health indicators within expected range.";

    // Alerts
    document.getElementById("topAlerts").textContent = demoAlerts.length;
    allAlerts = demoAlerts;
    renderAlerts();

    // Image feed placeholders (no server)
    const yWrap = document.getElementById("yesterdayWrap");
    const tWrap = document.getElementById("todayWrap");
    if (!yWrap.querySelector("img")) {
      yWrap.innerHTML = `<div class="img-placeholder"><span class="ph-icon">🛸</span>Feed from 21-04-26</div>`;
      tWrap.innerHTML = `<div class="img-placeholder"><span class="ph-icon">🌿</span>Live feed 22-04-26</div>`;
    }
  }

  /* ═══════════════════════════════════════════
     MAIN POLL — runs every 10 s
     Drone ON  → try live API, fallback to drone demo
     Drone OFF → sensor demo only (no API call)
  ═══════════════════════════════════════════ */
  async function fetchLive() {
    demoTick++;

    if (!droneActive) {
      injectSensorDemoData();
      return;
    }

    try {
      const res  = await fetch("http://127.0.0.1:8000/analyze-live");
      const data = await res.json();

      document.getElementById("modeDisplay").textContent  = data.mode || "—";
      document.getElementById("modeDisplay").classList.remove("offline");
      document.getElementById("topDrone").textContent     = data.drone?.level || "—";
      document.getElementById("topSensor").textContent    = data.sensor?.event || "—";

      document.getElementById("rDroneLevel").textContent      = data.drone?.level  ?? "—";
      document.getElementById("rDroneSensorEvt").textContent  = data.sensor?.event ?? "—";
      document.getElementById("rDroneRiskScore").textContent  = data.risk           ?? "—";

      const risk   = data.risk;
      const banner = document.getElementById("droneRiskBanner");
      banner.className = "risk-banner " + riskClass(risk) + " fade-in";
      banner.querySelector(".risk-icon").textContent        = riskIcon(risk);
      document.getElementById("droneRiskLevel").textContent  = risk;
      document.getElementById("droneRiskDetail").textContent = data.alert || "";

      if (data.drone?.image) {
        document.getElementById("yesterdayWrap").innerHTML =
          `<img src="http://127.0.0.1:8000/data/raw/drone/21-04-26/${data.drone.image}" alt="Yesterday">`;
        document.getElementById("todayWrap").innerHTML =
          `<img src="http://127.0.0.1:8000/data/raw/drone/22-04-26/${data.drone.image}" alt="Today">`;
      }

      loadAlerts();

    } catch (e) {
      // API offline — use drone demo data
      injectDroneDemoData();
    }
  }

  /* ═══════════════════════════════════════════
     INIT — start with drone active
  ═══════════════════════════════════════════ */
  droneActive = true;
  applyDroneState(true);
  fetchLive();
  setInterval(fetchLive, 10000);
</script>
</body>
</html>