#!/usr/bin/env python3
"""Reproducible Titanium Hacker GitHub profile hero V4 — Orbitron Typography Edition.

Source image: assets/images/profile.png (user supplied).
Outputs only SVGs, PNG previews and an optional GitHub-safe animated GIF. No remote assets.
Typography: Google Fonts Orbitron (Black 900, Medium 500, Regular 400).
Strict typography policy: silent fallbacks to Roboto or generic sans-serif are prohibited.
All published text is traced into SVG path outlines at generation time to guarantee
predictable, crisp rendering across GitHub dark and light modes on any client device.
"""
from __future__ import annotations
import argparse
import base64
from functools import lru_cache
import html
from io import BytesIO
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'design/hero-config.json').read_text(encoding='utf-8'))
COLORS = {
    'base': '#070B0C',
    'surface': '#1B2328',
    'surface2': '#253139',
    'steel': '#42535C',
    'accent': '#B6FF3B',
    'text': '#EEF7EF',
    'secondary': '#8EADB6',
    'muted': '#A6B6B2'
}
THEMES = ROOT / 'design/themes.json'
if THEMES.exists():
    theme_json = json.loads(THEMES.read_text(encoding='utf-8'))
    COLORS.update(theme_json['presets'][theme_json.get('active', 'titanium-hacker')])

W = CONFIG['canvas']['width']
H = CONFIG['canvas']['height']
P = CONFIG['portrait']
C = COLORS

ORBITRON_DIR = ROOT / 'design/fonts/orbitron'

FONT_CONFIG = {
    'black': {'weight': 900, 'filename': 'Orbitron-Black.ttf'},
    'medium': {'weight': 500, 'filename': 'Orbitron-Medium.ttf'},
    'regular': {'weight': 400, 'filename': 'Orbitron-Regular.ttf'},
    'bold': {'weight': 700, 'filename': 'Orbitron-Bold.ttf'},
}


def ensure_orbitron_fonts() -> None:
    """Download Google Fonts Orbitron variable font and instantiate static instances if missing."""
    ORBITRON_DIR.mkdir(parents=True, exist_ok=True)
    var_path = ORBITRON_DIR / 'Orbitron[wght].ttf'
    if not var_path.exists():
        url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/orbitron/Orbitron%5Bwght%5D.ttf'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                var_path.write_bytes(resp.read())
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Orbitron from Google Fonts: {e}")

    try:
        from fontTools.varLib.instancer import instantiateVariableFont
        vf = TTFont(var_path)
        for key, info in FONT_CONFIG.items():
            target = ORBITRON_DIR / info['filename']
            if not target.exists():
                inst = instantiateVariableFont(vf, {'wght': info['weight']})
                inst.save(target)
    except Exception as e:
        raise RuntimeError(f"Failed to instantiate Orbitron static fonts: {e}")


def find_font(weight: str) -> Path:
    """Locate Orbitron font file with exact weight. Prohibits silent fallbacks to Roboto or generic sans-serif."""
    if weight not in FONT_CONFIG:
        raise ValueError(f"Unknown font weight request: '{weight}'. Valid weights: {list(FONT_CONFIG.keys())}")

    env = os.getenv('ORBITRON_FONT_DIR')
    candidates = []
    if env:
        candidates.append(Path(env) / FONT_CONFIG[weight]['filename'])
    candidates.append(ORBITRON_DIR / FONT_CONFIG[weight]['filename'])
    candidates.append(ROOT / 'fonts/orbitron' / FONT_CONFIG[weight]['filename'])
    candidates.append(Path('C:/Windows/Fonts') / FONT_CONFIG[weight]['filename'])

    for c in candidates:
        if c.exists():
            return c

    # Attempt on-demand download/instantiation
    ensure_orbitron_fonts()
    target = ORBITRON_DIR / FONT_CONFIG[weight]['filename']
    if target.exists():
        return target

    raise RuntimeError(
        f"Orbitron {weight} ({FONT_CONFIG[weight]['weight']}) could not be found or generated at {target}. "
        "Strict typography policy: silent fallbacks to Roboto or generic sans-serif are prohibited."
    )


@lru_cache(None)
def font(weight: str):
    tt = TTFont(find_font(weight))
    return tt, tt.getGlyphSet(), tt.getBestCmap(), tt['head'].unitsPerEm


@lru_cache(600)
def glyph_path(weight: str, char: str) -> str:
    tt, gs, cmap, upm = font(weight)
    glyph_name = cmap.get(ord(char))
    if glyph_name is None:
        return ''
    pen = SVGPathPen(gs)
    gs[glyph_name].draw(pen)
    return pen.getCommands() or ''


