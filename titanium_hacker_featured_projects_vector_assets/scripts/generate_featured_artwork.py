#!/usr/bin/env python3
"""Editable, alpha-transparent vector illustrations for GitHub Featured Projects.

No browser runtime, JS, remote fonts, or external images are needed. Uses a
central theme if the script is installed into Phoenixarjun/Phoenixarjun.

    python scripts/generate_featured_artwork.py
    python scripts/generate_featured_artwork.py --theme titanium-hacker

Optional PNG previews require CairoSVG, only for validation and convenience.
"""
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/projects'
FALLBACK = {
    'base':'#0C0F10', 'surface':'#1B2328', 'surface2':'#253139',
    'stroke':'#42535C', 'accent':'#B6FF3B', 'secondary':'#8EADB6',
    'text':'#EEF7EF', 'muted':'#A6B6B2'
}


def palette(theme_key=None):
    central = ROOT / 'design/themes.json'
    if central.exists():
        data = json.loads(central.read_text(encoding='utf-8'))
        key = theme_key or data.get('active', 'titanium-hacker')
        if key not in data['presets']:
            raise ValueError('Unknown theme: '+key)
        t = dict(FALLBACK)
        t.update(data['presets'][key]); return t, key
    external = ROOT / 'config/featured-art-theme-fallback.json'
    if external.exists():
        d=json.loads(external.read_text(encoding='utf-8'))
        t=dict(FALLBACK);t.update(d.get('colors',d));return t,theme_key or 'titanium-hacker'
    return dict(FALLBACK),theme_key or 'titanium-hacker'


def esc(s): return html.escape(str(s),quote=True)
def fmt(x): return f'{x:.2f}'.rstrip('0').rstrip('.') if isinstance(x,float) else str(x)

def rect(x,y,w,h,*,fill='none',stroke='none',sw=1,r=0,extras=''):
    return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extras}/>'

def path(d,*,stroke='none',fill='none',sw=1,extras=''):
    return f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extras}/>'

def circ(x,y,r,*,fill='none',stroke='none',sw=1,extras=''):
    return f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extras}/>'

def txt(x,y,value,*,size=17,color=None,weight=500,anchor=None,mono=False,spacing=None,extras=''):
    family='JetBrains Mono, DejaVu Sans Mono, Consolas, monospace' if mono else 'Inter, DejaVu Sans, Segoe UI, sans-serif'
    a=f' text-anchor="{anchor}"' if anchor else ''
    a+=f' letter-spacing="{spacing}"' if spacing is not None else ''
    return f'<text x="{fmt(x)}" y="{fmt(y)}" fill="{color}" font-size="{size}" font-weight="{weight}" font-family="{family}"{a} {extras}>{esc(value)}</text>'


def defs(t):
    a,s,tx=t['accent'],t['stroke'],t['text']
    return f'''<defs>
      <linearGradient id="nodeFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['surface2']}" stop-opacity=".94"/>
        <stop offset="100%" stop-color="{t['surface']}" stop-opacity=".88"/>
      </linearGradient>
      <linearGradient id="limeEdge" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="{s}" stop-opacity=".6"/>
        <stop offset="62%" stop-color="{a}" stop-opacity=".9"/>
        <stop offset="100%" stop-color="{s}" stop-opacity=".6"/>
      </linearGradient>
      <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{a}" stop-opacity="0"/>
        <stop offset=".48" stop-color="{a}" stop-opacity=".84"/>
        <stop offset="1" stop-color="{a}" stop-opacity="0"/>
      </linearGradient>
      <filter id="softGlow" x="-85%" y="-85%" width="270%" height="270%">
        <feGaussianBlur stdDeviation="5" />
      </filter>
      <filter id="subtleGlow" x="-85%" y="-85%" width="270%" height="270%">
        <feGaussianBlur stdDeviation="2.4" />
      </filter>
      <pattern id="quietDots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="3" cy="3" r=".85" fill="{s}" opacity=".42" />
      </pattern>
    </defs>'''


