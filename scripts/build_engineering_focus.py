#!/usr/bin/env python3
"""Generate dependency-free, reusable GitHub README Engineering Focus SVGs.

Usage: python scripts/build_engineering_focus.py
All design tokens are read from config/theme.json; content from config/engineering_focus.json.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'engineering-focus'
# Important: if this bundle is extracted into the existing GitHub Profile 2.0
# starter, inherit its *central* design/themes.json. Never create a competing
# master palette. Otherwise use the self-contained config/theme.json fallback.
T = json.loads((ROOT/'config'/'theme.json').read_text(encoding='utf-8'))
DATA = json.loads((ROOT/'config'/'engineering_focus.json').read_text(encoding='utf-8'))

def blend(h1: str, h2: str, fraction: float) -> str:
    def rgb(s):
        v=s.lstrip('#');return tuple(int(v[i:i+2],16) for i in (0,2,4))
    a,b=rgb(h1),rgb(h2)
    return '#'+''.join(f'{round(v*(1-fraction)+w*fraction):02X}' for v,w in zip(a,b))

central = ROOT/'design'/'themes.json'
if central.exists():
    settings=json.loads(central.read_text(encoding='utf-8'))
    selected=settings['active']
    if selected not in settings['presets']:
        raise ValueError('Unknown active theme in design/themes.json: '+selected)
    chosen=settings['presets'][selected]
    base = '#070B0C'
    surface = chosen['surface']
    accent = chosen['accent']
    text_primary = chosen['text']
    steel = chosen['stroke']
    secondary = chosen['secondary']
    C = {
      'base': '#070B0C',
      'surface': surface,
      'steel': steel,
      'accent': accent,
      'text': text_primary,
      'deep': '#070B0C',
      'surfaceDeep': blend(surface, '#070B0C', .50),
      'surfaceRaised': blend(surface, accent, .055),
      'edge': blend(steel, secondary, .40),
      'textSecondary': chosen.get('muted', blend(text_primary, '#070B0C', .30)),
      'muted': chosen.get('muted', secondary),
      'aquaHighlight': secondary,
      'limeShadow': blend(accent, '#070B0C', .54),
      'transparent': '#000000',
    }
else:
    C=T['colors']
F=T['fonts']
A=C['accent']

def esc(value: str) -> str:
    return html.escape(str(value), quote=True)

def svg_open(w: int, h: int, title: str, *, defs: bool=True) -> str:
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">', f'<title>{esc(title)}</title>']
    if defs: out.append(shared_defs())
    return '\n'.join(out)

def shared_defs() -> str:
    return f'''<defs>
      <linearGradient id="pod" x1="0" y1="0" x2="0.7" y2="1"><stop offset="0%" stop-color="{C['surfaceRaised']}"/><stop offset="60%" stop-color="{C['surfaceDeep']}"/><stop offset="100%" stop-color="{C['deep']}"/></linearGradient>
      <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{C['edge']}"/><stop offset="55%" stop-color="{C['steel']}"/><stop offset="100%" stop-color="{C['deep']}"/></linearGradient>
      <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{C['aquaHighlight']}" stop-opacity=".55"/><stop offset="100%" stop-color="{C['surfaceRaised']}"/></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{C['surface']}"/><stop offset="70%" stop-color="{C['surfaceRaised']}"/><stop offset="100%" stop-color="{C['limeShadow']}"/></linearGradient>
      <linearGradient id="edgeGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{C['aquaHighlight']}" stop-opacity=".22"/><stop offset="45%" stop-color="{C['steel']}"/><stop offset="100%" stop-color="{A}" stop-opacity=".55"/></linearGradient>
      <radialGradient id="softLight"><stop offset="0" stop-color="{A}" stop-opacity=".23"/><stop offset=".55" stop-color="{A}" stop-opacity=".07"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>
      <filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>
      <filter id="glowSmall" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.6"/></filter>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".75" fill="{C['steel']}" opacity=".18"/></pattern>
      <clipPath id="clipPanel"><rect x="0" y="0" width="1280" height="765"/></clipPath>
    </defs>'''

def text(x,y,value,size=22,fill=None,weight=400,anchor=None,family='heading',extra=''):
    kw=f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-family="{esc(F[family])}" font-size="{size}" font-weight="{weight}" fill="{fill or C["text"]}"{kw} {extra}>{esc(value)}</text>'

def path(d,stroke=None,fill='none',width=1,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke or C["steel"]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'

def polygon(points,fill,stroke='none',width=1,extra=''):
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'

def pill_frame(w=360,h=66):
    d=f'M 15 3 H {w-26} L {w-3} 23 V {h-23} L {w-23} {h-3} H 3 V 17 Z'
    return '\n'.join([
        path(d,stroke='url(#edgeGrad)',fill='url(#pod)',width=1.6),
        path('M 3 23 V 15 L 16 3 H 61',stroke=A,width=3.4),
        path(f'M {w-75} {h-3} H {w-23} L {w-3} {h-23}',stroke=A,width=5,extra='opacity=".55" filter="url(#glow)"'),
        path(f'M {w-75} {h-3} H {w-23} L {w-3} {h-23}',stroke=A,width=2.8),
    ])

def icon_ai():
    p=['<g stroke-linejoin="round">']
    p+=['<ellipse cx="95" cy="110" rx="72" ry="28" fill="url(#softLight)"/>']
    for dy,scale in [(0,1.0),(21,.91),(41,.81)]:
        x0=94; y0=71+dy; w=61*scale; h=23*scale
        p+= [polygon(f'{x0},{y0-h} {x0+w},{y0} {x0},{y0+h} {x0-w},{y0}', 'url(#face)',C['edge'],1.6),
             polygon(f'{x0-w},{y0} {x0},{y0+h} {x0},{y0+h+10} {x0-w},{y0+10}', 'url(#metal)',C['steel'],1.1),
             polygon(f'{x0},{y0+h} {x0+w},{y0} {x0+w},{y0+10} {x0},{y0+h+10}', 'url(#floor)',A,1.1)]
    p += [path('M 50 68 L 94 44 L 139 68 L 94 92 Z',stroke=A,width=2.4,extra='opacity=".72"'),
          text(94,78,'AI',25,A,800,'middle',family='mono'),
          path('M 54 129 L 94 145 L 134 129',stroke=A,width=2.5,extra='opacity=".72"')]
    p.append('</g>')
    return ''.join(p)

def icon_backend():
    return ''.join(['<g stroke-linejoin="round">',
    '<ellipse cx="95" cy="115" rx="73" ry="25" fill="url(#softLight)"/>',
    polygon('36,103 94,125 155,103 97,80','url(#floor)',A,1.5),
    polygon('54,94 96,109 140,94 96,79',C['surfaceDeep'],C['steel'],1.8),
    polygon('51,35 133,15 133,84 51,104','url(#face)',A,2.2),
    polygon('51,35 58,39 58,96 51,104',C['steel']),
    path('M 79 51 L 67 64 L 79 73',stroke=A,width=4),
    path('M 109 41 L 119 48 L 109 62',stroke=A,width=4),
    path('M 101 38 L 87 79',stroke=A,width=4),
    path('M 45 111 L 94 127 L 147 110',stroke=A,width=2.1,extra='opacity=".65"'),'</g>'])

def cuboid(x,y,r=23):
    # x,y top centre and 3 visible faces
    return ''.join([
      polygon(f'{x},{y} {x+r},{y+r*.48} {x},{y+r*.98} {x-r},{y+r*.48}', 'url(#face)',C['aquaHighlight'],1.2),
      polygon(f'{x-r},{y+r*.48} {x},{y+r*.98} {x},{y+r*2.0} {x-r},{y+r*1.5}', 'url(#metal)',C['edge'],1.3),
      polygon(f'{x},{y+r*.98} {x+r},{y+r*.48} {x+r},{y+r*1.5} {x},{y+r*2.0}', 'url(#floor)',A,1.6),
      path(f'M {x} {y+r*.98} V {y+r*2}',stroke=A,width=.75,extra='opacity=".7"')])

def icon_distributed():
    p=['<g>','<ellipse cx="95" cy="117" rx="76" ry="26" fill="url(#softLight)"/>']
    p += [path('M 95 76 L 49 103 M 95 76 L 141 103',stroke=A,width=2,extra='opacity=".65"')]
    p += [cuboid(95,19,24),cuboid(52,79,22),cuboid(138,79,22)]
    p += ['</g>']
    return ''.join(p)

def gear_path(cx,cy,ro=17,ri=12,teeth=10):
    import math
    pts=[]
    for i in range(teeth*4):
        a=-math.pi/2+2*math.pi*i/(teeth*4)
        r=ro if i%4 in (0,1) else ri
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    return 'M '+' L '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+' Z'

def practice_icon(id):
    if id=='automation': return path(gear_path(30,30),A,C['surfaceDeep'],2.5)+f'<circle cx="30" cy="30" r="6" stroke="{A}" stroke-width="2.6" fill="none"/>'
    if id=='observability': return (path('M 13 10 H 48 V 50 H 13 Z',C['aquaHighlight'],C['surfaceDeep'],1.6)+path('M 17 41 L 25 30 L 33 35 L 40 21 L 47 18',A,width=2.5))
    if id=='production-engineering': return ''.join([
      polygon('30,11 46,19 30,28 14,19','url(#face)',A,1.5),
      polygon('30,25 49,34 30,44 11,34','none',A,2),
      polygon('30,36 49,45 30,54 11,45','none',A,2),
    ])
    raise ValueError(id)

def icon_svg(name, inner):
    return svg_open(190,155,name)+f'<rect x="0" y="0" width="190" height="155" fill="none"/>'+inner+'</svg>'

def pod_asset(w=386,h=353):
    d=f'M 24 2 H {w-36} L {w-2} 34 V {h-34} L {w-35} {h-2} H 2 V 22 Z'
    return ''.join([
        path(d,stroke='url(#edgeGrad)',fill='url(#pod)',width=1.8),
        path('M 2 37 V 22 L 24 2 H 112',stroke=A,width=3),
        path(f'M {w-105} {h-2} H {w-35} L {w-2} {h-34}',stroke=A,width=9,extra='filter="url(#glow)" opacity=".8"'),
        path(f'M {w-105} {h-2} H {w-35} L {w-2} {h-34}',stroke=A,width=3.8),
        path('M 3 134 V 220',stroke=C['aquaHighlight'],width=.7,extra='opacity=".35"')
    ])

def make_section(background: bool):
    w, h = 1280, 685
    p = [svg_open(w, h, 'Engineering Focus — Applied AI Systems, Backend Engineering, Distributed & Reliable Platforms')]
    if background:
        p.append(f'<rect width="{w}" height="{h}" fill="#070B0C"/>')
    else:
        p.append('<g id="background-alpha" opacity="1"><rect x="0" y="0" width="1280" height="685" fill="none"/></g>')
    # Heading area with no enclosing box
    p += ['<g id="heading">',
          f'<rect x="20" y="24" width="5" height="54" rx="2" fill="{A}"/>',
          text(44, 54, 'Engineering', 44, C['text'], 800),
          text(338, 54, 'Focus', 44, A, 800),
          text(46, 88, DATA['section']['subtitle'], 23, C['textSecondary'], 400),
          '</g>']
    # Card geometry
    positions = [(20, 138), (447, 138), (874, 138)]
    for i, pillar in enumerate(DATA['pillars']):
        x, y = positions[i]
        p.append(f'<g id="pillar-{pillar["id"]}" transform="translate({x},{y})">')
        p.append(pod_asset(386, 353))
        p.append(f'<g transform="translate(100,14)">{[icon_ai(),icon_backend(),icon_distributed()][i]}</g>')
        title_lines = pillar['titleLines']; ty = 196 if len(title_lines) == 2 else 211
        for j, ln in enumerate(title_lines):
            p.append(text(193, ty + j * 34, ln, 30, C['text'], 760, 'middle'))
        p.append(f'<rect x="169" y="257" width="48" height="4" rx="2" fill="{A}"/>')
        for j, ln in enumerate(pillar['descriptionLines']):
            p.append(text(193, 287 + j * 23, ln, 19, C['textSecondary'], 400, 'middle', family='mono'))
        p.append('</g>')
    # Practice heading with no enclosing box
    p += ['<g id="practice-heading">',
        text(20, 544, '//', 28, A, 700, family='mono'),
        text(68, 544, 'Enabling Practices', 27, C['text'], 600),
        path('M 312 534 H 1248', C['steel'], width=1.2, extra='opacity=".6"'),
        f'<circle cx="1254" cy="534" r="3" fill="{A}"/>', '</g>']
    pills = [(23, 584, 366), (452, 584, 366), (880, 584, 378)]
    for i, practice in enumerate(DATA['practices']):
        x, y, pw = pills[i]
        p.append(f'<g id="practice-{practice["id"]}" transform="translate({x},{y})">')
        p.append(pill_frame(pw, 66))
        p.append(f'<g transform="translate(18,4) scale(.88)">{practice_icon(practice["id"])}</g>')
        p.append(text((225 if practice['id'] == 'production-engineering' else pw / 2 + 8), 43, practice['label'], (21 if practice['id'] == 'production-engineering' else 24), C['text'], 650, 'middle'))
        p.append('</g>')
    p.append('</svg>')
    return '\n'.join(p)

def make_separator():
    p = [svg_open(1280, 56, 'Terminal section divider: engineering-focus')]
    p += [
      '<rect width="1280" height="56" fill="#070B0C"/>',
      text(20, 38, 'naresh@github:~$', 24, A, 700, family='mono'),
      text(310, 38, 'engineering-focus', 24, C['text'], 400, family='mono'),
      path('M 580 30 H 1248', C['steel'], width=1.3, extra='opacity=".7"'),
      f'<circle cx="1254" cy="30" r="3" fill="{A}"/>',
      '</svg>']
    return '\n'.join(p)

def make_frame():
    return svg_open(386,353,'Titanium Hacker pillar pod frame')+pod_asset()+'</svg>'

def make_pill():
    return svg_open(360,66,'Titanium Hacker enabling-practice pill frame')+pill_frame(360,66)+'</svg>'

def main():
    (OUT/'icons').mkdir(parents=True,exist_ok=True)
    (OUT/'frames').mkdir(parents=True,exist_ok=True)
    assets={
        OUT/'engineering-focus-dark.svg':make_section(True),
        OUT/'engineering-focus-transparent.svg':make_section(False),
        OUT/'section-command.svg':make_separator(),
        OUT/'frames'/'pillar-pod.svg':make_frame(),
        OUT/'frames'/'practice-pill.svg':make_pill(),
        OUT/'icons'/'applied-ai-systems.svg':icon_svg('Applied AI Systems chip layers',icon_ai()),
        OUT/'icons'/'backend-engineering.svg':icon_svg('Backend Engineering code console',icon_backend()),
        OUT/'icons'/'distributed-reliable-platforms.svg':icon_svg('Distributed and Reliable Platforms cubes',icon_distributed()),
    }
    for k in ['automation','observability','production-engineering']:
        assets[OUT/'icons'/f'{k}.svg']=svg_open(60,60,f'{k} icon')+practice_icon(k)+'</svg>'
    for path_, content in assets.items():
        path_.write_text(content,encoding='utf-8')
        print('Wrote',path_.relative_to(ROOT),round(len(content)/1024,1),'KB')

if __name__=='__main__':
    main()
