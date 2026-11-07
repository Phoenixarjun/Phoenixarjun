"""Generate static and animated Hero SVGs for GitHub profile.

Produces:
- assets/generated/hero/hero-static.svg
- assets/generated/hero/hero-animated.svg

Follows Titanium Hacker design tokens, cyber-HUD framing, halftone computational
portrait, prompt strip, name/role hierarchy, metadata row, and bottom wave mesh.
"""
from __future__ import annotations

import math
from pathlib import Path
from html import escape

try:
    from generate_halftone_portrait import generate_portrait_dots, render_portrait_svg_group
except ModuleNotFoundError:
    from scripts.generate_halftone_portrait import generate_portrait_dots, render_portrait_svg_group

ROOT = Path(__file__).resolve().parents[1]

TOKENS = {
    'background_main': '#070B0C',
    'background_panel': '#0B1113',
    'background_glow': '#0D1412',
    'border_main': '#335058',
    'border_soft': '#203037',
    'text_primary': '#F0F5EF',
    'text_secondary': '#B7C7BF',
    'text_dim': '#8A9B93',
    'accent_primary': '#B9FF38',
    'accent_soft': '#90D92C',
    'accent_glow': 'rgba(185, 255, 56, 0.28)',
    'accent_muted': '#6B8F2A',
}


def build_wave_mesh_svg(animated: bool = False) -> str:
    """Generate multi-layered mathematical flowing wave mesh at bottom-right."""
    start_x = 710
    end_x = 1220
    base_y = 368
    num_pts = 64
    step = (end_x - start_x) / (num_pts - 1)

    layers = [
        {'amp': 18.0, 'freq': 0.016, 'phase': 0.0, 'color': '#B9FF38', 'op': 0.85, 'sw': 1.4, 'r': 1.4},
        {'amp': 14.0, 'freq': 0.021, 'phase': 1.6, 'color': '#90D92C', 'op': 0.65, 'sw': 1.1, 'r': 1.1},
        {'amp': 22.0, 'freq': 0.013, 'phase': 3.1, 'color': '#6B8F2A', 'op': 0.45, 'sw': 0.9, 'r': 0.9},
        {'amp': 10.0, 'freq': 0.026, 'phase': 4.5, 'color': '#335058', 'op': 0.35, 'sw': 0.8, 'r': 0.8},
    ]

    out = ['<g id="mesh" class="wave-mesh">']

    for idx, lyr in enumerate(layers):
        pts = []
        for i in range(num_pts):
            x = start_x + i * step
            # Envelope to taper at ends
            progress = i / (num_pts - 1)
            envelope = math.sin(progress * math.pi) ** 0.85
            y = base_y + lyr['amp'] * math.sin(lyr['freq'] * x + lyr['phase']) * envelope
            pts.append((x, y))

        # Path definition
        d_arr = [f'M {pts[0][0]:.1f} {pts[0][1]:.1f}']
        for i in range(1, len(pts)):
            d_arr.append(f'L {pts[i][0]:.1f} {pts[i][1]:.1f}')
        path_d = ' '.join(d_arr)

        cls_name = f'wave-layer-{idx}'
        out.append(f'  <path class="{cls_name}" d="{path_d}" fill="none" stroke="{lyr["color"]}" stroke-width="{lyr["sw"]}" opacity="{lyr["op"]}"/>')

        # Particle nodes along wave
        out.append(f'  <g class="{cls_name}-dots" fill="{lyr["color"]}" opacity="{lyr["op"]}">' )
        for i in range(0, len(pts), 2 if idx == 0 else 3):
            px, py = pts[i]
            out.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="{lyr["r"]:.1f}"/>')
        out.append('  </g>')

    out.append('</g>')
    return '\n'.join(out)