def svg(w,h,label,body,t,*,with_defs=True):
    return '\n'.join([f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">',
                      '<title>'+esc(label)+'</title>',defs(t) if with_defs else '',body,'</svg>'])+'\n'


def node(t,x,y,w,h,*,selected=False,r=13):
    stroke=t['accent'] if selected else t['secondary']
    return '\n'.join([
        rect(x,y,w,h,fill='url(#nodeFill)',stroke=stroke,sw=2.3 if selected else 1.8,r=r),
        path(f'M {x+12} {y+3} H {x+w-12}',stroke=t['text'] if not selected else t['accent'],sw=.65,extras='opacity=".19"'),
        path(f'M {x+8} {y+h-4} H {x+w-8}',stroke=t['accent'],sw=1.3,extras=f'opacity="{.4 if selected else .1}"'),
    ])


def connected_arrow(t,x1,y,x2,*,accent=False):
    c=t['accent'] if accent else t['text']
    return path(f'M {fmt(x1)} {fmt(y)} H {fmt(x2)} M {fmt(x2-7)} {fmt(y-6)} L {fmt(x2)} {fmt(y)} L {fmt(x2-7)} {fmt(y+6)}',stroke=c,sw=2.2,extras='opacity=".82"')


def icon_layer(t,x,y):
    c=t['accent']; steel=t['secondary']
    return '\n'.join([path(f'M{x} {y-12} l16 8 -16 8 -16 -8 Z',stroke=c,fill=t['surface'],sw=2),
     path(f'M{x-16} {y+2} l16 8 16 -8',stroke=steel,sw=1.6),path(f'M{x-16} {y+10} l16 8 16 -8',stroke=steel,sw=1.6)])


def icon_grid(t,x,y):
    return '\n'.join(rect(x+dx,y+dy,10,10,stroke=t['text'],sw=1.6,r=1.5) for dx in [0,14] for dy in [0,14])


def icon_hex(t,x,y):
    return path(f'M{x+13} {y} l12 7 v15 l-12 7 -12 -7 v-15 Z M{x+13} {y+14} l12 -7 M{x+13} {y+14} l-12 -7 M{x+13} {y+14} v15',stroke=t['text'],sw=1.5)


def icon_rect(t,x,y):return rect(x,y,29,22,stroke=t['text'],sw=1.8,r=2)


def aam(t):
    """AAM: exact visual vocabulary from reference—legend at left, layered topology at right."""
    s=[]
    # no outer fill; all outer pixels remain transparent
    # faint grid only as semi-transparent points to preserve readability
    for row in range(4):
        for col in range(9):
            s.append(circ(304+col*36,40+row*38,.7,fill=t['stroke'],extras='opacity=".22"'))
    # legend
    s.append(rect(15,15,185,205,fill=t['surface'],stroke=t['stroke'],sw=1.3,r=14,extras='fill-opacity=".77"'))
    s += [icon_layer(t,45,51),txt(77,55,'System',size=17,color=t['text'],weight=570),
          path('M34 77 H179',stroke=t['stroke'],extras='opacity=".55"'),
          icon_grid(t,34,92),txt(77,110,'Domain',size=17,color=t['text']),
          path('M34 127 H179',stroke=t['stroke'],extras='opacity=".55"'),
          icon_hex(t,27,137),txt(77,156,'Feature',size=17,color=t['text']),
          path('M34 176 H179',stroke=t['stroke'],extras='opacity=".55"'),
          icon_rect(t,34,188),txt(77,205,'Component',size=17,color=t['text'])]
    s.append(path('M220 25 V214',stroke=t['stroke'],sw=1.3))
    # topology edges behind nodes, top = 1; mid = 3; bottom = 6, faithful
    s.append(path('M480 62 V84 M480 84 L352 111 M480 84 L480 111 M480 84 L608 111',stroke=t['secondary'],sw=2.1,extras='opacity=".86"'))
    for mid,low1,low2 in [(352,300,366),(480,447,513),(608,594,660)]:
        s.append(path(f'M {mid} 136 V156 M {mid} 156 L {low1} 174 M {mid} 156 L {low2} 174',stroke=t['secondary'],sw=1.9,extras='opacity=".85"'))
    # luminous lime vertical focus path
    s.append(path('M480 62 V84 M480 84 V110',stroke=t['accent'],sw=2,extras='opacity=".58"'))
    s.append(path('M480 62 V84 M480 84 V110',stroke=t['accent'],sw=7,extras='opacity=".35" filter="url(#softGlow)"'))
    def smallbox(cx,cy,selected=False,w=52,h=27):
        s.append(rect(cx-w/2,cy-h/2,w,h,r=6,fill='url(#nodeFill)',stroke=t['accent'] if selected else t['secondary'],sw=2.5 if selected else 1.9))
        if selected:s.append(rect(cx-w/2+3,cy-h/2+3,w-6,h-6,r=4,stroke=t['accent'],extras='opacity=".25"'))
    smallbox(480,42,True,60,27)
    for mid in [352,480,608]:smallbox(mid,124,mid==480,53,30)
    for bottom in [300,366,447,513,594,660]:smallbox(bottom,187,bottom==594,35,26)
    # visual accent below central cluster
    s.append(path('M450 224 H510',stroke=t['accent'],sw=1.4,extras='opacity=".35"'))
    return svg(710,236,'Architecture-as-Memory — architecture topology (System, Domain, Feature, Component)', '\n'.join(s),t)


