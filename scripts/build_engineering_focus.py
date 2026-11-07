#!/usr/bin/env python3
"""Generate dependency-free, reusable GitHub README Engineering Focus SVGs.

Standardized canvas width: 1160px (aligned with profile system geometry).
Transparent root canvas (Mode A) with intentional contained pods (Mode B).
Dual-mode output: Dark and Light theme variants.
All design tokens are read strictly from design/themes.json (central source of truth).
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'engineering-focus'

central = ROOT / 'design' / 'themes.json'
if central.exists():
    settings = json.loads(central.read_text(encoding='utf-8'))
    selected = settings['active']
    if selected not in settings['presets']:
        raise ValueError('Unknown active theme in design/themes.json: ' + selected)
    chosen = settings['presets'][selected]
else:
    T = json.loads((ROOT / 'config' / 'theme.json').read_text(encoding='utf-8'))
    chosen = T['colors']

DATA = json.loads((ROOT / 'config' / 'engineering_focus.json').read_text(encoding='utf-8'))


def blend(h1: str, h2: str, fraction: float) -> str:
    def rgb(s):
        v = s.lstrip('#')
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    a, b = rgb(h1), rgb(h2)
    return '#' + ''.join(f'{round(v * (1 - fraction) + w * fraction):02X}' for v, w in zip(a, b))


def get_palette(is_light: bool = False) -> dict:
    base = chosen['base']
    surface = chosen['surface']
    accent = chosen['accent']
    text_primary = chosen['text']
    steel = chosen['stroke']
    secondary = chosen['secondary']
    muted = chosen.get('muted', secondary)

    if is_light:
        return {
            'base': '#FFFFFF',
            'surface': '#F4F7F8',
            'steel': '#8EADB6',
            'accent': '#3B6600',
            'text': '#11171A',
            'deep': '#DCE4E8',
            'surfaceDeep': '#E8EEF1',
            'surfaceRaised': '#FFFFFF',
            'edge': '#8EADB6',
            'textSecondary': '#586A73',
            'muted': '#586A73',
            'aquaHighlight': '#42535C',
            'limeShadow': '#789F43',
            'headingText': '#11171A',
            'headingAccent': '#3B6600',
            'headingMuted': '#586A73',
            'practiceRule': '#8EADB6',
        }

    return {
        'base': base,
        'surface': surface,
        'steel': steel,
        'accent': accent,
        'text': text_primary,
        'deep': blend(base, '#000000', 0.25),
        'surfaceDeep': blend(surface, base, 0.50),
        'surfaceRaised': blend(surface, accent, 0.055),
        'edge': blend(steel, secondary, 0.40),
        'textSecondary': chosen.get('muted', blend(text_primary, base, 0.30)),
        'muted': muted,
        'aquaHighlight': secondary,
        'limeShadow': blend(accent, base, 0.54),
        'headingText': text_primary,
        'headingAccent': accent,
        'headingMuted': chosen.get('muted', blend(text_primary, base, 0.30)),
        'practiceRule': steel,
    }


F = {
    'heading': "Inter, 'DejaVu Sans', Arial, sans-serif",
    'mono': "'JetBrains Mono', 'DejaVu Sans Mono', Consolas, monospace",
}


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def svg_open(w: int, h: int, title: str, C: dict, *, defs: bool = True) -> str:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">',
        f'<title>{esc(title)}</title>',
    ]
    if defs:
        out.append(shared_defs(C))
    return '\n'.join(out)


def shared_defs(C: dict) -> str:
    A = C['accent']
    return f'''<defs>
      <linearGradient id="pod" x1="0" y1="0" x2="0.7" y2="1"><stop offset="0%" stop-color="{C['surfaceRaised']}"/><stop offset="60%" stop-color="{C['surfaceDeep']}"/><stop offset="100%" stop-color="{C['deep']}"/></linearGradient>
      <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{C['edge']}"/><stop offset="55%" stop-color="{C['steel']}"/><stop offset="100%" stop-color="{C['deep']}"/></linearGradient>
      <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{C['aquaHighlight']}" stop-opacity=".55"/><stop offset="100%" stop-color="{C['surfaceRaised']}"/></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{C['surface']}"/><stop offset="70%" stop-color="{C['surfaceRaised']}"/><stop offset="100%" stop-color="{C['limeShadow']}"/></linearGradient>
      <linearGradient id="edgeGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{C['aquaHighlight']}" stop-opacity=".22"/><stop offset="45%" stop-color="{C['steel']}"/><stop offset="100%" stop-color="{A}" stop-opacity=".55"/></linearGradient>
      <radialGradient id="softLight"><stop offset="0" stop-color="{A}" stop-opacity=".23"/><stop offset=".55" stop-color="{A}" stop-opacity=".07"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>
      <filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>
      <filter id="glowSmall" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.6"/></filter>
    </defs>'''


def text(x, y, value, size=22, fill=None, weight=400, anchor=None, family='heading', extra=''):
    kw = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-family="{esc(F[family])}" font-size="{size}" font-weight="{weight}" fill="{fill}"{kw} {extra}>{esc(value)}</text>'


def path(d, stroke=None, fill='none', width=1, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def polygon(points, fill, stroke='none', width=1, extra=''):
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'


def pill_frame(w=360, h=64, C=None):
    C = C or get_palette(False)
    A = C['accent']
    d = f'M 15 3 H {w-26} L {w-3} 23 V {h-23} L {w-23} {h-3} H 3 V 17 Z'
    return '\n'.join([
        path(d, stroke='url(#edgeGrad)', fill='url(#pod)', width=1.6),
        path('M 3 23 V 15 L 16 3 H 61', stroke=A, width=3.4),
        path(f'M {w-75} {h-3} H {w-23} L {w-3} {h-23}', stroke=A, width=5, extra='opacity=".55" filter="url(#glow)"'),
        path(f'M {w-75} {h-3} H {w-23} L {w-3} {h-23}', stroke=A, width=2.8),
    ])


def pod_asset(w=360, h=350, C=None):
    C = C or get_palette(False)
    A = C['accent']
    d = f'M 24 2 H {w-36} L {w-2} 34 V {h-34} L {w-35} {h-2} H 2 V 22 Z'
    return ''.join([
        path(d, stroke='url(#edgeGrad)', fill='url(#pod)', width=1.8),
        path('M 2 37 V 22 L 24 2 H 112', stroke=A, width=3),
        path(f'M {w-105} {h-2} H {w-35} L {w-2} {h-34}', stroke=A, width=9, extra='filter="url(#glow)" opacity=".8"'),
        path(f'M {w-105} {h-2} H {w-35} L {w-2} {h-34}', stroke=A, width=3.8),
        path('M 3 134 V 220', stroke=C['aquaHighlight'], width=0.7, extra='opacity=".35"'),
    ])


def icon_ai(C):
    A = C['accent']
    p = ['<g stroke-linejoin="round">']
    p += ['<ellipse cx="95" cy="110" rx="72" ry="28" fill="url(#softLight)"/>']
    for dy, scale in [(0, 1.0), (21, 0.91), (41, 0.81)]:
        x0 = 94
        y0 = 71 + dy
        w = 61 * scale
        h = 23 * scale
        p += [
            polygon(f'{x0},{y0-h} {x0+w},{y0} {x0},{y0+h} {x0-w},{y0}', 'url(#face)', C['edge'], 1.6),
            polygon(f'{x0-w},{y0} {x0},{y0+h} {x0},{y0+h+10} {x0-w},{y0+10}', 'url(#metal)', C['steel'], 1.1),
            polygon(f'{x0},{y0+h} {x0+w},{y0} {x0+w},{y0+10} {x0},{y0+h+10}', 'url(#floor)', A, 1.1),
        ]
    p += [
        path('M 50 68 L 94 44 L 139 68 L 94 92 Z', stroke=A, width=2.4, extra='opacity=".72"'),
        text(94, 78, 'AI', 25, A, 800, 'middle', family='mono'),
        path('M 54 129 L 94 145 L 134 129', stroke=A, width=2.5, extra='opacity=".72"'),
    ]
    p.append('</g>')
    return ''.join(p)


def icon_backend(C):
    A = C['accent']
    return ''.join([
        '<g stroke-linejoin="round">',
        '<ellipse cx="95" cy="115" rx="73" ry="25" fill="url(#softLight)"/>',
        polygon('36,103 94,125 155,103 97,80', 'url(#floor)', A, 1.5),
        polygon('54,94 96,109 140,94 96,79', C['surfaceDeep'], C['steel'], 1.8),
        polygon('51,35 133,15 133,84 51,104', 'url(#face)', A, 2.2),
        polygon('51,35 58,39 58,96 51,104', C['steel']),
        path('M 79 51 L 67 64 L 79 73', stroke=A, width=4),
        path('M 109 41 L 119 48 L 109 62', stroke=A, width=4),
        path('M 101 38 L 87 79', stroke=A, width=4),
        path('M 45 111 L 94 127 L 147 110', stroke=A, width=2.1, extra='opacity=".65"'),
        '</g>',
    ])


def cuboid(x, y, r=23, C=None):
    C = C or get_palette(False)
    A = C['accent']
    return ''.join([
        polygon(f'{x},{y} {x+r},{y+r*.48} {x},{y+r*.98} {x-r},{y+r*.48}', 'url(#face)', C['aquaHighlight'], 1.2),
        polygon(f'{x-r},{y+r*.48} {x},{y+r*.98} {x},{y+r*2.0} {x-r},{y+r*1.5}', 'url(#metal)', C['edge'], 1.3),
        polygon(f'{x},{y+r*.98} {x+r},{y+r*.48} {x+r},{y+r*1.5} {x},{y+r*2.0}', 'url(#floor)', A, 1.6),
        path(f'M {x} {y+r*.98} V {y+r*2}', stroke=A, width=0.75, extra='opacity=".7"'),
    ])


def icon_distributed(C):
    A = C['accent']
    p = ['<g>', '<ellipse cx="95" cy="117" rx="76" ry="26" fill="url(#softLight)"/>']
    p += [path('M 95 76 L 49 103 M 95 76 L 141 103', stroke=A, width=2, extra='opacity=".65"')]
    p += [cuboid(95, 19, 24, C), cuboid(52, 79, 22, C), cuboid(138, 79, 22, C)]
    p += ['</g>']
    return ''.join(p)


def gear_path(cx, cy, ro=17, ri=12, teeth=10):
    import math
    pts = []
    for i in range(teeth * 4):
        a = -math.pi / 2 + 2 * math.pi * i / (teeth * 4)
        r = ro if i % 4 in (0, 1) else ri
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'


def practice_icon(id: str, C: dict):
    A = C['accent']
    if id == 'automation':
        return path(gear_path(30, 30), A, C['surfaceDeep'], 2.5) + f'<circle cx="30" cy="30" r="6" stroke="{A}" stroke-width="2.6" fill="none"/>'
    if id == 'observability':
        return path('M 13 10 H 48 V 50 H 13 Z', C['aquaHighlight'], C['surfaceDeep'], 1.6) + path('M 17 41 L 25 30 L 33 35 L 40 21 L 47 18', A, width=2.5)
    if id == 'production-engineering':
        return ''.join([
            polygon('30,11 46,19 30,28 14,19', 'url(#face)', A, 1.5),
            polygon('30,25 49,34 30,44 11,34', 'none', A, 2),
            polygon('30,36 49,45 30,54 11,45', 'none', A, 2),
        ])
    raise ValueError(id)


def icon_svg(name, inner, C):
    return svg_open(190, 155, name, C) + f'<rect x="0" y="0" width="190" height="155" fill="none"/>' + inner + '</svg>'


def make_section(is_light: bool = False) -> str:
    C = get_palette(is_light)
    w, h = 1160, 670
    p = [svg_open(w, h, 'Engineering Focus — Applied AI Systems, Backend Engineering, Distributed & Reliable Platforms', C)]

    # Mode A: Transparent outer canvas, no full-canvas opaque rect
    p.append('<g id="background-alpha" opacity="1"><rect x="0" y="0" width="1160" height="670" fill="none"/></g>')

    # Heading area (aligned at x=20)
    p += [
        '<g id="heading">',
        f'<rect x="20" y="24" width="5" height="54" rx="2" fill="{C["headingAccent"]}"/>',
        text(44, 54, 'Engineering', 44, C['headingText'], 800),
        text(338, 54, 'Focus', 44, C['headingAccent'], 800),
        text(46, 88, DATA['section']['subtitle'], 22, C['headingMuted'], 400),
        '</g>',
    ]

    # 3 Pods (Width 360 each, centered at x=20, 400, 780; spanning 20..1140 with 20px side insets)
    positions = [(20, 138), (400, 138), (780, 138)]
    icons = [icon_ai(C), icon_backend(C), icon_distributed(C)]

    for i, pillar in enumerate(DATA['pillars']):
        x, y = positions[i]
        p.append(f'<g id="pillar-{pillar["id"]}" transform="translate({x},{y})">')
        p.append(pod_asset(360, 350, C))
        # Icon centered inside 360-width pod (translate x=85, icon width ~190, center at 180)
        p.append(f'<g transform="translate(85,14)">{icons[i]}</g>')
        title_lines = pillar['titleLines']
        ty = 196 if len(title_lines) == 2 else 211
        for j, ln in enumerate(title_lines):
            p.append(text(180, ty + j * 34, ln, 29, C['text'], 760, 'middle'))
        p.append(f'<rect x="156" y="257" width="48" height="4" rx="2" fill="{C["accent"]}"/>')
        for j, ln in enumerate(pillar['descriptionLines']):
            p.append(text(180, 287 + j * 23, ln, 17.5, C['textSecondary'], 400, 'middle', family='mono'))
        p.append('</g>')

    # Enabling Practices heading (aligned at x=20, connecting line to x=1140)
    p += [
        '<g id="practice-heading">',
        text(20, 536, '//', 26, C['headingAccent'], 700, family='mono'),
        text(64, 536, 'Enabling Practices', 26, C['headingText'], 600),
        path('M 290 526 H 1134', C['practiceRule'], width=1.2, extra='opacity=".6"'),
        f'<circle cx="1140" cy="526" r="3" fill="{C["headingAccent"]}"/>',
        '</g>',
    ]

    # 3 Practice pills (Width 360 each at x=20, 400, 780)
    pills = [(20, 574, 360), (400, 574, 360), (780, 574, 360)]
    for i, practice in enumerate(DATA['practices']):
        x, y, pw = pills[i]
        p.append(f'<g id="practice-{practice["id"]}" transform="translate({x},{y})">')
        p.append(pill_frame(pw, 64, C))
        p.append(f'<g transform="translate(16,4) scale(.85)">{practice_icon(practice["id"], C)}</g>')
        lbl_x = 216 if practice['id'] == 'production-engineering' else pw / 2 + 8
        f_size = 20 if practice['id'] == 'production-engineering' else 22
        p.append(text(lbl_x, 41, practice['label'], f_size, C['text'], 650, 'middle'))
        p.append('</g>')

    p.append('</svg>')
    return '\n'.join(p)


def make_separator(is_light: bool = False) -> str:
    C = get_palette(is_light)
    h = 40
    p = [svg_open(1160, h, 'Terminal section divider: engineering-focus', C)]
    p += [
        f'<rect x="10" y="14" width="3.2" height="15" rx="1.5" fill="{C["headingAccent"]}"/>',
        text(22, 26, 'naresh@github:~$', 15, C['headingAccent'], 700, family='mono'),
        text(172, 26, 'inspect --engineering-focus', 15, C['headingText'], 500, family='mono'),
        path('M 442 22 H 1130', C['practiceRule'], width=1.2, extra='opacity=".75"'),
        f'<path d="M 1132 17 L 1138 22 L 1132 27" fill="none" stroke="{C["headingAccent"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
        '</svg>',
    ]
    return '\n'.join(p)


def make_frame():
    C = get_palette(False)
    return svg_open(360, 350, 'Titanium Hacker pillar pod frame', C) + pod_asset(360, 350, C) + '</svg>'


def make_pill():
    C = get_palette(False)
    return svg_open(360, 64, 'Titanium Hacker enabling-practice pill frame', C) + pill_frame(360, 64, C) + '</svg>'


def main():
    (OUT / 'icons').mkdir(parents=True, exist_ok=True)
    (OUT / 'frames').mkdir(parents=True, exist_ok=True)
    C_dark = get_palette(False)

    assets = {
        OUT / 'engineering-focus-dark.svg': make_section(is_light=False),
        OUT / 'engineering-focus-light.svg': make_section(is_light=True),
        OUT / 'engineering-focus-transparent.svg': make_section(is_light=False),
        OUT / 'section-command.svg': make_separator(is_light=False),
        OUT / 'section-command-light.svg': make_separator(is_light=True),
        OUT / 'frames' / 'pillar-pod.svg': make_frame(),
        OUT / 'frames' / 'practice-pill.svg': make_pill(),
        OUT / 'icons' / 'applied-ai-systems.svg': icon_svg('Applied AI Systems chip layers', icon_ai(C_dark), C_dark),
        OUT / 'icons' / 'backend-engineering.svg': icon_svg('Backend Engineering code console', icon_backend(C_dark), C_dark),
        OUT / 'icons' / 'distributed-reliable-platforms.svg': icon_svg('Distributed and Reliable Platforms cubes', icon_distributed(C_dark), C_dark),
    }

    for k in ['automation', 'observability', 'production-engineering']:
        assets[OUT / 'icons' / f'{k}.svg'] = svg_open(60, 60, f'{k} icon', C_dark) + practice_icon(k, C_dark) + '</svg>'

    for path_, content in assets.items():
        path_.write_text(content, encoding='utf-8')
        print('Wrote', path_.relative_to(ROOT), round(len(content) / 1024, 1), 'KB')


if __name__ == '__main__':
    main()
