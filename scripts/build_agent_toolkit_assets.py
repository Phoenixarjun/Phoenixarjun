#!/usr/bin/env python3
"""Generate ONLY the original Agent Toolkit artwork, not third-party tech logos.

All SVG canvases have transparent backgrounds; palette derives from design/themes.json
if present in the host GitHub profile repo, otherwise bundle fallback.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets' / 'agent-toolkit'
DEST.mkdir(parents=True, exist_ok=True)
DEFAULT = {'base':'#0C0F10','surface':'#1B2328','surface2':'#253139','stroke':'#42535C','accent':'#B6FF3B','secondary':'#8EADB6','text':'#EEF7EF','muted':'#A6B6B2'}

def read_theme():
    tf = ROOT / 'design' / 'themes.json'
    if tf.exists():
        data=json.loads(tf.read_text(encoding='utf-8'))
        active = data['active']
        if active not in data['presets']:
            raise ValueError(f'Unknown theme {active}')
        return {**DEFAULT,**data['presets'][active]}
    return DEFAULT
T=read_theme()
A=T['accent']; S=T['stroke']; M=T['surface']; D=T['base']; W=T['text']; SUB=T['secondary']

def defs():
    return f'''<defs>
    <linearGradient id="top" x1="0" y1="0" x2=".9" y2="1"><stop offset="0" stop-color="{SUB}" stop-opacity=".75"/><stop offset=".46" stop-color="{M}"/><stop offset="1" stop-color="{D}"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{A}" stop-opacity=".82"/><stop offset="1" stop-color="{S}"/></linearGradient>
    <radialGradient id="halo"><stop stop-color="{A}" stop-opacity=".27"/><stop offset=".46" stop-color="{A}" stop-opacity=".07"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>
    <filter id="soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="micro-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.6"/></filter>
    </defs>'''

def root(w,h,name,body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(name,quote=True)}">'
      +f'<title>{html.escape(name)}</title>'+defs()+body+'</svg>')

def diamond(cx,cy,rx,ry,thick,fill,edge):
    pts=f'{cx},{cy-ry} {cx+rx},{cy} {cx},{cy+ry} {cx-rx},{cy}'
    body=f'<polygon points="{pts}" fill="{fill}" stroke="{edge}" stroke-width="2" stroke-linejoin="round"/>'
    body+=f'<path d="M {cx-rx} {cy} L {cx} {cy+ry} L {cx+rx} {cy} v {thick} L {cx} {cy+ry+thick} L {cx-rx} {cy+thick} Z" fill="{M}" stroke="{edge}" stroke-width="2" stroke-linejoin="round"/>'
    return body

def stack_icon():
    out=[f'<ellipse cx="160" cy="183" rx="145" ry="63" fill="url(#halo)"/>']
    for y,scale in [(150,0.90),(122,0.96),(91,1.0)]:
        rx=100*scale; ry=39*scale
        # low-opacity glow around bottom edges
        out.append(f'<polyline points="{160-rx},{y+4} 160,{y+ry+15} {160+rx},{y+4}" stroke="{A}" stroke-width="7" opacity=".24" fill="none" filter="url(#soft-glow)"/>')
        out.append(diamond(160,y,rx,ry,11,'url(#top)',('url(#edge)' if y==91 else A)))
    # top plate code <> and slash deliberately vector-drawn
    out.append(f'<g fill="none" stroke="{A}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="M 128 86 L 114 96 L 128 106"/><path d="M 192 86 L 206 96 L 192 106"/>'
               '<path d="M 175 81 L 146 111"/></g>')
    out.append(f'<path d="M 66 173 L 160 211 L 254 173" fill="none" stroke="{A}" stroke-width="2" opacity=".55"/>')
    return root(320,260,'Agent Toolkit — stacked engineering playbooks logo, Titanium Hacker', ''.join(out))

def micro_frame():
    return f'''<rect x="14" y="14" width="100" height="100" rx="21" fill="{M}" fill-opacity=".82" stroke="{S}" stroke-width="2"/>
    <path d="M 14 38 V 34 Q 14 14 34 14 H 57" fill="none" stroke="{A}" stroke-width="2.2" opacity=".9"/>
    <path d="M 71 114 H 94 Q 114 114 114 94 V 72" fill="none" stroke="{A}" stroke-width="2.2" opacity=".9"/>
    <circle cx="64" cy="64" r="58" fill="url(#halo)"/>'''

def intent():
    b=micro_frame()+f'''<g fill="none" stroke="{A}" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="64" cy="64" r="24" stroke-width="4"/>
      <circle cx="64" cy="64" r="9" stroke-width="3"/>
      <path d="M 64 28 V 46 M 64 82 V 100 M 28 64 H 46 M 82 64 H 100" stroke-width="4"/>
      <path d="M 61 64 L 64 59 L 67 64 L 64 69 Z" fill="{A}" stroke="none"/>
      </g>'''
    return root(128,128,'Intent Capture — target icon',b)

def implement():
    b=micro_frame()+f'''<g fill="none" stroke="{A}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 52 49 L 37 64 L 52 79"/><path d="M 76 49 L 91 64 L 76 79"/>
      <path d="M 70 43 L 58 85"/>
      </g>'''
    return root(128,128,'Implement — code brackets icon',b)

def verify():
    b=micro_frame()+f'''<path d="M 64 31 L 91 41 V 63 Q 91 82 64 99 Q 37 82 37 63 V 41 Z" fill="{D}" stroke="{A}" stroke-width="4" stroke-linejoin="round"/>
    <path d="M 51 65 L 61 75 L 79 56" fill="none" stroke="{A}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'''
    return root(128,128,'Verify — shield and check icon',b)

def workflow():
    # Reuse the exact vector path geometry via individual SVG files at composition time is
    # awkward across external file references. Compose icon bodies directly in <g> transforms.
    fragments=[intent(),implement(),verify()]
    def inner(svg):
        # everything between </defs> and </svg> 
        return svg.split('</defs>',1)[1].rsplit('</svg>',1)[0]
    body=[]
    for i,x in enumerate((25,259,493)):
        # unique IDs in shared defs not replicated inside g
        body.append(f'<g transform="translate({x},10) scale(1.0)">{inner(fragments[i])}</g>')
    for x in (166,400):
        body.append(f'<path d="M {x} 74 H {x+65}" stroke="{A}" stroke-width="3.5" stroke-linecap="round"/>')
        body.append(f'<path d="M {x+54} 65 L {x+65} 74 L {x+54} 83" fill="none" stroke="{A}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    for x,t in zip((89,323,557),('INTENT','IMPLEMENT','VERIFY')):
        body.append(f'<text x="{x}" y="167" text-anchor="middle" fill="{W}" font-family="JetBrains Mono,DejaVu Sans Mono,monospace" font-weight="650" font-size="18">{t}</text>')
    return root(670,183,'Agent Toolkit workflow: Intent, Implement, Verify', ''.join(body))

def small_motif():
    return root(320,62,'Agent Toolkit small technical accent',f'<path d="M 2 48 H 296 L 314 30" fill="none" stroke="{S}" stroke-width="2"/><path d="M 265 48 H 296 L 314 30" fill="none" stroke="{A}" stroke-width="3"/><circle cx="12" cy="48" r="3" fill="{A}"/>')

OUT={
    'agent-toolkit-emblem.svg':stack_icon(),
    'intent-capture.svg':intent(),
    'implement.svg':implement(),
    'verify.svg':verify(),
    'intent-implement-verify.svg':workflow(),
    'technical-accent.svg':small_motif(),
}

def build():
    for name,svg in OUT.items():
        path=DEST/name
        path.write_text(svg,encoding='utf-8')
        print(f'Created {path.relative_to(ROOT)} ({len(svg)} bytes)')
if __name__=='__main__':
    build()