def promptnova(t):
    s=[]
    # Dots and bright curve go behind four nodes
    for y in range(27,221,24):
        for x in range(30,710,28):
            s.append(circ(x,y,.85,fill=t['stroke'],extras='opacity=".18"'))
    curve='M 0 154 C 75 200, 129 213, 200 153 S 317 73, 400 98 S 517 190, 603 156 S 692 150, 710 140'
    s.append(path(curve,stroke=t['accent'],sw=15,extras='opacity=".28" filter="url(#softGlow)"'))
    s.append(path(curve,stroke=t['accent'],sw=2.7,extras='opacity=".92"'))
    xys=[(54,66),(225,66),(396,66),(567,66)]
    labels=['Intent','Refine','Evaluate','Output']
    for i,(x,y) in enumerate(xys):
        s.append(node(t,x,y,91,110,selected=i==2,r=13))
        s.append(txt(x+45.5,y+94,labels[i],size=16,color=t['text'],weight=650,anchor='middle'))
        if i<3:s.append(connected_arrow(t,x+104,y+55,x+156))
    # input speech bubble
    s.append(rect(81,90,38,28,r=7,stroke=t['text'],sw=2))
    s.append(path('M89 118 L86 125 L99 118',stroke=t['text'],sw=1.8))
    for x in [92,100,108]:s.append(circ(x,104,1.5,fill=t['text']))
    # sliders with adjustable knobs
    for dy,pos in [(94,257),(109,269),(124,251)]:
        s.append(path(f'M244 {dy} H296',stroke=t['text'],sw=1.7))
        s.append(circ(pos,dy,4,fill=t['surface2'],stroke=t['text'],sw=1.4))
    # evaluation bars
    s.append(path('M418 122 V109 H430 V122 M435 122 V99 H447 V122 M452 122 V90 H464 V122',stroke=t['accent'],sw=4.4))
    # output sparkle
    s.append(path('M612 88 L619 104 L636 111 L619 118 L612 134 L605 118 L589 111 L605 104 Z',stroke=t['text'],sw=1.75))
    return svg(710,236,'PromptNova — intent to refinement, evaluation and output workflow', '\n'.join(s),t)


