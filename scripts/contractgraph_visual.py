"""ContractGraph directed verification-DAG illustration for the Titanium Hacker profile.
No external dependencies. Embed inside existing graphics.py's project_card() or export standalone SVG.
Illustrative topology, not a runtime trace. Theme supplied by design/themes.json.
"""
from __future__ import annotations
from html import escape


def graph_svg(theme: dict, is_light: bool = False, embedded: bool = False) -> str:
    t = theme if not is_light else {**theme, 'base':'#F4F7F8', 'surface':'#E9F0F3', 'surface2':'#DBE6EA', 'stroke':'#8CA4AB', 'accent':'#56890A', 'text':'#1B2A30', 'muted':'#4D666E', 'secondary':'#4D666E'}
    accent, stroke, text, muted = (t[k] for k in ['accent','stroke','text','muted'])
    bg = '#0B1315' if not is_light else '#EDF3F5'
    panel = '#172125' if not is_light else '#DCE7E9'
    faint = '#2D4249' if not is_light else '#9BAFB5'
    # Node lanes: contract source -> 3 scoped subagent tasks -> individual verifier gates -> finalizer.
    # Dashed return from verifier to node represents targeted repair, not a global rerun.
    parts = [
      f'<title>ContractGraph: compiled directed acyclic graph with independent verification gates</title>',
      '<desc>Illustrative graph with a contract input feeding three scoped agents, individual verification nodes, a targeted repair loop, and a final artifact.</desc>',
      '<defs><linearGradient id="cg-node-grad" x1="0" y1="0" x2="0" y2="1">'
      f'<stop stop-color="{t["surface2"]}"/><stop offset="1" stop-color="{panel}"/></linearGradient>'
      '<marker id="cg-arrow" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="'+accent+'" /></marker>'
      '<marker id="cg-muted-arrow" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="'+stroke+'" /></marker>'
      '<filter id="cg-soft-glow" x="-75%" y="-75%" width="250%" height="250%"><feGaussianBlur stdDeviation="2.3"/></filter></defs>',
      # small top-left notation and graph index
      f'<text x="14" y="23" font-family="DejaVu Sans Mono, monospace" font-size="9" letter-spacing="1.4" fill="{muted}">CONTRACT / DAG</text>',
      f'<circle cx="324" cy="19" r="2.5" fill="{accent}"/><text x="315" y="22" font-family="DejaVu Sans Mono, monospace" font-size="8" text-anchor="end" fill="{muted}">VALIDATED</text>',
      f'<line x1="14" y1="30" x2="334" y2="30" stroke="{stroke}" stroke-opacity=".45"/>',
    ]
    # Connections: use right-angle routing to distinguish a DAG from a decorative architecture hierarchy.
    for y in (53,93,133):
        parts.append(f'<path d="M 80 94 H 93 V {y} H 114" fill="none" stroke="{stroke}" stroke-width="1.1" stroke-opacity=".95"/>')
        parts.append(f'<path d="M 161 {y} H 196" fill="none" stroke="{accent}" stroke-width="1.6" marker-end="url(#cg-arrow)" opacity=".85"/>')
        parts.append(f'<path d="M 235 {y} H 252 V 93 H 285" fill="none" stroke="{stroke}" stroke-width="1.1" opacity=".95"/>')
    # dotted loop denotes scoped repair of the middle agent only
    parts.extend([
      f'<path d="M 197 108 V 119 H 163" fill="none" stroke="{accent}" stroke-width="1.2" stroke-dasharray="3.5 3.5" marker-end="url(#cg-arrow)"/>',
      f'<text x="178" y="130" text-anchor="middle" font-size="8.5" font-family="DejaVu Sans Mono, monospace" fill="{muted}">REPAIR</text>',
    ])
    # source hex node
    parts.extend([
       f'<path d="M 18 69 L 70 69 L 82 81 L 82 105 L 70 117 H 18 L 9 105 V 81 Z" fill="{panel}" stroke="{accent}" stroke-width="1.6"/>',
       f'<path d="M 21 78 H 57 M 21 83 H 51 M 21 88 H 60" stroke="{accent}" stroke-width="1.6" opacity=".7"/>',
       f'<text x="45" y="105" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="10" font-weight="700" fill="{text}">SCHEMA</text>',
    ])
    # agent nodes and verification gates
    labels = [('N1',53),('N2',93),('N3',133)]
    for num,y in labels:
        parts.append(f'<rect x="114" y="{y-15}" width="47" height="30" rx="5" fill="url(#cg-node-grad)" stroke="{stroke}" stroke-width="1.05"/>')
        parts.append(f'<text x="137.5" y="{y+3.5}" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="12" font-weight="700" fill="{text}">{num}</text>')
        parts.append(f'<rect x="197" y="{y-13}" width="39" height="26" rx="6" fill="{panel}" stroke="{accent}" stroke-width="1.2"/>')
        parts.append(f'<path d="M 208 {y} l 4 4 l 9 -9" fill="none" stroke="{accent}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')
    # right side finalizer
    parts += [
       f'<path d="M 289 72 H 325 L 335 82 V 105 L 325 115 H 289 L 280 105 V 82 Z" fill="{accent}" fill-opacity="0.14" stroke="{accent}" stroke-width="1.4"/>',
       f'<text x="307.5" y="92" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="11" font-weight="700" fill="{text}">FINAL</text>',
       f'<text x="307.5" y="104" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="8" fill="{accent}">✓ OK</text>',
       f'<text x="14" y="157" font-family="DejaVu Sans Mono, monospace" font-size="9" fill="{muted}">SCOPED AGENTS</text>',
       f'<text x="199" y="157" font-family="DejaVu Sans Mono, monospace" font-size="9" fill="{muted}">GATES</text>',
    ]
    xattr = ' x="776" y="24"' if embedded else ''
    # Keep outer background transparent; existing project card draws framed container.
    return f'<svg xmlns="http://www.w3.org/2000/svg"{xattr} width="348" height="168" viewBox="0 0 348 168" role="img">'+''.join(parts)+'</svg>'
