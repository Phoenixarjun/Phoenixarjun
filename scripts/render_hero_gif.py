"""Render high-performance animated GIF for GitHub hero.

Pipeline:
1. Renders high-fidelity vector base card via headless Chrome (once).
2. Generates 54 animation frames (15 fps, 3.6s loop) using Pillow:
   - Portrait dots reveal scanline (t = 0.0s -> 1.3s)
   - Role typewriter effect (t = 0.5s -> 1.8s)
   - Cursor blink (500ms intervals)
   - Subtle wave mesh undulating motion
3. Assembles optimized GIF: assets/generated/hero/hero-animated.gif.
"""
from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from generate_halftone_portrait import generate_portrait_dots
    from generate_hero_svg import generate_hero_svg, TOKENS
except ModuleNotFoundError:
    from scripts.generate_halftone_portrait import generate_portrait_dots
    from scripts.generate_hero_svg import generate_hero_svg, TOKENS

ROOT = Path(__file__).resolve().parents[1]


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


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    h = hex_code.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def render_base_card_png(out_path: Path) -> Image.Image:
    """Render the static background and frame from SVG using Chrome to ensure 100% SVG fidelity."""
    chrome = get_chrome_path()
    if not chrome:
        print("Chrome/Edge not detected; falling back to pure PIL canvas.")
        return Image.new('RGBA', (1280, 420), hex_to_rgb(TOKENS['background_main']) + (255,))

    # Generate an SVG that has frame, prompt, name, tagline, metadata, brackets,
    # but omits the dynamic elements (portrait dots, role text, wave mesh).
    w, h = 1280, 420
    t = TOKENS

    # We can use the existing hero-static.svg or generate a specific base
    # Generating clean base SVG
    svg_path = ROOT / "previews" / "hero_base_temp.svg"
    html_path = ROOT / "previews" / "hero_base_temp.html"

    # Base SVG without role text, wave, or dots
    from generate_hero_svg import build_frame_svg, build_icons_svg
    frame_xml = build_frame_svg()
    icons = build_icons_svg()

    # Portrait brackets only
    portrait_data = generate_portrait_dots(target_w=325, target_h=305, offset_x=65.0, offset_y=58.0)
    b = portrait_data['bounds']
    bx, by, bw, bh = b['x'] - 10, b['y'] - 10, b['w'] + 20, b['h'] + 20
    accent = t['accent_primary']
    bracket_len = 22

    brackets_xml = f"""
    <!-- Ambient coordinate guide dots -->
    <g id="portrait_guides">
      {''.join(f'<circle cx="{g["x"]}" cy="{g["y"]}" r="{g["r"]}" fill="{g["color"]}" opacity="{g["opacity"]}"/>' for g in portrait_data['guide_dots'])}
    </g>
    <!-- Corner technical HUD brackets -->
    <g id="portrait_brackets" stroke="{accent}" stroke-width="2" fill="none">
      <path d="M{bx+bracket_len} {by} H{bx} V{by+bracket_len}"/>
      <path d="M{bx+bw-bracket_len} {by} H{bx+bw} V{by+bracket_len}"/>
      <path d="M{bx} {by+bh-bracket_len} V{by+bh} H{bx+bracket_len}"/>
      <path d="M{bx+bw} {by+bh-bracket_len} V{by+bh} H{bx+bw-bracket_len}"/>
    </g>
    <circle cx="{bx+bracket_len+6}" cy="{by}" r="1.5" fill="{accent}"/>
    <circle cx="{bx}" cy="{by+bracket_len+6}" r="1.5" fill="{accent}"/>
    """

    base_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="panelBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{t['background_main']}"/>
    <stop offset="45%" stop-color="{t['background_panel']}"/>
    <stop offset="100%" stop-color="{t['background_main']}"/>
  </linearGradient>
  <linearGradient id="promptBg" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#0E1618"/>
    <stop offset="100%" stop-color="#090E10"/>
  </linearGradient>
  <radialGradient id="portraitBacklight" cx="220" cy="210" r="180" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="{t['accent_primary']}" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="{t['accent_primary']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="identityBacklight" cx="620" cy="200" r="260" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="{t['accent_primary']}" stop-opacity="0.05"/>
    <stop offset="70%" stop-color="{t['accent_primary']}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="bgDots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="0.75" fill="{t['border_main']}" opacity="0.18"/>
  </pattern>
  <filter id="glowSoft" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowStrong" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="5.0" result="blur1"/>
    <feGaussianBlur stdDeviation="2.0" result="blur2"/>
    <feMerge><feMergeNode in="blur1"/><feMergeNode in="blur2"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<rect width="{w}" height="{h}" fill="{t['background_main']}"/>