def telecom_icon(t,cx,cy):
    parts=[path(f'M {cx} {cy+31} L {cx} {cy-14} M {cx-15} {cy+31} L {cx} {cy-14} L {cx+15} {cy+31} M {cx-15} {cy+31} H {cx+15}',stroke=t['text'],sw=1.9)]
    for radius in [20,32]:
        parts.append(path(f'M {cx-radius*.65:.1f} {cy-radius*.7:.1f} Q {cx-radius*1.04:.1f} {cy:.1f} {cx-radius*.65:.1f} {cy+radius*.7:.1f} M {cx+radius*.65:.1f} {cy-radius*.7:.1f} Q {cx+radius*1.04:.1f} {cy:.1f} {cx+radius*.65:.1f} {cy+radius*.7:.1f}',stroke=t['accent'],sw=2.4))
    parts.append(circ(cx,cy-14,3,fill=t['accent']))
    return '\n'.join(parts)


def invoice_icon(t,x,y):
    return '\n'.join([path(f'M{x-14} {y-19} H{x+10} L{x+16} {y-13} V{y+22} H{x-14} Z',stroke=t['text'],sw=1.7),
     path(f'M{x+10} {y-19} V{y-12} H{x+16} M{x-6} {y-5} H{x+8} M{x-6} {y+3} H{x+8} M{x-6} {y+11} H{x+2}',stroke=t['text'],sw=1.4)])

def payment_icon(t,x,y):
    return '\n'.join([rect(x-19,y-14,38,27,r=4,stroke=t['text'],sw=1.8),path(f'M{x-17} {y-5} H{x+17} M{x+3} {y+6} H{x+13}',stroke=t['text'],sw=1.7)])

def database_icon(t,x,y):
    return '\n'.join([f'<ellipse cx="{x}" cy="{y-14}" rx="17" ry="7" fill="none" stroke="{t["accent"]}" stroke-width="2"/>',
     path(f'M{x-17} {y-14} V{y+16} C{x-17} {y+26} {x+17} {y+26} {x+17} {y+16} V{y-14} M{x-17} {y-3} C{x-17} {y+7} {x+17} {y+7} {x+17} {y-3} M{x-17} {y+8} C{x-17} {y+18} {x+17} {y+18} {x+17} {y+8}',stroke=t['accent'],sw=1.8)])

def dashboard_icon(t,x,y):
    return '\n'.join([rect(x-26,y-21,52,42,r=3,stroke=t['text'],sw=1.6),
     path(f'M{x-26} {y+12} H{x+26} M{x} {y+12} V{y+20}',stroke=t['text'],sw=1.4),
     path(f'M{x-16} {y+6} V{y-1} H{x-11} V{y+6} M{x-6} {y+6} V{y-10} H{x-1} V{y+6} M{x+4} {y+6} V{y-15} H{x+9} V{y+6}',stroke=t['accent'],sw=1.7)])

def gear_icon(t,x,y):
    p=[]
    n=12;points=[]
    for i in range(n*2):
        a=-math.pi/2+i*math.pi/n;r=12 if i%2==0 else 10
        points.append(f'{x+math.cos(a)*r:.2f},{y+math.sin(a)*r:.2f}')
    p.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="{t["accent"]}" stroke-width="2"/>')
    p.append(circ(x,y,4,stroke=t['accent'],sw=1.5))
    return ''.join(p)


