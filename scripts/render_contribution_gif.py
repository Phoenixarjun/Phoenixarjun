"""Contribution Atlas GIF animation engine.

Generates a lightweight, high-fidelity animated GIF showing the 3D Contribution Atlas
rising chronologically from flat grid to completed architectural skyline.

Phases:
1. Grid initialization (0.6s) - Ground plane and flat tiles.
2. Construction (2.2s) - Staggered chronological rise using ease-out cubic.
3. Settling (0.6s) - Tallest towers finalize height without overshoot.
4. Completed hold (2.1s) - Fully constructed city holds for inspection.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.contribution_geometry import (
    IsometricGrid,
    calculate_tower_height,
    get_intensity_level,
)
from scripts.contribution_metrics import compute_metrics
from scripts.render_contribution_svg import get_atlas_palette, render_contribution_atlas_svg


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    h = hex_code.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)


def get_chrome_path() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if Path(c).is_file():
            return c
    return None


def render_base_card_image(contrib_data: dict, theme: dict, width: int = 1160, height: int = 460) -> Image.Image:
    """Render base card SVG (without active towers, only flat platform and UI) using headless Chrome."""
    chrome = get_chrome_path()
    if not chrome:
        # Fallback to dark background
        return Image.new("RGBA", (width, height), (12, 15, 16, 255))

    # Generate static SVG with height_progress = 0 (only flat ground tiles)
    base_svg = render_contribution_atlas_svg(
        contrib_data, theme, width=width, height=height, is_light=False, height_progress=0.0
    )

    tmp_dir = Path(tempfile.mkdtemp())
    tmp_html = tmp_dir / "base.html"
    out_png = tmp_dir / "base.png"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #070B0C; width: {width}px; height: {height}px; overflow: hidden; }}
  </style>
</head>
<body>
  {base_svg}
</body>
</html>"""
    tmp_html.write_text(html_content, encoding="utf-8")

    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--screenshot={out_png}",
        str(tmp_html),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    img = Image.open(out_png).convert("RGBA")
    return img