<circle cx="220" cy="210" r="180" fill="url(#portraitBacklight)"/>
<circle cx="620" cy="200" r="260" fill="url(#identityBacklight)"/>
{frame_xml}
{brackets_xml}
<g id="identity_content">
  <g id="prompt_strip">
    <rect x="468" y="52" width="372" height="46" rx="14" fill="url(#promptBg)" stroke="{t['border_main']}" stroke-width="1.2"/>
    <text x="488" y="81" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="16" font-weight="600" fill="{t['accent_primary']}">naresh@github:~$ <tspan fill="{t['text_primary']}" font-weight="500">whoami</tspan></text>
    <line x1="840" y1="75" x2="1200" y2="75" stroke="{t['border_soft']}" stroke-width="1" stroke-dasharray="4 4" opacity="0.65"/>
    <circle cx="1200" cy="75" r="2" fill="{t['accent_primary']}" opacity="0.8"/>
  </g>
  <g id="name_title">
    <text x="468" y="160" font-family="'Inter', 'Space Grotesk', 'Segoe UI', Arial, sans-serif" font-size="68" font-weight="800" fill="{t['text_primary']}" letter-spacing="-0.5">Naresh B A</text>
  </g>
  <g id="tagline_block">
    <rect x="468" y="246" width="4" height="46" rx="2" fill="{t['accent_primary']}" filter="url(#glowSoft)"/>
    <text x="488" y="265" font-family="'Inter', 'Segoe UI', Arial, sans-serif" font-size="18" font-weight="500" fill="{t['text_secondary']}">Building intelligent software</text>
    <text x="488" y="289" font-family="'Inter', 'Segoe UI', Arial, sans-serif" font-size="18" font-weight="500" fill="{t['text_secondary']}">on reliable systems.</text>
  </g>
  <g id="metadata_row">
    <rect x="468" y="322" width="670" height="44" rx="14" fill="{t['background_panel']}" stroke="{t['border_soft']}" stroke-width="1.2"/>
    {icons['briefcase']}
    <text x="516" y="349" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="15" font-weight="500" fill="{t['text_primary']}">Software Engineer @ Prodapt</text>
    <line x1="765" y1="332" x2="765" y2="356" stroke="{t['border_main']}" stroke-width="1.2"/>
    {icons['location']}
    <text x="814" y="349" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="15" font-weight="500" fill="{t['text_primary']}">Chennai, India</text>
  </g>
