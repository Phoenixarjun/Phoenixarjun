#!/usr/bin/env python3
"""Generate dependency-free, reusable GitHub README About Me SVGs.

Standardized canvas width: 1160px (aligned with profile system geometry).
Dual-mode output: Dark and Light theme variants.
All design tokens align strictly with Titanium Hacker theme.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'sections'

def escape(s: str) -> str:
    return html.escape(s)

def generate_about_me_svg(theme: dict, is_light: bool = False, width: int = 1160) -> str:
    h = 645
    card_w = width - 12
    card_h = h - 12

    # Color palette
    if is_light:
        bg_canvas = "transparent"
        bg_card = "#FFFFFF"
        border_col = "#D0D7DE"
        accent_col = "#1A7F37"
        text_col = "#1F2328"
        text_secondary = "#57606A"
        text_muted = "#57606A"
        editor_bg = "#F6F8FA"
        editor_stroke = "#D0D7DE"
        gutter_border = "#D8DEE4"
        line_num_col = "#8C959F"
        badge_bg = "rgba(26, 127, 55, 0.08)"
        badge_border = "rgba(26, 127, 55, 0.25)"
        pill_card_bg = "#F6F8FA"
        pill_card_stroke = "#D0D7DE"
        dot_col = "#656D76"
    else:
        bg_canvas = "transparent"
        bg_card = "#0C0F10"
        border_col = "#253139"
        accent_col = "#B6FF3B"
        text_col = "#EEF7EF"
        text_secondary = "#8EADB6"
        text_muted = "#7B96A0"
        editor_bg = "#0D1316"
        editor_stroke = "#222E35"
        gutter_border = "#25353D"
        line_num_col = "#4C626C"
        badge_bg = "rgba(182, 255, 59, 0.08)"
        badge_border = "rgba(182, 255, 59, 0.25)"
        pill_card_bg = "#0E1519"
        pill_card_stroke = "#233038"
        dot_col = "#42535C"

    # Decorative dots matrix (12 x 3 grid)
    dots_svg = []
    for row in range(3):
        for col in range(12):
            dx = 1000 + col * 9
            dy = 38 + row * 8
            dots_svg.append(f'<circle cx="{dx}" cy="{dy}" r="1.3" fill="{dot_col}"/>')

    # Line numbers (01 to 13)
    gutter_lines = []
    line_ys = [
        110,  # 01: # About Me
        134,  # 02: I'm a Software Engineer at Prodapt...
        156,  # 03: and production infrastructure.
        178,  # 04: (blank)
        200,  # 05: I'm particularly interested...
        222,  # 06: I enjoy exploring the systems...
        244,  # 07: and the engineering decisions...
        266,  # 08: (blank)
        288,  # 09: Outside work, I build...
        310,  # 10: engineering approaches...
        332,  # 11: (blank)
        354,  # 12: I'm the kind of engineer...
        376,  # 13: and how it can be designed better.
    ]

    for idx, ly in enumerate(line_ys, 1):
        num_str = f"{idx:02d}"
        gutter_lines.append(
            f'<text x="62" y="{ly}" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="12" font-weight="600" fill="{line_num_col}" text-anchor="middle">{num_str}</text>'
        )

    # Compass Icon
    compass_icon = f'''<g transform="translate(48, 517)" stroke="{accent_col}" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="13" cy="13" r="9"/>
      <polygon points="16.5 9.5 14.5 14.5 9.5 16.5 11.5 11.5" fill="{accent_col}" fill-opacity="0.35"/>
    </g>'''

    # Layers Icon
    layers_icon = f'''<g transform="translate(606, 517)" stroke="{accent_col}" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 4 8 L 13 4 L 22 8 L 13 12 Z"/>
      <path d="M 4 12.5 L 13 16.5 L 22 12.5"/>
      <path d="M 4 17 L 13 21 L 22 17"/>
    </g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="About Me — Naresh B A">
<title>About Me — Naresh B A</title>
<defs>
  <filter id="aboutAccentGlow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<!-- Outer Card Container -->
<rect x="6" y="6" width="{card_w}" height="{card_h}" rx="14" fill="{bg_card}" stroke="{border_col}" stroke-width="1.2"/>

<!-- Outer Glowing Corner Brackets -->
<path d="M 6 30 L 6 6 L 30 6" fill="none" stroke="{accent_col}" stroke-width="2" />
<path d="M {width - 30} 6 L {width - 6} 6 L {width - 6} 30" fill="none" stroke="{accent_col}" stroke-width="2" />
<path d="M 6 {h - 30} L 6 {h - 6} L 30 {h - 6}" fill="none" stroke="{accent_col}" stroke-width="2" />
<path d="M {width - 30} {h - 6} L {width - 6} {h - 6} L {width - 6} {h - 30}" fill="none" stroke="{accent_col}" stroke-width="2" />

<!-- Section Title Bar inside Card -->
<rect x="32" y="28" width="4.5" height="28" rx="2" fill="{accent_col}"/>
<text x="46" y="50" font-family="'Orbitron', system-ui, -apple-system, sans-serif" font-size="28" font-weight="900" fill="{text_col}" letter-spacing="-0.3">About Me</text>

<!-- Decorative Dot Grid -->
<g opacity="0.32">
  {''.join(dots_svg)}
</g>

<!-- ==================== MAIN CODE EDITOR BOX ==================== -->
<rect x="32" y="76" width="1096" height="402" rx="12" fill="{editor_bg}" stroke="{editor_stroke}" stroke-width="1.2"/>

<!-- Editor Corner Accents -->
<path d="M 32 94 L 32 76 L 50 76" fill="none" stroke="{accent_col}" stroke-width="1.5" opacity="0.8"/>
<path d="M 1110 478 L 1128 478 L 1128 460" fill="none" stroke="{accent_col}" stroke-width="1.5" opacity="0.8"/>

<!-- Left Gutter Divider -->
<line x1="90" y1="90" x2="90" y2="464" stroke="{gutter_border}" stroke-width="1"/>

<!-- Gutter Line Numbers -->
{''.join(gutter_lines)}

<!-- Editor Code Content -->
<g font-family="'JetBrains Mono', Consolas, 'Liberation Mono', monospace" font-size="13.2">
  <!-- Line 01: # About Me -->
  <text x="110" y="110" font-weight="700" fill="{accent_col}"># About Me</text>

  <!-- Line 02 & 03: Paragraph 1 -->
  <text x="110" y="134" fill="{text_col}">I'm a <tspan fill="{accent_col}" font-weight="700">Software Engineer at Prodapt</tspan>, working on backend systems, distributed data pipelines,</text>
  <text x="110" y="156" fill="{text_col}">and production infrastructure.</text>

  <!-- Line 05 - 07: Paragraph 2 -->
  <text x="110" y="200" fill="{text_col}">I'm particularly interested in what makes intelligent software reliable. Beyond integrating AI models,</text>
  <text x="110" y="222" fill="{text_col}">I enjoy exploring the systems around them — <tspan fill="{text_secondary}">architecture, data flows, failure handling, observability,</tspan></text>
  <text x="110" y="244" fill="{text_col}">and the engineering decisions that make software dependable.</text>

  <!-- Line 09 & 10: Paragraph 3 -->
  <text x="110" y="288" fill="{text_col}">Outside work, I build applied AI projects and open-source developer tools, experiment with new</text>
  <text x="110" y="310" fill="{text_col}">engineering approaches, and write about the lessons and trade-offs behind them.</text>

  <!-- Line 12 & 13: Paragraph 4 -->
  <text x="110" y="354" fill="{text_col}">I'm the kind of engineer who wants to understand <tspan fill="{accent_col}" font-weight="700">why something works, what happens when it fails,</tspan></text>
  <text x="110" y="376" font-weight="700" fill="{accent_col}">and how it can be designed better.<tspan fill="{text_secondary}" font-weight="400">_</tspan></text>
</g>

<!-- ==================== BOTTOM TWO PODS ==================== -->

<!-- Pod 1: Currently exploring (Left) -->
<rect x="32" y="496" width="538" height="122" rx="10" fill="{pill_card_bg}" stroke="{pill_card_stroke}" stroke-width="1.2"/>
<!-- Top Badge Pill -->
<rect x="44" y="512" width="186" height="34" rx="7" fill="{badge_bg}" stroke="{badge_border}" stroke-width="0.9"/>
{compass_icon}
<text x="82" y="534" font-family="'JetBrains Mono', Consolas, monospace" font-size="12.5" font-weight="700" fill="{text_col}">Currently exploring</text>
<!-- Description -->
<text x="48" y="574" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13.5" fill="{text_secondary}">Advanced backend patterns, AI-enabled systems, and more</text>
<text x="48" y="596" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13.5" fill="{text_secondary}">reliable, observable architectures.</text>

<!-- Pod 2: Engineering mindset (Right) -->
<rect x="590" y="496" width="538" height="122" rx="10" fill="{pill_card_bg}" stroke="{pill_card_stroke}" stroke-width="1.2"/>
<!-- Top Badge Pill -->
<rect x="602" y="512" width="186" height="34" rx="7" fill="{badge_bg}" stroke="{badge_border}" stroke-width="0.9"/>
{layers_icon}
<text x="640" y="534" font-family="'JetBrains Mono', Consolas, monospace" font-size="12.5" font-weight="700" fill="{text_col}">Engineering mindset</text>
<!-- Description -->
<text x="606" y="574" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13.5" fill="{text_secondary}">Build → Measure → Observe → Iterate — to create intelligent,</text>
<text x="606" y="596" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13.5" fill="{text_secondary}">resilient, and high-impact software systems.</text>

</svg>'''

def main():
    central = ROOT / 'design' / 'themes.json'
    theme = {}
    if central.exists():
        settings = json.loads(central.read_text(encoding='utf-8'))
        active = settings.get('active', 'titanium-hacker')
        theme = settings.get('presets', {}).get(active, {})

    OUT.mkdir(parents=True, exist_ok=True)
    dark_svg = generate_about_me_svg(theme, is_light=False)
    light_svg = generate_about_me_svg(theme, is_light=True)

    (OUT / 'about-me.svg').write_text(dark_svg, encoding='utf-8')
    (OUT / 'about-me-light.svg').write_text(light_svg, encoding='utf-8')
    print("Wrote assets/sections/about-me.svg and about-me-light.svg")

if __name__ == '__main__':
    main()
