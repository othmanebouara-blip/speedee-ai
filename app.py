from flask import Flask, jsonify
import random
from model import get_model

model = get_model()

app = Flask(__name__)

import pandas as pd
import random

def generate_real_data():
    state = {
        "orders_in_queue": random.randint(0, 20),
        "avg_items_per_order": round(random.uniform(1, 6), 1),
        "crew_grill": random.randint(1, 4),
        "crew_fries": random.randint(1, 3),
        "crew_assembly": random.randint(1, 4),
        "grill_busy": round(random.uniform(0.3, 1.0), 2),
        "fries_busy": round(random.uniform(0.2, 1.0), 2),
        "assembly_busy": round(random.uniform(0.3, 1.0), 2),
    }

    input_df = pd.DataFrame([state])
    predicted_load = model.predict(input_df)[0]

    recommendations = []

    if predicted_load >= 0.8:
        if state["grill_busy"] > 0.75:
            recommendations.append("🔥 Add crew to GRILL")
        if state["assembly_busy"] > 0.75:
            recommendations.append("🍔 Add crew to ASSEMBLY")
        if state["fries_busy"] < 0.5:
            recommendations.append("🍟 Move crew FROM FRIES")
        if not recommendations:
            recommendations.append("⚠️ High load - monitor closely")
    elif predicted_load < 0.4:
        recommendations.append("🟢 Reduce crew / slow period")
    else:
        recommendations.append("🟡 System stable")

    return {
        **state,
        "predicted_load": round(predicted_load, 2),
        "recommendations": recommendations
    }