def build_frame_svg() -> str:
    """Generate cyber-HUD angular outer frame with technical notches, glow spots, and indicators."""
    w, h = 1280, 420
    x, y, fw, fh = 24, 20, 1232, 380
    c = 52  # chamfer size

    # Outer polygonal path with engineered bevels
    path = (
        f"M {x+c} {y} "
        f"L {x+fw-24} {y} "
        f"Q {x+fw} {y} {x+fw} {y+24} "
        f"L {x+fw} {y+fh-36} "
        f"L {x+fw-36} {y+fh} "
        f"L {x+36} {y+fh} "
        f"L {x} {y+fh-36} "
        f"L {x} {y+c} "
        f"Z"
    )

    t = TOKENS
    out = [
        '<g id="frame" class="cyber-frame">',
        '  <!-- Ambient Panel Gradient Background -->',
        f'  <path d="{path}" fill="url(#panelBg)" />',
        '  <!-- Dotted Matrix Texture Overlay -->',
        f'  <path d="{path}" fill="url(#bgDots)" />',
        '  <!-- Outer Cyber Border -->',
        f'  <path d="{path}" fill="none" stroke="{t["border_main"]}" stroke-width="1.6" />',
        f'  <path d="{path}" fill="none" stroke="{t["border_soft"]}" stroke-width="0.8" opacity="0.6" />',
        '',
        '  <!-- Top-Left Neon Bevel Highlight -->',
        f'  <line x1="{x}" y1="{y+c}" x2="{x+c}" y2="{y}" stroke="{t["accent_primary"]}" stroke-width="3" filter="url(#glowStrong)" />',
        f'  <line x1="{x}" y1="{y+c}" x2="{x+c}" y2="{y}" stroke="{t["text_primary"]}" stroke-width="1" />',
        '',
        '  <!-- Vertical Hotspot Bars -->',
        f'  <rect x="{x-1}" y="{y+110}" width="3.5" height="48" rx="1.5" fill="{t["accent_primary"]}" filter="url(#glowStrong)" />',
        f'  <rect x="{x+fw-2}" y="{y+220}" width="3.5" height="44" rx="1.5" fill="{t["accent_primary"]}" filter="url(#glowStrong)" />',
        '',
        '  <!-- Top-Right Cyber Slashes /// -->',
        f'  <g id="cyber_slashes" stroke="{t["accent_primary"]}" stroke-width="2.5" opacity="0.9">',
        f'    <line x1="{x+fw-80}" y1="{y+18}" x2="{x+fw-64}" y2="{y+34}" />',
        f'    <line x1="{x+fw-66}" y1="{y+18}" x2="{x+fw-50}" y2="{y+34}" />',
        f'    <line x1="{x+fw-52}" y1="{y+18}" x2="{x+fw-36}" y2="{y+34}" />',
        '  </g>',
        '',
        '  <!-- Bottom-Left Status Indicators -->',
        f'  <g id="status_indicators">',
        f'    <circle cx="{x+54}" cy="{y+fh-16}" r="3" fill="{t["accent_primary"]}" filter="url(#glowSoft)" />',
        f'    <circle cx="{x+68}" cy="{y+fh-16}" r="3" fill="{t["accent_soft"]}" />',
        f'    <circle cx="{x+82}" cy="{y+fh-16}" r="3" fill="{t["border_main"]}" />',
        f'    <line x1="{x+100}" y1="{y+fh-16}" x2="{x+180}" y2="{y+fh-16}" stroke="{t["border_main"]}" stroke-width="1" />',
        '  </g>',
        '',
        '  <!-- Bottom-Right Accent Corner Line -->',
        f'  <line x1="{x+fw-36}" y1="{y+fh}" x2="{x+fw-10}" y2="{y+fh-26}" stroke="{t["accent_primary"]}" stroke-width="2.5" filter="url(#glowStrong)" />',
        '</g>',
    ]
    return '\n'.join(out)


def build_icons_svg() -> dict:
    """Return concise vector path data for briefcase and location pin."""
    # Briefcase icon (viewBox 0 0 24 24 standard)
    briefcase = (
        '<svg x="488" y="334" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#B9FF38" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>'
        '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
        '</svg>'
    )
    # Location pin icon (viewBox 0 0 24 24 standard)
    location = (
        '<svg x="786" y="334" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#B9FF38" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/>'
        '</svg>'
    )
    return {'briefcase': briefcase, 'location': location}