def render_atlas_gif(
    contrib_data: Dict[str, Any],
    theme: Dict[str, Any],
    out_path: Path,
    num_frames: int = 36,
    fps: int = 8,
) -> Path:
    """Generate the animated GIF."""
    width, height = 1160, 460
    palette = get_atlas_palette(theme, is_light=False)
    days = contrib_data.get("days", [])
    total_reported = contrib_data.get("total_contributions")
    metrics = compute_metrics(days, total_reported=total_reported)
    ref_max = metrics["busiest_day"]["count"] or 26

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

    # All days sorted chronologically
    sorted_days = sorted(days, key=lambda d: d["date"])
    num_days = len(sorted_days)

    # Base card background (rendered with headless Chrome for 100% SVG typography & icon fidelity)
    print("Rendering base card template with Chrome...")
    base_card = render_base_card_image(contrib_data, theme, width, height)

    # Precompute RGB colors for towers
    color_map = []
    for lvl_info in palette["levels"]:
        color_map.append({
            "top": hex_to_rgb(lvl_info["top"]),
            "left": hex_to_rgb(lvl_info["left"]),
            "right": hex_to_rgb(lvl_info["right"]),
            "stroke": hex_to_rgb(lvl_info["stroke"]),
            "glow": lvl_info["glow"],
        })

    frame_duration_ms = int(1000 / fps)
    total_time = num_frames / fps  # e.g. 36 / 8 = 4.5 seconds

    t_init = 0.5    # 0.0s to 0.5s: flat grid
    t_rise = 2.2    # 0.5s to 2.7s: staggered construction
    t_settle = 0.5  # 2.7s to 3.2s: settling
    # 3.2s to 4.5s: completed hold

    print(f"Generating {num_frames} animation frames ({fps} fps, {total_time:.1f}s loop)...")
    frames: List[Image.Image] = []

    for f_idx in range(num_frames):
        current_time = (f_idx / num_frames) * total_time

        # Calculate heights for all days at this frame
        towers_at_frame: List[Dict[str, Any]] = []

        for i, d in enumerate(sorted_days):
            target_h = calculate_tower_height(d["count"], ref_max=ref_max, h_min=grid.h_min, h_max=grid.h_max, h_cap=grid.h_cap)
            intensity = get_intensity_level(d["count"])

            if target_h <= 0.0:
                h_now = 0.0
            elif current_time <= t_init:
                h_now = 0.0
            else:
                # Staggered chronological activation
                # Stagger window across t_rise
                chrono_ratio = i / max(1, num_days - 1)
                t_start = t_init + (t_rise * 0.7) * chrono_ratio
                t_window = 0.6  # duration of individual tower rise

                if current_time < t_start:
                    progress = 0.0
                elif current_time >= t_start + t_window:
                    progress = 1.0
                else:
                    norm = (current_time - t_start) / t_window
                    progress = ease_out_cubic(norm)

                h_now = round(target_h * progress, 2)

            # Map to geometry
            date_obj = dt.date.fromisoformat(d["date"])
            gh_weekday = (date_obj.weekday() + 1) % 7
            first_d_obj = dt.date.fromisoformat(sorted_days[0]["date"])
            gh_weekday_0 = (first_d_obj.weekday() + 1) % 7
            first_sunday = first_d_obj - dt.timedelta(days=gh_weekday_0)
            week_idx = (date_obj - first_sunday).days // 7

            cx, cy = grid.project_cell(week_idx, gh_weekday)
            ground = grid.compute_tile_corners(cx, cy)
            depth = cy + (week_idx * 0.01)

            top_corners = {
                "top": (ground["top"][0], ground["top"][1] - h_now),
                "right": (ground["right"][0], ground["right"][1] - h_now),
                "bottom": (ground["bottom"][0], ground["bottom"][1] - h_now),
                "left": (ground["left"][0], ground["left"][1] - h_now),
            }

            towers_at_frame.append({
                "count": d["count"],
                "target_height": target_h,
                "current_height": h_now,
                "intensity": intensity,
                "ground": ground,
                "top": top_corners,
                "depth": depth,
            })

        # Sort back-to-front
        towers_at_frame.sort(key=lambda t: t["depth"])

        # Composite towers onto copy of base card
        frame = base_card.copy()
        draw = ImageDraw.Draw(frame)

        for t in towers_at_frame:
            curr_h = t["current_height"]
            if curr_h <= 0.1:
                continue  # Base card already has flat tiles rendered

            col = color_map[t["intensity"]]
            g = t["ground"]
            top_pts = t["top"]

            # Left side face
            left_poly = [
                g["left"],
                top_pts["left"],
                top_pts["bottom"],
                g["bottom"],
            ]
            draw.polygon(left_poly, fill=col["left"], outline=col["left"])

            # Right side face
            right_poly = [
                g["bottom"],
                top_pts["bottom"],
                top_pts["right"],
                g["right"],
            ]
            draw.polygon(right_poly, fill=col["right"], outline=col["right"])

            # Top face
            top_poly = [
                top_pts["top"],
                top_pts["right"],
                top_pts["bottom"],
                top_pts["left"],
            ]
            draw.polygon(top_poly, fill=col["top"], outline=col["stroke"])

            # Peak glow effect (if top intensity and near completion)
            if col["glow"] and curr_h > 15:
                # Highlight corner dot
                dot_x, dot_y = top_pts["top"]
                draw.ellipse([dot_x - 1.5, dot_y - 1.5, dot_x + 1.5, dot_y + 1.5], fill=(212, 255, 120))

        # Quantize frame to 128 colors with Floyd-Steinberg dithering for compact, crisp palette
        rgb_frame = frame.convert("RGB")
        quantized = rgb_frame.quantize(colors=128, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quantized)

    print("Assembling optimized animated GIF...")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=1,
        optimize=True,
    )
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"Success! Saved: {out_path} ({size_mb:.2f} MB, {num_frames} frames)")
    return out_path


def main():
    data_file = ROOT / "data" / "contributions.json"
    data = json.loads(data_file.read_text(encoding="utf-8"))

    themes_file = ROOT / "design" / "themes.json"
    themes = json.loads(themes_file.read_text(encoding="utf-8"))
    theme = themes.get("titanium_hacker", themes.get("default", {}))

    out_gif = ROOT / "assets" / "contributions" / "atlas-animated.gif"
    render_atlas_gif(data, theme, out_gif, num_frames=36, fps=8)


if __name__ == "__main__":
    main()

