"""Contribution Atlas SVG renderer.

Renders high-fidelity, Titanium-Hacker-themed static SVG visualization of
GitHub contribution data in 3D isometric projection.
"""
from __future__ import annotations

import datetime as dt
import html
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.contribution_geometry import (
    IsometricGrid,
    calculate_tower_height,
    get_intensity_level,
)
from scripts.contribution_metrics import compute_metrics


def _xml_escape(val: Any) -> str:
    return html.escape(str(val), quote=True)


def get_atlas_palette(theme: dict, is_light: bool = False) -> dict:
    """Return theme color palette for Contribution Atlas."""
    if is_light:
        return {
            "bg": "transparent",
            "card_bg": "url(#atlasCardBg)",
            "card_bg_start": "#FFFFFF",
            "card_bg_end": "#F2F6F8",
            "card_stroke": "#A8C0CB",
            "stat_bg": "#FFFFFF",
            "stat_stroke": "#D0D7DE",
            "accent": "#1A7F37",
            "accent_bright": "#2DA44E",
            "text": "#1F2328",
            "muted": "#656D76",
            "meta": "#57606A",
            "grid_line": "#E1E4E8",
            "platform_top": "#F6F8FA",
            "platform_edge": "#D0D7DE",
            "platform_front": "#AFB8C1",
            # Towers by intensity (top, left, right, stroke)
            "levels": [
                {"top": "#EBEDF0", "left": "#D0D7DE", "right": "#AFB8C1", "stroke": "#D8DEE4", "glow": False}, # 0
                {"top": "#9BE9A8", "left": "#7BC96F", "right": "#57A14D", "stroke": "#7BC96F", "glow": False}, # 1
                {"top": "#40C463", "left": "#30A14E", "right": "#216E39", "stroke": "#30A14E", "glow": False}, # 2
                {"top": "#30A14E", "left": "#216E39", "right": "#144620", "stroke": "#216E39", "glow": False}, # 3
                {"top": "#216E39", "left": "#144620", "right": "#0D2E14", "stroke": "#195B28", "glow": True},  # 4
            ],
        }

    # Dark Titanium Hacker Palette (matching #141B20 -> #0E1317 contained surfaces)
    return {
        "bg": "transparent",
        "card_bg": "url(#atlasCardBg)",
        "card_bg_start": "#141B20",
        "card_bg_end": "#0E1317",
        "card_stroke": theme.get("stroke", "#42535C"),
        "stat_bg": "#10171B",
        "stat_stroke": "#33444D",
        "accent": theme.get("accent", "#B6FF3B"),
        "accent_bright": "#D4FF78",
        "text": theme.get("text", "#EEF7EF"),
        "muted": theme.get("muted", "#7A8C99"),
        "meta": "#52636E",
        "grid_line": "#162026",
        "platform_top": "#080C0E",
        "platform_edge": "#1A252B",
        "platform_front": "#0E1518",
        # Towers by intensity (top, left, right, stroke)
        "levels": [
            {"top": "#10161A", "left": "#0D1215", "right": "#090D0F", "stroke": "#182228", "glow": False}, # 0: Inactive
            {"top": "#2E424D", "left": "#1E2C33", "right": "#141E23", "stroke": "#3A5260", "glow": False}, # 1: Low
            {"top": "#3E702A", "left": "#2B4F1D", "right": "#1D3613", "stroke": "#529437", "glow": False}, # 2: Moderate
            {"top": "#6EBC2C", "left": "#4B821E", "right": "#335914", "stroke": "#8AE33A", "glow": False}, # 3: High
            {"top": "#B6FF3B", "left": "#78A826", "right": "#54751A", "stroke": "#D4FF78", "glow": True},  # 4: Peak
        ],
    }