def generate_hero_svg(animated: bool = False) -> str:
    """Assemble complete hero SVG (static or animated)."""
    w, h = 1280, 420
    t = TOKENS

    # Fetch portrait data
    portrait_data = generate_portrait_dots(
        target_w=325,
        target_h=305,
        offset_x=65.0,
        offset_y=58.0,
        spacing=6.2,
    )
    portrait_xml = render_portrait_svg_group(portrait_data, animated=animated)
    frame_xml = build_frame_svg()
    wave_xml = build_wave_mesh_svg(animated=animated)
    icons = build_icons_svg()

    # CSS styles and animations
    css_block = ''
    if animated:
        css_block = f"""
  <style>
    @keyframes dotReveal {{
      0% {{ opacity: 0; transform: scale(0.3); }}
      70% {{ opacity: 0.9; transform: scale(1.15); }}
      100% {{ opacity: 1; transform: scale(1); }}
    }}
    @keyframes typewriter {{
      from {{ width: 0; }}
      to {{ width: 20ch; }}
    }}
    @keyframes blinkCursor {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    @keyframes waveShimmer {{
      0% {{ transform: translateX(0); opacity: 0.75; }}
      50% {{ transform: translateX(-8px); opacity: 0.95; }}
      100% {{ transform: translateX(0); opacity: 0.75; }}
    }}
    @keyframes pulseGlow {{
      0%, 100% {{ opacity: 0.85; }}
      50% {{ opacity: 1.0; }}
    }}
    .cursor-blink {{
      animation: blinkCursor 0.9s infinite;
    }}
    .wave-mesh {{
      animation: waveShimmer 6s ease-in-out infinite;
    }}
    .role-glow {{
      animation: pulseGlow 3s ease-in-out infinite;
    }}
  </style>
"""

    # Role text block
    if animated:
        role_content = (
            f'    <text x="468" y="218" font-family="\'JetBrains Mono\', \'Fira Code\', Consolas, monospace" '
            f'font-size="32" font-weight="700" fill="{t["accent_primary"]}" filter="url(#glowSoft)" class="role-glow">'
            f'AI Systems Engineer<tspan class="cursor-blink" fill="{t["accent_primary"]}">_</tspan></text>'
        )
    else:
        role_content = (
            f'    <text x="468" y="218" font-family="\'JetBrains Mono\', \'Fira Code\', Consolas, monospace" '
            f'font-size="32" font-weight="700" fill="{t["accent_primary"]}" filter="url(#glowSoft)">'
            f'AI Systems Engineer<tspan fill="{t["accent_primary"]}">_</tspan></text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Naresh B A — AI Systems Engineer">
<title>Naresh B A — AI Systems Engineer</title>
<defs>
{css_block}
  <!-- Gradients -->
  <linearGradient id="panelBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{t['background_main']}"/>
    <stop offset="45%" stop-color="{t['background_panel']}"/>
    <stop offset="100%" stop-color="{t['background_main']}"/>
  </linearGradient>

  <linearGradient id="promptBg" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#0E1618"/>
    <stop offset="100%" stop-color="#090E10"/>
  </linearGradient>

  <radialGradient id="portraitBacklight" cx="220" cy="210" r="180" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="{t['accent_primary']}" stop-opacity="0.08"/>
    <stop offset="50%" stop-color="{t['accent_primary']}" stop-opacity="0.02"/>
    <stop offset="100%" stop-color="{t['accent_primary']}" stop-opacity="0"/>
  </radialGradient>

  <radialGradient id="identityBacklight" cx="620" cy="200" r="260" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="{t['accent_primary']}" stop-opacity="0.05"/>
    <stop offset="70%" stop-color="{t['accent_primary']}" stop-opacity="0"/>
  </radialGradient>

  <!-- Dot Matrix Pattern -->
  <pattern id="bgDots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="0.75" fill="{t['border_main']}" opacity="0.18"/>
  </pattern>

  <!-- Glow Filters -->
  <filter id="glowSoft" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <filter id="glowStrong" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="5.0" result="blur1"/>
    <feGaussianBlur stdDeviation="2.0" result="blur2"/>
    <feMerge>
      <feMergeNode in="blur1"/>
      <feMergeNode in="blur2"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<!-- BACKGROUND -->
<rect width="{w}" height="{h}" fill="{t['background_main']}"/>
<circle cx="220" cy="210" r="180" fill="url(#portraitBacklight)"/>
<circle cx="620" cy="200" r="260" fill="url(#identityBacklight)"/>

<!-- CYBER HUD FRAME -->
{frame_xml}

<!-- LEFT PORTRAIT MODULE -->
{portrait_xml}

<!-- RIGHT-SIDE IDENTITY BLOCK -->
<g id="identity_content">
  <!-- 1. Terminal Prompt Capsule -->
  <g id="prompt_strip">
    <rect x="468" y="52" width="372" height="46" rx="14" fill="url(#promptBg)" stroke="{t['border_main']}" stroke-width="1.2"/>
    <!-- Terminal Text -->
    <text x="488" y="81" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="16" font-weight="600" fill="{t['accent_primary']}">naresh@github:~$ <tspan fill="{t['text_primary']}" font-weight="500">whoami</tspan></text>
    <!-- Extension Guide Line -->
    <line x1="840" y1="75" x2="1200" y2="75" stroke="{t['border_soft']}" stroke-width="1" stroke-dasharray="4 4" opacity="0.65"/>
    <circle cx="1200" cy="75" r="2" fill="{t['accent_primary']}" opacity="0.8"/>
  </g>

  <!-- 2. Main Name -->
  <g id="name_title">
    <text x="468" y="160" font-family="'Inter', 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="68" font-weight="800" fill="{t['text_primary']}" letter-spacing="-0.5">Naresh B A</text>
  </g>

  <!-- 3. Role -->
  <g id="role_line">
{role_content}
  </g>

  <!-- 4. Tagline with Accent Bar -->
  <g id="tagline_block">
    <rect x="468" y="246" width="4" height="46" rx="2" fill="{t['accent_primary']}" filter="url(#glowSoft)"/>
    <text x="488" y="265" font-family="'Inter', 'Segoe UI', sans-serif" font-size="18" font-weight="500" fill="{t['text_secondary']}">Building intelligent software</text>
    <text x="488" y="289" font-family="'Inter', 'Segoe UI', sans-serif" font-size="18" font-weight="500" fill="{t['text_secondary']}">on reliable systems.</text>
  </g>

  <!-- 5. Metadata Row Capsule -->
  <g id="metadata_row">
    <rect x="468" y="322" width="670" height="44" rx="14" fill="{t['background_panel']}" stroke="{t['border_soft']}" stroke-width="1.2"/>
    
    <!-- Briefcase Icon + Prodapt -->
    {icons['briefcase']}
    <text x="516" y="349" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="15" font-weight="500" fill="{t['text_primary']}">Software Engineer @ Prodapt</text>
    
    <!-- Vertical Separator -->
    <line x1="765" y1="332" x2="765" y2="356" stroke="{t['border_main']}" stroke-width="1.2"/>
    
    <!-- Location Pin + Chennai -->
    {icons['location']}
    <text x="814" y="349" font-family="'JetBrains Mono', 'Fira Code', Consolas, monospace" font-size="15" font-weight="500" fill="{t['text_primary']}">Chennai, India</text>
  </g>
</g>

<!-- BOTTOM-RIGHT FLOWING WAVE MESH -->
{wave_xml}

</svg>"""
    return svg


def main():
    dest_dir = ROOT / 'assets' / 'generated' / 'hero'
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("Building hero-static.svg...")
    static_svg = generate_hero_svg(animated=False)
    (dest_dir / 'hero-static.svg').write_text(static_svg, encoding='utf-8')
    print("Saved:", dest_dir / 'hero-static.svg')

    print("Building hero-animated.svg...")
    animated_svg = generate_hero_svg(animated=True)
    (dest_dir / 'hero-animated.svg').write_text(animated_svg, encoding='utf-8')
    print("Saved:", dest_dir / 'hero-animated.svg')


if __name__ == '__main__':
    main()
