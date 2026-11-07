"""Generate interactive GitHub Pages Contribution Atlas (docs/atlas.html).

Features:
- Pure HTML5 Canvas + vanilla JavaScript (zero external CDN or runtime dependencies).
- Scroll-triggered reveal via IntersectionObserver.
- High-DPI / Retina canvas support.
- Interactive mouse hover with date & contribution tooltip.
- Replay animation button.
- Embedded verified public dataset from data/contributions.json.
- Adheres strictly to Titanium Hacker design system.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_interactive_atlas():
    data_file = ROOT / "data" / "contributions.json"
    data = json.loads(data_file.read_text(encoding="utf-8"))

    themes_file = ROOT / "design" / "themes.json"
    themes = json.loads(themes_file.read_text(encoding="utf-8"))
    theme = themes.get("titanium_hacker", themes.get("default", {}))

    out_file = ROOT / "docs" / "atlas.html"

    data_json_str = json.dumps(data)
    theme_json_str = json.dumps(theme)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phoenixarjun — 3D Contribution Atlas</title>
  <style>
    :root {{
      --bg: #070B0C;
      --card-bg: #0C0F10;
      --surface: #10161A;
      --border: #222D33;
      --border-light: #1E2B33;
      --accent: #B6FF3B;
      --text: #EEF7EF;
      --muted: #7A8C99;
      --meta: #52636E;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }}
    .container {{
      max-width: 1180px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .terminal-header {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid #162026;
    }}
    .terminal-header .prompt {{ color: var(--accent); font-weight: bold; }}
    .atlas-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px 28px;
      position: relative;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }}
    .title-group {{
      display: flex;
      align-items: baseline;
      gap: 14px;
    }}
    .accent-bar {{
      width: 4px;
      height: 22px;
      background: var(--accent);
      border-radius: 2px;
      display: inline-block;
      vertical-align: middle;
      margin-right: 8px;
    }}
    .title {{
      font-size: 22px;
      font-weight: 750;
      color: var(--accent);
      display: flex;
      align-items: center;
    }}
    .subtitle {{
      font-size: 13.5px;
      color: var(--muted);
    }}
    .btn-replay {{
      background: var(--surface);
      color: var(--accent);
      border: 1px solid var(--border-light);
      padding: 6px 14px;
      border-radius: 6px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}
    .btn-replay:hover {{
      background: #182228;
      border-color: var(--accent);
    }}
    .stats-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      margin-bottom: 24px;
    }}
    .stat-box {{
      background: var(--surface);
      border: 1px solid var(--border-light);
      border-radius: 6px;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .stat-icon {{
      width: 26px;
      height: 26px;
      fill: currentColor;
    }}
    .stat-text {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .stat-label {{
      font-size: 11px;
      color: var(--muted);
      text-transform: capitalize;
    }}
    .stat-val {{
      font-size: 18px;
      font-weight: 750;
      color: var(--text);
    }}
    .stat-val.accent {{ color: var(--accent); }}
    .canvas-container {{
      width: 100%;
      height: 380px;
      position: relative;
    }}
    canvas {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 14px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      color: var(--meta);
    }}
    .legend {{
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--muted);
    }}
    .legend-box {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }}
    #tooltip {{
      position: absolute;
      background: rgba(16, 22, 26, 0.95);
      border: 1px solid var(--accent);
      padding: 8px 12px;
      border-radius: 6px;
      pointer-events: none;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      color: var(--text);
      display: none;
      z-index: 100;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      transform: translate(-50%, -120%);
    }}
    #tooltip .tt-date {{ color: var(--muted); margin-bottom: 2px; }}
    #tooltip .tt-count {{ font-size: 13px; font-weight: bold; color: var(--accent); }}
  </style>
</head>
<body>

<div class="container">
  <div class="terminal-header">
    <span class="prompt">naresh@github:~$</span> render --contribution-atlas
  </div>

  <div class="atlas-card" id="atlasSection">
    <div class="card-top">
      <div class="title-group">
        <h1 class="title"><span class="accent-bar"></span>Contribution Atlas</h1>
        <span class="subtitle">// My GitHub activity, visualized as a contribution city</span>
      </div>
      <button class="btn-replay" id="btnReplay"><span>↺</span> Replay Construction</button>
    </div>

    <div class="stats-strip" id="statsStrip"></div>

    <div class="canvas-container">
      <canvas id="atlasCanvas"></canvas>
      <div id="tooltip"></div>
    </div>

    <div class="card-footer">
      <div id="metadataText">Data: GitHub Contributions · Updated: 2026-11-07</div>
      <div class="legend">
        <span>Less</span>
        <div class="legend-box" style="background: #10161A; border: 1px solid #182228;"></div>
        <div class="legend-box" style="background: #2E424D; border: 1px solid #3A5260;"></div>
        <div class="legend-box" style="background: #3E702A; border: 1px solid #529437;"></div>
        <div class="legend-box" style="background: #6EBC2C; border: 1px solid #8AE33A;"></div>
        <div class="legend-box" style="background: #B6FF3B; border: 1px solid #D4FF78;"></div>
        <span>More</span>
      </div>
    </div>
  </div>
</div>

<script>
const DATA = {data_json_str};

// Metrics Computation
function computeMetrics(days) {{
  const sorted = [...days].sort((a,b) => a.date.localeCompare(b.date));
  const total = DATA.total_contributions || sorted.reduce((sum, d) => sum + d.count, 0);
  const active = sorted.filter(d => d.count > 0).length;
  let busiest = {{ count: 0, date: "" }};
  let longest = 0, cur = 0;

  for (const d of sorted) {{
    if (d.count > busiest.count) {{ busiest = d; }}
    if (d.count > 0) {{
      cur++;
      if (cur > longest) longest = cur;
    }} else {{
      cur = 0;
    }}
  }}

  // Current streak (ending today or yesterday)
  let currStreak = 0;
  const n = sorted.length;
  if (n > 0) {{
    if (sorted[n - 1].count > 0) {{
      let i = n - 1;
      while (i >= 0 && sorted[i].count > 0) {{ currStreak++; i--; }}
    }} else if (n > 1 && sorted[n - 2].count > 0) {{
      let i = n - 2;
      while (i >= 0 && sorted[i].count > 0) {{ currStreak++; i--; }}
    }}
  }}

  return {{ total, active, busiest, currStreak, longest }};
}}

const metrics = computeMetrics(DATA.days);

// Populate Stats Strip
const statsStrip = document.getElementById("statsStrip");
const statsConfig = [
  {{ label: "Total Contributions", val: metrics.total.toLocaleString(), accent: true }},
  {{ label: "Active Days", val: metrics.active.toString(), accent: false }},
  {{ label: "Busiest Day", val: metrics.busiest.count + " contributions", accent: false }},
  {{ label: "Current Streak", val: metrics.currStreak + " days", accent: false }},
  {{ label: "Longest Streak", val: metrics.longest + " days", accent: false }},
];

statsConfig.forEach(s => {{
  const box = document.createElement("div");
  box.className = "stat-box";
  box.innerHTML = `
    <div class="stat-text">
      <span class="stat-label">${{s.label}}</span>
      <span class="stat-val ${{s.accent ? 'accent' : ''}}">${{s.val}}</span>
    </div>
  `;
  statsStrip.appendChild(box);
}});

document.getElementById("metadataText").innerText =
  `Data: GitHub Contributions · Updated: ${{DATA.fetched_at_utc ? DATA.fetched_at_utc.slice(0, 10) : '2026-11-07'}}`;

// Geometry & Projection
const canvas = document.getElementById("atlasCanvas");
const ctx = canvas.getContext("2d");
const tooltip = document.getElementById("tooltip");

const levels = [
  {{ top: "#10161A", left: "#0D1215", right: "#090D0F", stroke: "#182228" }},
  {{ top: "#2E424D", left: "#1E2C33", right: "#141E23", stroke: "#3A5260" }},
  {{ top: "#3E702A", left: "#2B4F1D", right: "#1D3613", stroke: "#529437" }},
  {{ top: "#6EBC2C", left: "#4B821E", right: "#335914", stroke: "#8AE33A" }},
  {{ top: "#B6FF3B", left: "#78A826", right: "#54751A", stroke: "#D4FF78" }}
];

function getLevel(c) {{
  if (c <= 0) return 0;
  if (c <= 2) return 1;
  if (c <= 6) return 2;
  if (c <= 14) return 3;
  return 4;
}}

function getTargetHeight(c, refMax=26) {{
  if (c <= 0) return 0;
  const scale = Math.log(1 + c) / Math.log(1 + Math.max(1, refMax));
  return Math.min(88, 12 + (76 - 12) * scale);
}}

let towers = [];
let animProgress = 0;
let isAnimating = false;
let animStartTime = null;
let hoveredTower = null;

function setupGeometry() {{
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.resetTransform();
  ctx.scale(dpr, dpr);

  const W = rect.width;
  const H = rect.height;

  const dx_w = (W / 1160) * 17.2;
  const dy_w = 1.4;
  const dx_d = (W / 1160) * -8.6;
  const dy_d = 7.8;
  const originX = W * 0.135;
  const originY = H * 0.48;

  const sorted = [...DATA.days].sort((a,b) => a.date.localeCompare(b.date));
  const firstDate = new Date(sorted[0].date + "T00:00:00Z");
  const firstSunday = new Date(firstDate);
  firstSunday.setUTCDate(firstDate.getUTCDate() - firstDate.getUTCDay());

  towers = sorted.map((d, i) => {{
    const curDate = new Date(d.date + "T00:00:00Z");
    const ghWeekday = curDate.getUTCDay();
    const diffDays = Math.floor((curDate - firstSunday) / (86400000));
    const weekIdx = Math.floor(diffDays / 7);

    const cx = originX + weekIdx * dx_w + ghWeekday * dx_d;
    const cy = originY + weekIdx * dy_w + ghWeekday * dy_d;
    const targetH = getTargetHeight(d.count, metrics.busiest.count);
    const lvl = getLevel(d.count);

    const hwx = (dx_w * 0.88) / 2;
    const hwy = (dy_w * 0.88) / 2;
    const hdx = (dx_d * 0.88) / 2;
    const hdy = (dy_d * 0.88) / 2;

    const ground = {{
      top: [cx - hwx - hdx, cy - hwy - hdy],
      right: [cx + hwx - hdx, cy + hwy - hdy],
      bottom: [cx + hwx + hdx, cy + hwy + hdy],
      left: [cx - hwx + hdx, cy - hwy + hdy]
    }};

    return {{
      date: d.date,
      count: d.count,
      cx, cy,
      ground,
      targetH,
      lvl,
      depth: cy + weekIdx * 0.01,
      chronoIndex: i
    }};
  }});

  towers.sort((a,b) => a.depth - b.depth);
}}

function easeOutCubic(t) {{
  t = Math.max(0, Math.min(1, t));
  return 1 - Math.pow(1 - t, 3);
}}

function render(time) {{
  const rect = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, rect.width, rect.height);

  const totalRise = 2.4;
  const numDays = towers.length;

  for (const t of towers) {{
    let currentH = 0;
    if (t.targetH > 0) {{
      const ratio = t.chronoIndex / Math.max(1, numDays - 1);
      const tStart = 0.4 + 1.6 * ratio;
      const tWin = 0.55;
      if (animProgress >= tStart + tWin) {{
        currentH = t.targetH;
      }} else if (animProgress > tStart) {{
        currentH = t.targetH * easeOutCubic((animProgress - tStart) / tWin);
      }}
    }}

    const g = t.ground;
    const col = levels[t.lvl];
    const isHovered = (hoveredTower === t);

    if (currentH <= 0.1) {{
      // Flat ground tile
      ctx.beginPath();
      ctx.moveTo(g.top[0], g.top[1]);
      ctx.lineTo(g.right[0], g.right[1]);
      ctx.lineTo(g.bottom[0], g.bottom[1]);
      ctx.lineTo(g.left[0], g.left[1]);
      ctx.closePath();
      ctx.fillStyle = isHovered ? "#22333B" : col.top;
      ctx.fill();
      ctx.strokeStyle = isHovered ? "#B6FF3B" : col.stroke;
      ctx.lineWidth = 0.7;
      ctx.stroke();
    }} else {{
      const topPts = {{
        top: [g.top[0], g.top[1] - currentH],
        right: [g.right[0], g.right[1] - currentH],
        bottom: [g.bottom[0], g.bottom[1] - currentH],
        left: [g.left[0], g.left[1] - currentH]
      }};

      // Left face
      ctx.beginPath();
      ctx.moveTo(g.left[0], g.left[1]);
      ctx.lineTo(topPts.left[0], topPts.left[1]);
      ctx.lineTo(topPts.bottom[0], topPts.bottom[1]);
      ctx.lineTo(g.bottom[0], g.bottom[1]);
      ctx.closePath();
      ctx.fillStyle = col.left;
      ctx.fill();

      // Right face
      ctx.beginPath();
      ctx.moveTo(g.bottom[0], g.bottom[1]);
      ctx.lineTo(topPts.bottom[0], topPts.bottom[1]);
      ctx.lineTo(topPts.right[0], topPts.right[1]);
      ctx.lineTo(g.right[0], g.right[1]);
      ctx.closePath();
      ctx.fillStyle = col.right;
      ctx.fill();

      // Top face
      ctx.beginPath();
      ctx.moveTo(topPts.top[0], topPts.top[1]);
      ctx.lineTo(topPts.right[0], topPts.right[1]);
      ctx.lineTo(topPts.bottom[0], topPts.bottom[1]);
      ctx.lineTo(topPts.left[0], topPts.left[1]);
      ctx.closePath();
      ctx.fillStyle = isHovered ? "#D4FF78" : col.top;
      ctx.fill();
      ctx.strokeStyle = isHovered ? "#FFFFFF" : col.stroke;
      ctx.lineWidth = isHovered ? 1.5 : 0.8;
      ctx.stroke();
    }}
  }}
}}

function animate(timestamp) {{
  if (!animStartTime) animStartTime = timestamp;
  const elapsed = (timestamp - animStartTime) / 1000;
  animProgress = elapsed;

  render(timestamp);

  if (elapsed < 3.2) {{
    requestAnimationFrame(animate);
  }} else {{
    animProgress = 10.0;
    render(timestamp);
    isAnimating = false;
  }}
}}

function startAnimation() {{
  animStartTime = null;
  animProgress = 0;
  isAnimating = true;
  requestAnimationFrame(animate);
}}

// Scroll trigger via IntersectionObserver
let hasTriggered = false;
const observer = new IntersectionObserver((entries) => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting && !hasTriggered) {{
      hasTriggered = true;
      startAnimation();
    }}
  }});
}}, {{ threshold: 0.25 }});

window.addEventListener("load", () => {{
  setupGeometry();
  render();
  observer.observe(document.getElementById("atlasSection"));
}});

window.addEventListener("resize", () => {{
  setupGeometry();
  render();
}});

document.getElementById("btnReplay").addEventListener("click", () => {{
  startAnimation();
}});

// Interactive hover detection
canvas.addEventListener("mousemove", (e) => {{
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;

  let found = null;
  // Test in reverse depth order (front to back)
  for (let i = towers.length - 1; i >= 0; i--) {{
    const t = towers[i];
    const dx = mx - t.cx;
    const dy = my - (t.cy - (t.targetH * (animProgress > 3.0 ? 1 : 0)) / 2);
    if (Math.abs(dx) < 9 && Math.abs(dy) < 18) {{
      found = t;
      break;
    }}
  }}

  if (found !== hoveredTower) {{
    hoveredTower = found;
    render();
  }}

  if (found) {{
    tooltip.style.display = "block";
    tooltip.style.left = mx + "px";
    tooltip.style.top = (my - 10) + "px";
    tooltip.innerHTML = `
      <div class="tt-date">${{found.date}}</div>
      <div class="tt-count">${{found.count}} ${{found.count === 1 ? 'contribution' : 'contributions'}}</div>
    `;
  }} else {{
    tooltip.style.display = "none";
  }}
}});

canvas.addEventListener("mouseleave", () => {{
  hoveredTower = null;
  tooltip.style.display = "none";
  render();
}});
</script>

</body>
</html>
"""
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Generated interactive atlas: {out_file}")

if __name__ == "__main__":
    build_interactive_atlas()