def glyph_advance(weight: str, char: str) -> int:
    tt, gs, cmap, upm = font(weight)
    name = cmap.get(ord(char))
    return tt['hmtx'][name][0] if name else upm // 2


def width(text: str, size: float, weight='regular', spacing=0.0):
    upm = font(weight)[3]
    return sum(glyph_advance(weight, ch) / upm * size + spacing for ch in text) - (spacing if text else 0)


def svg_text(text: str, x: float, y: float, size: float, weight='regular', fill=None, spacing=0.0, opacity=1.0, ident=None):
    """Convert Orbitron glyph outlines to exact SVG paths. Canvas y is typographic baseline."""
    upm = font(weight)[3]
    scale = size / upm
    current = x
    gid = f' id="{html.escape(ident, quote=True)}"' if ident else ""
    parts = [f'<g{gid} aria-label="{html.escape(text, quote=True)}" fill="{fill or C["text"]}" opacity="{opacity:.3f}">']
    for ch in text:
        d = glyph_path(weight, ch)
        if d:
            parts.append(f'<path d="{d}" transform="translate({current:.2f} {y:.2f}) scale({scale:.7f} {-scale:.7f})"/>')
        current += glyph_advance(weight, ch) * scale + spacing
    parts.append('</g>')
    return ''.join(parts)


def defs():
    return f'''<defs>
      <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['base']}"/><stop offset="0.48" stop-color="#091112"/><stop offset="1" stop-color="#07100E"/></linearGradient>
      <linearGradient id="lineSteel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['accent']}"/><stop offset=".23" stop-color="#7FD9C3"/><stop offset=".55" stop-color="{C['steel']}"/><stop offset=".85" stop-color="#6FB8A2"/><stop offset="1" stop-color="{C['accent']}"/></linearGradient>
      <radialGradient id="portraitHalo"><stop offset="0" stop-color="{C['accent']}" stop-opacity="0.15"/><stop offset=".55" stop-color="#287957" stop-opacity="0.07"/><stop offset="1" stop-color="#081111" stop-opacity="0"/></radialGradient>
      <radialGradient id="rightHalo"><stop offset="0" stop-color="{C['accent']}" stop-opacity=".085"/><stop offset="1" stop-color="{C['accent']}" stop-opacity="0"/></radialGradient>
      <radialGradient id="metadataBg"><stop offset="0" stop-color="#162224"/><stop offset="1" stop-color="#091212"/></radialGradient>
      <pattern id="tinyDots" width="21" height="21" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#6CA084" opacity=".20"/></pattern>
      <pattern id="smallDots" width="17" height="17" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.25" fill="{C['accent']}" opacity=".28"/></pattern>
      <filter id="limeGlow" x="-90%" y="-90%" width="280%" height="280%"><feGaussianBlur stdDeviation="5.5"/></filter>
      <filter id="microGlow" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="2.2"/></filter>
      <clipPath id="panelClip"><path d="M 104 32 L 565 32 L 585 51 L 1506 51 L 1558 103 L 1558 652 L 1512 702 L 97 702 L 40 646 L 40 100 Z"/></clipPath>
      <clipPath id="portraitClip"><rect x="93" y="137" width="488" height="507" rx="6"/></clipPath>
    </defs>'''