</g>
</svg>"""

    svg_path.write_text(base_svg, encoding='utf-8')
    html_content = f"""<!doctype html><html><head><meta charset="utf-8"><style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    html, body {{ width:1280px; height:420px; overflow:hidden; background:#070B0C; }}
    img {{ display:block; width:1280px; height:420px; }}
    </style></head><body><img src="file:///{svg_path.as_posix()}" width="1280" height="420"/></body></html>"""
    html_path.write_text(html_content, encoding='utf-8')

    tmp = tempfile.mkdtemp()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={tmp}",
        "--window-size=1280,420",
        "--hide-scrollbars",
        f"--screenshot={out_path}",
        f"file:///{html_path.as_posix()}",
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp files
    if svg_path.is_file():
        svg_path.unlink()
    if html_path.is_file():
        html_path.unlink()

    if out_path.is_file():
        base_im = Image.open(out_path).convert('RGBA')
        if base_im.size != (1280, 420):
            base_im = base_im.crop((0, 0, min(1280, base_im.width), min(420, base_im.height)))
            base_im = base_im.resize((1280, 420), Image.Resampling.LANCZOS)
        return base_im

    return Image.new('RGBA', (1280, 420), hex_to_rgb(TOKENS['background_main']) + (255,))


def render_hero_gif():
    out_dir = ROOT / "assets" / "generated" / "hero"
    out_dir.mkdir(parents=True, exist_ok=True)
    gif_path = out_dir / "hero-animated.gif"

    print("Rendering vector base card...")
    base_png_temp = ROOT / "previews" / "base_card.png"
    base_im = render_base_card_png(base_png_temp)
    if base_png_temp.is_file():
        base_png_temp.unlink()
    print("Base card rendered successfully.")

    # Load dot data
    portrait_data = generate_portrait_dots(target_w=325, target_h=305, offset_x=65.0, offset_y=58.0)
    dots = portrait_data['dots']
    min_x = portrait_data['bounds']['min_x']
    max_x = portrait_data['bounds']['max_x']
    range_x = max(1.0, max_x - min_x)

    # Load font for role text
    font_paths = [
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    font = None
    for fp in font_paths:
        if Path(fp).is_file():
            font = ImageFont.truetype(fp, 32)
            break
    if not font:
        font = ImageFont.load_default()

    full_role = "AI Systems Engineer"
    lime_rgb = hex_to_rgb(TOKENS['accent_primary'])

    # Wave parameters
    start_x = 710
    end_x = 1220
    base_y = 368
    num_pts = 52
    step_x = (end_x - start_x) / (num_pts - 1)

    wave_layers = [
        {'amp': 18.0, 'freq': 0.016, 'phase': 0.0, 'color': hex_to_rgb(TOKENS['accent_primary']), 'alpha': 210, 'r': 1.4},
        {'amp': 14.0, 'freq': 0.021, 'phase': 1.6, 'color': hex_to_rgb(TOKENS['accent_soft']), 'alpha': 160, 'r': 1.1},
        {'amp': 22.0, 'freq': 0.013, 'phase': 3.1, 'color': hex_to_rgb(TOKENS['accent_muted']), 'alpha': 110, 'r': 0.9},
        {'amp': 10.0, 'freq': 0.026, 'phase': 4.5, 'color': hex_to_rgb(TOKENS['border_main']), 'alpha': 80, 'r': 0.8},
    ]

    total_duration = 3.6  # seconds
    fps = 15
    total_frames = int(total_duration * fps)
    frame_ms = int(1000 / fps)

    print(f"Generating {total_frames} animation frames ({fps} fps)...")
    frames = []

    for f_idx in range(total_frames):
        t = f_idx / fps
        frame = base_im.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Portrait dots reveal
        reveal_progress = min(1.0, t / 1.35)
        cutoff_x = min_x + reveal_progress * range_x

        for d in dots:
            if d['x'] <= cutoff_x:
                color_rgb = hex_to_rgb(d['color'])
                # Scale up dot slightly if it just appeared
                r = d['r']
                if d['x'] > cutoff_x - 12:
                    r = min(3.5, r * 1.25)
                x0, y0 = d['x'] - r, d['y'] - r
                x1, y1 = d['x'] + r, d['y'] + r
                draw.ellipse((x0, y0, x1, y1), fill=color_rgb)

        # 2. Role text typewriter animation
        # t: 0.0 - 0.4s: cursor blink
        # t: 0.4 - 1.8s: type characters
        # t: 1.8 - 3.6s: cursor blink at end
        if t < 0.4:
            cursor_visible = (int(t * 3.5) % 2 == 0)
            role_text = "_" if cursor_visible else ""
        elif t < 1.8:
            type_progress = (t - 0.4) / 1.4
            num_chars = min(len(full_role), max(1, int(type_progress * len(full_role))))
            role_text = full_role[:num_chars] + "_"
        else:
            cursor_visible = (int(t * 2.5) % 2 == 0)
            role_text = full_role + ("_" if cursor_visible else " ")

        # Draw role text with soft glow layer
        # Baseline y=218 => PIL top y ≈ 194
        role_x, role_y = 468, 194
        # Subtle glow underneath
        draw.text((role_x - 1, role_y), role_text, font=font, fill=hex_to_rgb(TOKENS['accent_soft']))
        draw.text((role_x + 1, role_y), role_text, font=font, fill=hex_to_rgb(TOKENS['accent_soft']))
        draw.text((role_x, role_y), role_text, font=font, fill=lime_rgb)

        # 3. Wave mesh motion
        wave_surface = Image.new('RGBA', (1280, 420), (0, 0, 0, 0))
        w_draw = ImageDraw.Draw(wave_surface)

        for lyr in wave_layers:
            curr_phase = lyr['phase'] + t * 1.8
            pts = []
            for i in range(num_pts):
                wx = start_x + i * step_x
                progress = i / (num_pts - 1)
                envelope = math.sin(progress * math.pi) ** 0.85
                wy = base_y + lyr['amp'] * math.sin(lyr['freq'] * wx + curr_phase) * envelope
                pts.append((wx, wy))

            # Draw lines
            col_with_alpha = lyr['color'] + (lyr['alpha'],)
            for i in range(len(pts) - 1):
                w_draw.line((pts[i], pts[i+1]), fill=col_with_alpha, width=1)

            # Draw dot particles
            for i in range(0, len(pts), 2):
                px, py = pts[i]
                rad = lyr['r']
                w_draw.ellipse((px - rad, py - rad, px + rad, py + rad), fill=col_with_alpha)

        # Composite wave onto frame
        frame.alpha_composite(wave_surface)

        # Convert to RGB with high-quality adaptive palette
        rgb_frame = frame.convert('RGB')
        quantized = rgb_frame.quantize(colors=128, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quantized)

    print("Assembling optimized GIF...")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_ms,
        loop=0,
        optimize=True,
    )
    print(f"Success! Saved: {gif_path} ({gif_path.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    render_hero_gif()
