"""Deterministic, dependency-free SVG artwork for GitHub profile v2.

No external fonts, CSS, JavaScript or network-hosted assets are embedded.
All design colors come from design/themes.json through the selected theme dict.
"""
from __future__ import annotations

import calendar
import datetime as dt
import math
import random
import textwrap
from collections import defaultdict
from html import escape


def E(s: object) -> str:
    return escape(str(s), quote=True)


def txt(x, y, value, *, size=18, color='#fff', weight=400, mono=False, letter=None, anchor=None, opacity=None):
    attributes = f'x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"'
    attributes += ' font-family="Consolas,Menlo,monospace"' if mono else ' font-family="Segoe UI,Arial,sans-serif"'
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


def shell(w, h, theme, body, title, *, grid=True):
    t = theme
    pattern = '<rect width="100%" height="100%" fill="url(#dots)" opacity=".35"/>' if grid else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}">
<title>{E(title)}</title>
<defs>
  <linearGradient id="panelGradient" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['base']}"/>
    <stop offset="1" stop-color="{t['surface']}"/>
  </linearGradient>
  <linearGradient id="edgeGradient" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['accent']}" stop-opacity=".6"/>
    <stop offset="1" stop-color="{t['stroke']}" stop-opacity=".5"/>
  </linearGradient>
  <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r=".7" fill="{t['secondary']}" opacity=".38"/>
  </pattern>