@app.route("/data")
def data():
    return jsonify(generate_real_data())

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Speedee AI Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #1a1a2e;
      color: #eee;
      font-family: 'Segoe UI', Arial, sans-serif;
      min-height: 100vh;
      padding: 20px;
    }

    header {
      text-align: center;
      margin-bottom: 24px;
    }
    header h1 {
      font-size: 2rem;
      letter-spacing: 2px;
      color: #f5c518;
    }
    header p {
      font-size: 0.85rem;
      color: #aaa;
      margin-top: 4px;
    }

    /* ── top stats bar ── */
    .stats-bar {
      display: flex;
      justify-content: center;
      gap: 20px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }
    .stat-pill {
      background: #16213e;
      border: 1px solid #0f3460;
      border-radius: 50px;
      padding: 10px 24px;
      text-align: center;
      min-width: 150px;
    }
    .stat-pill .label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .stat-pill .value { font-size: 1.6rem; font-weight: bold; margin-top: 2px; }

    /* ── kitchen floor ── */
    .kitchen-title {
      text-align: center;
      font-size: 0.8rem;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-bottom: 12px;
    }

    .kitchen-floor {
      display: flex;
      justify-content: center;
      gap: 18px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }

    /* ── station card ── */
    .station {
      width: 220px;
      border-radius: 14px;
      padding: 20px 18px 18px;
      position: relative;
      border: 2px solid transparent;
      transition: border-color 0.4s, box-shadow 0.4s;
      background: #16213e;
    }
    .station.attention {
      animation: pulse-border 1s ease-in-out infinite;
    }
    @keyframes pulse-border {
      0%, 100% { box-shadow: 0 0 0 0 rgba(255,60,60,0.6); border-color: #ff3c3c; }
      50%       { box-shadow: 0 0 18px 6px rgba(255,60,60,0.35); border-color: #ff8080; }
    }

    .station-icon {
      font-size: 2.8rem;
      display: block;
      text-align: center;
      margin-bottom: 8px;
    }

    .station-name {
      text-align: center;
      font-size: 1rem;
      font-weight: bold;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 14px;
    }

    /* status badge */
    .badge {
      display: inline-block;
      border-radius: 30px;
      padding: 2px 12px;
      font-size: 0.72rem;
      font-weight: bold;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 14px;
    }
    .badge-green  { background: #1a4a1a; color: #4caf50; }
    .badge-yellow { background: #3a3000; color: #ffc107; }
    .badge-red    { background: #4a1a1a; color: #f44336; }

    /* progress bar */
    .bar-label {
      font-size: 0.72rem;
      color: #999;
      margin-bottom: 4px;
    }
    .bar-track {
      background: #0d1b35;
      border-radius: 8px;
      height: 14px;
      margin-bottom: 10px;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      border-radius: 8px;
      transition: width 0.6s ease, background 0.4s;
    }

    /* crew dots */
    .crew-row {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 4px;
      flex-wrap: wrap;
    }
    .crew-dot {
      width: 18px; height: 18px;
      border-radius: 50%;
      background: #4caf50;
      display: flex; align-items: center; justify-content: center;
      font-size: 10px;
    }
    .crew-label { font-size: 0.72rem; color: #888; margin-right: 4px; }

    /* attention badge overlay */
    .attention-tag {
      position: absolute;
      top: -10px; right: 12px;
      background: #ff3c3c;
      color: #fff;
      font-size: 0.68rem;
      font-weight: bold;
      border-radius: 20px;
      padding: 2px 10px;
      letter-spacing: 1px;
      display: none;
    }
    .station.attention .attention-tag { display: block; }

    /* ── overall load gauge ── */
    .load-section {
      display: flex;
      justify-content: center;
      margin-bottom: 28px;
    }
    .load-card {
      background: #16213e;
      border: 1px solid #0f3460;
      border-radius: 14px;
      padding: 20px 40px;
      text-align: center;
      min-width: 320px;
    }
    .load-card h3 { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
    .load-number { font-size: 3rem; font-weight: bold; }
    .load-bar-track {
      background: #0d1b35;
      border-radius: 8px;
      height: 20px;
      margin: 12px 0 6px;
      overflow: hidden;
    }
    .load-bar-fill {
      height: 100%;
      border-radius: 8px;
      transition: width 0.6s ease, background 0.4s;
    }
    .load-status-text { font-size: 0.8rem; color: #888; }

    /* ── recommendations ── */
    .rec-section {
      max-width: 640px;
      margin: 0 auto 28px;
    }
    .rec-section h3 {
      text-align: center;
      font-size: 0.8rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }
    .rec-list { list-style: none; }
    .rec-item {
      background: #16213e;
      border-left: 4px solid #f5c518;
      border-radius: 6px;
      padding: 10px 16px;
      margin-bottom: 8px;
      font-size: 0.95rem;
    }

    /* ── alert banner ── */
    #alert-banner {
      display: none;
      text-align: center;
      background: #ff3c3c;
      color: #fff;
      font-weight: bold;
      font-size: 1rem;
      padding: 12px;
      border-radius: 10px;
      max-width: 640px;
      margin: 0 auto 20px;
      letter-spacing: 1px;
      animation: flash 0.8s ease-in-out infinite;
    }
    @keyframes flash { 0%,100%{opacity:1} 50%{opacity:0.6} }

    footer {
      text-align: center;
      font-size: 0.72rem;
      color: #444;
      margin-top: 10px;
    }
  </style>
</head>
<body>

<header>
  <h1>🍔 SPEEDEE AI DASHBOARD</h1>
  <p>McDonald's Kitchen Load Simulator — live update every 2s</p>
</header>

<div id="alert-banner">🚨 SUSTAINED HIGH LOAD — TAKE ACTION NOW</div>

<!-- top stats -->
<div class="stats-bar">
  <div class="stat-pill">
    <div class="label">Orders in Queue</div>
    <div class="value" id="orders">—</div>
  </div>
  <div class="stat-pill">
    <div class="label">Avg Items / Order</div>
    <div class="value" id="avg-items">—</div>
  </div>
  <div class="stat-pill">
    <div class="label">Overall Status</div>
    <div class="value" id="status-text" style="font-size:1.2rem;">—</div>
  </div>
</div>

<!-- kitchen floor visualisation -->
<p class="kitchen-title">Kitchen Floor</p>
<div class="kitchen-floor">

  <!-- GRILL -->
  <div class="station" id="station-grill">
    <span class="attention-tag">NEEDS ATTENTION</span>
    <span class="station-icon">🔥</span>
    <div class="station-name">Grill</div>
    <span class="badge" id="badge-grill">—</span>
    <div class="bar-label">Busyness</div>
    <div class="bar-track"><div class="bar-fill" id="bar-grill" style="width:0%"></div></div>
    <div style="font-size:0.8rem; color:#ccc; margin-bottom:8px;" id="pct-grill">0%</div>
    <div class="crew-row" id="crew-grill"></div>
  </div>

  <!-- FRIES -->
  <div class="station" id="station-fries">
    <span class="attention-tag">NEEDS ATTENTION</span>
    <span class="station-icon">🍟</span>
    <div class="station-name">Fries</div>
    <span class="badge" id="badge-fries">—</span>
    <div class="bar-label">Busyness</div>
    <div class="bar-track"><div class="bar-fill" id="bar-fries" style="width:0%"></div></div>
    <div style="font-size:0.8rem; color:#ccc; margin-bottom:8px;" id="pct-fries">0%</div>
    <div class="crew-row" id="crew-fries"></div>
  </div>

  <!-- ASSEMBLY -->
  <div class="station" id="station-assembly">
    <span class="attention-tag">NEEDS ATTENTION</span>
    <span class="station-icon">🍔</span>
    <div class="station-name">Assembly</div>
    <span class="badge" id="badge-assembly">—</span>
    <div class="bar-label">Busyness</div>
    <div class="bar-track"><div class="bar-fill" id="bar-assembly" style="width:0%"></div></div>
    <div style="font-size:0.8rem; color:#ccc; margin-bottom:8px;" id="pct-assembly">0%</div>
    <div class="crew-row" id="crew-assembly"></div>
  </div>

</div>

<!-- overall load -->
<div class="load-section">
  <div class="load-card">
    <h3>Predicted Kitchen Load</h3>
    <div class="load-number" id="load-number">—</div>
    <div class="load-bar-track">
      <div class="load-bar-fill" id="load-bar" style="width:0%"></div>
    </div>
    <div class="load-status-text" id="load-status-text">Calculating…</div>
  </div>
</div>

<!-- recommendations -->
<div class="rec-section">
  <h3>AI Recommendations</h3>
  <ul class="rec-list" id="rec-list"></ul>
</div>

<footer>Speedee AI · Simulated data · Refreshes every 2 seconds</footer>

<script>
  let highLoadCount = 0;

  function stationColor(busy) {
    if (busy >= 0.8) return "#f44336";
    if (busy >= 0.5) return "#ffc107";
    return "#4caf50";
  }

  function badgeClass(busy) {
    if (busy >= 0.8) return ["badge-red",   "CRITICAL"];
    if (busy >= 0.5) return ["badge-yellow", "MODERATE"];
    return               ["badge-green",  "OK"];
  }

  function renderCrew(containerId, count) {
    const el = document.getElementById(containerId);
    el.innerHTML = '<span class="crew-label">Crew:</span>';
    for (let i = 0; i < count; i++) {
      const dot = document.createElement("div");
      dot.className = "crew-dot";
      dot.textContent = "👤";
      dot.style.fontSize = "11px";
      el.appendChild(dot);
    }
  }

  function updateStation(name, busy, crew) {
    const pct = Math.round(busy * 100);
    const color = stationColor(busy);
    const [cls, label] = badgeClass(busy);
    const needsAttention = busy >= 0.8;

    document.getElementById(`bar-${name}`).style.width  = pct + "%";
    document.getElementById(`bar-${name}`).style.background = color;
    document.getElementById(`pct-${name}`).textContent  = pct + "%";

    const badge = document.getElementById(`badge-${name}`);
    badge.className = "badge " + cls;
    badge.textContent = label;

    const station = document.getElementById(`station-${name}`);
    if (needsAttention) station.classList.add("attention");
    else                station.classList.remove("attention");

    renderCrew(`crew-${name}`, crew);
  }

  async function fetchData() {
    const res  = await fetch('/data');
    const data = await res.json();

    // top stats
    document.getElementById("orders").textContent    = data.orders_in_queue;
    document.getElementById("avg-items").textContent = data.avg_items_per_order;

    // stations
    updateStation("grill",    data.grill_busy,    data.crew_grill);
    updateStation("fries",    data.fries_busy,    data.crew_fries);
    updateStation("assembly", data.assembly_busy, data.crew_assembly);

    // overall load
    const load    = data.predicted_load;
    const loadPct = Math.min(Math.round(load * 100), 100);
    const loadColor = load >= 0.8 ? "#f44336" : load < 0.4 ? "#4caf50" : "#ffc107";

    document.getElementById("load-number").textContent    = load.toFixed(2);
    document.getElementById("load-number").style.color    = loadColor;
    document.getElementById("load-bar").style.width       = loadPct + "%";
    document.getElementById("load-bar").style.background  = loadColor;

    let statusLabel;
    if (load >= 0.8) {
      highLoadCount++;
      statusLabel = "🔴 HIGH";
    } else if (load < 0.4) {
      highLoadCount = 0;
      statusLabel = "🟢 LOW";
    } else {
      highLoadCount = 0;
      statusLabel = "🟡 MEDIUM";
    }

    document.getElementById("status-text").textContent     = statusLabel;
    document.getElementById("load-status-text").textContent = statusLabel;

    const banner = document.getElementById("alert-banner");
    banner.style.display = (highLoadCount >= 3) ? "block" : "none";

    // recommendations
    const recList = document.getElementById("rec-list");
    recList.innerHTML = "";
    (data.recommendations.length ? data.recommendations : ["No action needed"]).forEach(rec => {
      const li = document.createElement("li");
      li.className = "rec-item";
      li.textContent = rec;
      recList.appendChild(li);
    });
  }

  fetchData();
  setInterval(fetchData, 2000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