def credflow(t):
    s=[]
    for y in range(26,218,23):
        for x in range(35,710,32):s.append(circ(x,y,.7,fill=t['stroke'],extras='opacity=".15"'))
    # thin vertical separators like reference
    s.append(path('M116 44 V188 M626 44 V188',stroke=t['secondary'],sw=1.2,extras='opacity=".46"'))
    s.append(telecom_icon(t,55,104))
    s.append(txt(55,194,'Telecom',size=16,color=t['text'],anchor='middle'))
    config=[(158,'Invoice'),(292,'Payment'),(426,'Collection')]
    for i,(x,label) in enumerate(config):
        s.append(node(t,x,50,103,100,selected=(i==2),r=13))
        s.append(txt(x+51,138,label,size=15.5,color=t['text'],weight=630,anchor='middle'))
    s.append(invoice_icon(t,209,94))
    s.append(payment_icon(t,343,91))
    s.append(database_icon(t,477,94))
    # dashboard no node frame, as reference
    s.append(dashboard_icon(t,669,89))
    s.append(txt(668,159,'Ops',size=16,color=t['text'],anchor='middle'))
    s.append(txt(668,180,'Dashboard',size=14,color=t['text'],anchor='middle'))
    s.append(connected_arrow(t,112,100,143))
    s.append(connected_arrow(t,268,100,278))
    s.append(connected_arrow(t,402,100,412))
    s.append(connected_arrow(t,541,100,634))
    # Rules engine loop under row, dashed circuit lines + arrowheads
    s.append(path('M 211 151 V 195 H 301 M 213 164 L 211 151 L 203 160',stroke=t['text'],sw=1.6,extras='stroke-dasharray="5 5" opacity=".8"'))
    s.append(path('M 555 195 H 477 V 152 M 469 161 L 477 152 L 484 161',stroke=t['text'],sw=1.6,extras='stroke-dasharray="5 5" opacity=".8"'))
    s.append(rect(275,176,320,46,r=11,fill='url(#nodeFill)',stroke=t['secondary'],sw=1.55))
    s.append(gear_icon(t,300,198))
    s.append(txt(455,203,'Dunning Rules (Automated)',size=14.5,color=t['text'],weight=600,anchor='middle'))
    return svg(710,236,'CredFlow — telecom invoice, payment, collection, dashboard and dunning rules', '\n'.join(s),t)


def dots(t):
    s=[]
    # deliberate sparse regular technical grid, with emphasis at bottom-right and some green dots
    for row in range(5):
        for col in range(12):
            x=22+col*25;y=18+row*25
            shine=((row*5+col*7)%9==0 or col in (9,10) and row in (1,2))
            opacity = .15 + .06*row + (.16 if shine else 0)
            r=1.9 if shine else 1.25
            s.append(circ(x,y,r,fill=t['accent'] if shine else t['stroke'],extras=f'opacity="{opacity:.2f}"'))
    return svg(328,144,'Subtle technical dot grid — transparent accent for Featured Projects header', '\n'.join(s),t)


def slashes(t):
    c=t['accent'];s=[]
    for i in range(3):
        x=12+27*i
        s.append(path(f'M {x+16} 5 H {x+32} L {x+15} 26 H {x-1} Z',fill=c if i==2 else t['secondary'],extras=f'opacity="{.95 if i==2 else .50}"'))
    return svg(116,34,'Triple titanium accent slashes', ''.join(s),t)


def frame(t):
    w,h=1160,224
    s=[]
    d='M 28 3 H 1135 L 1157 26 V 191 L 1131 221 H 21 L 3 197 V 28 Z'
    s.append(path(d,fill='url(#nodeFill)',stroke=t['secondary'],sw=1.55,extras='fill-opacity=".48"'))
    s.append(path('M 3 72 V 28 L 28 3 H 113',stroke=t['accent'],sw=3.5))
    s.append(path('M 1060 221 H 1131 L 1157 191 V 157',stroke=t['accent'],sw=9,extras='filter="url(#softGlow)" opacity=".46"'))
    s.append(path('M 1060 221 H 1131 L 1157 191 V 157',stroke=t['accent'],sw=2.6))
    s.append(path('M 19 192 H 382',stroke=t['stroke'],sw=.8,extras='opacity=".20"'))
    return svg(w,h,'Transparent-canvas titanium project row frame with bevel and two corner accents', '\n'.join(s),t)


def header(t):
    # lightweight separator with no opaque background
    s=[path('M 10 14 L 24 26 L 10 38',stroke=t['accent'],sw=4),
       txt(46,32,'naresh@github:~$',size=20,color=t['accent'],mono=True,weight=700),
       txt(289,32,'ls --flagship-projects',size=20,color=t['text'],mono=True,weight=500),
       path('M 600 26 H 1130',stroke=t['stroke'],sw=1.25),
       circ(1138,26,3,fill=t['accent'])]
    return svg(1160,52,'Terminal heading for Featured Projects — transparent background', '\n'.join(s),t)