</defs>
<rect width="{w}" height="{h}" rx="18" fill="url(#panelGradient)"/>
{pattern}
<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="17" fill="none" stroke="url(#edgeGradient)" stroke-width="2"/>
{body}
</svg>'''


def pill(x, y, label, theme, w=None, h=28, font=12):
    t = theme
    w = w or int(len(label)*7.6 + 28)
    return rect(x, y, w, h, t['surface2'], r=h/2, stroke=t['stroke']) + txt(x+w/2, y+h/2+4, label, size=font, color=t['text'], anchor='middle', mono=True)


def hero(profile, t):
    w, h = 1160, 360
    body = rect(28, 26, 4, h-52, t['accent'], r=2)
    body += txt(65, 62, 'PROFILE / IDENTITY', size=15, color=t['accent'], weight=700, mono=True, letter=2.6)
    body += txt(65, 132, profile['name'], size=63, color=t['text'], weight=750)
    body += txt(68, 183, profile['identity'], size=32, color=t['accent'], weight=650)
    body += txt(68, 221, profile['tagline'], size=20, color=t['text'])
    body += txt(68, 257, f"{profile['official_role']} @ {profile['employer']}  ·  {profile['location']}", size=15, color=t['muted'])
    x = 68
    for word in profile['focus']:
        width = len(word)*8+25
        body += pill(x, 286, word, t, width, 32, 12)
        x += width + 12
    body += line(720, 62, 720, 308, t['stroke'], 1.2, .6)
    # Architectural network drawing: intentionally decorative, not a claim about a deployed architecture.
    coords = [(772,111),(856,68),(955,101),(1046,72),(791,222),(880,183),(995,232),(1080,185)]
    edges = [(0,1),(1,2),(2,3),(0,4),(1,5),(2,5),(2,6),(3,7),(4,5),(5,6),(6,7)]
    for a,b in edges:
        ax,ay=coords[a];bx,by=coords[b]
        body += line(ax,ay,bx,by,t['stroke'],1.8,.85)
    for i,(cx,cy) in enumerate(coords):
        color = t['accent'] if i in (0,2,5,7) else t['secondary']
        body += f'<circle cx="{cx}" cy="{cy}" r="{15 if i==5 else 9}" fill="{t["surface"]}" stroke="{color}" stroke-width="2"/>'
        body += f'<circle cx="{cx}" cy="{cy}" r="{3 if i==5 else 2}" fill="{color}"/>'
    body += txt(755, 297, 'ENGINEERED FOR CLARITY', size=12, color=t['secondary'], mono=True, letter=1.2)
    return shell(w,h,t,body,f"{profile['name']} — {profile['identity']}")


def project_card(p, t, idx):
    w,h = 1160, 226
    body = rect(28, 30, 5, 166, t['accent'], r=2)
    body += txt(59, 54, f"{idx:02d} / {p['category'].upper()}", size=13, color=t['accent'], weight=700, mono=True, letter=1)
    body += txt(58, 107, p['name'], size=36, color=t['text'], weight=700)
    for k, content in enumerate(textwrap.wrap(p['description'], 79)[:2]):
        body += txt(60, 143+k*22, content, size=16, color=t['muted'])
    x=59
    for tag in p['technologies'][:4]:
        width=int(len(tag)*7.5+24)
        body += pill(x,182,tag,t,width,27,11)
        x+=width+8
    body += line(850, 38, 850, 192, t['stroke'], 1, .9)
    body += txt(877, 48, 'SYSTEM NODES', size=11, color=t['secondary'], mono=True, letter=1)
    # distinctive non-semantic topology visual; no invented benchmark
    nodes=[(913,88),(1033,75),(1090,127),(968,159),(1046,174)]
    for a,b in [(0,1),(1,2),(0,3),(3,4),(2,4),(1,4)]:
        ax,ay=nodes[a];bx,by=nodes[b];body+=line(ax,ay,bx,by,t['stroke'],2,.9)
    for j,(x,y) in enumerate(nodes):
        col=t['accent'] if j in [0,3] else t['secondary']
        body += rect(x-11,y-11,22,22,t['surface2'],r=5,stroke=col,sw=2)
        body += rect(x-3,y-3,6,6,col,r=2)
    return shell(w,h,t,body,p['name'])


def now_building(p,t):
    w,h=1160,208
    body = txt(60,48,'IN PROGRESS / REFINING',size=14,color=t['accent'],mono=True,weight=700,letter=1.6)
    body += txt(60,100,p['name'],size=40,color=t['text'],weight=750)
    body += txt(60,136,p['description'][:86],size=16,color=t['muted'])
    body += pill(60,156,p['status'].upper(),t,110,30,12)
    for i,name in enumerate(p['highlights'][:3]):
        x=812+i*106
        body+=rect(x,55,90,84,t['surface2'],r=10,stroke=t['stroke'])
        body+=rect(x+33,70,24,24,t['accent'] if i==1 else t['secondary'],r=7)
        body+=txt(x+45,118,str(i+1).zfill(2),size=16,color=t['text'],anchor='middle',mono=True)
        if i<2: body+=line(x+90,98,x+106,98,t['accent'],2)
    return shell(w,h,t,body,p['name'])


def stack_card(stack,t):
    w,h=1160,405
    body=txt(48,59,'ENGINEERING TOOLKIT',size=16,color=t['accent'],mono=True,weight=700,letter=2)
    body+=txt(48,96,'Tools behind the systems',size=28,color=t['text'],weight=700)
    domains=stack['domains']
    for i,d in enumerate(domains[:6]):
        col=i%3;row=i//3
        x=48+col*362;y=130+row*128
        body+=rect(x,y,337,113,t['surface2'],r=12,stroke=t['stroke'])
        body+=rect(x+14,y+16,5,16,t['accent'],r=2)
        body+=txt(x+29,y+29,d['name'].upper(),size=13,color=t['text'],weight=700,mono=True)
        vals=d['items']
        for j,v in enumerate(vals[:4]):
            vx=x+18+(j%2)*158;vy=y+60+(j//2)*23
            body+=f'<circle cx="{vx+3}" cy="{vy-5}" r="3" fill="{t["accent"]}"/>'
            body+=txt(vx+13,vy,v,size=13,color=t['muted'])
    return shell(w,h,t,body,'Engineering stack')


def _month_start(yr,month):
    return dt.date(yr,month,1)


def _months_ending(ending,months=12):
    yr,mo=ending.year,ending.month
    out=[]
    for offset in reversed(range(months)):
        serial=yr*12+(mo-1)-offset
        out.append((serial//12,(serial%12)+1))
    return out


def _tower(cx,cy,height,t,intensity):
    # Real isometric rectangular prism: both side faces are vertical and top face lies above.
    a=8.0; b=4.4
    top=[(cx,cy-height-b),(cx+a,cy-height),(cx,cy-height+b),(cx-a,cy-height)]
    right=[(cx+a,cy-height),(cx+a,cy),(cx,cy+b),(cx,cy-height+b)]
    left=[(cx-a,cy-height),(cx,cy-height+b),(cx,cy+b),(cx-a,cy)]
    # Capped/log-style scaling ensures rare spikes remain legible without flattening every other day.
    coltop=t['accent'] if intensity>1 else t['secondary']
    return poly(left,t['stroke'])+poly(right,t['surface2'])+poly(top,coltop)


def city(contrib,t):
    w,h=1160,703
    live = contrib.get('status') == 'ok' and bool(contrib.get('days'))
    if live:
        days={r['date']:int(r['count']) for r in contrib['days']}
        end=dt.date.fromisoformat(max(days))
        total=sum(days.values())
        active=sum(v>0 for v in days.values())
    else:
        # Strictly illustrative distribution, intentionally not presented as GitHub statistics.
        rng=random.Random(121)
        end=dt.date(2026,11,7)
        days={}
        for i in range(365):
            d=end-dt.timedelta(days=i)
            days[d.isoformat()]=(0 if rng.random()<.72 else rng.choice([1,2,3,4,5,7,12]))
        total=None;active=None
    body=txt(48,56,'CONTRIBUTION ATLAS',size=16,color=t['accent'],mono=True,letter=2,weight=700)
    body+=txt(48,95,'A year of building',size=31,color=t['text'],weight=750)
    if live:
        body+=txt(48,127,f'{total:,} contributions  ·  {active} active days  ·  GitHub GraphQL',size=15,color=t['muted'])
    else:
        body+=txt(48,127,'ILLUSTRATIVE GEOMETRY — SAMPLE DATA, NOT LIVE CONTRIBUTIONS',size=14,color=t['accent'],mono=True)
    months=_months_ending(end)
    for idx,(yr,mo) in enumerate(months):
        c=idx%4;r=idx//4
        px=45+c*278;py=152+r*174
        body+=rect(px,py,262,164,t['surface'],r=10,stroke=t['stroke'])
        body+=txt(px+16,py+26,f'{calendar.month_abbr[mo].upper()} {yr}',size=13,color=t['text'],mono=True,weight=700)
        month_total=sum(cnt for date_s,cnt in days.items() if date_s.startswith(f'{yr:04d}-{mo:02d}-'))
        body+=txt(px+246,py+26,(str(month_total)+' ACTIVITY') if live else 'PREVIEW',size=10,color=t['secondary'],mono=True,anchor='end')
        cal=calendar.Calendar(firstweekday=6).monthdatescalendar(yr,mo)
        cells=[]
        for week_idx,week in enumerate(cal):
            for weekday,date in enumerate(week):
                if date.month != mo: continue
                count=days.get(date.isoformat(),0)
                cells.append((week_idx,weekday,count))
        # Sort back-to-front so pillars do not clip one another.
        for col,row,count in sorted(cells,key=lambda x:(x[0]+x[1],x[0])):
            cx=px+141+(col-row)*11.3
            cy=py+79+(col+row)*5.9
            top=[(cx,cy-5.9),(cx+10.5,cy),(cx,cy+5.9),(cx-10.5,cy)]
            body+=poly(top, t['surface2'] if count==0 else t['stroke'],opacity=.9)
            if count:
                height=min(49,max(4,7*math.log2(count+1)))
                body+=_tower(cx,cy,height,t,2 if count>3 else 1)
    body+=line(48,681,1111,681,t['stroke'],1)
    if live:
        body+=txt(48,696,f'SOURCE: GitHub GraphQL  ·  UPDATED: {contrib.get("fetched_at_utc","unknown")}',size=10,color=t['muted'],mono=True)
    else:
        body+=txt(48,696,'SET GH_TOKEN AND RUN scripts/fetch_contributions.py TO REPLACE DEMO DATA',size=10,color=t['muted'],mono=True)
    return shell(w,h,t,body,'GitHub contribution atlas — live data' if live else 'Contribution atlas design preview — sample data')


def playground(t):
    w,h=1160,220
    body=txt(55,50,'DEVELOPER PLAYGROUND / CONCEPT ONLY',size=14,color=t['accent'],mono=True,weight=700,letter=1)
    body+=txt(55,99,'System Runner',size=41,color=t['text'],weight=750)
    body+=txt(55,134,'An optional playable micro-game will live on GitHub Pages.',size=17,color=t['muted'])
    body+=txt(55,169,'Not enabled in the README until a functional version exists.',size=15,color=t['secondary'])
    for i in range(12):
        x=795+(i%6)*50;y=60+(i//6)*55
        body+=rect(x,y,40,40,t['surface2'],r=7,stroke=t['accent'] if i in (1,4,8) else t['stroke'])
        if i in (1,4,8): body+=txt(x+20,y+26,'◆',size=20,color=t['accent'],anchor='middle')
    return shell(w,h,t,body,'System Runner playground concept')
