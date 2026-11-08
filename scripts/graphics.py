"""Deterministic, dependency-free SVG artwork for GitHub Profile 2.0.

Fully adheres to Variation 01 (Terminal Editorial) design specifications:
- Unified command headers: naresh@github:~$ <command> --<flag> ─── •
- 3-column engineering focus
- Flagship project cards with right-side architecture node diagrams
- Currently building active repository card with 3-stage INTENT/IMPLEMENT/VERIFY indicators
- Clean terminal stack matrix
- Technical writing article rows with ↗ indicators
- Wide Contribution Atlas with isometric 3D city skyline
- Developer playground with audio spectrum visualizer
- Clickable connect buttons and terminal editorial footer
"""
from __future__ import annotations

import calendar
import datetime as dt
import math
import random
import textwrap
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

_ROOT = Path(__file__).resolve().parents[1]
_VENDOR_DIR = _ROOT / "assets" / "stack" / "vendor"


def get_vendor_icon(slug: str, x: float, y: float, size: float = 22, is_light: bool = False) -> str:
    path = _VENDOR_DIR / f"{slug}.svg"
    if not path.is_file():
        return ""
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        vb = root.attrib.get("viewBox", "0 0 24 24").split()
        min_x, min_y, w, h = map(float, vb)
        scale = min(size / w, size / h)
        act_w = w * scale
        act_h = h * scale
        off_x = x + (size - act_w) / 2.0
        off_y = y + (size - act_h) / 2.0
        raw = path.read_text(encoding="utf-8")
        if is_light:
            if slug in {"langgraph", "langchain", "crewai", "threejs"}:
                raw = raw.replace("#EEF7EF", "#141B20").replace("#FFFFFF", "#141B20").replace("#ffffff", "#141B20")
        inner = raw.split(">", 1)[1].rsplit("</svg>", 1)[0]
        return f'<g transform="translate({off_x:.2f}, {off_y:.2f}) scale({scale:.4f}) translate({-min_x:.1f}, {-min_y:.1f})">{inner}</g>'
    except Exception:
        return ""


def E(s: object) -> str:
    return escape(str(s), quote=True)


def txt(x, y, value, *, size=18, color='#fff', weight=400, mono=False, letter=None, anchor=None, opacity=None):
    attributes = f'x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"'
    attributes += ' font-family="\'JetBrains Mono\', \'Fira Code\', Consolas, monospace"' if mono else ' font-family="\'Inter\', -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif"'
    if letter is not None:
        attributes += f' letter-spacing="{letter}"'
    if anchor:
        attributes += f' text-anchor="{anchor}"'
    if opacity is not None:
        attributes += f' opacity="{opacity}"'
    return f'<text {attributes}>{E(value)}</text>'


def rect(x, y, w, h, fill, *, r=0, stroke=None, sw=1, opacity=None):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
    if stroke:
        out += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity is not None:
        out += f' opacity="{opacity}"'
    return out + '/>'


def line(x1, y1, x2, y2, color, width=1, opacity=None):
    out = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'
    if opacity is not None:
        out += f' opacity="{opacity}"'
    return out + '/>'


def poly(points, fill, stroke=None, opacity=None):
    p = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    s = f'<polygon points="{p}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width=".6"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    return s + '/>'


def get_light_theme(theme: dict) -> dict:
    """Derive Titanium Hacker light-mode palette tokens strictly from theme palette."""
    return {
        'base': '#FFFFFF',
        'surface': '#F4F7F8',
        'surface2': '#E5ECEF',
        'stroke': '#8EADB6',
        'accent': '#3B6600',  # high-contrast Titanium Hacker lime on light background (WCAG AAA)
        'secondary': '#42535C',
        'text': '#11171A',     # dark graphite text
        'muted': '#586A73',    # readable secondary slate
    }


def shell(w, h, theme, body, title, *, bg_mode='transparent', grid=False):
    t = theme
    defs = []
    if grid:
        defs.append(f'''<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r=".7" fill="{t['stroke']}" opacity=".35"/>
  </pattern>''')
    defs_block = f'<defs>\n{"".join(defs)}\n</defs>\n' if defs else ''

    bg = ''
    if bg_mode == 'surface':
        bg = f'<rect width="{w}" height="{h}" rx="14" fill="{t["surface"]}" stroke="{t["stroke"]}" stroke-width="1"/>\n'
    elif bg_mode == 'hero':
        bg = f'<rect width="{w}" height="{h}" rx="14" fill="{t["base"]}"/>\n'
    # 'transparent' (Mode A) renders no full-canvas background rect
    pattern = '<rect width="100%" height="100%" fill="url(#dots)" opacity=".25"/>\n' if grid else ''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}">
<title>{E(title)}</title>
{defs_block}{bg}{pattern}{body}
</svg>'''


def pill(x, y, label, theme, w=None, h=28, font=12):
    t = theme
    w = w or int(len(label) * 7.6 + 28)
    return rect(x, y, w, h, t['surface2'], r=h / 2, stroke=t['stroke']) + txt(
        x + w / 2, y + h / 2 + 4, label, size=font, color=t['text'], anchor='middle', mono=True
    )


# -------------------------------------------------------------
# 1. SECTION TERMINAL HEADERS
# -------------------------------------------------------------
def section_terminal_header(command: str, flag: str, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate standardized naresh@github:~$ <command> --<flag> ─────── • header strip (Mode A: transparent root)."""
    t = get_light_theme(theme) if is_light else theme
    prompt_str = "naresh@github:~$"
    cmd_str = f" {command} --{flag}" if flag else f" {command}"

    # Typography targets (Phase 3.2):
    # Prompt: 26px font size, Command: 25px font size
    # Canvas height: 52px, Left inset: 20px
    prompt_len = len(prompt_str) * 15.6
    cmd_len = len(cmd_str) * 14.8
    text_end_x = 34 + prompt_len + cmd_len + 16
    line_end_x = width - 24

    accessible_title = "Featured Projects" if (command == "ls" and flag == "flagship-projects") else f"{prompt_str}{cmd_str}"

    body = [
        f'<title>{E(accessible_title)}</title>',
        # Vertical lime accent bar at start
        f'<rect x="20" y="13" width="4" height="26" rx="2" fill="{t["accent"]}"/>',
        # Terminal prompt and command text
        f'<text x="34" y="33" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="26" font-weight="700" fill="{t["accent"]}">{E(prompt_str)}'
        f'<tspan fill="{t["text"]}" font-size="25" font-weight="500">{E(cmd_str)}</tspan></text>',
        # Horizontal steel continuation line
        f'<line x1="{text_end_x:.1f}" y1="26" x2="{line_end_x - 14}" y2="26" stroke="{t["stroke"]}" stroke-width="1.3" opacity="0.8"/>',
        # Lime endpoint circle
        f'<circle cx="{line_end_x - 4}" cy="26" r="3.5" fill="{t["accent"]}"/>',
    ]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="52" viewBox="0 0 {width} 52" role="img" aria-label="{E(accessible_title)}">
{''.join(body)}
</svg>'''


def section_heading(title: str, subtitle: str, theme: dict, accent_word: str = "", width: int = 1160, is_light: bool = False) -> str:
    """Generate standardized Titanium Hacker section heading banner (Mode A: transparent root)."""
    t = get_light_theme(theme) if is_light else theme
    h = 58
    accent_bar = f'<rect x="20" y="12" width="4.5" height="34" rx="2.2" fill="{t["accent"]}"/>'

    if accent_word and accent_word in title:
        parts = title.split(accent_word, 1)
        title_markup = f'{E(parts[0])}<tspan fill="{t["accent"]}">{E(accent_word)}</tspan>{E(parts[1])}'
    else:
        title_markup = E(title)

    explicit_widths = {
        "Featured Projects": 295,
        "Currently Building": 310,
        "Engineering Stack": 285,
        "Technical Writing": 275,
        "Contribution Atlas": 290,
    }
    title_w = explicit_widths.get(title, len(title) * 17.5)
    sub_x = 36 + title_w + 18

    body = [
        f'<title>{E(title)} // {E(subtitle)}</title>',
        accent_bar,
        f'<text x="36" y="38" font-family="system-ui, -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="32" font-weight="750" fill="{t["text"]}">{title_markup}</text>',
        f'<text x="{sub_x:.1f}" y="38" font-family="system-ui, -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="16.5" font-weight="400" fill="{t["muted"]}">// {E(subtitle)}</text>',
    ]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 2. SECTION 02: ENGINEERING FOCUS (3 Columns)