def portrait_dots():
    """Build the static dot-field matrix from the actual supplied portrait."""
    img_path = ROOT / 'assets/images/profile.png'
    raw = Image.open(img_path).convert('RGBA')
    crop_box = CONFIG['portrait']['crop']
    cropped = raw.crop(crop_box).resize((int(P['width']), int(P['height'])), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(cropped)
    gray = ImageEnhance.Contrast(gray).enhance(1.22)
    gray = ImageEnhance.Sharpness(gray).enhance(1.4)
    alpha = cropped.getchannel('A')
    step = float(P.get('dot_spacing', 4.8))
    cols = int(round(P['width'] / step))
    rows = int(round(P['height'] / step))
    circles_actual = []
    circles_pure = []
    tot = 0
    for r in range(rows):
        y = r * step + step / 2
        for c in range(cols):
            x = c * step + step / 2
            a = alpha.getpixel((int(min(P['width'] - 1, x)), int(min(P['height'] - 1, y))))
            if a < 45:
                continue
            v = gray.getpixel((int(min(P['width'] - 1, x)), int(min(P['height'] - 1, y)))) / 255.0
            radius = (1.0 - v) * (step * 0.49) + 0.55
            if radius < 0.6:
                continue
            is_lime = (v < 0.38) and ((r + c) % 4 == 0)
            fill = C['accent'] if is_lime else '#80BEA4'
            op = min(1.0, 0.42 + (1.0 - v) * 0.58)
            cx = P['x'] + x
            cy = P['y'] + y
            circles_actual.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" fill="{fill}" opacity="{op:.2f}"/>')
            circles_pure.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{fill}" opacity="{op:.2f}"/>')
            tot += 1
    actual_svg = f'<g id="portrait-dots" clip-path="url(#portraitClip)">{"".join(circles_actual)}</g>'
    pure_svg = f'<g id="portrait-pure">{"".join(circles_pure)}</g>'
    return actual_svg, pure_svg, tot


def frame():
    A = C['accent']
    return f'''<g id="outer-chassis">
      <path d="M 104 32 L 565 32 L 585 51 L 1506 51 L 1558 103 L 1558 652 L 1512 702 L 97 702 L 40 646 L 40 100 Z" fill="url(#panel)" stroke="{C['steel']}" stroke-width="1.8"/>
      <path d="M 104 32 L 565 32 L 585 51 L 1506 51 L 1558 103 L 1558 652 L 1512 702 L 97 702 L 40 646 L 40 100 Z" fill="none" stroke="#2A5C4A" stroke-width="0.7" opacity=".4"/>
      <path d="M 102 32 L 40 100 V 220" fill="none" stroke="{A}" stroke-width="3.5"/>
      <circle cx="40" cy="223" r="3" fill="{A}"/>
      <path d="M 1480 702 L 1512 702 L 1558 652 V 570" fill="none" stroke="{A}" stroke-width="3.5"/>
      <circle cx="1558" cy="567" r="3" fill="{A}"/>
      <g id="lower-right-slashes">
        <path d="M1412 649 H1432 L1399 682 H1379Z" fill="none" stroke="{A}" stroke-width="2"/>
        <path d="M1445 649 H1473 L1440 682 H1412Z" fill="{A}"/>
        <path d="M1486 649 H1514 L1481 682 H1453Z" fill="{A}"/>
      </g>
      <g id="upper-right-slashes">
        <path d="M1362 67 H1380 L1359 88 H1341Z" fill="none" stroke="{A}" stroke-width="1.8"/>
        <path d="M1388 67 H1406 L1385 88 H1367Z" fill="{A}"/>
        <path d="M1414 67 H1432 L1411 88 H1393Z" fill="{A}"/>
      </g>
      <circle cx="112" cy="73" r="3" fill="{A}"/>
      <circle cx="127" cy="73" r="3" fill="#2E6852"/>
      <circle cx="142" cy="73" r="3" fill="#1C3F32"/>
      <circle cx="112" cy="660" r="3" fill="{A}"/>
      <circle cx="127" cy="660" r="3" fill="#2E6852"/>
      <circle cx="142" cy="660" r="3" fill="#1C3F32"/>
    </g>'''


def portrait_image_rgba():
    img_path = ROOT / 'assets/images/profile.png'
    raw = Image.open(img_path).convert('RGBA')
    crop_box = CONFIG['portrait']['crop']
    return raw.crop(crop_box).resize((int(P['width']), int(P['height'])), Image.Resampling.LANCZOS)


def portrait_frame_and_field():
    A = C['accent']
    return f'''<g id="portrait-frame">
      <ellipse cx="{P['x'] + P['width'] // 2}" cy="{P['y'] + P['height'] // 2}" rx="{P['width'] * 0.58:.1f}" ry="{P['height'] * 0.58:.1f}" fill="url(#portraitHalo)"/>
      <rect x="{P['x'] - 1}" y="{P['y'] - 1}" width="{P['width'] + 2}" height="{P['height'] + 2}" rx="7" fill="none" stroke="{C['steel']}" stroke-width="1.4"/>
      <path d="M {P['x'] + 50} {P['y'] - 1} H {P['x'] + 8} Q {P['x'] - 1} {P['y'] - 1} {P['x'] - 1} {P['y'] + 8} V {P['y'] + 50}" fill="none" stroke="{A}" stroke-width="2.6"/>
      <path d="M {P['x'] + P['width'] - 50} {P['y'] - 1} H {P['x'] + P['width'] - 8} Q {P['x'] + P['width'] + 1} {P['y'] - 1} {P['x'] + P['width'] + 1} {P['y'] + 8} V {P['y'] + 50}" fill="none" stroke="{A}" stroke-width="2.6"/>
      <path d="M {P['x'] - 1} {P['y'] + P['height'] - 50} V {P['y'] + P['height'] - 8} Q {P['x'] - 1} {P['y'] + P['height'] + 1} {P['x'] + 8} {P['y'] + P['height'] + 1} H {P['x'] + 50}" fill="none" stroke="{A}" stroke-width="2.6"/>
      <path d="M {P['x'] + P['width'] + 1} {P['y'] + P['height'] - 50} V {P['y'] + P['height'] - 8} Q {P['x'] + P['width'] + 1} {P['y'] + P['height'] + 1} {P['x'] + P['width'] - 8} {P['y'] + P['height'] + 1} H {P['x'] + P['width'] - 50}" fill="none" stroke="{A}" stroke-width="2.6"/>
    </g>'''


def portrait(mode='photo'):
    field = portrait_frame_and_field()
    if mode == 'none':
        return field, 0
    if mode == 'dots':
        dots, _, num = portrait_dots()
        return field + dots, num
    im = portrait_image_rgba()
    b = BytesIO()
    im.save(b, format='PNG', optimize=True)
    href = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii')
    elem = (f'<g id="photographic-portrait" clip-path="url(#portraitClip)">'
            f'<image x="{P["x"]}" y="{P["y"]}" width="{P["width"]}" height="{P["height"]}" '
            f'preserveAspectRatio="none" href="{href}"/></g>')
    return field + elem, 0


def portrait_only():
    actual, pure, num = portrait_dots()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{int(P['width'])}" height="{int(P['height'])}" viewBox="0 0 {P['width']} {P['height']}" role="img" aria-label="Halftone portrait of Naresh B A"><title>Vector halftone portrait</title>{pure}</svg>'''


def wave():
    """Parametric dot-field landscape: three visible crest bands and faint connected mesh."""
    A = C['accent']
    rows = 25
    cols = 128
    p = ['<g id="signal-terrain">']

    def coord(col, row):
        u = col / (cols - 1)
        v = row / (rows - 1)
        x = 635 + 895 * u + 22 * v
        peaks = (31 * math.exp(-((u - .23) / .095)**2) +
                 37 * math.exp(-((u - .51) / .11)**2) +
                 43 * math.exp(-((u - .79) / .09)**2))
        ripple = 7.2 * math.sin(15.2 * u + .6 * v) * (1 - v)
        y = 649 + 44 * v - (peaks + ripple) * (1 - .40 * v)
        return (x, y, peaks)

    for row in (0, 12, 24):
        pts = ['%.2f,%.2f' % (coord(col, row)[:2]) for col in range(cols)]
        p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{A if row==0 else "#3D8167"}" stroke-width="{.68 if row==0 else .42}" opacity="{.26 if row==0 else .06}"/>')
    for col in range(0, cols, 24):
        pts = ['%.2f,%.2f' % (coord(col, row)[:2]) for row in range(rows)]
        p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#68A780" stroke-width=".42" opacity=".09"/>')
    for row in range(rows):
        for col in range(cols):
            x, y, pk = coord(col, row)
            u = col / (cols - 1)
            edge = (math.sin(math.pi * col / (cols - 1))**.6 if col not in (0, cols - 1) else 0)
            op = max(.02, (.23 + .61 * (pk / 42) * (1 - row / (rows * 1.7))) * edge * (1 - .20 * row / (rows - 1)))
            lime = pk > 18 and ((row + col) % 5 in (0, 1, 3))
            color = A if lime else ('#77C6A6' if row % 3 == 0 else '#3C8874')
            r = 1.13 + (pk / 42) * .66 + (0.12 if row in (0, 12, 24) else 0)
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{op:.2f}"/>')
    pts = ['%.1f,%.1f' % coord(col, 0)[:2] for col in range(cols)]
    p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{A}" stroke-width="2.0" opacity=".18" filter="url(#microGlow)"/>')
    p.append('</g>')
    return ''.join(p)


def wave_only():
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="125" viewBox="610 595 960 125">{wave()}</svg>'


def ico_briefcase(x=0, y=0, s=1):
    return f'<g transform="translate({x} {y}) scale({s})" stroke="{C["accent"]}" fill="none" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"><rect x="2" y="8" width="31" height="23" rx="3"/><path d="M 12 8 V 5 Q 12 2 16 2 H 21 Q 25 2 25 5 V 8 M 2 18 H 33 M 15 18 V 22 H 21 V 18"/></g>'


def ico_pin(x=0, y=0, s=1):
    return f'<g transform="translate({x} {y}) scale({s})" stroke="{C["accent"]}" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M 18 34 C 10 24 4 18 4 12 A 14 14 0 1 1 32 12 C32 19 26 27 18 34 Z"/><circle cx="18" cy="12" r="4.5"/></g>'


def _cube(cx, top_y, radius, ht, index=0):
    """Isometric triple-face cube, steel-dark left facet and selective lime highlights."""
    r = radius
    top = f'{cx},{top_y} {cx+r},{top_y+r*.47} {cx},{top_y+r*.94} {cx-r},{top_y+r*.47}'
    left = f'{cx-r},{top_y+r*.47} {cx},{top_y+r*.94} {cx},{top_y+r*.94+ht} {cx-r},{top_y+r*.47+ht}'
    right = f'{cx},{top_y+r*.94} {cx+r},{top_y+r*.47} {cx+r},{top_y+r*.47+ht} {cx},{top_y+r*.94+ht}'
    return (f'<g class="iso-cube cube-{index}">'
            f'<polygon points="{left}" fill="#102B23" stroke="#639D75" stroke-width="1.6"/>'
            f'<polygon points="{right}" fill="#06160E" stroke="{C["accent"]}" stroke-width="1.5"/>'
            f'<polygon points="{top}" fill="{C["accent"] if index==0 else "#74BA58"}" fill-opacity="{.86 if index==0 else .52}" stroke="#DFFF99" stroke-width="1.4"/>'
            f'</g>')


def circuit_motif(cx=1405, cy=350):
    """Isometric architectural accent: base wafer, glowing rail and stacked 3D processing blocks, centered in right column."""
    A = C['accent']
    p = ['<g id="right-circuit-visual">']
    # Outer concentric halo rings
    p.append(f'<ellipse cx="{cx}" cy="{cy-40}" rx="146" ry="76" fill="none" stroke="#255A46" stroke-width="1.1" stroke-dasharray="4 6" opacity=".5"/>')
    p.append(f'<ellipse cx="{cx}" cy="{cy-40}" rx="178" ry="94" fill="none" stroke="#163C2E" stroke-width="0.9" opacity=".38"/>')
    # Floating orbital dots
    for deg in (18, 76, 142, 215, 290, 332):
        rad = math.radians(deg)
        ox = cx + 178 * math.cos(rad)
        oy = (cy - 40) + 94 * math.sin(rad)
        p.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="2.2" fill="{A}" opacity=".65"/>')
    # Stacked substrate platform
    w_top = f'{cx},{cy+30} {cx+118},{cy+82} {cx},{cy+134} {cx-118},{cy+82}'
    w_side_l = f'{cx-118},{cy+82} {cx},{cy+134} {cx},{cy+152} {cx-118},{cy+100}'
    w_side_r = f'{cx},{cy+134} {cx+118},{cy+82} {cx+118},{cy+100} {cx},{cy+152}'
    p.append(f'<polygon points="{w_side_l}" fill="#091814" stroke="#265B48" stroke-width="1.4"/>')
    p.append(f'<polygon points="{w_side_r}" fill="#06120F" stroke="#265B48" stroke-width="1.4"/>')
    p.append(f'<polygon points="{w_top}" fill="#0E241E" stroke="{A}" stroke-width="1.8"/>')
    # Inner wafer inset
    iw_top = f'{cx},{cy+42} {cx+98},{cy+84} {cx},{cy+126} {cx-98},{cy+84}'
    p.append(f'<polygon points="{iw_top}" fill="#061612" stroke="#48866E" stroke-width="1.2"/>')
    # Isometric processing core cubes
    p.append(_cube(cx, cy - 78, 38, 44, index=0))
    p.append(_cube(cx - 32, cy - 35, 29, 34, index=1))
    p.append(_cube(cx + 30, cy - 36, 29, 34, index=2))
    # Bus connection trace to base
    p.append(f'<polyline points="{cx},{cy+4} {cx},{cy+42}" fill="none" stroke="{A}" stroke-width="2.2" stroke-dasharray="3 3"/>')
    p.append('</g>')
    return ''.join(p)


def content(chars=None, cursor=True):
    """Build the identity typography block using Orbitron Black 900, Medium 500, and Regular 400."""
    i = CONFIG['identity']
    role = i['role']
    if chars is None:
        chars = len(role)
    chars = min(max(0, chars), len(role))
    prompt = 'naresh@github:~$'
    p = []

    # 1. Terminal prompt capsule (Orbitron Regular 400)
    prompt_size = 28
    pw = width(prompt, prompt_size, 'regular', 0.5)
    cw = width(' whoami', prompt_size, 'regular', 0.2)
    capsule_w = pw + cw + 48
    p.append(f'<path d="M 650 128 Q 650 105 674 105 H {650 + capsule_w - 24:.1f} Q {650 + capsule_w:.1f} 105 {650 + capsule_w + 12:.1f} 128 L {650 + capsule_w + 12:.1f} 150 Q {650 + capsule_w + 12:.1f} 172 {650 + capsule_w - 8:.1f} 172 H 674 Q 650 172 650 150 Z" fill="#0A1615" stroke="#4F8A76" stroke-width="1.8"/>')
    p.append(svg_text(prompt, 674, 149, prompt_size, 'regular', C['accent'], 0.5, ident='whoami-prompt'))
    p.append(svg_text(' whoami', 674 + pw + 8, 149, prompt_size, 'regular', C['text'], 0.2, ident='whoami-command'))
    p.append(f'<path d="M {650 + capsule_w + 32:.1f} 139 H 1345" stroke="#5A9F8E" stroke-width="1.5"/>')

    # 2. Name: Orbitron Black (900)
    name_size = 92
    p.append(svg_text(i['name'], 646, 274, name_size, 'black', C['text'], 1.0, ident='display-name'))

    # 3. Role: Orbitron Medium (500)
    role_size = 46
    active_role = role[:chars]
    p.append(svg_text(active_role, 650, 356, role_size, 'medium', C['accent'], 1.2, ident='role-typing'))
    role_x = 650 + width(active_role, role_size, 'medium', 1.2) + 8
    if cursor:
        p.append(f'<rect x="{role_x:.1f}" y="324" width="26" height="6" rx="1.5" fill="{C["accent"]}" filter="url(#microGlow)"/><rect x="{role_x:.1f}" y="324" width="26" height="6" rx="1.5" fill="{C["accent"]}"/>')

    # 4. Accent split tagline: Orbitron Regular (400)
    tagline_size = 26
    p.append(f'<path d="M 657 408 V 484" stroke="{C["accent"]}" stroke-width="5"/>')
    p.append(svg_text(i['tagline_lines'][0], 684, 438, tagline_size, 'regular', C['text'], 0.3, ident='tagline-top'))
    p.append(svg_text(i['tagline_lines'][1], 684, 476, tagline_size, 'regular', C['text'], 0.3, ident='tagline-bottom'))

    # 5. Metadata strip: Orbitron Regular (400)
    p.append(f'<rect x="650" y="534" width="844" height="72" rx="28" fill="#0B1715" stroke="#53826D" stroke-width="1.6"/>')
    p.append(ico_briefcase(676, 552, .96))
    p.append(svg_text(i['employer'], 722, 579, 23, 'regular', C['text'], 0.2, ident='employer'))
    p.append(f'<path d="M 1164 548 V 592" stroke="{C["accent"]}" stroke-width="1.8"/>')
    p.append(ico_pin(1194, 553, .87))
    p.append(svg_text(i['location'], 1238, 579, 23, 'regular', C['text'], 0.2, ident='location'))
    return ''.join(p)


def main_svg(chars=None, cursor=True, portrait_mode='photo'):
    figure, nd = portrait(portrait_mode)
    content_xml = content(chars, cursor)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Naresh B A — AI Systems Engineer. Building intelligent software on reliable systems. Software Engineer at Prodapt, Chennai, India."><title>Naresh B A — AI Systems Engineer</title><desc>Custom dark Titanium Hacker GitHub profile hero with Orbitron typography, an accurate vector halftone portrait made from the supplied photo, a terminal prompt, professional identity and a signal terrain.</desc>
    {defs()}
    {frame()}
    <g clip-path="url(#panelClip)"><rect x="40" y="48" width="1518" height="645" fill="url(#tinyDots)" opacity=".66"/><ellipse cx="1405" cy="350" rx="183" ry="165" fill="url(#rightHalo)"/>{wave()}{circuit_motif()}{figure}</g>
    <g id="identity">{content_xml}</g>
    </svg>'''


def role_overlay(chars: int, cursor: bool = True) -> str:
    role = CONFIG['identity']['role'][:chars]
    role_size = 46
    r = svg_text(role, 650, 356, role_size, 'medium', C['accent'], 1.2)
    x = 650 + width(role, role_size, 'medium', 1.2) + 8
    if cursor:
        r += f'<rect x="{x:.1f}" y="324" width="26" height="6" rx="1.5" fill="{C["accent"]}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{r}</svg>'


def svg_to_png(svg_str: str, width: int = 1600, height: int = 740) -> bytes:
    """Render SVG to PNG using CairoSVG if available, falling back to headless Chrome for 100% vector fidelity."""
    try:
        import cairosvg
        return cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), output_width=width, output_height=height)
    except Exception:
        pass

    chrome = None
    for cand in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]:
        if Path(cand).is_file():
            chrome = cand
            break
    if not chrome:
        import shutil
        chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if not chrome:
        raise RuntimeError("Neither CairoSVG nor a headless Chrome/Edge browser is available for rendering.")

    tmp_dir = Path(tempfile.mkdtemp())
    tmp_html = tmp_dir / "render.html"
    out_png = tmp_dir / "render.png"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background: transparent; width:{width}px; height:{height}px; overflow:hidden; }}
  svg {{ width:{width}px; height:{height}px; display:block; }}
</style>
</head>
<body>
{svg_str}
</body>
</html>"""
    tmp_html.write_text(html_content, encoding='utf-8')
    cmd = [
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--default-background-color=00000000',
        f'--window-size={width},{height}',
        f'--screenshot={out_png}',
        str(tmp_html)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_png.read_bytes()


def write_outputs(static_only=False):
    """Generate realistic static hero, vector halftone alternative and a nonlooping one-time GIF."""
    out = ROOT / 'assets/generated/hero'
    out.mkdir(parents=True, exist_ok=True)
    previews = ROOT / 'previews'
    previews.mkdir(parents=True, exist_ok=True)

    print("Generating Orbitron V4 SVG assets...")
    main_svg_str = main_svg()
    (out / 'hero-static.svg').write_text(main_svg_str, encoding='utf-8')
    (out / 'hero-vector-halftone.svg').write_text(main_svg(portrait_mode='dots'), encoding='utf-8')
    (out / 'portrait-halftone.svg').write_text(portrait_only(), encoding='utf-8')
    (out / 'right-architecture.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="310" height="315" viewBox="1250 150 310 330">{defs()}{circuit_motif()}</svg>', encoding='utf-8')
    (out / 'wave-terrain.svg').write_text(wave_only(), encoding='utf-8')
    (out / 'three-slashes.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="140" height="52" viewBox="1375 638 145 58"><path d="M1412 649 H1432 L1399 682 H1379Z" fill="none" stroke="{C["accent"]}" stroke-width="2"/><path d="M1445 649 H1473 L1440 682 H1412Z" fill="{C["accent"]}"/><path d="M1486 649 H1514 L1481 682 H1453Z" fill="{C["accent"]}"/></svg>', encoding='utf-8')
    print('Wrote self-contained static SVGs and vector assets.')

    print("Rendering high-res static PNG preview...")
    preview_bytes = svg_to_png(main_svg_str, width=1600, height=740)
    (out / 'hero-preview.png').write_bytes(preview_bytes)
    (out / 'hero-static.png').write_bytes(preview_bytes)
    (out / 'portrait-halftone.png').write_bytes(svg_to_png(portrait_only(), width=int(P['width']), height=int(P['height'])))

    if static_only:
        return

    gif_w = int(CONFIG['animation'].get('gif_width', 1120))
    gif_h = round(H * gif_w / W)
    scale = gif_w / W
    anim = CONFIG['animation']
    fps = float(anim['fps'])
    dur = float(anim['duration_seconds'])
    n = int(round(fps * dur))

    print(f"Rendering animated base card ({gif_w}x{gif_h})...")
    base_bytes = svg_to_png(main_svg(chars=0, cursor=False, portrait_mode='none'), width=gif_w, height=gif_h)
    base = Image.open(BytesIO(base_bytes)).convert('RGBA')

    photo = portrait_image_rgba().resize((round(P['width'] * scale), round(P['height'] * scale)), Image.Resampling.LANCZOS)
    dot_bytes = svg_to_png(portrait_only(), width=photo.width, height=photo.height)
    dot_img = Image.open(BytesIO(dot_bytes)).convert('RGBA')

    xoff, yoff = round(P['x'] * scale), round(P['y'] * scale)
    alpha_photo = np.asarray(photo.getchannel('A'), dtype=np.float32)
    dots_arr = np.asarray(dot_img, dtype=np.uint8)

    xv = np.arange(photo.width, dtype=np.float32)[None, :]
    w = photo.width
    imgs = []
    frames_for_preview = {0, round(n * .18), round(n * .43), round(n * .65), n - 1}

    # Pre-render / cache role overlays
    role_overlay_cache = {}
    print(f"Generating {n} animation frames (one-time portrait reveal + typewriter)...")

    for j in range(n):
        t = j / fps
        start = float(anim.get('portrait_start_seconds', .25))
        end = float(anim.get('portrait_end_seconds', 2.5))
        progress = np.clip((t - start) / (end - start), 0, 1)
        ease = progress * progress * (3 - 2 * progress)
        front = -65 * scale + (w + 140 * scale) * ease
        full = np.clip((front - xv - 48 * scale) / (20 * scale), 0, 1)
        dotted = np.clip((front - xv) / (17 * scale), 0, 1) * (1 - full)

        portrait_layer = photo.copy()
        pa = (alpha_photo * full).clip(0, 255).astype('uint8')
        portrait_layer.putalpha(Image.fromarray(np.broadcast_to(pa, (photo.height, photo.width)).copy(), 'L'))
        glow_layer = dot_img.copy()
        da = (dots_arr[:, :, 3].astype(np.float32) * dotted).clip(0, 255).astype('uint8')
        glow_layer.putalpha(Image.fromarray(np.broadcast_to(da, (photo.height, photo.width)).copy(), 'L'))

        frame_img = base.copy()
        frame_img.alpha_composite(portrait_layer, (xoff, yoff))
        frame_img.alpha_composite(glow_layer, (xoff, yoff))

        if 0 < progress < 1:
            line_x = xoff + int(front)
            if xoff <= line_x < xoff + w:
                draw = ImageDraw.Draw(frame_img, 'RGBA')
                draw.line([(line_x, yoff + 10), (line_x, yoff + photo.height - 8)], fill=(182, 255, 59, 110), width=2)

        # Looping typewriter animation:
        # Phase 1: Initial pause with blinking cursor
        # Phase 2: Forward typing of "AI Systems Engineer"
        # Phase 3: Hold full text with blinking cursor for readability
        # Phase 4: Backspace delete characters back to empty
        # Phase 5: Brief pause at empty with blinking cursor before seamless loop
        role_text_full = CONFIG['identity']['role']
        role_len = len(role_text_full)
        st = float(anim.get('typing_start_seconds', .6))
        ed = float(anim.get('typing_end_seconds', 2.7))
        hold_end = float(anim.get('typing_hold_seconds', 3.9))
        erase_end = float(anim.get('typing_erase_seconds', 4.6))

        if t < st:
            typed = 0
            cursor = (int(t * 3.0) % 2 == 0)
        elif t < ed:
            prog = (t - st) / max(0.01, ed - st)
            typed = int(round(role_len * prog))
            cursor = True
        elif t < hold_end:
            typed = role_len
            cursor = (int((t - ed) * 2.5) % 2 == 0)
        elif t < erase_end:
            prog = (t - hold_end) / max(0.01, erase_end - hold_end)
            typed = int(round(role_len * (1.0 - prog)))
            cursor = True
        else:
            typed = 0
            cursor = (int((t - erase_end) * 3.0) % 2 == 0)

        cache_key = (typed, cursor)
        if cache_key not in role_overlay_cache:
            overlay_svg = role_overlay(typed, cursor)
            overlay_bytes = svg_to_png(overlay_svg, width=gif_w, height=gif_h)
            role_overlay_cache[cache_key] = Image.open(BytesIO(overlay_bytes)).convert('RGBA')

        frame_img.alpha_composite(role_overlay_cache[cache_key])
        imgs.append(frame_img)

        if j in frames_for_preview:
            preview_rgb = Image.new('RGB', frame_img.size, C['base'])
            preview_rgb.paste(frame_img, mask=frame_img.getchannel('A'))
            preview_rgb.save(previews / f'reveal-frame-{j:02d}.png')

    # Save 800px README preview with transparent background
    preview_800 = imgs[-1].resize((800, round(gif_h * 800 / gif_w)), Image.Resampling.LANCZOS)
    preview_800.save(previews / 'readme-800px.png')

    print("Assembling animated GIF with true outer transparency and loop...")
    out_gif = out / 'hero-animated.gif'
    save_kwargs = {
        'save_all': True,
        'append_images': imgs[1:],
        'duration': round(1000 / fps),
        'disposal': 2,
        'optimize': True
    }
    if anim.get('loop', True):
        save_kwargs['loop'] = 0

    imgs[0].save(out_gif, **save_kwargs)
    print(f'Success! Hero GIF: {out_gif} ({out_gif.stat().st_size} bytes, {len(imgs)} frames, loop={save_kwargs.get("loop", "none")})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--static-only', action='store_true')
    args = ap.parse_args()
    write_outputs(static_only=args.static_only)