def render_contribution_atlas_svg(
    contrib_data: Dict[str, Any],
    theme: Dict[str, Any],
    width: int = 1160,
    height: int = 460,
    is_light: bool = False,
    height_progress: float = 1.0,
) -> str:
    """Generate the complete 3D Contribution Atlas SVG."""
    palette = get_atlas_palette(theme, is_light)
    days = contrib_data.get("days", [])
    total_reported = contrib_data.get("total_contributions")
    metrics = compute_metrics(days, total_reported=total_reported)

    # Initialize isometric grid
    # Centered for width 1160
    # Week span ~946px, origin_x ~156, origin_y ~215
    grid = IsometricGrid(
        origin_x=156.0,
        origin_y=215.0,
        dx_w=17.2,
        dy_w=1.4,
        dx_d=-8.6,
        dy_d=7.8,
        tile_scale=0.88,
        h_min=12.0,
        h_max=76.0,
        h_cap=88.0,
    )

    ref_max = metrics["busiest_day"]["count"] or 26
    towers = grid.compute_day_towers(days, ref_max=ref_max, height_progress=height_progress)

    # Calculate platform bounding polygon
    # 4 corners of complete platform based on week 0..52 and weekday 0..6
    num_weeks = max(53, max((t["week_idx"] for t in towers), default=52) + 1)
    
    # Platform margin
    pw_start, pw_end = -0.6, num_weeks - 0.4
    pd_start, pd_end = -0.6, 6.6

    p_top = (grid.origin_x + pw_start * grid.dx_w + pd_start * grid.dx_d,
             grid.origin_y + pw_start * grid.dy_w + pd_start * grid.dy_d)
    p_right = (grid.origin_x + pw_end * grid.dx_w + pd_start * grid.dx_d,
               grid.origin_y + pw_end * grid.dy_w + pd_start * grid.dy_d)
    p_bottom = (grid.origin_x + pw_end * grid.dx_w + pd_end * grid.dx_d,
                grid.origin_y + pw_end * grid.dy_w + pd_end * grid.dy_d)
    p_left = (grid.origin_x + pw_start * grid.dx_w + pd_end * grid.dx_d,
              grid.origin_y + pw_start * grid.dy_w + pd_end * grid.dy_d)

    slab_thickness = 10.0
    p_bottom_drop = (p_bottom[0], p_bottom[1] + slab_thickness)
    p_left_drop = (p_left[0], p_left[1] + slab_thickness)
    p_right_drop = (p_right[0], p_right[1] + slab_thickness)

    # Build SVG elements
    svg_parts: List[str] = []

    # Defs: card background gradient, glow filter and platform gradients
    svg_parts.append(f'''<defs>
  <linearGradient id="atlasCardBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{palette['card_bg_start']}" />
    <stop offset="100%" stop-color="{palette['card_bg_end']}" />
  </linearGradient>
  <filter id="atlas-lime-glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
  <linearGradient id="platform-left-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{palette['platform_edge']}" />
    <stop offset="100%" stop-color="{palette['platform_front']}" />
  </linearGradient>
  <linearGradient id="platform-right-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{palette['platform_edge']}" stop-opacity="0.8" />
    <stop offset="100%" stop-color="{palette['platform_front']}" stop-opacity="0.9" />
  </linearGradient>
</defs>''')

    # 1. Main outer card container (chamfered path matching profile design)
    # Card bounds: x=8, y=6, w=width-16, h=height-12
    cw = width - 16
    ch = height - 12
    cx0, cy0 = 8, 6
    chamfer = 14
    c_path = (
        f"M {cx0 + chamfer} {cy0} "
        f"H {cx0 + cw - chamfer} L {cx0 + cw} {cy0 + chamfer} "
        f"V {cy0 + ch - chamfer} L {cx0 + cw - chamfer} {cy0 + ch} "
        f"H {cx0 + chamfer} L {cx0} {cy0 + ch - chamfer} "
        f"V {cy0 + chamfer} Z"
    )
    svg_parts.append(
        f'<path d="{c_path}" fill="{palette["card_bg"]}" stroke="{palette["card_stroke"]}" stroke-width="1.2" />'
    )

    # Accent glow mark on bottom-right corner
    if not is_light:
        glow_corner = f"M {cx0 + cw - 32} {cy0 + ch} L {cx0 + cw - chamfer} {cy0 + ch} L {cx0 + cw} {cy0 + ch - chamfer} L {cx0 + cw} {cy0 + ch - 32}"
        svg_parts.append(f'<path d="{glow_corner}" fill="none" stroke="{palette["accent"]}" stroke-width="2.5" filter="url(#atlas-lime-glow)" opacity="0.85" />')

    # 2. Statistics strip (5 metric boxes)
    # Box layout: width ~216, height 58, gap ~6
    stat_y = 24
    box_w = 216
    box_h = 58
    gap = 7
    start_x = 24

    stats_meta = [
        {
            "icon": "octocat",
            "label": "Total Contributions",
            "val": f"{metrics['total_contributions']:,}",
            "color": palette["accent"],
        },
        {
            "icon": "calendar",
            "label": "Active Days",
            "val": f"{metrics['active_days']}",
            "color": palette["text"],
        },
        {
            "icon": "bolt",
            "label": "Busiest Day",
            "val": f"{metrics['busiest_day']['count']} contributions",
            "color": palette["text"],
        },
        {
            "icon": "flame",
            "label": "Current Streak",
            "val": f"{metrics['current_streak']} days",
            "color": palette["text"],
        },
        {
            "icon": "trophy",
            "label": "Longest Streak",
            "val": f"{metrics['longest_streak']} days",
            "color": palette["text"],
        },
    ]

    # Pre-render standard vector icons for stat boxes
    icons_svg = {
        "octocat": '<path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0012 2z" fill="currentColor"/>',
        "calendar": '<path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 002 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2z" fill="currentColor"/><circle cx="8" cy="14" r="1.5" fill="currentColor"/><circle cx="12" cy="14" r="1.5" fill="currentColor"/><circle cx="16" cy="14" r="1.5" fill="currentColor"/>',
        "bolt": '<path d="M7 2v11h3v9l7-12h-4l4-8H7z" fill="currentColor"/>',
        "flame": '<path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z" fill="currentColor"/>',
        "trophy": '<path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94A5.01 5.01 0 0011 15.9V19H7v2h10v-2h-4v-3.1c1.86-.44 3.27-1.89 3.61-3.72C19.08 11.83 21 9.75 21 8V7c0-1.1-.9-2-2-2zm-14 3V7h2v3c-1.1 0-2-.9-2-2zm14 0c0 1.1-.9 2-2 2V7h2v1z" fill="currentColor"/>',
    }

    for i, s in enumerate(stats_meta):
        bx = start_x + i * (box_w + gap)
        # Card background
        svg_parts.append(
            f'<rect x="{bx}" y="{stat_y}" width="{box_w}" height="{box_h}" rx="8" fill="{palette["stat_bg"]}" stroke="{palette["stat_stroke"]}" stroke-width="1" />'
        )
        # Icon
        svg_parts.append(
            f'<g transform="translate({bx + 12}, {stat_y + 16}) scale(1.1)" color="{s["color"]}">{icons_svg[s["icon"]]}</g>'
        )
        # Metric Label
        svg_parts.append(
            f'<text x="{bx + 48}" y="{stat_y + 23}" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="500" fill="{palette["muted"]}">{s["label"]}</text>'
        )
        # Metric Value
        val_size = "17" if "contributions" in s["val"] else "19"
        svg_parts.append(
            f'<text x="{bx + 48}" y="{stat_y + 46}" font-family="system-ui, -apple-system, sans-serif" font-size="{val_size}" font-weight="750" fill="{s["color"]}">{s["val"]}</text>'
        )

    # 3. Platform Base (Isometric slab)
    # Top face
    p_top_pts = f"{p_top[0]},{p_top[1]} {p_right[0]},{p_right[1]} {p_bottom[0]},{p_bottom[1]} {p_left[0]},{p_left[1]}"
    svg_parts.append(f'<polygon points="{p_top_pts}" fill="{palette["platform_top"]}" stroke="{palette["platform_edge"]}" stroke-width="1" />')

    # Left thickness face
    p_left_face = f"{p_left[0]},{p_left[1]} {p_bottom[0]},{p_bottom[1]} {p_bottom_drop[0]},{p_bottom_drop[1]} {p_left_drop[0]},{p_left_drop[1]}"
    svg_parts.append(f'<polygon points="{p_left_face}" fill="url(#platform-left-grad)" stroke="{palette["platform_edge"]}" stroke-width="0.8" />')

    # Right thickness face
    p_right_face = f"{p_bottom[0]},{p_bottom[1]} {p_right[0]},{p_right[1]} {p_right_drop[0]},{p_right_drop[1]} {p_bottom_drop[0]},{p_bottom_drop[1]}"
    svg_parts.append(f'<polygon points="{p_right_face}" fill="url(#platform-right-grad)" stroke="{palette["platform_edge"]}" stroke-width="0.8" />')

    # Platform grid wireframe lines
    # Subtle longitudinal and lateral grid lines on top of the platform
    for w_line in range(0, num_weeks + 1, 4):
        x1 = grid.origin_x + w_line * grid.dx_w + pd_start * grid.dx_d
        y1 = grid.origin_y + w_line * grid.dy_w + pd_start * grid.dy_d
        x2 = grid.origin_x + w_line * grid.dx_w + pd_end * grid.dx_d
        y2 = grid.origin_y + w_line * grid.dy_w + pd_end * grid.dy_d
        svg_parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{palette["grid_line"]}" stroke-width="0.5" opacity="0.6" />')

    # 4. Isometric Day Towers & Tiles (rendered back-to-front)
    for t in towers:
        count = t["count"]
        curr_h = t["current_height"]
        lvl = t["intensity"]
        col = palette["levels"][lvl]

        g = t["ground"]
        top_pts = t["top"]

        if curr_h <= 0.1:
            # Flat ground tile (count == 0 or progress == 0)
            pts_str = f"{g['top'][0]},{g['top'][1]} {g['right'][0]},{g['right'][1]} {g['bottom'][0]},{g['bottom'][1]} {g['left'][0]},{g['left'][1]}"
            svg_parts.append(f'<polygon points="{pts_str}" fill="{col["top"]}" stroke="{col["stroke"]}" stroke-width="0.6" opacity="0.8" />')
        else:
            # 3D Prism: Left face, Right face, Top face
            # Left visible side face: [left, top_left, top_bottom, bottom]
            left_pts = (
                f"{g['left'][0]},{g['left'][1]} "
                f"{top_pts['left'][0]},{top_pts['left'][1]} "
                f"{top_pts['bottom'][0]},{top_pts['bottom'][1]} "
                f"{g['bottom'][0]},{g['bottom'][1]}"
            )
            # Right visible side face: [bottom, top_bottom, top_right, right]
            right_pts = (
                f"{g['bottom'][0]},{g['bottom'][1]} "
                f"{top_pts['bottom'][0]},{top_pts['bottom'][1]} "
                f"{top_pts['right'][0]},{top_pts['right'][1]} "
                f"{g['right'][0]},{g['right'][1]}"
            )
            # Top visible face: [top, right, bottom, left]
            roof_pts = (
                f"{top_pts['top'][0]},{top_pts['top'][1]} "
                f"{top_pts['right'][0]},{top_pts['right'][1]} "
                f"{top_pts['bottom'][0]},{top_pts['bottom'][1]} "
                f"{top_pts['left'][0]},{top_pts['left'][1]}"
            )

            # Draw left side face
            svg_parts.append(f'<polygon points="{left_pts}" fill="{col["left"]}" stroke="{col["left"]}" stroke-width="0.5" />')
            # Draw right side face
            svg_parts.append(f'<polygon points="{right_pts}" fill="{col["right"]}" stroke="{col["right"]}" stroke-width="0.5" />')
            # Draw top face
            glow_attr = ' filter="url(#atlas-lime-glow)"' if col.get("glow") and not is_light else ""
            svg_parts.append(f'<polygon points="{roof_pts}" fill="{col["top"]}" stroke="{col["stroke"]}" stroke-width="0.7"{glow_attr} />')

    # 5. Bottom Metadata & Activity Legend
    # Metadata on bottom-left
    meta_date = contrib_data.get("fetched_at_utc", "")[:10] or dt.date.today().isoformat()
    svg_parts.append(
        f'<text x="24" y="{height - 18}" font-family="ui-monospace, SFMono-Regular, monospace" font-size="11" fill="{palette["meta"]}">'
        f'Data: GitHub Contributions · Updated: {meta_date}'
        f'</text>'
    )

    # Legend on bottom-right: Less [ ][ ][ ][ ][ ] More
    leg_x = width - 180
    leg_y = height - 26
    svg_parts.append(
        f'<text x="{leg_x - 30}" y="{leg_y + 8}" font-family="ui-monospace, SFMono-Regular, monospace" font-size="11" fill="{palette["muted"]}">Less</text>'
    )
    for l_idx, l_col in enumerate(palette["levels"]):
        lx = leg_x + l_idx * 15
        glow_attr = ' filter="url(#atlas-lime-glow)"' if l_col.get("glow") and not is_light else ""
        svg_parts.append(
            f'<rect x="{lx}" y="{leg_y}" width="10" height="10" rx="2" fill="{l_col["top"]}" stroke="{l_col["stroke"]}" stroke-width="0.5"{glow_attr} />'
        )
    svg_parts.append(
        f'<text x="{leg_x + 5 * 15 + 8}" y="{leg_y + 8}" font-family="ui-monospace, SFMono-Regular, monospace" font-size="11" fill="{palette["muted"]}">More</text>'
    )

    # Close SVG
    body_content = "\n".join(svg_parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution Atlas: {metrics['total_contributions']:,} contributions · {metrics['active_days']} active days as an isometric 3D city">
<title>Contribution Atlas: {metrics['total_contributions']:,} contributions</title>
<desc>{metrics['total_contributions']:,} contributions across {metrics['active_days']} active days</desc>
{body_content}
</svg>'''


def main():
    root = Path(__file__).resolve().parents[1]
    import json
    data_file = root / "data" / "contributions.json"
    if not data_file.is_file():
        raise SystemExit(f"Missing {data_file}")
    data = json.loads(data_file.read_text(encoding="utf-8"))

    themes_file = root / "design" / "themes.json"
    themes = json.loads(themes_file.read_text(encoding="utf-8"))
    theme = themes.get("titanium_hacker", themes.get("default", {}))

    out_dir = root / "assets" / "contributions"
    out_dir.mkdir(parents=True, exist_ok=True)

    dark_svg = render_contribution_atlas_svg(data, theme, is_light=False)
    light_svg = render_contribution_atlas_svg(data, theme, is_light=True)

    (out_dir / "atlas-static.svg").write_text(dark_svg, encoding="utf-8")
    (out_dir / "atlas-static-light.svg").write_text(light_svg, encoding="utf-8")
    print(f"Generated {out_dir / 'atlas-static.svg'} and light variant.")


if __name__ == "__main__":
    main()
