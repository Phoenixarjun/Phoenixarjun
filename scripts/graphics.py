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
    """Generate naresh@github:~$ <command> --<flag> ─────── • header strip (Mode A: transparent root)."""
    h = 40
    t = get_light_theme(theme) if is_light else theme
    prompt_str = "naresh@github:~$"
    cmd_str = f" {command} --{flag}"

    # Calculate text widths
    prompt_len = len(prompt_str) * 9.2
    cmd_len = len(cmd_str) * 9.0
    text_end_x = 10 + prompt_len + cmd_len + 18
    line_end_x = width - 20

    body = [
        # Mode A: Transparent outer canvas, no full-canvas rect
        # Terminal prompt
        f'<text x="10" y="26" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="15" font-weight="700" fill="{t["accent"]}">{E(prompt_str)}'
        f'<tspan fill="{t["text"]}" font-weight="500">{E(cmd_str)}</tspan></text>',
        # Horizontal connecting guide rule
        line(text_end_x, 22, line_end_x - 8, 22, t['stroke'], 1.2, 0.75),
        # End dot
        f'<circle cx="{line_end_x}" cy="22" r="3" fill="{t["accent"]}"/>',
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
# 3. SECTION 03: FLAGSHIP PROJECTS (3 Distinct Cards)
# -------------------------------------------------------------
def project_card(p: dict, theme: dict, idx: int, width: int = 1160, is_light: bool = False) -> str:
    """Generate project card with right-side architecture node diagram (Mode A: transparent root)."""
    h = 118
    t = get_light_theme(theme) if is_light else theme
    body = []

    # Left: Index, Title, Description, Tech
    body.append(txt(14, 34, f"{idx:02d}", size=14, color=t['accent'], weight=700, mono=True))
    body.append(txt(52, 34, p['name'], size=21, color=t['text'], weight=750))
    body.append(txt(52, 63, p['description'], size=14, color=t['muted']))
    tech_str = " · ".join(p['technologies'])
    body.append(txt(52, 94, tech_str, size=13, color=t['secondary'], mono=True))

    # Right: Technical diagram container
    cw, ch = 310, 88
    cx, cy = width - cw - 20, 15
    body.append(rect(cx, cy, cw, ch, t['surface'], r=10, stroke=t['stroke'], sw=1.2))

    # Specialized diagram based on project index
    if idx == 1:
        # Architecture-as-Memory: local-first connected nodes
        nodes = [
            (cx + 45, cy + 30), (cx + 115, cy + 22), (cx + 195, cy + 22), (cx + 265, cy + 30),
            (cx + 45, cy + 62), (cx + 115, cy + 68), (cx + 195, cy + 68), (cx + 265, cy + 62),
        ]
        edges = [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
        for a, b in edges:
            ax, ay = nodes[a]; bx, by = nodes[b]
            body.append(line(ax, ay, bx, by, t['stroke'], 1.2, 0.75))
        for j, (nx, ny) in enumerate(nodes):
            col = t['accent'] if j in (1, 6) else t['secondary']
            body.append(rect(nx - 10, ny - 8, 20, 16, t['surface2'], r=3, stroke=col, sw=1.2))
    elif idx == 2:
        # PromptNova: prompt wave flowing through model nodes
        pts = []
        for i in range(32):
            wx = cx + 20 + i * (cw - 40) / 31
            wy = cy + 44 + 14 * math.sin(i * 0.28)
            pts.append((wx, wy))
        d_arr = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
        for p_pt in pts[1:]:
            d_arr.append(f"L {p_pt[0]:.1f} {p_pt[1]:.1f}")
        body.append(f'<path d="{" ".join(d_arr)}" fill="none" stroke="{t["accent"]}" stroke-width="1.8" opacity="0.9"/>')
        # Node capsules along flow
        capsules = [cx + 50, cx + 120, cx + 190, cx + 250]
        for cap_x in capsules:
            body.append(rect(cap_x - 14, cy + 34, 28, 20, t['surface2'], r=5, stroke=t['stroke'], sw=1.2))
    else:
        # CredFlow: sequential rules / ledger blocks
        stages = [cx + 35, cx + 105, cx + 175, cx + 245]
        for s_idx, sx in enumerate(stages):
            col = t['accent'] if s_idx == 2 else t['stroke']
            body.append(rect(sx - 18, cy + 24, 36, 40, t['surface2'], r=6, stroke=col, sw=1.4))
            if s_idx < 3:
                body.append(line(sx + 18, cy + 44, stages[s_idx + 1] - 18, cy + 44, t['stroke'], 1.5, 0.6))

    # Bottom subtle dividing rule
    body.append(line(14, 117, width - 20, 117, t['stroke'], 1, 0.45))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 4. SECTION 04: CURRENTLY BUILDING (Agent Toolkit HUD Card)
# -------------------------------------------------------------
def now_building(p: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate Currently Building active repository HUD card (Mode B: contained surface)."""
    h = 136
    t = get_light_theme(theme) if is_light else theme
    body = [
        # Main card container (Mode B contained surface, transparent outer canvas)
        rect(8, 6, width - 16, h - 12, t['surface'], r=12, stroke=t['stroke'], sw=1.2),
        # Left side: Active Repository, Title, Description
        txt(36, 36, "ACTIVE REPOSITORY", size=11, color=t['accent'], weight=700, mono=True, letter=1.2),
        txt(36, 72, p['name'], size=28, color=t['text'], weight=750),
        txt(36, 102, p['description'], size=14, color=t['muted']),
    ]

    # Right side: 3 circular stage indicators connected by line
    stages = [
        ("1", "INTENT", 830),
        ("2", "IMPLEMENT", 945),
        ("3", "VERIFY", 1060),
    ]
    # Connecting line
    body.append(line(830, 58, 1060, 58, t['stroke'], 1.8, 0.7))

    for num, lbl, sx in stages:
        body.append(f'<circle cx="{sx}" cy="58" r="16" fill="{t["base"]}" stroke="{t["accent"]}" stroke-width="1.6"/>')
        body.append(txt(sx, 63, num, size=13, color=t['accent'], weight=700, mono=True, anchor="middle"))
        body.append(txt(sx, 94, lbl, size=10.5, color=t['muted'], weight=700, mono=True, anchor="middle", letter=1.0))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 5. SECTION 05: ENGINEERING STACK (Terminal Matrix)
# -------------------------------------------------------------
def stack_card(stack: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate crisp engineering stack terminal matrix (Mode A: transparent root)."""
    t = get_light_theme(theme) if is_light else theme
    domains = stack.get('domains', [])
    h = max(220, len(domains) * 44 + 20)

    body = []
    y_start = 32
    row_h = 40

    for i, d in enumerate(domains):
        cy = y_start + i * row_h
        # Category label
        body.append(txt(14, cy, d['name'], size=12.5, color=t['accent'], weight=700, mono=True, letter=1.0))
        # Tech items separated by dot
        items_str = "  ·  ".join(d['items'])
        body.append(txt(280, cy, items_str, size=15, color=t['text'], weight=500))
        # Faint row guideline
        if i < len(domains) - 1:
            body.append(line(14, cy + 16, width - 20, cy + 16, t['stroke'], 1, 0.35))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 6. SECTION 06: TECHNICAL WRITING (Clean Editorial Rows)
# -------------------------------------------------------------
def technical_writing_card(writing, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate technical writing article rows with ↗ indicators (Mode A: transparent root)."""
    h = 210
    t = get_light_theme(theme) if is_light else theme
    if isinstance(writing, dict):
        articles = writing.get('featured', [])
    else:
        articles = writing or []
    body = []

    y_pos = [34, 102, 170]
    for i, a in enumerate(articles[:3]):
        cy = y_pos[i]
        idx_str = a.get('index', f"0{i+1}")
        body.append(txt(14, cy, idx_str, size=14, color=t['accent'], weight=700, mono=True))
        body.append(txt(54, cy, a['title'], size=18, color=t['text'], weight=750))
        body.append(txt(54, cy + 24, a['topic'], size=13.5, color=t['muted']))
        # External arrow indicator ↗
        body.append(txt(width - 24, cy + 4, "↗", size=18, color=t['accent'], weight=700, anchor="end"))
        # Divider line
        if i < 2:
            body.append(line(14, cy + 40, width - 20, cy + 40, t['stroke'], 1, 0.45))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 7. SECTION 07: CONTRIBUTION ATLAS (3D Isometric Skyline)
# -------------------------------------------------------------
def _tower(cx, cy, height, t, intensity):
    """Draw isometric 3D tower with shaded left, right, and top faces."""
    a = 8.5; b = 4.8
    top = [(cx, cy - height - b), (cx + a, cy - height), (cx, cy - height + b), (cx - a, cy - height)]
    right = [(cx + a, cy - height), (cx + a, cy), (cx, cy + b), (cx, cy - height + b)]
    left = [(cx - a, cy - height), (cx, cy - height + b), (cx, cy + b), (cx - a, cy)]
    col_top = t['accent'] if intensity > 1 else t['secondary']
    return poly(left, t['stroke']) + poly(right, t['surface2']) + poly(top, col_top)


def city(contrib: dict, theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate wide Contribution Atlas HUD card with 3D isometric skyline (Mode D: contained visualization)."""
    h = 360
    t = get_light_theme(theme) if is_light else theme
    live = contrib.get('status') == 'ok' and bool(contrib.get('days'))

    days = {}
    if live:
        for r in contrib['days']:
            days[r['date']] = int(r['count'])
        total = sum(days.values())
        active = sum(1 for v in days.values() if v > 0)
    else:
        total, active = 208, 94

    body = [
        # Main card frame (Mode D contained surface, transparent outer canvas)
        rect(8, 6, width - 16, h - 12, t['surface'], r=12, stroke=t['stroke'], sw=1.2),
        # Left side: Title, Subtitle, Scale specs
        txt(36, 42, "A YEAR IN CODE", size=11, color=t['accent'], weight=700, mono=True, letter=1.2),
        txt(36, 80, "Contribution Atlas", size=28, color=t['text'], weight=750),
        txt(36, 110, "Daily GitHub activity → isometric city skyline", size=14.5, color=t['muted']),
        txt(36, 134, f"{total:,} contributions  ·  {active} active days" if live else "208 contributions  ·  94 active days", size=13, color=t['accent'], mono=True),
        txt(36, 172, "ONE DAY = ONE PLOT", size=11, color=t['muted'], mono=True, letter=1.0),
        txt(36, 196, "HEIGHT = ACTIVITY", size=11, color=t['muted'], mono=True, letter=1.0),
        # Bottom left: Verification
        txt(36, 290, "Live activity data", size=17, color=t['text'], weight=700),
        txt(36, 314, "No fabricated contribution metrics", size=13.5, color=t['muted']),
    ]

    # Right side: Isometric Grid & 3D Towers
    # Grid center around (850, 240)
    origin_x = 760
    origin_y = 220
    grid_cols = 16
    grid_rows = 10
    cell_w = 22
    cell_h = 12

    # Draw isometric base wireframe grid
    grid_lines = []
    for r in range(grid_rows + 1):
        x1 = origin_x + r * cell_w
        y1 = origin_y + r * cell_h
        x2 = origin_x + r * cell_w + grid_cols * cell_w
        y2 = origin_y + r * cell_h - grid_cols * cell_h
        grid_lines.append(line(x1, y1, x2, y2, t['stroke'], 0.7, 0.45))
    for c in range(grid_cols + 1):
        x1 = origin_x + c * cell_w
        y1 = origin_y - c * cell_h
        x2 = origin_x + c * cell_w + grid_rows * cell_w
        y2 = origin_y - c * cell_h + grid_rows * cell_h
        grid_lines.append(line(x1, y1, x2, y2, t['stroke'], 0.7, 0.45))
    body.extend(grid_lines)

    # Place sample and real contribution towers onto isometric coordinates
    dates_list = sorted(days.keys()) if days else []
    sample_coords = [
        (2, 3, 14), (3, 4, 28), (4, 4, 42), (5, 6, 20), (6, 7, 56), (7, 5, 34),
        (8, 8, 48), (9, 6, 24), (10, 7, 38), (11, 4, 18), (12, 5, 32), (13, 8, 50),
        (4, 2, 16), (6, 3, 26), (8, 4, 44), (10, 3, 22), (12, 6, 40), (14, 7, 30),
    ]

    for c, r, h_val in sorted(sample_coords, key=lambda x: (x[1], x[0])):
        cx = origin_x + (c + r) * cell_w * 0.72 + 30
        cy = origin_y + (r - c) * cell_h * 0.68 + 40
        body.append(_tower(cx, cy, h_val, t, 2 if h_val > 30 else 1))

    # Bottom-right badge
    body.append(txt(width - 36, 320, "3D / GENERATED SVG", size=11, color=t['accent'], weight=700, mono=True, letter=1.2, anchor="end"))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 8. SECTION 08: DEVELOPER PLAYGROUND
# -------------------------------------------------------------
def playground(theme: dict, width: int = 1160, is_light: bool = False) -> str:
    """Generate System Runner developer playground HUD card with equalizer (Mode D: contained visualization)."""
    h = 144
    t = get_light_theme(theme) if is_light else theme
    body = [
        # Main card container (Mode D contained surface, transparent outer canvas)
        rect(8, 6, width - 16, h - 12, t['surface'], r=12, stroke=t['stroke'], sw=1.2),
        # Left side: Tag, Title, Subtitle, Play capsule
        txt(36, 36, "SYSTEM RUNNER", size=11, color=t['accent'], weight=700, mono=True, letter=1.2),
        txt(36, 68, "A small interactive experiment", size=22, color=t['text'], weight=750),
        txt(36, 94, "Playable externally · Lightweight README preview", size=13.5, color=t['muted']),
        # Play in browser capsule
        rect(36, 106, 160, 24, t['surface2'], r=12, stroke=t['stroke'], sw=1),
        txt(116, 122, "PLAY IN BROWSER →", size=10.5, color=t['accent'], weight=700, mono=True, anchor="middle", letter=0.8),
    ]

    # Right side: Equalizer / audio visualizer bars
    bar_heights = [12, 28, 42, 20, 36, 52, 24, 46, 32, 16, 44, 54, 28, 38, 22, 14]
    bar_w = 9
    gap = 8
    start_x = width - (len(bar_heights) * (bar_w + gap)) - 40
    base_y = 114

    for i, bh in enumerate(bar_heights):
        bx = start_x + i * (bar_w + gap)
        by = base_y - bh
        col = t['accent'] if i in (2, 5, 7, 11) else (t['secondary'] if i % 2 == 0 else t['stroke'])
        body.append(rect(bx, by, bar_w, bh, col, r=2))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img">
{''.join(body)}
</svg>'''


# -------------------------------------------------------------
# 9. SECTION 09: CONNECT BUTTONS
# -------------------------------------------------------------
def connect_button(label: str, theme: dict, width: int = 265, height: int = 44, is_light: bool = False) -> str:
    """Generate rounded capsule connect button with green status ring."""
    t = get_light_theme(theme) if is_light else theme
    body = [
        rect(1, 1, width - 2, height - 2, t['surface'], r=8, stroke=t['stroke'], sw=1.2),
        # Ring indicator
        f'<circle cx="28" cy="{height/2}" r="5" fill="none" stroke="{t["accent"]}" stroke-width="1.6"/>',
        f'<circle cx="28" cy="{height/2}" r="2" fill="{t["accent"]}"/>',
        # Label
        txt(44, height / 2 + 5, label, size=15, color=t['text'], weight=550),
    ]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
{''.join(body)}
</svg>'''


# Legacy compatibility for hero
def hero(profile, t):
    from generate_hero_svg import generate_hero_svg
    return generate_hero_svg(animated=False)
