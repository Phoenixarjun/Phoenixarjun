"""Generate halftone / dot-matrix computational portrait from source profile image.

Reads assets/images/profile.png (or Profile.png), applies contrast optimization,
and produces a high-fidelity halftone dot field with titanium-hacker palette colors.
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]

# Palette tokens for portrait
PORTRAIT_TOKENS = {
    'highlight': '#F0F5EF',    # Crisp off-white for bright facial highlights
    'mid': '#DDF8E4',          # Pale mint for midtone facial areas
    'shadow': '#567A6F',       # Muted steel-mint for dark areas / hair silhouette
    'accent': '#B9FF38',       # Neon lime for perimeter edge & technical dots
    'accent_soft': '#90D92C',  # Secondary lime
    'guide': '#23383F',        # Subtle guide dots
}


def find_profile_image() -> Path:
    candidates = [
        ROOT / 'assets' / 'images' / 'Profile.png',
        ROOT / 'assets' / 'images' / 'profile.png',
        ROOT / 'assets' / 'images' / 'profile.jpg',
        ROOT / 'assets' / 'images' / 'Profile.jpg',
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError("Profile image not found in assets/images/")


def generate_portrait_dots(
    target_w: int = 320,
    target_h: int = 300,
    offset_x: float = 65.0,
    offset_y: float = 60.0,
    spacing: float = 6.2,
) -> dict:
    """Process profile image and return structured dot data."""
    img_path = find_profile_image()
    orig = Image.open(img_path)

    # Ensure RGBA
    if orig.mode != 'RGBA':
        orig = orig.convert('RGBA')

    # Crop to non-transparent bounding box
    alpha = orig.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        orig = orig.crop(bbox)

    # Resize to target area
    aspect = orig.width / orig.height
    w = target_w
    h = int(w / aspect)
    if h > target_h:
        h = target_h
        w = int(h * aspect)

    resized = orig.resize((w, h), Image.Resampling.LANCZOS)
    alpha = resized.split()[-1]
    gray = resized.convert('L')

    # Enhance contrast & sharpness for crisp dot definition
    gray = ImageOps.autocontrast(gray, cutoff=(1, 1))
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    gray = ImageEnhance.Sharpness(gray).enhance(1.4)

    # Horizontal center alignment inside target bounding box
    pad_x = (target_w - w) / 2.0
    pad_y = (target_h - h) / 2.0

    dots = []
    step = int(spacing)
    half_step = step // 2

    # Edge detection kernel
    def is_edge_pixel(gx: int, gy: int) -> bool:
        if gx < 0 or gx >= w or gy < 0 or gy >= h:
            return True
        for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if alpha.getpixel((nx, ny)) < 40:
                    return True
            else:
                return True
        return False

    min_x_seen = 9999.0
    max_x_seen = -9999.0

    for gy in range(0, h, step):
        for gx in range(0, w, step):
            # Sample box average around (gx, gy)
            box_alpha = []
            box_lum = []
            for by in range(max(0, gy - 1), min(h, gy + 2)):
                for bx in range(max(0, gx - 1), min(w, gx + 2)):
                    box_alpha.append(alpha.getpixel((bx, by)))
                    box_lum.append(gray.getpixel((bx, by)))

            avg_a = sum(box_alpha) / len(box_alpha)
            if avg_a < 35:
                continue

            avg_lum = sum(box_lum) / len(box_lum)
            norm = avg_lum / 255.0
            is_edge = is_edge_pixel(gx, gy)

            abs_x = offset_x + pad_x + gx
            abs_y = offset_y + pad_y + gy

            min_x_seen = min(min_x_seen, abs_x)
            max_x_seen = max(max_x_seen, abs_x)

            # Radius calculation
            r = 0.65 + (norm ** 1.32) * 2.45
            if is_edge and norm < 0.25:
                r = max(r, 1.15)

            # Color assignment based on luminance and boundary
            if is_edge:
                color = PORTRAIT_TOKENS['accent'] if (gx + gy) % 3 == 0 else PORTRAIT_TOKENS['mid']
                opacity = 0.90
            elif norm > 0.62:
                color = PORTRAIT_TOKENS['highlight']
                opacity = 0.98
            elif norm > 0.32:
                color = PORTRAIT_TOKENS['mid']
                opacity = 0.88
            else:
                color = PORTRAIT_TOKENS['shadow']
                opacity = 0.72

            col_idx = int(gx / spacing)

            dots.append({
                'x': round(abs_x, 1),
                'y': round(abs_y, 1),
                'r': round(r, 2),
                'color': color,
                'opacity': opacity,
                'norm': round(norm, 3),
                'is_edge': is_edge,
                'col_idx': col_idx,
            })

    # Generate sparse background coordinate guide grid
    guide_dots = []
    guide_step = 16
    for gy in range(0, target_h + 10, guide_step):
        for gx in range(0, target_w + 10, guide_step):
            gx_abs = offset_x + gx
            gy_abs = offset_y + gy
            # Check distance from person dots to keep guides ambient
            guide_dots.append({
                'x': round(gx_abs, 1),
                'y': round(gy_abs, 1),
                'r': 0.7,
                'color': PORTRAIT_TOKENS['guide'],
                'opacity': 0.35,
            })

    return {
        'dots': dots,
        'guide_dots': guide_dots,
        'bounds': {
            'x': offset_x,
            'y': offset_y,
            'w': target_w,
            'h': target_h,
            'min_x': min_x_seen,
            'max_x': max_x_seen,
        },
    }


def render_portrait_svg_group(data: dict, animated: bool = False) -> str:
    """Generate SVG XML for portrait group."""
    b = data['bounds']
    bx, by, bw, bh = b['x'] - 10, b['y'] - 10, b['w'] + 20, b['h'] + 20
    accent = PORTRAIT_TOKENS['accent']

    lines = [f'<g id="portrait" class="hud-portrait">']

    # 1. Ambient guide dots
    lines.append('  <!-- Ambient coordinate guide dots -->')
    lines.append('  <g id="portrait_guides">')
    for g in data['guide_dots']:
        lines.append(f'    <circle cx="{g["x"]}" cy="{g["y"]}" r="{g["r"]}" fill="{g["color"]}" opacity="{g["opacity"]}"/>')
    lines.append('  </g>')

    # 2. Corner HUD brackets
    bracket_len = 22
    lines.append('  <!-- Corner technical HUD brackets -->')
    lines.append('  <g id="portrait_brackets" stroke="{}" stroke-width="2" fill="none">'.format(accent))
    # Top-Left
    lines.append(f'    <path d="M{bx+bracket_len} {by} H{bx} V{by+bracket_len}"/>')
    # Top-Right
    lines.append(f'    <path d="M{bx+bw-bracket_len} {by} H{bx+bw} V{by+bracket_len}"/>')
    # Bottom-Left
    lines.append(f'    <path d="M{bx} {by+bh-bracket_len} V{by+bh} H{bx+bracket_len}"/>')
    # Bottom-Right
    lines.append(f'    <path d="M{bx+bw} {by+bh-bracket_len} V{by+bh} H{bx+bw-bracket_len}"/>')
    lines.append('  </g>')

    # Small bracket ticks
    lines.append(f'  <circle cx="{bx+bracket_len+6}" cy="{by}" r="1.5" fill="{accent}"/>')
    lines.append(f'  <circle cx="{bx}" cy="{by+bracket_len+6}" r="1.5" fill="{accent}"/>')

    # 3. Portrait Halftone Dots
    lines.append('  <!-- Halftone portrait dots -->')
    if animated:
        # Group dots by column index for sequential scanline reveal
        cols = {}
        for d in data['dots']:
            cols.setdefault(d['col_idx'], []).append(d)

        max_col = max(cols.keys()) if cols else 1
        total_reveal_time = 1.35  # seconds

        for col_idx in sorted(cols.keys()):
            delay = round((col_idx / max_col) * total_reveal_time, 2)
            lines.append(f'  <g class="portrait-col" style="animation: dotReveal 0.4s ease-out {delay}s forwards; opacity: 0;">')
            for d in cols[col_idx]:
                lines.append(f'    <circle cx="{d["x"]}" cy="{d["y"]}" r="{d["r"]}" fill="{d["color"]}" opacity="{d["opacity"]}"/>')
            lines.append('  </g>')
    else:
        for d in data['dots']:
            lines.append(f'    <circle cx="{d["x"]}" cy="{d["y"]}" r="{d["r"]}" fill="{d["color"]}" opacity="{d["opacity"]}"/>')

    lines.append('</g>')
    return '\n'.join(lines)


if __name__ == '__main__':
    data = generate_portrait_dots()
    print(f"Generated {len(data['dots'])} portrait dots and {len(data['guide_dots'])} guide dots.")
    svg_fragment = render_portrait_svg_group(data)
    print("Sample SVG snippet length:", len(svg_fragment))