# -------------------------------------------------------------
def engineering_focus_card(profile: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate 3-column editorial engineering focus layout (Mode A: transparent root)."""
    h = 100
    t = get_light_theme(theme) if is_light else theme
    pillars = profile.get('engineering_pillars', [])
    col_w = (width - 40) / 3

    body = []
    for i, p in enumerate(pillars[:3]):
        cx = 10 + i * col_w
        idx_str = f"0{i+1}"
        # Index number
        body.append(txt(cx, 28, idx_str, size=14, color=t['accent'], weight=700, mono=True))
        # Title
        body.append(txt(cx, 58, p['title'], size=21, color=t['text'], weight=750))
        # Description
        body.append(txt(cx, 82, p['description'], size=13.5, color=t['muted'], weight=400))

    # Bottom dividing rule
    body.append(line(10, 98, width - 20, 98, t['stroke'], 1, 0.45))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 3. SECTION 03: FLAGSHIP PROJECTS & VISUALIZATIONS
# -------------------------------------------------------------
def wrap_text_lines(text_str: str, max_chars: int = 76, max_lines: int = 3) -> list[str]:
    """Wrap text gracefully into up to max_lines lines without cutting words."""
    words = text_str.split()
    lines = []
    current = []
    current_len = 0
    for w in words:
        if current and (current_len + len(w) + 1 > max_chars) and len(lines) < max_lines - 1:
            lines.append(' '.join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += len(w) + (1 if len(current) > 1 else 0)
    if current:
        lines.append(' '.join(current))
    return lines


def visual_aam(theme: dict, is_light: bool = False, standalone: bool = False) -> str:
    """Architecture-as-Memory: Legend + 4-level Architecture Hierarchy Tree (centered)."""
    t = get_light_theme(theme) if is_light else theme
    accent = t['accent']
    stroke = t['stroke']
    muted = t['muted']
    text_col = t['text']
    surface = t['surface']
    box_tint = f"{accent}" if not is_light else "#D4E8CE"
    box_tint_op = "0.18" if not is_light else "0.55"

    ox, oy = (0, 0) if standalone else (776, 24)
    w, h = (348, 168)

    inner = []
    # Standalone container if standalone
    if standalone:
        bg = "#0C1215" if not is_light else "#F2F6F8"
        inner.append(f'<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{stroke}" stroke-width="1"/>')

    # Legend (x: ox + 20 .. ox + 90)
    # Row 1: System
    inner.append(f'<g transform="translate({ox + 22}, {oy + 40})">'
                 f'<polygon points="10,0 18,4 10,8 2,4" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.1"/>'
                 f'<polygon points="10,4 18,8 10,12 2,8" fill="none" stroke="{accent}" stroke-width="1.1"/>'
                 f'<polygon points="10,8 18,12 10,16 2,12" fill="none" stroke="{accent}" stroke-width="1.1"/>'
                 f'</g>')
    inner.append(txt(ox + 46, oy + 51, "System", size=10.5, color=text_col, mono=True))

    # Row 2: Domain
    inner.append(f'<g transform="translate({ox + 22}, {oy + 67})">'
                 f'<rect x="3" y="1" width="5" height="5" rx="1" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'<rect x="11" y="1" width="5" height="5" rx="1" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'<rect x="3" y="9" width="5" height="5" rx="1" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'<rect x="11" y="9" width="5" height="5" rx="1" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'</g>')
    inner.append(txt(ox + 46, oy + 78, "Domain", size=10.5, color=muted, mono=True))

    # Row 3: Feature
    inner.append(f'<g transform="translate({ox + 22}, {oy + 95})">'
                 f'<polygon points="10,1 17,5 10,9 3,5" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'<polygon points="3,5 10,9 10,16 3,12" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'<polygon points="10,9 17,5 17,12 10,16" fill="none" stroke="{stroke}" stroke-width="1"/>'
                 f'</g>')
    inner.append(txt(ox + 46, oy + 106, "Feature", size=10.5, color=muted, mono=True))

    # Row 4: Component
    inner.append(f'<rect x="{ox + 26}" y="{oy + 123}" width="11" height="11" rx="2" fill="none" stroke="{stroke}" stroke-width="1"/>')
    inner.append(txt(ox + 46, oy + 133, "Component", size=10.5, color=muted, mono=True))

    # Subtle vertical dividing rule between Legend and Tree
    inner.append(line(ox + 96, oy + 28, ox + 96, oy + 146, stroke, 1, 0.35))

    # Architecture Tree (x: ox + 110 .. ox + 330)
    # Tree Root (System)
    root_x = ox + 220
    inner.append(f'<rect x="{root_x - 22}" y="{oy + 26}" width="44" height="17" rx="4" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.6"/>')

    # Lines from root to Level 2 (Domain)
    inner.append(line(root_x, oy + 43, root_x, oy + 55, stroke, 1.2, 0.75))
    inner.append(line(ox + 140, oy + 55, ox + 300, oy + 55, stroke, 1.2, 0.75))
    inner.append(line(ox + 140, oy + 55, ox + 140, oy + 65, stroke, 1.2, 0.75))
    inner.append(line(root_x, oy + 55, root_x, oy + 65, stroke, 1.2, 0.75))
    inner.append(line(ox + 300, oy + 55, ox + 300, oy + 65, stroke, 1.2, 0.75))

    # Level 2 Nodes (Domain)
    inner.append(rect(ox + 122, oy + 65, 36, 15, surface, r=3, stroke=stroke, sw=1.1))
    inner.append(f'<rect x="{root_x - 18}" y="{oy + 65}" width="36" height="15" rx="3" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.5"/>')
    inner.append(rect(ox + 282, oy + 65, 36, 15, surface, r=3, stroke=stroke, sw=1.1))

    # Lines to Level 3 (Feature)
    # Left branches
    inner.append(line(ox + 140, oy + 80, ox + 140, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 126, oy + 90, ox + 154, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 126, oy + 90, ox + 126, oy + 97, stroke, 1.1, 0.6))
    inner.append(line(ox + 154, oy + 90, ox + 154, oy + 97, stroke, 1.1, 0.6))
    # Center branches
    inner.append(line(root_x, oy + 80, root_x, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 206, oy + 90, ox + 234, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 206, oy + 90, ox + 206, oy + 97, stroke, 1.1, 0.6))
    inner.append(line(ox + 234, oy + 90, ox + 234, oy + 97, stroke, 1.1, 0.6))
    # Right branches
    inner.append(line(ox + 300, oy + 80, ox + 300, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 286, oy + 90, ox + 314, oy + 90, stroke, 1.1, 0.6))
    inner.append(line(ox + 286, oy + 90, ox + 286, oy + 97, stroke, 1.1, 0.6))
    inner.append(line(ox + 314, oy + 90, ox + 314, oy + 97, stroke, 1.1, 0.6))

    # Level 3 Nodes (Feature)
    inner.append(rect(ox + 114, oy + 97, 24, 13, surface, r=3, stroke=stroke, sw=1.1))
    inner.append(rect(ox + 142, oy + 97, 24, 13, surface, r=3, stroke=stroke, sw=1.1))
    inner.append(rect(ox + 194, oy + 97, 24, 13, surface, r=3, stroke=stroke, sw=1.1))
    inner.append(f'<rect x="{ox + 222}" y="{oy + 97}" width="24" height="13" rx="3" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.4"/>')
    inner.append(rect(ox + 274, oy + 97, 24, 13, surface, r=3, stroke=stroke, sw=1.1))
    inner.append(rect(ox + 302, oy + 97, 24, 13, surface, r=3, stroke=stroke, sw=1.1))

    # Lines to Level 4 (Component)
    inner.append(line(ox + 118, oy + 110, ox + 118, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 132, oy + 110, ox + 132, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 154, oy + 110, ox + 154, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 200, oy + 110, ox + 200, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 214, oy + 110, ox + 214, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 234, oy + 110, ox + 234, oy + 122, accent, 1.2, 0.8))
    inner.append(line(ox + 280, oy + 110, ox + 280, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 294, oy + 110, ox + 294, oy + 122, stroke, 1, 0.5))
    inner.append(line(ox + 314, oy + 110, ox + 314, oy + 122, stroke, 1, 0.5))

    # Level 4 Nodes (Component)
    inner.append(rect(ox + 110, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 127, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 146, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 192, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 209, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    # Highlighted Component
    inner.append(f'<rect x="{ox + 226}" y="{oy + 122}" width="16" height="11" rx="2" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.4"/>')
    inner.append(rect(ox + 272, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 289, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))
    inner.append(rect(ox + 306, oy + 122, 16, 11, surface, r=2, stroke=stroke, sw=1))

    content = ''.join(inner)
    if standalone:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Architecture-as-Memory Topology">
{content}
</svg>'''
    return content


def visual_promptnova(theme: dict, is_light: bool = False, standalone: bool = False) -> str:
    """PromptNova: Prompt wave + 4 connected stages (Intent -> Refine -> Evaluate -> Output) (centered)."""
    t = get_light_theme(theme) if is_light else theme
    accent = t['accent']
    stroke = t['stroke']
    muted = t['muted']
    surface = t['surface']
    box_tint = f"{accent}" if not is_light else "#D4E8CE"
    box_tint_op = "0.2" if not is_light else "0.55"

    ox, oy = (0, 0) if standalone else (776, 24)
    w, h = (348, 168)

    inner = []
    if standalone:
        bg = "#0C1215" if not is_light else "#F2F6F8"
        inner.append(f'<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{stroke}" stroke-width="1"/>')

    # Ambient sine wave flowing through nodes (centered along y = oy + 84)
    wave_d = (
        f"M {ox + 12} {oy + 84} "
        f"C {ox + 65} {oy + 124}, {ox + 115} {oy + 40}, {ox + 165} {oy + 82} "
        f"C {ox + 215} {oy + 124}, {ox + 255} {oy + 36}, {ox + 300} {oy + 78} "
        f"C {ox + 325} {oy + 102}, {ox + 338} {oy + 68}, {ox + 344} {oy + 82}"
    )
    inner.append(f'<path d="{wave_d}" fill="none" stroke="{accent}" stroke-width="3.5" opacity="0.35" filter="url(#glow)"/>')
    inner.append(f'<path d="{wave_d}" fill="none" stroke="{accent}" stroke-width="1.6" opacity="0.85"/>')

    # 4 Pipeline Stage Nodes (Centered horizontally from ox + 32 to ox + 316)
    # Node 1: Intent (ox + 32)
    n1_x = ox + 32
    inner.append(rect(n1_x, oy + 54, 52, 58, surface, r=10, stroke=stroke, sw=1.2))
    # Chat bubble icon
    inner.append(f'<g transform="translate({n1_x + 18}, {oy + 66})">'
                 f'<path d="M 0 0 H 16 C 18 0 20 2 20 4 V 11 C 20 13 18 15 16 15 H 6 L 1 19 V 15 H 0 C -2 15 -4 13 -4 11 V 4 C -4 2 -2 0 0 0 Z" fill="none" stroke="{muted}" stroke-width="1.3"/>'
                 f'<circle cx="3" cy="7" r="1.1" fill="{muted}"/><circle cx="8" cy="7" r="1.1" fill="{muted}"/><circle cx="13" cy="7" r="1.1" fill="{muted}"/>'
                 f'</g>')
    inner.append(txt(n1_x + 26, oy + 103, "Intent", size=10.5, color=muted, mono=True, anchor="middle"))

    # Arrow 1 -> 2
    inner.append(f'<path d="M {n1_x + 58} {oy + 83} H {n1_x + 70} M {n1_x + 66} {oy + 79} L {n1_x + 70} {oy + 83} L {n1_x + 66} {oy + 87}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')

    # Node 2: Refine (ox + 108)
    n2_x = ox + 108
    inner.append(rect(n2_x, oy + 54, 52, 58, surface, r=10, stroke=stroke, sw=1.2))
    # Sliders icon
    inner.append(f'<g transform="translate({n2_x + 12}, {oy + 68})">'
                 f'<line x1="2" y1="4" x2="26" y2="4" stroke="{muted}" stroke-width="1.3"/>'
                 f'<circle cx="8" cy="4" r="2.4" fill="{muted}"/>'
                 f'<line x1="2" y1="13" x2="26" y2="13" stroke="{muted}" stroke-width="1.3"/>'
                 f'<circle cx="20" cy="13" r="2.4" fill="{muted}"/>'
                 f'</g>')
    inner.append(txt(n2_x + 26, oy + 103, "Refine", size=10.5, color=muted, mono=True, anchor="middle"))

    # Arrow 2 -> 3
    inner.append(f'<path d="M {n2_x + 58} {oy + 83} H {n2_x + 70} M {n2_x + 66} {oy + 79} L {n2_x + 70} {oy + 83} L {n2_x + 66} {oy + 87}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')

    # Node 3: Evaluate (ACTIVE HIGHLIGHTED STAGE) (ox + 184)
    n3_x = ox + 184
    inner.append(f'<rect x="{n3_x}" y="{oy + 52}" width="56" height="62" rx="10" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.8" filter="url(#glowSmall)"/>')
    # Bar chart icon
    inner.append(f'<g transform="translate({n3_x + 17}, {oy + 64})">'
                 f'<rect x="0" y="14" width="4" height="10" rx="1" fill="{accent}"/>'
                 f'<rect x="8" y="7" width="4" height="17" rx="1" fill="{accent}"/>'
                 f'<rect x="16" y="0" width="4" height="24" rx="1" fill="{accent}"/>'
                 f'</g>')
    inner.append(txt(n3_x + 28, oy + 105, "Evaluate", size=11, color=accent, weight=700, mono=True, anchor="middle"))

    # Arrow 3 -> 4
    inner.append(f'<path d="M {n3_x + 62} {oy + 83} H {n3_x + 74} M {n3_x + 70} {oy + 79} L {n3_x + 74} {oy + 83} L {n3_x + 70} {oy + 87}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')

    # Node 4: Output (ox + 264)
    n4_x = ox + 264
    inner.append(rect(n4_x, oy + 54, 52, 58, surface, r=10, stroke=stroke, sw=1.2))
    # Sparkle / Star icon
    inner.append(f'<g transform="translate({n4_x + 26}, {oy + 76})">'
                 f'<path d="M 0 -8 Q 0 0 8 0 Q 0 0 0 8 Q 0 0 -8 0 Q 0 0 0 -8 Z" fill="{muted}"/>'
                 f'</g>')
    inner.append(txt(n4_x + 26, oy + 103, "Output", size=10.5, color=muted, mono=True, anchor="middle"))

    content = ''.join(inner)
    if standalone:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="PromptNova Workflow">
<defs>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5"/></filter>
  <filter id="glowSmall" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
</defs>
{content}
</svg>'''
    return content


def visual_credflow(theme: dict, is_light: bool = False, standalone: bool = False) -> str:
    """CredFlow: Telecom cell mast + 4 billing nodes + Automated Dunning Rules feedback loop (centered)."""
    t = get_light_theme(theme) if is_light else theme
    accent = t['accent']
    stroke = t['stroke']
    muted = t['muted']
    text_col = t['text']
    surface = t['surface']
    box_tint = f"{accent}" if not is_light else "#D4E8CE"
    box_tint_op = "0.2" if not is_light else "0.55"

    ox, oy = (0, 0) if standalone else (776, 24)
    w, h = (348, 168)

    inner = []
    if standalone:
        bg = "#0C1215" if not is_light else "#F2F6F8"
        inner.append(f'<rect width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{stroke}" stroke-width="1"/>')

    # Telecom Mast (Centered around x = ox + 49, waves span ox + 36 .. ox + 62)
    inner.append(f'<g transform="translate({ox + 49}, {oy + 44})">'
                 f'<path d="M 0 4 L -6 26 H 6 Z M -5 18 H 5" stroke="{muted}" fill="none" stroke-width="1.2"/>'
                 f'<circle cx="0" cy="1" r="2.5" fill="{accent}"/>'
                 f'<path d="M -9 5 A 7 7 0 0 0 -9 19 M -13 1 A 13 13 0 0 0 -13 23" stroke="{accent}" fill="none" stroke-width="1.2"/>'
                 f'<path d="M 9 5 A 7 7 0 0 1 9 19 M 13 1 A 13 13 0 0 1 13 23" stroke="{accent}" fill="none" stroke-width="1.2"/>'
                 f'</g>')
    inner.append(txt(ox + 49, oy + 84, "Telecom", size=9.5, color=muted, mono=True, anchor="middle"))

    # Arrow to Invoice
    inner.append(f'<path d="M {ox + 65} {oy + 64} H {ox + 77} M {ox + 73} {oy + 61} L {ox + 77} {oy + 64} L {ox + 73} {oy + 67}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')

    # Main Pipeline of 4 Nodes (Centered vertically at y = oy + 42, height = 44)
    # Node 1: Invoice (ox + 79)
    n1_x = ox + 79
    inner.append(rect(n1_x, oy + 42, 44, 44, surface, r=7, stroke=stroke, sw=1.2))
    # Document icon
    inner.append(f'<g transform="translate({n1_x + 14}, {oy + 49})">'
                 f'<rect x="0" y="0" width="16" height="18" rx="2" fill="none" stroke="{muted}" stroke-width="1.2"/>'
                 f'<line x1="3" y1="5" x2="13" y2="5" stroke="{muted}" stroke-width="1"/>'
                 f'<line x1="3" y1="9" x2="11" y2="9" stroke="{muted}" stroke-width="1"/>'
                 f'</g>')
    inner.append(txt(n1_x + 22, oy + 78, "Invoice", size=9, color=muted, mono=True, anchor="middle"))

    # Arrow 1 -> 2
    inner.append(f'<path d="M {n1_x + 49} {oy + 64} H {n1_x + 59} M {n1_x + 55} {oy + 61} L {n1_x + 59} {oy + 64} L {n1_x + 55} {oy + 67}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')

    # Node 2: Payment (ox + 143)
    n2_x = ox + 143
    inner.append(rect(n2_x, oy + 42, 44, 44, surface, r=7, stroke=stroke, sw=1.2))
    # Credit Card icon
    inner.append(f'<g transform="translate({n2_x + 13}, {oy + 51})">'
                 f'<rect x="0" y="0" width="18" height="13" rx="2" fill="none" stroke="{muted}" stroke-width="1.2"/>'
                 f'<line x1="0" y1="4" x2="18" y2="4" stroke="{muted}" stroke-width="1.2"/>'
                 f'<circle cx="5" cy="9" r="1.3" fill="{accent}"/>'
                 f'</g>')
    inner.append(txt(n2_x + 22, oy + 78, "Payment", size=9, color=muted, mono=True, anchor="middle"))

    # Arrow 2 -> 3
    inner.append(f'<path d="M {n2_x + 49} {oy + 64} H {n2_x + 59} M {n2_x + 55} {oy + 61} L {n2_x + 59} {oy + 64} L {n2_x + 55} {oy + 67}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')

    # Node 3: Collection (ACTIVE HIGHLIGHTED STAGE) (ox + 207)
    n3_x = ox + 207
    inner.append(f'<rect x="{n3_x}" y="{oy + 40}" width="48" height="48" rx="8" fill="{box_tint}" fill-opacity="{box_tint_op}" stroke="{accent}" stroke-width="1.8" filter="url(#glowSmall)"/>')
    # Stack of coins icon
    inner.append(f'<g transform="translate({n3_x + 24}, {oy + 49})">'
                 f'<ellipse cx="0" cy="3" rx="8" ry="3" fill="none" stroke="{accent}" stroke-width="1.2"/>'
                 f'<path d="M -8 3 V 7 A 8 3 0 0 0 8 7 V 3" fill="none" stroke="{accent}" stroke-width="1.2"/>'
                 f'<path d="M -8 7 V 11 A 8 3 0 0 0 8 11 V 7" fill="none" stroke="{accent}" stroke-width="1.2"/>'
                 f'</g>')
    inner.append(txt(n3_x + 24, oy + 79, "Collection", size=9.5, color=accent, weight=700, mono=True, anchor="middle"))

    # Arrow 3 -> 4
    inner.append(f'<path d="M {n3_x + 53} {oy + 64} H {n3_x + 63} M {n3_x + 59} {oy + 61} L {n3_x + 63} {oy + 64} L {n3_x + 59} {oy + 67}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')

    # Node 4: Ops Dashboard (ox + 273)
    n4_x = ox + 273
    inner.append(rect(n4_x, oy + 42, 44, 44, surface, r=7, stroke=stroke, sw=1.2))
    # Ops dashboard chart icon
    inner.append(f'<g transform="translate({n4_x + 13}, {oy + 50})">'
                 f'<rect x="0" y="0" width="18" height="15" rx="2" fill="none" stroke="{muted}" stroke-width="1.2"/>'
                 f'<line x1="3" y1="11" x2="7" y2="6" stroke="{accent}" stroke-width="1.2"/>'
                 f'<line x1="8" y1="11" x2="12" y2="3" stroke="{accent}" stroke-width="1.2"/>'
                 f'<line x1="13" y1="11" x2="16" y2="8" stroke="{accent}" stroke-width="1.2"/>'
                 f'</g>')
    inner.append(txt(n4_x + 22, oy + 76, "Ops", size=8.5, color=muted, mono=True, anchor="middle"))
    inner.append(txt(n4_x + 22, oy + 84, "Dashboard", size=8.5, color=muted, mono=True, anchor="middle"))

    # Dunning Rules (Automated) Loop (Centered below Invoice and Payment)
    pill_w = 154
    # Center pill between Invoice center (101) and Collection center (231) -> midpoint 166
    pill_x = ox + 166 - pill_w // 2
    pill_y = oy + 112
    inner.append(rect(pill_x, pill_y, pill_w, 24, surface, r=12, stroke=stroke, sw=1.1))
    # Rotating gear icon inside pill
    inner.append(f'<g transform="translate({pill_x + 14}, {pill_y + 12})">'
                 f'<circle cx="0" cy="0" r="4.2" fill="none" stroke="{accent}" stroke-width="1.2"/>'
                 f'<path d="M 0 -6 V -4 M 0 4 V 6 M -6 0 H -4 M 4 0 H 6 M -4 -4 L -3 -3 M 3 3 L 4 4 M -4 4 L -3 3 M 3 -3 L 4 -4" stroke="{accent}" stroke-width="1.1"/>'
                 f'</g>')
    inner.append(txt(pill_x + 80, pill_y + 16, "Dunning Rules (Automated)", size=8.5, color=text_col, mono=True, anchor="middle"))

    # Dashed feedback loop connections
    # From Invoice drop down to pill left
    inner.append(f'<path d="M {n1_x + 22} {oy + 86} V {pill_y + 12} H {pill_x}" fill="none" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="3,3"/>')
    # From pill right curving up into Collection
    inner.append(f'<path d="M {pill_x + pill_w} {pill_y + 12} H {n3_x + 36} V {oy + 90} M {n3_x + 39} {oy + 94} L {n3_x + 36} {oy + 90} L {n3_x + 33} {oy + 94}" fill="none" stroke="{accent}" stroke-width="1.2" stroke-dasharray="3,3"/>')

    content = ''.join(inner)
    if standalone:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="CredFlow Collections">
<defs>
  <filter id="glowSmall" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
</defs>
{content}
</svg>'''
    return content


def project_card(p: dict, theme: dict, idx: int, width: int = 1160, is_light: bool = False) -> str:
    """Generate authentic Titanium Hacker flagship project module (Mode A: transparent outer canvas).

    Matches Variation 01 reference image:
    - Angular chamfered container with beveled top-left (c=22) and bottom-right (c=22)
    - Vertical neon-lime accent bar on the left edge next to index number
    - Large monospace index number (01, 02, 03) in lime accent
    - Vertical divider rule
    - Bold project title + 3-line readable description + tech stack tags + 'View on GitHub ↗'
    - Right-side framed architecture/pipeline diagram container
    """
    h = 216
    t = get_light_theme(theme) if is_light else theme
    card_id = f"proj-{idx}-{'light' if is_light else 'dark'}"

    # Visual background gradients
    bg_grad_id = f"cardBg-{card_id}"
    glow_id = "glow"
    glow_sm_id = "glowSmall"

    defs = [
        f'<defs>\n'
        f'  <linearGradient id="{bg_grad_id}" x1="0" y1="0" x2="1" y2="1">\n',
    ]
    if is_light:
        defs.append(f'    <stop offset="0%" stop-color="#FFFFFF"/>\n'
                    f'    <stop offset="100%" stop-color="#F2F6F8"/>\n')
    else:
        defs.append(f'    <stop offset="0%" stop-color="#141B20"/>\n'
                    f'    <stop offset="100%" stop-color="#0E1317"/>\n')
    defs.append(f'  </linearGradient>\n'
                f'  <filter id="{glow_id}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter>\n'
                f'  <filter id="{glow_sm_id}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2"/></filter>\n'
                f'</defs>\n')

    # Card Container Geometry (w=1136, h=200, chamfer=22)
    # Origin: (12, 8)
    card_path = "M 34 8 H 1134 L 1148 22 V 186 L 1126 208 H 26 L 12 194 V 30 Z"
    stroke_col = t['stroke'] if not is_light else "#A8C0CB"

    body = [
        ''.join(defs),
        # 1. Base Container Surface & Outline
        f'<path d="{card_path}" fill="url(#{bg_grad_id})" stroke="{stroke_col}" stroke-width="1.2"/>\n',
        # 2. Top-left Chamfer Lime Accent Stroke
        f'<path d="M 135 8 H 34 L 12 30 V 70" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
        # 3. Left Vertical Edge Lime Accent Strip (Next to Index Number)
        f'<line x1="12" y1="48" x2="12" y2="168" stroke="{t["accent"]}" stroke-width="3.5" stroke-linecap="round"/>\n',
        # 4. Bottom-Right Corner Accent with Restrained Glow
        f'<path d="M 1030 208 H 1126 L 1148 186 V 145" fill="none" stroke="{t["accent"]}" stroke-width="6" opacity="0.65" filter="url(#{glow_id})"/>\n',
        f'<path d="M 1030 208 H 1126 L 1148 186 V 145" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
    ]

    # Left Zone: Index Number & Vertical Divider
    idx_str = f"{idx:02d}"
    body.append(f'<text x="65" y="116" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="34" font-weight="750" fill="{t["accent"]}" text-anchor="middle">{idx_str}</text>\n')
    body.append(line(118, 26, 118, 190, t['stroke'], 1.2, 0.55) + '\n')

    # Center Zone: Title, Description, Tech Stack, CTA
    # Title
    body.append(txt(145, 46, p['name'], size=26, color=t['text'], weight=750) + '\n')

    # Description (Wrapped cleanly in 3 lines)
    desc_lines = wrap_text_lines(p['description'], max_chars=76, max_lines=3)
    line_y_coords = [78, 102, 126]
    for dy, dline in zip(line_y_coords, desc_lines):
        body.append(txt(145, dy, dline, size=14.5, color=t['muted'], weight=400) + '\n')

    # Tech Stack (Positioned at y=166 above the lower technical shelf line)
    tech_tags = p.get('technologies', [])
    bullet = f'<tspan fill="{t["accent"]}">  ·  </tspan>'
    tech_str = bullet.join(E(tag) for tag in tech_tags)
    body.append(f'<text x="145" y="166" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="14" font-weight="500" fill="{t["text"]}">{tech_str}</text>\n')

    # Stepped Technical Shelf Line above 'View on GitHub ↗'
    # Runs horizontally under tech stack (y=184), chamfers up-right at 45° (x=485..501, y=184..168),
    # and extends horizontally above 'View on GitHub ↗' to meet the right container (x=776, y=168).
    shelf_path = "M 145 184 H 485 L 501 168 H 776"
    body.append(f'<path d="{shelf_path}" fill="none" stroke="{t["stroke"]}" stroke-width="1.2" opacity="0.65"/>\n')

    # Action Label (View on GitHub ↗) nestled in the recessed shelf
    cta_x = 515
    cta_y = 191
    body.append(
        f'<text x="{cta_x}" y="{cta_y}" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="14.5" font-weight="650" fill="{t["accent"]}">'
        f'View on GitHub ↗</text>\n'
    )

    # Right Zone: Subtle framed container for architecture diagram (centered vertically at y=24)
    right_bg = "#0C1215" if not is_light else "#EBF1F4"
    right_op = "0.7" if not is_light else "0.85"
    cont_path = "M 788 24 H 1112 L 1124 36 V 180 L 1112 192 H 788 L 776 180 V 36 Z"
    body.append(f'<path d="{cont_path}" fill="{right_bg}" fill-opacity="{right_op}" stroke="{t["stroke"]}" stroke-width="1" opacity="0.7"/>\n')

    # Embed specialized architecture / workflow diagram based on idx
    if idx == 1:
        body.append(visual_aam(theme, is_light=is_light, standalone=False))
    elif idx == 2:
        body.append(visual_promptnova(theme, is_light=is_light, standalone=False))
    else:
        body.append(visual_credflow(theme, is_light=is_light, standalone=False))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="{E(p['name'])} — {E(p.get('category', 'Featured Project'))}">
<title>{E(p['name'])}</title>
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 4. SECTION 04: CURRENTLY BUILDING (Agent Toolkit HUD Card)
# -------------------------------------------------------------
def now_building(p: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate Currently Building active repository HUD card (Mode A: transparent root)."""
    h = 196
    t = get_light_theme(theme) if is_light else theme
    card_id = f"now-building-{'light' if is_light else 'dark'}"
    bg_grad_id = f"cardBg-{card_id}"

    defs = [
        f'<defs>\n'
        f'  <linearGradient id="{bg_grad_id}" x1="0" y1="0" x2="1" y2="1">\n',
    ]
    if is_light:
        defs.append(f'    <stop offset="0%" stop-color="#FFFFFF"/>\n'
                    f'    <stop offset="100%" stop-color="#F2F6F8"/>\n')
    else:
        defs.append(f'    <stop offset="0%" stop-color="#141B20"/>\n'
                    f'    <stop offset="100%" stop-color="#0E1317"/>\n')
    defs.append(f'  </linearGradient>\n'
                f'  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter>\n'
                f'  <filter id="glowSmall" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2"/></filter>\n'
                f'</defs>\n')

    card_path = "M 34 8 H 1134 L 1148 22 V 174 L 1126 196 H 26 L 12 182 V 30 Z"
    stroke_col = t['stroke'] if not is_light else "#A8C0CB"

    body = [
        ''.join(defs),
        # 1. Base Container Surface & Outline
        f'<path d="{card_path}" fill="url(#{bg_grad_id})" stroke="{stroke_col}" stroke-width="1.2"/>\n',
        # 2. Top-left Chamfer Accent Stroke
        f'<path d="M 135 8 H 34 L 12 30 V 70" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
        # 3. Bottom-Right Corner Accent with Restrained Glow
        f'<path d="M 1030 196 H 1126 L 1148 174 V 135" fill="none" stroke="{t["accent"]}" stroke-width="6" opacity="0.65" filter="url(#glow)"/>\n',
        f'<path d="M 1030 196 H 1126 L 1148 174 V 135" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
    ]

    # Left Zone: 3-Layer Isometric Stacked Emblem
    emblem_file = _ROOT / 'assets' / 'agent-toolkit' / 'agent-toolkit-emblem.svg'
    if emblem_file.is_file():
        emblem_raw = emblem_file.read_text(encoding='utf-8')
        if '</defs>' in emblem_raw:
            inner_emblem = emblem_raw.split('</defs>', 1)[1].rsplit('</svg>', 1)[0]
        else:
            inner_emblem = emblem_raw.split('>', 1)[1].rsplit('</svg>', 1)[0]
        body.append(f'<g transform="translate(18, 12) scale(0.58)">{inner_emblem}</g>\n')

    # Center Zone: Title, Subtitle, Description
    name_str = p.get('name', 'Agent Toolkit')
    sub_str = p.get('subtitle', 'Engineering playbooks for coding agents.')
    body.append(txt(215, 52, name_str, size=28, color=t['text'], weight=750) + '\n')
    body.append(txt(215, 78, sub_str, size=16, color=t['accent'], weight=650) + '\n')

    desc_lines = [
        "Portable, tool-agnostic procedures for Intent Capture,",
        "Code Explore, TDD, Code Review, Security Audit, and",
        "verification — with an evidence-driven approach."
    ]
    for dy, dline in zip([110, 132, 154], desc_lines):
        body.append(txt(215, dy, dline, size=14.5, color=t['muted'], weight=400) + '\n')

    # Right Zone: 3 Workflow Micro-Pods (Intent -> Implement -> Verify)
    pod_bg = t['surface'] if not is_light else "#EBF1F4"
    # Pod 1: Intent
    body.append(rect(734, 34, 76, 58, pod_bg, r=14, stroke=stroke_col, sw=1.2, opacity=0.85) + '\n')
    body.append(f'<g transform="translate(772, 53)">\n'
                f'  <circle cx="0" cy="0" r="11" fill="none" stroke="{t["accent"]}" stroke-width="1.8"/>\n'
                f'  <circle cx="0" cy="0" r="4.5" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                f'  <line x1="0" y1="-14" x2="0" y2="-7" stroke="{t["accent"]}" stroke-width="1.8"/>\n'
                f'  <line x1="0" y1="7" x2="0" y2="14" stroke="{t["accent"]}" stroke-width="1.8"/>\n'
                f'  <line x1="-14" y1="0" x2="-7" y2="0" stroke="{t["accent"]}" stroke-width="1.8"/>\n'
                f'  <line x1="7" y1="0" x2="14" y2="0" stroke="{t["accent"]}" stroke-width="1.8"/>\n'
                f'  <circle cx="0" cy="0" r="1.5" fill="{t["accent"]}"/>\n'
                f'</g>\n')
    body.append(f'<text x="772" y="82" font-size="11" font-weight="600" fill="{t["text"]}" font-family="\'JetBrains Mono\', monospace" text-anchor="middle">Intent</text>\n')

    # Arrow 1 -> 2
    body.append(f'<path d="M 820 63 H 844 M 838 58 L 844 63 L 838 68" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n')

    # Pod 2: Implement
    body.append(rect(854, 34, 84, 58, pod_bg, r=14, stroke=stroke_col, sw=1.2, opacity=0.85) + '\n')
    body.append(f'<g transform="translate(896, 53)">\n'
                f'  <path d="M -7 -6 L -13 0 L -7 6" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <path d="M 7 -6 L 13 0 L 7 6" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'  <line x1="3" y1="-8" x2="-3" y2="8" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round"/>\n'
                f'</g>\n')
    body.append(f'<text x="896" y="82" font-size="11" font-weight="600" fill="{t["text"]}" font-family="\'JetBrains Mono\', monospace" text-anchor="middle">Implement</text>\n')

    # Arrow 2 -> 3
    body.append(f'<path d="M 948 63 H 972 M 966 58 L 972 63 L 966 68" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n')

    # Pod 3: Verify
    body.append(rect(982, 34, 76, 58, pod_bg, r=14, stroke=stroke_col, sw=1.2, opacity=0.85) + '\n')
    body.append(f'<g transform="translate(1020, 53)">\n'
                f'  <path d="M 0 -11 L 10 -7 V 1 Q 10 9 0 14 Q -10 9 -10 1 V -7 Z" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linejoin="round"/>\n'
                f'  <path d="M -4 1 L -1 4 L 5 -3" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n'
                f'</g>\n')
    body.append(f'<text x="1020" y="82" font-size="11" font-weight="600" fill="{t["text"]}" font-family="\'JetBrains Mono\', monospace" text-anchor="middle">Verify</text>\n')

    # Lower: GitHub CTA button pill (x=814, y=116, w=248, h=44)
    btn_bg = "#11171A" if not is_light else "#E5ECF0"
    body.append(rect(814, 116, 248, 44, btn_bg, r=12, stroke=t['accent'], sw=1.6) + '\n')
    octo = "M 8 0 C 3.58 0 0 3.58 0 8 c 0 3.54 2.29 6.53 5.47 7.59 c 0.4 0.07 0.55 -0.17 0.55 -0.38 c 0 -0.19 -0.01 -0.82 -0.01 -1.49 c -2.01 0.37 -2.53 -0.49 -2.69 -0.94 c -0.09 -0.23 -0.48 -0.94 -0.82 -1.13 c -0.28 -0.15 -0.68 -0.52 -0.01 -0.53 c 0.63 -0.01 1.08 0.58 1.23 0.82 c 0.72 1.21 1.87 0.87 2.33 0.66 c 0.07 -0.52 0.28 -0.87 0.51 -1.07 c -1.78 -0.2 -3.64 -0.89 -3.64 -3.95 c 0 -0.87 0.31 -1.59 0.82 -2.15 c -0.08 -0.2 -0.36 -1.02 0.08 -2.12 c 0 0 0.67 -0.21 2.2 0.82 c 0.64 -0.18 1.32 -0.27 2 -0.27 c 0.68 0 1.36 0.09 2 0.27 c 1.53 -1.04 2.2 -0.82 2.2 -0.82 c 0.44 1.1 0.16 1.92 0.08 2.12 c 0.51 0.56 0.82 1.27 0.82 2.15 c 0 3.07 -1.87 3.75 -3.65 3.95 c 0.29 0.25 0.54 0.73 0.54 1.48 c 0 1.07 -0.01 1.93 -0.01 2.2 c 0 0.21 0.15 0.46 0.55 0.38 A 8.013 8.013 0 0 0 16 8 c 0 -4.42 -3.58 -8 -8 -8 Z"
    body.append(f'<g transform="translate(836, 128) scale(1.2)"><path d="{octo}" fill="{t["text"]}"/></g>\n')
    body.append(f'<text x="868" y="144" font-size="14.5" font-weight="650" fill="{t["text"]}" font-family="\'JetBrains Mono\', monospace">View repository ↗</text>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="Currently Building: {E(name_str)}">
<title>Currently Building: {E(name_str)}</title>
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 5. SECTION 05: ENGINEERING STACK (Titanium Hacker Component)
# -------------------------------------------------------------
def stack_card(stack: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate authentic Titanium Hacker engineering stack component card (Mode A: transparent root)."""
    domains = stack.get('domains', [])
    n_domains = max(1, len(domains))
    row_step = 54
    h = 20 + n_domains * row_step + 16

    t = get_light_theme(theme) if is_light else theme
    card_id = f"stack-{'light' if is_light else 'dark'}"
    bg_grad_id = f"cardBg-{card_id}"

    defs = [
        f'<defs>\n',
        f'  <linearGradient id="{bg_grad_id}" x1="0" y1="0" x2="1" y2="1">\n',
    ]
    if is_light:
        defs.append(f'    <stop offset="0%" stop-color="#FFFFFF"/>\n'
                    f'    <stop offset="100%" stop-color="#F2F6F8"/>\n')
    else:
        defs.append(f'    <stop offset="0%" stop-color="#141B20"/>\n'
                    f'    <stop offset="100%" stop-color="#0E1317"/>\n')
    defs.append(f'  </linearGradient>\n'
                f'  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter>\n'
                f'</defs>\n')

    card_path = f"M 34 8 H {width - 26} L {width - 12} 22 V {h - 22} L {width - 34} {h} H 26 L 12 {h - 14} V 30 Z"
    stroke_col = t['stroke'] if not is_light else "#A8C0CB"
    badge_bg = "#FFFFFF" if is_light else "#10171B"

    body = [
        ''.join(defs),
        # 1. Base Container Surface & Outline
        f'<path d="{card_path}" fill="url(#{bg_grad_id})" stroke="{stroke_col}" stroke-width="1.2"/>\n',
        # 2. Top-left Chamfer Accent Stroke
        f'<path d="M 135 8 H 34 L 12 30 V 70" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
        # 3. Bottom-Right Corner Accent with Restrained Glow
        f'<path d="M {width - 130} {h} H {width - 34} L {width - 12} {h - 22} V {h - 61}" fill="none" stroke="{t["accent"]}" stroke-width="6" opacity="0.65" filter="url(#glow)"/>\n',
        f'<path d="M {width - 130} {h} H {width - 34} L {width - 12} {h - 22} V {h - 61}" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linecap="round"/>\n',
    ]

    row_y_coords = [20 + i * row_step for i in range(n_domains)]

    for d, ry in zip(domains, row_y_coords):
        row_id = d.get('id', '')
        label = d.get('name', '')
        icon_type = d.get('icon', 'code')
        items = d.get('items', [])

        # 1. Left Domain Badge (w=225, h=42)
        body.append(rect(28, ry, 225, 42, badge_bg, r=12, stroke=stroke_col, sw=1.2) + '\n')

        # Domain icon in accent
        ic_x = 48
        ic_y = ry + 21
        if icon_type == "code":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <path d="M -5 -5 L -10 0 L -5 5" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n'
                        f'  <path d="M 5 -5 L 10 0 L 5 5" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n'
                        f'  <line x1="2" y1="-7" x2="-2" y2="7" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round"/>\n'
                        f'</g>\n')
        elif icon_type == "brain":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <path d="M -8 -4 A 4 4 0 0 1 -4 -9 A 5 5 0 0 1 4 -9 A 4 4 0 0 1 8 -4 A 4 4 0 0 1 8 4 A 4 4 0 0 1 4 9 A 5 5 0 0 1 -4 9 A 4 4 0 0 1 -8 4 Z" fill="none" stroke="{t["accent"]}" stroke-width="1.6"/>\n'
                        f'  <path d="M 0 -9 V 9 M -4 -4 C -2 -2 -2 2 -4 4 M 4 -4 C 2 -2 2 2 4 4" fill="none" stroke="{t["accent"]}" stroke-width="1.2"/>\n'
                        f'</g>\n')
        elif icon_type == "layers":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <polygon points="0,-7 8,-3 0,1 -8,-3" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'  <polyline points="-8,1 0,5 8,1" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'  <polyline points="-8,5 0,9 8,5" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'</g>\n')
        elif icon_type == "cube":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <polygon points="0,-8 7,-4 0,0 -7,-4" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'  <polygon points="-7,-4 0,0 0,8 -7,4" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'  <polygon points="0,0 7,-4 7,4 0,8" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>\n'
                        f'</g>\n')
        elif icon_type == "cpu":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <rect x="-7" y="-7" width="14" height="14" rx="2" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                        f'  <rect x="-3" y="-3" width="6" height="6" rx="1" fill="{t["accent"]}" opacity="0.4"/>\n'
                        f'  <line x1="-10" y1="-3.5" x2="-7" y2="-3.5" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="-10" y1="3.5" x2="-7" y2="3.5" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="7" y1="-3.5" x2="10" y2="-3.5" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="7" y1="3.5" x2="10" y2="3.5" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="-3.5" y1="-10" x2="-3.5" y2="-7" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="3.5" y1="-10" x2="3.5" y2="-7" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="-3.5" y1="7" x2="-3.5" y2="10" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'  <line x1="3.5" y1="7" x2="3.5" y2="10" stroke="{t["accent"]}" stroke-width="1.3"/>\n'
                        f'</g>\n')
        elif icon_type == "monitor":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <rect x="-9" y="-7" width="18" height="12" rx="2" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                        f'  <line x1="-3" y1="5" x2="-5" y2="8" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                        f'  <line x1="3" y1="5" x2="5" y2="8" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                        f'  <line x1="-6" y1="8" x2="6" y2="8" stroke="{t["accent"]}" stroke-width="1.5"/>\n'
                        f'</g>\n')
        elif icon_type == "pulse":
            body.append(f'<g transform="translate({ic_x}, {ic_y})">\n'
                        f'  <polyline points="-10,0 -5,0 -2,-7 2,7 5,0 10,0" fill="none" stroke="{t["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n'
                        f'</g>\n')

        # Domain label
        body.append(txt(74, ry + 27, label, size=15, color=t['text'], weight=750) + '\n')

        # Vertical divider next to badge
        body.append(line(268, ry + 9, 268, ry + 33, stroke_col, 1.2, 0.45) + '\n')

        # Natural left-aligned item placement across the row (no giant stretching voids)
        is_obs = (row_id == "observability" or d.get('has_more', False))
        start_x = 284
        n = len(items)
        gap = 18 if n >= 7 else 20
        font_sz = 13 if n >= 7 else 13.5

        def _char_w(name: str) -> float:
            w = 0.0
            for ch in name:
                if ch in "ijlI.,:;' ":
                    w += 3.8
                elif ch in "mwMW@%":
                    w += 9.6
                elif ch.isupper() or ch.isdigit() or ch in "+#-":
                    w += 7.8
                else:
                    w += 6.6
            return w

        cur_x = start_x
        for i, item in enumerate(items):
            ix = round(cur_x)
            item_name = item.get('name', '')
            slug = item.get('slug', item_name.lower().replace(' ', '-'))
            # Embed vendor vector icon
            icon_markup = get_vendor_icon(slug, ix, ry + 10, size=22, is_light=is_light)
            body.append(icon_markup + '\n')
            # Text label
            body.append(txt(ix + 27, ry + 26, item_name, size=font_sz, color=t['text'], weight=550) + '\n')

            # Calculate item width: icon(22) + gap-to-text(6) + text width
            item_w = 22 + 6 + round(_char_w(item_name) * (font_sz / 13.0))

            # Inter-item divider
            if i < n - 1:
                div_x = round(cur_x + item_w + gap / 2.0)
                body.append(line(div_x, ry + 11, div_x, ry + 31, stroke_col, 1.1, 0.35) + '\n')

            cur_x += item_w + gap

        # Observability '+ more' pill placed neatly after the items
        if is_obs:
            div_x = round(cur_x - gap / 2.0)
            body.append(line(div_x, ry + 11, div_x, ry + 31, stroke_col, 1.1, 0.35) + '\n')
            px = round(cur_x)
            body.append(rect(px, ry + 7, 78, 28, badge_bg, r=14, stroke=t['accent'], sw=1.3) + '\n')
            body.append(f'<text x="{px + 39}" y="{ry + 25}" font-size="12" font-weight="650" fill="{t["accent"]}" font-family="\'JetBrains Mono\', monospace" text-anchor="middle">+ more</text>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="Engineering Stack">
<title>Engineering Stack</title>
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 6. SECTION 06: TECHNICAL WRITING (Clean Editorial Rows)
# -------------------------------------------------------------
def technical_writing_header(theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate title banner for technical writing section."""
    h = 44
    t = get_light_theme(theme) if is_light else theme
    accent = t.get("accent", "#B6FF3B")
    muted = t.get("muted", "#7A8C99")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
  <rect x="8" y="10" width="4" height="24" rx="2" fill="{accent}" />
  <text x="22" y="28" font-family="system-ui, -apple-system, sans-serif" font-size="21" font-weight="750" fill="{accent}">Technical Writing</text>
  <text x="202" y="28" font-family="system-ui, -apple-system, sans-serif" font-size="13.5" font-weight="400" fill="{muted}">// Articles, ideas, and engineering write-ups</text>
</svg>'''


def technical_writing_row_card(article: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate individual clickable article row card (Mode D: contained surface)."""
    h = 68
    t = get_light_theme(theme) if is_light else theme
    stroke = "#A8C0CB" if is_light else t.get("stroke", "#42535C")
    accent = "#1A7F37" if is_light else t.get("accent", "#B6FF3B")
    text = "#1F2328" if is_light else t.get("text", "#EEF7EF")
    muted = "#656D76" if is_light else t.get("muted", "#A6B6B2")
    surf = "#FFFFFF" if is_light else "#10171B"
    surf_stroke = "#D0D7DE" if is_light else "#33444D"
    grad_id = f"twRowBg-{'light' if is_light else 'dark'}"

    idx = article.get("index", "01")
    title = article.get("title", "")
    topic = article.get("topic", "Applied AI")
    read_time = article.get("read_time", "~8 min read")
    tag_icon = '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8 8a2 2 0 0 0 2.828 0l7.172-7.172a2 2 0 0 0 0-2.828l-8-8zM7 9a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" fill="currentColor"/>'

    stop0 = "#FFFFFF" if is_light else "#141B20"
    stop1 = "#F2F6F8" if is_light else "#0E1317"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{stop0}" />
      <stop offset="100%" stop-color="{stop1}" />
    </linearGradient>
  </defs>
  <rect x="8" y="4" width="{width - 16}" height="{h - 8}" rx="8" ry="8" fill="url(#{grad_id})" stroke="{stroke}" stroke-width="1.2" />
  <rect x="28" y="18" width="40" height="28" rx="6" fill="{surf}" stroke="{surf_stroke}" stroke-width="1" />
  <text x="48" y="37" font-family="ui-monospace, SFMono-Regular, monospace" font-size="13" font-weight="700" fill="{text}" text-anchor="middle">{idx}</text>
  <text x="84" y="33" font-family="system-ui, -apple-system, sans-serif" font-size="16.5" font-weight="750" fill="{text}">{escape(title)}</text>
  <g transform="translate(84, 42) scale(0.68)" color="{muted}">{tag_icon}</g>
  <text x="102" y="52" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{muted}">{escape(topic)} · Medium · {escape(read_time)}</text>
  <rect x="{width - 54}" y="18" width="28" height="28" rx="6" fill="{surf}" stroke="{surf_stroke}" stroke-width="1" />
  <text x="{width - 40}" y="37" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="700" fill="{accent}" text-anchor="middle">↗</text>
</svg>'''


def technical_writing_card(writing, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate technical writing card matching Titanium Hacker system (Mode D: contained surface)."""
    h = 262
    t = get_light_theme(theme) if is_light else theme
    card_stroke = "#A8C0CB" if is_light else t.get("stroke", "#42535C")
    surf_bg = "#FFFFFF" if is_light else "#10171B"
    grad_id = f"twCardBg-{'light' if is_light else 'dark'}"
    stop0 = "#FFFFFF" if is_light else "#141B20"
    stop1 = "#F2F6F8" if is_light else "#0E1317"
    if isinstance(writing, dict):
        articles = writing.get('featured', [])
    else:
        articles = writing or []

    cw = width - 16
    ch = h - 12
    cx0, cy0 = 8, 6
    chamfer = 14
    c_path = (
        f"M {cx0 + chamfer} {cy0} "
        f"H {cx0 + cw - chamfer} L {cx0 + cw} {cy0 + chamfer} "
        f"V {cy0 + ch - chamfer} L {cx0 + cw - chamfer} {cy0 + ch} "
        f"H {cx0 + chamfer} L {cx0} {cy0 + ch - chamfer} "
        f"V {cy0 + chamfer} Z"
    )

    body = [
        f'''<defs>
  <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{stop0}" />
    <stop offset="100%" stop-color="{stop1}" />
  </linearGradient>
  <filter id="tw-lime-glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>''',
        # Main card surface (matching #141B20 -> #0E1317)
        f'<path d="{c_path}" fill="url(#{grad_id})" stroke="{card_stroke}" stroke-width="1.2" />',
    ]

    # Corner glow highlight at bottom right
    if not is_light:
        glow_corner = f"M {cx0 + cw - 32} {cy0 + ch} L {cx0 + cw - chamfer} {cy0 + ch} L {cx0 + cw} {cy0 + ch - chamfer} L {cx0 + cw} {cy0 + ch - 32}"
        body.append(f'<path d="{glow_corner}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" filter="url(#tw-lime-glow)" opacity="0.85" />')

    # Top-left accent bar
    body.append(rect(24, 24, 4, 22, t['accent'], r=2))

    # Header title and subtitle
    body.append(txt(36, 41, "Technical Writing", size=20, color=t['accent'], weight=750))
    body.append(txt(215, 41, "// Articles, ideas, and engineering write-ups", size=13, color=t['muted']))

    y_starts = [68, 130, 192]
    tag_icon_svg = '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8 8a2 2 0 0 0 2.828 0l7.172-7.172a2 2 0 0 0 0-2.828l-8-8zM7 9a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" fill="currentColor"/>'

    for i, a in enumerate(articles[:3]):
        y = y_starts[i]
        idx_str = a.get('index', f"0{i+1}")
        url = a.get('url', '#')
        title = a.get('title', '')
        topic = a.get('topic', 'Applied AI')
        platform = a.get('platform', 'Medium')
        read_time = a.get('read_time', '~8 min read')

        row_content = []
        # Index capsule
        row_content.append(rect(32, y, 40, 26, surf_bg, r=6, stroke=card_stroke, sw=1))
        row_content.append(txt(52, y + 17, idx_str, size=12.5, color=t['text'], weight=700, mono=True, anchor="middle"))

        # Title
        row_content.append(txt(88, y + 16, title, size=16.5, color=t['text'], weight=750))

        # Tag icon and metadata
        meta_str = f"{topic}  ·  {platform}  ·  {read_time}"
        row_content.append(f'<g transform="translate(88, {y + 25}) scale(0.7)" color="{t["muted"]}">{tag_icon_svg}</g>')
        row_content.append(txt(106, y + 36, meta_str, size=12.5, color=t['muted']))

        # External button on right
        row_content.append(rect(width - 56, y, 26, 26, surf_bg, r=6, stroke=card_stroke, sw=1))
        row_content.append(txt(width - 43, y + 17, "↗", size=14, color=t['accent'], weight=700, anchor="middle"))

        # Wrap in clickable link for standalone viewers
        body.append(f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{"".join(row_content)}</a>')

        # Divider line between rows
        if i < 2:
            body.append(line(32, y + 49, width - 30, y + 49, card_stroke, 1, 0.4))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="Technical Writing articles">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 7. SECTION 07: CONTRIBUTION ATLAS (3D Isometric Skyline)
# -------------------------------------------------------------
def city(contrib: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate wide Contribution Atlas HUD card with 3D isometric skyline (Mode D: contained visualization).
    
    Data-driven 3D isometric city with verified GitHub contribution metrics.
    No fabricated metrics, no hardcoded sample coordinates.
    """
    try:
        from scripts.render_contribution_svg import render_contribution_atlas_svg
    except ModuleNotFoundError:
        from render_contribution_svg import render_contribution_atlas_svg
    return render_contribution_atlas_svg(contrib, theme, width=width, height=460, is_light=is_light)


# -------------------------------------------------------------
# 8. SECTION 08: DEVELOPER PLAYGROUND
# -------------------------------------------------------------
def playground(theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate System Runner developer playground Architecture Grid Runner card (Mode D: contained visualization)."""
    h = 560
    t = get_light_theme(theme) if is_light else theme

    bg_card = "#FFFFFF" if is_light else "#0E1317"
    hud_bg = "#FFFFFF" if is_light else "#10171B"
    node_bg = "#FFFFFF" if is_light else "#141C21"
    stroke_col = "#A8C0CB" if is_light else t.get("stroke", "#42535C")
    accent_col = "#1A7F37" if is_light else "#B6FF3B"
    text_col = "#1F2328" if is_light else "#EEF7EF"
    muted_col = "#656D76" if is_light else "#8EADB6"
    sub_col = "#57606A" if is_light else "#A6B6B2"
    dashed_stroke = "#D0D7DE" if is_light else "#253139"

    body = [
        f'''<defs>
  <filter id="limeGlow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="4.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="pulseGlow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <linearGradient id="cardSheen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{"#FFFFFF" if is_light else "#141B20"}"/>
    <stop offset="100%" stop-color="{"#F2F6F8" if is_light else "#0E1317"}"/>
  </linearGradient>
</defs>'''
    ]

    # 1. Section Header Banner (Terminal icon + Title + Subtitle + CONCEPT badge)
    # [>_] Terminal Badge at x=14, y=14, w=44, h=44
    body.append(f'<rect x="14" y="14" width="44" height="44" rx="8" fill="{hud_bg}" stroke="{accent_col}" stroke-width="1.8"/>')
    body.append(f'<text x="24" y="42" font-family="\'JetBrains Mono\', monospace" font-size="19" font-weight="800" fill="{accent_col}">&gt;_</text>')

    # Vertical divider line
    body.append(f'<line x1="72" y1="16" x2="72" y2="56" stroke="{stroke_col}" stroke-width="1.2" opacity="0.65"/>')

    # Title: Developer Playground // System Runner
    body.append(f'<text x="88" y="42" font-family="system-ui, -apple-system, sans-serif" font-size="28" font-weight="750" fill="{text_col}">Developer Playground</text>')
    body.append(f'<text x="398" y="42" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="700" fill="{accent_col}">// System Runner</text>')

    # Description Line
    body.append(f'<text x="16" y="86" font-family="system-ui, -apple-system, sans-serif" font-size="15">'
                f'<tspan fill="{accent_col}" font-weight="700">Architecture Grid Runner // </tspan>'
                f'<tspan fill="{sub_col}">Solve a systems puzzle by connecting backend components and creating a valid data flow from source to target.</tspan>'
                f'</text>')

    # 2. Main Architecture Card (Contained surface)
    cw = width - 28
    ch = 435
    cx = 14
    cy = 105
    body.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16" fill="url(#cardSheen)" stroke="{stroke_col}" stroke-width="1.2"/>')
    body.append(f'<path d="M {cx + 16} {cy + 1} H {cx + cw - 16}" stroke="rgba(255,255,255,{"0.6" if is_light else "0.08"})" stroke-width="1"/>')

    # 3. Left Pod: /// ARCHITECTURE (x=cx+20, y=cy+20, w=275, h=330)
    pw, ph = 275, 330
    px, py = cx + 20, cy + 20
    body.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{hud_bg}" stroke="{stroke_col}" stroke-width="1"/>')
    body.append(f'<text x="{px + 18}" y="{py + 32}" font-family="\'JetBrains Mono\', monospace" font-size="13" font-weight="750" fill="{muted_col}" letter-spacing="1.2">/// ARCHITECTURE</text>')
    body.append(f'<line x1="{px + 18}" y1="{py + 44}" x2="{px + pw - 18}" y2="{py + 44}" stroke="{stroke_col}" stroke-width="1" opacity="0.4"/>')

    # 4 Rows of specs
    rows = [
        ("Grid", "4 × 4", False, '<path d="M 0 0 H 4 V 4 H 0 Z M 6 0 H 10 V 4 H 6 Z M 12 0 H 16 V 4 H 12 Z M 0 6 H 4 V 10 H 0 Z M 6 6 H 10 V 10 H 6 Z M 12 6 H 16 V 10 H 12 Z M 0 12 H 4 V 16 H 0 Z M 6 12 H 10 V 16 H 6 Z M 12 12 H 16 V 16 H 12 Z" fill="currentColor"/>'),
        ("Links", "6", False, '<path d="M 8 2 A 4 4 0 0 0 4 6 L 4 8 A 4 4 0 0 0 8 12 L 10 12 A 4 4 0 0 0 14 8 M 6 12 A 4 4 0 0 0 10 16 L 12 16 A 4 4 0 0 0 16 12 L 16 10 A 4 4 0 0 0 12 6" fill="none" stroke="currentColor" stroke-width="1.8"/>'),
        ("Goal", "Connect", False, '<circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="1.2" fill="currentColor"/>'),
        ("Status", "Solvable", True, '<polyline points="2,8 6,12 14,3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    ]
    ry_starts = [py + 84, py + 144, py + 204, py + 264]
    for (label, val, is_accent, icon_svg), ry in zip(rows, ry_starts):
        ic_col = accent_col if is_accent else muted_col
        body.append(f'<g transform="translate({px + 18}, {ry - 12}) scale(1)" color="{ic_col}">{icon_svg}</g>')
        body.append(f'<text x="{px + 44}" y="{ry}" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="550" fill="{text_col}">{label}</text>')
        v_col = accent_col if is_accent else muted_col
        v_weight = "750" if is_accent else "550"
        body.append(f'<text x="{px + pw - 18}" y="{ry}" font-family="\'JetBrains Mono\', monospace" font-size="15" font-weight="{v_weight}" fill="{v_col}" text-anchor="end">{val}</text>')
        if ry != ry_starts[-1]:
            body.append(f'<line x1="{px + 18}" y1="{ry + 22}" x2="{px + pw - 18}" y2="{ry + 22}" stroke="{stroke_col}" stroke-width="1" opacity="0.3"/>')

    # 4. Right Grid: 4x3 node matrix
    gx = px + pw + 20
    gy = cy + 20
    gw = cw - pw - 40
    gh = 330
    body.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="12" fill="{hud_bg}" stroke="{stroke_col}" stroke-width="1"/>')

    cols = [gx + 22, gx + 214, gx + 406, gx + 598]
    rows_y = [gy + 20, gy + 124, gy + 228]
    nw, nh = 166, 82

    db_icon = '''<ellipse cx="14" cy="6" rx="12" ry="4" fill="none" stroke="currentColor" stroke-width="1.8"/>
<path d="M 2 6 V 12 A 12 4 0 0 0 26 12 V 6" fill="none" stroke="currentColor" stroke-width="1.8"/>
<path d="M 2 12 V 18 A 12 4 0 0 0 26 18 V 12" fill="none" stroke="currentColor" stroke-width="1.8"/>'''

    gear_icon = '''<circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="2"/>
<path d="M 12 2 V 5 M 12 19 V 22 M 2 12 H 5 M 19 12 H 22 M 4.9 4.9 L 7 7 M 17 17 L 19.1 19.1 M 4.9 19.1 L 7 17 M 17 7 L 19.1 4.9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'''

    cube_icon = '''<polygon points="12,2 22,7 12,12 2,7" fill="none" stroke="currentColor" stroke-width="1.8"/>
<polygon points="2,7 12,12 12,22 2,17" fill="none" stroke="currentColor" stroke-width="1.8"/>
<polygon points="12,12 22,7 22,17 12,22" fill="none" stroke="currentColor" stroke-width="1.8"/>'''

    analytics_icon = '''<rect x="2" y="12" width="5" height="10" rx="1" fill="currentColor"/>
<rect x="9.5" y="6" width="5" height="16" rx="1" fill="currentColor"/>
<rect x="17" y="2" width="5" height="20" rx="1" fill="currentColor"/>'''

    lock_icon = '''<rect x="4" y="9" width="16" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/>
<path d="M 7 9 V 6 A 5 5 0 0 1 17 6 V 9" fill="none" stroke="currentColor" stroke-width="1.8"/>
<circle cx="12" cy="15" r="1.5" fill="currentColor"/>'''

    queue_icon = '''<rect x="2" y="3" width="5" height="5" rx="1" fill="currentColor"/>
<rect x="9.5" y="3" width="5" height="5" rx="1" fill="currentColor"/>
<rect x="17" y="3" width="5" height="5" rx="1" fill="currentColor"/>
<rect x="2" y="10" width="5" height="5" rx="1" fill="currentColor"/>
<rect x="9.5" y="10" width="5" height="5" rx="1" fill="currentColor"/>
<rect x="17" y="10" width="5" height="5" rx="1" fill="currentColor"/>'''

    shield_icon = '''<path d="M 12 2 L 20 5 V 11 C 20 16 12 21 12 21 C 12 21 4 16 4 11 V 5 Z" fill="none" stroke="currentColor" stroke-width="1.8"/>
<polyline points="8,11 11,14 16,9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'''

    # Connecting Neon Pipes
    # Pipe 1: Ingest -> API
    p1_start_x = cols[0] + nw
    p1_start_y = rows_y[0] + nh / 2
    p1_mid_x = (cols[0] + nw + cols[1]) / 2 + 10
    p1_end_x = cols[1]
    p1_end_y = rows_y[1] + nh / 2
    body.append(f'<path d="M {p1_start_x} {p1_start_y} H {p1_mid_x - 12} Q {p1_mid_x} {p1_start_y} {p1_mid_x} {p1_start_y + 12} V {p1_end_y - 12} Q {p1_mid_x} {p1_end_y} {p1_mid_x + 12} {p1_end_y} H {p1_end_x}" fill="none" stroke="{accent_col}" stroke-width="3.5" stroke-linecap="round" filter="url(#limeGlow)"/>')
    body.append(f'<circle cx="{p1_mid_x}" cy="{(p1_start_y + p1_end_y)/2}" r="4.5" fill="{accent_col}" filter="url(#pulseGlow)"/>')
    body.append(f'<circle cx="{p1_mid_x}" cy="{(p1_start_y + p1_end_y)/2}" r="2" fill="#FFFFFF"/>')

    # Pipe 2: API -> Service
    p2_start_x = cols[1] + nw
    p2_end_x = cols[2]
    p2_y = rows_y[1] + nh / 2
    body.append(f'<line x1="{p2_start_x}" y1="{p2_y}" x2="{p2_end_x}" y2="{p2_y}" stroke="{accent_col}" stroke-width="3.5" stroke-linecap="round" filter="url(#limeGlow)"/>')
    body.append(f'<circle cx="{(p2_start_x + p2_end_x)/2}" cy="{p2_y}" r="4.5" fill="{accent_col}" filter="url(#pulseGlow)"/>')
    body.append(f'<circle cx="{(p2_start_x + p2_end_x)/2}" cy="{p2_y}" r="2" fill="#FFFFFF"/>')

    # Pipe 3: Service -> Analytics
    p3_start_x = cols[2] + nw / 2
    p3_start_y = rows_y[1] + nh
    p3_corner_y = rows_y[2] + nh / 2
    p3_end_x = cols[3]
    body.append(f'<path d="M {p3_start_x} {p3_start_y} V {p3_corner_y - 14} Q {p3_start_x} {p3_corner_y} {p3_start_x + 14} {p3_corner_y} H {p3_end_x}" fill="none" stroke="{accent_col}" stroke-width="3.5" stroke-linecap="round" filter="url(#limeGlow)"/>')
    body.append(f'<circle cx="{p3_start_x + 28}" cy="{p3_corner_y}" r="4.5" fill="{accent_col}" filter="url(#pulseGlow)"/>')
    body.append(f'<circle cx="{p3_start_x + 28}" cy="{p3_corner_y}" r="2" fill="#FFFFFF"/>')

    # Render all 12 grid slots:
    # (0,0): Ingest (Active Start)
    body.append(f'<rect x="{cols[0]}" y="{rows_y[0]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{accent_col}" stroke-width="2.5" filter="url(#limeGlow)"/>')
    body.append(f'<g transform="translate({cols[0] + 69}, {rows_y[0] + 16}) scale(1)" color="{accent_col}">{db_icon}</g>')
    body.append(f'<text x="{cols[0] + nw/2}" y="{rows_y[0] + 62}" font-family="system-ui, -apple-system, sans-serif" font-size="14.5" font-weight="750" fill="{accent_col}" text-anchor="middle">Ingest</text>')

    # (0,1): Empty
    body.append(f'<rect x="{cols[1]}" y="{rows_y[0]}" width="{nw}" height="{nh}" rx="14" fill="none" stroke="{dashed_stroke}" stroke-width="1.5" stroke-dasharray="6,6"/>')

    # (0,2): Lock
    body.append(f'<rect x="{cols[2]}" y="{rows_y[0]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.2"/>')
    body.append(f'<g transform="translate({cols[2] + nw/2 - 12}, {rows_y[0] + nh/2 - 12}) scale(1)" color="{muted_col}">{lock_icon}</g>')

    # (0,3): Queue
    body.append(f'<rect x="{cols[3]}" y="{rows_y[0]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.2"/>')
    body.append(f'<g transform="translate({cols[3] + nw/2 - 12}, {rows_y[0] + 18}) scale(1)" color="{muted_col}">{queue_icon}</g>')
    body.append(f'<text x="{cols[3] + nw/2}" y="{rows_y[0] + 60}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="650" fill="{text_col}" text-anchor="middle">Queue</text>')

    # (1,0): Empty
    body.append(f'<rect x="{cols[0]}" y="{rows_y[1]}" width="{nw}" height="{nh}" rx="14" fill="none" stroke="{dashed_stroke}" stroke-width="1.5" stroke-dasharray="6,6"/>')

    # (1,1): API (Active intermediate)
    body.append(f'<rect x="{cols[1]}" y="{rows_y[1]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.8"/>')
    body.append(f'<g transform="translate({cols[1] + nw/2 - 12}, {rows_y[1] + 16}) scale(1)" color="{text_col}">{gear_icon}</g>')
    body.append(f'<text x="{cols[1] + nw/2}" y="{rows_y[1] + 60}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="{text_col}" text-anchor="middle">API</text>')

    # (1,2): Service (Active intermediate)
    body.append(f'<rect x="{cols[2]}" y="{rows_y[1]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.8"/>')
    body.append(f'<g transform="translate({cols[2] + nw/2 - 12}, {rows_y[1] + 16}) scale(1)" color="{text_col}">{cube_icon}</g>')
    body.append(f'<text x="{cols[2] + nw/2}" y="{rows_y[1] + 60}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="{text_col}" text-anchor="middle">Service</text>')

    # (1,3): Empty
    body.append(f'<rect x="{cols[3]}" y="{rows_y[1]}" width="{nw}" height="{nh}" rx="14" fill="none" stroke="{dashed_stroke}" stroke-width="1.5" stroke-dasharray="6,6"/>')

    # (2,0): DB
    body.append(f'<rect x="{cols[0]}" y="{rows_y[2]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.2"/>')
    body.append(f'<g transform="translate({cols[0] + 69}, {rows_y[2] + 18}) scale(1)" color="{muted_col}">{db_icon}</g>')
    body.append(f'<text x="{cols[0] + nw/2}" y="{rows_y[2] + 60}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="650" fill="{text_col}" text-anchor="middle">DB</text>')

    # (2,1): Empty
    body.append(f'<rect x="{cols[1]}" y="{rows_y[2]}" width="{nw}" height="{nh}" rx="14" fill="none" stroke="{dashed_stroke}" stroke-width="1.5" stroke-dasharray="6,6"/>')

    # (2,2): Auth
    body.append(f'<rect x="{cols[2]}" y="{rows_y[2]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{stroke_col}" stroke-width="1.2"/>')
    body.append(f'<g transform="translate({cols[2] + nw/2 - 12}, {rows_y[2] + 16}) scale(1)" color="{muted_col}">{shield_icon}</g>')
    body.append(f'<text x="{cols[2] + nw/2}" y="{rows_y[2] + 60}" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="650" fill="{text_col}" text-anchor="middle">Auth</text>')

    # (2,3): Analytics (Active Target)
    body.append(f'<rect x="{cols[3]}" y="{rows_y[2]}" width="{nw}" height="{nh}" rx="14" fill="{node_bg}" stroke="{accent_col}" stroke-width="2.5" filter="url(#limeGlow)"/>')
    body.append(f'<g transform="translate({cols[3] + nw/2 - 12}, {rows_y[2] + 18}) scale(1)" color="{accent_col}">{analytics_icon}</g>')
    body.append(f'<text x="{cols[3] + nw/2}" y="{rows_y[2] + 62}" font-family="system-ui, -apple-system, sans-serif" font-size="14.5" font-weight="750" fill="{accent_col}" text-anchor="middle">Analytics</text>')

    # 5. Bottom Shelf: Tags + Play Button (y = cy + ch - 48 = 492)
    by = cy + ch - 48
    # Tag 1: Puzzle
    body.append(f'<g transform="translate({cx + 24}, {by - 14}) scale(1)" color="{muted_col}">'
                f'<path d="M 4 4 H 8 A 2 2 0 0 1 12 4 H 16 V 8 A 2 2 0 0 1 16 12 V 16 H 12 A 2 2 0 0 1 8 16 H 4 V 12 A 2 2 0 0 1 4 8 Z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
                f'</g>')
    body.append(f'<text x="{cx + 52}" y="{by}" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="600" fill="{text_col}">Puzzle</text>')

    body.append(f'<line x1="{cx + 125}" y1="{by - 18}" x2="{cx + 125}" y2="{by + 4}" stroke="{stroke_col}" stroke-width="1.2" opacity="0.5"/>')

    # Tag 2: Architecture
    body.append(f'<g transform="translate({cx + 145}, {by - 14}) scale(1)" color="{muted_col}">'
                f'<circle cx="4" cy="14" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
                f'<circle cx="16" cy="14" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
                f'<circle cx="10" cy="4" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
                f'<line x1="6.5" y1="12" x2="8.5" y2="6.5" stroke="currentColor" stroke-width="1.5"/>'
                f'<line x1="13.5" y1="12" x2="11.5" y2="6.5" stroke="currentColor" stroke-width="1.5"/>'
                f'</g>')
    body.append(f'<text x="{cx + 175}" y="{by}" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="600" fill="{text_col}">Architecture</text>')

    body.append(f'<line x1="{cx + 288}" y1="{by - 18}" x2="{cx + 288}" y2="{by + 4}" stroke="{stroke_col}" stroke-width="1.2" opacity="0.5"/>')

    # Tag 3: Data Flow
    body.append(f'<g transform="translate({cx + 308}, {by - 14}) scale(0.9)" color="{muted_col}">{db_icon}</g>')
    body.append(f'<text x="{cx + 342}" y="{by}" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="600" fill="{text_col}">Data Flow</text>')

    # Right Action Button: Play System Runner ↗
    btn_w = 236
    btn_h = 44
    btn_x = cx + cw - btn_w - 20
    btn_y = by - 26
    btn_bg = "#EBF1F4" if is_light else "#0E1417"
    body.append(f'<rect x="{btn_x}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="12" fill="{btn_bg}" stroke="{accent_col}" stroke-width="2" filter="url(#limeGlow)"/>')
    body.append(f'<text x="{btn_x + btn_w/2}" y="{btn_y + 28}" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="750" fill="{accent_col}" text-anchor="middle">Play System Runner ↗</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="Developer Playground // System Runner">
<title>Developer Playground // System Runner</title>
<desc>Architecture Grid Runner: Solve a systems puzzle by connecting backend components and creating a valid data flow from source to target.</desc>
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 9. SECTION 09: CONNECT BUTTONS & EDITORIAL FOOTER
# -------------------------------------------------------------
def connect_button(
    platform: str,
    label: str = None,
    theme: dict = None,
    width: int = 206,
    height: int = 50,
    is_light: bool = False,
    is_highlight: bool = None
) -> str:
    """Generate compact rounded glass capsule connect button with authentic brand icon, external arrow, and built-in vector spacing."""
    # Backwards compatibility if called as connect_button(label, theme)
    if theme is None and isinstance(label, dict):
        theme = label
        label = platform
        platform = platform.lower().split()[0]
    if label is None:
        label = platform.capitalize()

    plat_clean = platform.lower().replace('btn-', '').replace(' (soon)', '').strip()
    if is_highlight is None:
        is_highlight = (plat_clean == 'portfolio')

    t = get_light_theme(theme) if is_light else theme
    accent_col = "#1A7F37" if is_light else "#B6FF3B"
    text_col = "#1F2328" if is_light else "#EEF7EF"
    arrow_col = "#57606A" if is_light else "#A6B6B2"

    if is_highlight:
        btn_bg = "#FFFFFF" if is_light else "#141E15"
        stroke_col = accent_col
        stroke_w = "2"
        filter_str = 'filter="url(#btnGlow)"'
    else:
        btn_bg = "#FFFFFF" if is_light else "#12191D"
        stroke_col = "#D0D7DE" if is_light else "#2A3840"
        stroke_w = "1.2"
        filter_str = ''

    octocat_path = (
        'M 12 2 C 6.48 2 2 6.48 2 12 c 0 4.42 2.87 8.17 6.84 9.5 c 0.5 0.09 0.68 -0.22 0.68 -0.48 '
        'c 0 -0.24 -0.01 -1.04 -0.01 -1.88 c -2.78 0.6 -3.37 -1.18 -3.37 -1.18 c -0.45 -1.15 -1.11 -1.46 -1.11 -1.46 '
        'c -0.91 -0.62 0.07 -0.61 0.07 -0.61 c 1 0.07 1.53 1.03 1.53 1.03 c 0.89 1.52 2.34 1.08 2.91 0.83 '
        'c 0.09 -0.65 0.35 -1.08 0.63 -1.33 c -2.22 -0.25 -4.56 -1.11 -4.56 -4.95 c 0 -1.09 0.39 -1.99 1.03 -2.69 '
        'c -0.1 -0.25 -0.45 -1.27 0.1 -2.65 c 0 0 0.84 -0.27 2.75 1.02 c 0.8 -0.22 1.65 -0.33 2.5 -0.33 '
        'c 0.85 0 1.7 0.11 2.5 0.33 c 1.91 -1.29 2.75 -1.02 2.75 -1.02 c 0.55 1.38 0.2 2.4 0.1 2.65 '
        'c 0.64 0.7 1.03 1.6 1.03 2.69 c 0 3.85 -2.34 4.7 -4.57 4.95 c 0.36 0.31 0.68 0.92 0.68 1.85 '
        'c 0 1.34 -0.01 2.41 -0.01 2.74 c 0 0.27 0.18 0.58 0.69 0.48 C 19.13 20.17 22 16.42 22 12 C 22 6.48 17.52 2 12 2 Z'
    )

    linkedin_path = (
        'M 19 3 A 2 2 0 0 1 21 5 V 19 A 2 2 0 0 1 19 21 H 5 A 2 2 0 0 1 3 19 V 5 A 2 2 0 0 1 5 3 H 19 Z '
        'M 8.5 18 V 10.5 H 6 V 18 H 8.5 Z M 7.25 9.2 A 1.45 1.45 0 1 0 7.25 6.3 A 1.45 1.45 0 0 0 7.25 9.2 Z '
        'M 18 18 V 13.8 C 18 11.6 16.8 10.5 15.2 10.5 C 13.9 10.5 13.3 11.2 13 11.7 V 10.5 H 10.5 V 18 H 13 V 14 '
        'C 13 12.9 13.5 12.3 14.3 12.3 C 15.1 12.3 15.5 12.9 15.5 14 V 18 H 18 Z'
    )

    medium_path = (
        'M 4 4.5 L 8.5 4.5 L 12 12 L 15.5 4.5 L 20 4.5 L 20 19.5 L 17.5 19.5 L 17.5 9 L 13.5 17.5 L 10.5 17.5 L 6.5 9 L 6.5 19.5 L 4 19.5 Z'
    )

    laptop_icon = (
        '<rect x="3" y="4" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/>'
        '<line x1="1" y1="19" x2="23" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
    )

    ext_arrow = (
        '<path d="M 12 9 v 5 a 1.5 1.5 0 0 1 -1.5 1.5 h -7 A 1.5 1.5 0 0 1 2 14 V 7 A 1.5 1.5 0 0 1 3.5 5.5 h 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
        '<polyline points="10 3 15 3 15 8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="7" y1="11" x2="15" y2="3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
    )

    card_x = 15
    card_w = width - 30
    card_h = 42

    body = [
        f'''<defs>
  <filter id="btnGlow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="3.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <linearGradient id="btnSheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{"#FFFFFF" if is_light else "#182329"}" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="{"#F2F6F8" if is_light else "#0E1418"}" stop-opacity="0.95"/>
  </linearGradient>'''
    ]

    if is_highlight:
        body.append(f'''  <radialGradient id="portfolioUnderglow" cx="50%" cy="100%" r="50%">
    <stop offset="0%" stop-color="{accent_col}" stop-opacity="{"0.4" if is_light else "0.85"}"/>
    <stop offset="60%" stop-color="{accent_col}" stop-opacity="{"0.15" if is_light else "0.35"}"/>
    <stop offset="100%" stop-color="{accent_col}" stop-opacity="0"/>
  </radialGradient>''')

    body.append('</defs>')

    if is_highlight:
        body.append(f'<ellipse cx="{width/2}" cy="{height - 2}" rx="{card_w * 0.38}" ry="4.5" fill="url(#portfolioUnderglow)"/>')

    # Main Button Rounded Card with vector spacing
    body.append(f'<rect x="{card_x}" y="2" width="{card_w}" height="{card_h}" rx="11" fill="url(#btnSheen)" stroke="{stroke_col}" stroke-width="{stroke_w}" {filter_str}/>')
    # Specular top highlight line
    body.append(f'<path d="M {card_x + 10} 3 H {card_x + card_w - 10}" stroke="rgba(255,255,255,{"0.6" if is_light else "0.12"})" stroke-width="1"/>')

    # Brand Icon
    icon_x = card_x + 15
    icon_y = (card_h - 20) / 2 + 2
    if plat_clean == 'github':
        body.append(f'<g transform="translate({icon_x}, {icon_y}) scale(0.85)"><path d="{octocat_path}" fill="{text_col}"/></g>')
    elif plat_clean == 'linkedin':
        body.append(f'<g transform="translate({icon_x}, {icon_y}) scale(0.85)"><path d="{linkedin_path}" fill="{text_col}"/></g>')
    elif plat_clean == 'medium':
        body.append(f'<g transform="translate({icon_x}, {icon_y}) scale(0.85)"><path d="{medium_path}" fill="{text_col}"/></g>')
    elif plat_clean == 'portfolio':
        body.append(f'<g transform="translate({icon_x}, {icon_y}) scale(0.85)" color="{text_col}">{laptop_icon}</g>')

    # Label text
    body.append(f'<text x="{card_x + 44}" y="{card_h/2 + 7.5}" font-family="system-ui, -apple-system, sans-serif" font-size="14.5" font-weight="650" fill="{text_col}">{escape(label)}</text>')

    # Right external arrow
    body.append(f'<g transform="translate({card_x + card_w - 26}, {(card_h - 16)/2 + 2}) scale(0.88)" color="{arrow_col}">{ext_arrow}</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
{''.join(body)}
</svg>'''


def arcade_game_button(
    num: str,
    name: str,
    theme: dict,
    width: int = 216,
    height: int = 46,
    is_light: bool = False
) -> str:
    """Generate compact rounded glass capsule game launcher button with Titanium Hacker styling."""
    t = get_light_theme(theme) if is_light else theme
    accent_col = "#1A7F37" if is_light else "#B6FF3B"
    text_col = "#1F2328" if is_light else "#EEF7EF"
    arrow_col = "#57606A" if is_light else "#A6B6B2"
    badge_bg = "rgba(26, 127, 55, 0.1)" if is_light else "rgba(182, 255, 59, 0.12)"
    badge_border = "rgba(26, 127, 55, 0.3)" if is_light else "rgba(182, 255, 59, 0.28)"

    sheen_top = "#FFFFFF" if is_light else "#182329"
    sheen_bot = "#F2F6F8" if is_light else "#0E1418"
    stroke_col = "#D0D7DE" if is_light else "#2A3840"
    specular_col = "rgba(255,255,255,0.7)" if is_light else "rgba(255,255,255,0.12)"

    card_x = 5
    card_w = width - 10
    card_h = height - 6

    ext_arrow = (
        '<path d="M 12 9 v 5 a 1.5 1.5 0 0 1 -1.5 1.5 h -7 A 1.5 1.5 0 0 1 2 14 V 7 A 1.5 1.5 0 0 1 3.5 5.5 h 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
        '<polyline points="10 3 15 3 15 8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="7" y1="11" x2="15" y2="3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
    )

    body = [
        f'''<defs>
  <linearGradient id="btnSheen_{num}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{sheen_top}" stop-opacity="0.92"/>
    <stop offset="100%" stop-color="{sheen_bot}" stop-opacity="0.96"/>
  </linearGradient>
</defs>''',
        # Main Button Rounded Card
        f'<rect x="{card_x}" y="3" width="{card_w}" height="{card_h}" rx="10" fill="url(#btnSheen_{num})" stroke="{stroke_col}" stroke-width="1.2" />',
        # Specular top highlight
        f'<path d="M {card_x + 8} 4 H {card_x + card_w - 8}" stroke="{specular_col}" stroke-width="1"/>',
        # Mini number badge pill: 01
        f'<rect x="{card_x + 9}" y="{(card_h - 22)/2 + 3}" width="25" height="22" rx="5" fill="{badge_bg}" stroke="{badge_border}" stroke-width="0.8"/>',
        f'<text x="{card_x + 21.5}" y="{(card_h - 22)/2 + 18}" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="11" font-weight="700" fill="{accent_col}" text-anchor="middle">{num}</text>',
        # Game Label text
        f'<text x="{card_x + 42}" y="{card_h/2 + 7.5}" font-family="system-ui, -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="12" font-weight="650" fill="{text_col}">{escape(name)}</text>',
        # Right external arrow
        f'<g transform="translate({card_x + card_w - 20}, {(card_h - 14)/2 + 3}) scale(0.8)" color="{arrow_col}">{ext_arrow}</g>'
    ]

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="[{num}] {escape(name)}">
<title>[{num}] {escape(name)}</title>
{''.join(body)}
</svg>'''


def terminal_footer(profile: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate authentic Titanium Hacker terminal editorial footer (Mode A: transparent root)."""
    h = 70
    t = get_light_theme(theme) if is_light else theme
    tagline = profile.get("tagline", "Building intelligent software on reliable systems.")
    sub_col = "#57606A" if is_light else "#7A8C99"
    meta_col = "#8C959F" if is_light else "#52636E"
    body = [
        txt(width / 2, 28, tagline, size=14.5, color=sub_col, mono=True, anchor="middle", weight=400),
        txt(width / 2, 54, "VARIATION 01 / TERMINAL EDITORIAL", size=11, color=meta_col, mono=True, anchor="middle", weight=700, letter=1.8),
    ]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="Variation 01 / Terminal Editorial">
<title>Variation 01 / Terminal Editorial</title>
{''.join(body)}
</svg>'''


# Legacy compatibility for hero
def hero(profile, t):
    from generate_hero_svg import generate_hero_svg
    return generate_hero_svg(animated=False)