def write_all(t):
    outputs={
        'illustrations/aam-topology.svg':aam(t),
        'illustrations/promptnova-workflow.svg':promptnova(t),
        'illustrations/credflow-billing.svg':credflow(t),
        'decor/header-dot-field.svg':dots(t),
        'decor/triple-slashes.svg':slashes(t),
        'frames/project-row-frame.svg':frame(t),
        'decor/featured-projects-terminal.svg':header(t),
    }
    for rel,val in outputs.items():
        target=OUT / rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(val,encoding='utf-8')
    return outputs


def render_previews(outputs):
    try:
        import cairosvg
        from PIL import Image, ImageDraw, ImageFont
        import io
    except ImportError:
        print('Optional CairoSVG/Pillow not installed; skipping PNG previews')
        return
    prev=ROOT/'previews';prev.mkdir(parents=True,exist_ok=True)
    rendered={}
    for rel,svg_content in outputs.items():
        if rel.startswith('illustrations/') or rel=='decor/header-dot-field.svg':
            p=prev/(Path(rel).stem+'-transparent.png')
            png=cairosvg.svg2png(bytestring=svg_content.encode(),output_width=(1420 if rel.startswith('illustrations/') else 656))
            p.write_bytes(png)
            rendered[rel]=Image.open(io.BytesIO(png)).convert('RGBA')
            # show dark preview with pixel-perfect alpha compositing
            bg=Image.new('RGBA',rendered[rel].size,'#0C0F10');bg.alpha_composite(rendered[rel]); bg.convert('RGB').save(prev/(Path(rel).stem+'-dark-preview.png'))
    # composited three-panel preview using the actual source SVGs; no text raster source
    W,H=1520,960
    bg=Image.new('RGBA',(W,H),'#0C0F10')
    dr=ImageDraw.Draw(bg)
    try:
        ff='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        fm='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
        bold=ImageFont.truetype(ff,34);norm=ImageFont.truetype(ff,19);mono=ImageFont.truetype(fm,17)
    except Exception:
        bold=norm=mono=ImageFont.load_default()
    dr.text((42,23),'naresh@github:~$  ls --flagship-projects',fill='#B6FF3B',font=mono)
    dr.line((44,67,W-44,67),fill='#42535C',width=2)
    dr.text((42,88),'Featured Projects  /  Art Assets',fill='#EEF7EF',font=bold)
    dr.text((42,136),'Transparent vectors placed on a titanium background for visualization',fill='#A6B6B2',font=norm)
    labels=['01  Architecture-as-Memory','02  PromptNova','03  CredFlow']
    names=['aam-topology','promptnova-workflow','credflow-billing']
    for i,(name,label) in enumerate(zip(names,labels)):
        y=200+i*250
        dr.rounded_rectangle((40,y,W-40,y+231),radius=20,fill='#131B1C',outline='#42535C',width=2)
        dr.text((65,y+30),label,fill='#EEF7EF',font=bold)
        desc=['System → Domain → Feature → Component','Intent → Refine → Evaluate → Output','Telecom → Invoice → Payment → Collection → Operations'][i]
        dr.text((68,y+86),desc,fill='#A6B6B2',font=norm)
        im=rendered['illustrations/'+name+'.svg']
        # adjust composite dimension to fit preview row
        im.thumbnail((760,230),Image.Resampling.LANCZOS)
        bg.alpha_composite(im,(W-40-760,y+4))
        dr.text((68,y+168),'SVG + transparent PNG  •  Editable theme tokens',fill='#B6FF3B',font=mono)
    bg.convert('RGB').save(prev/'all-three-artworks-dark-preview.png')
    print('PNG previews written to',prev)


def main():
    p=argparse.ArgumentParser();p.add_argument('--theme',help='One of design/themes.json presets, if present')
    p.add_argument('--no-preview',action='store_true')
    args=p.parse_args()
    t,key=palette(args.theme)
    outputs=write_all(t)
    print(f'Wrote {len(outputs)} SVGs with active theme {key}')
    if not args.no_preview:render_previews(outputs)

if __name__=='__main__':main()
