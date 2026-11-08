#!/usr/bin/env python3
"""Generate dependency-free, reusable GitHub README About Me SVGs.

Standardized canvas width: 1160px (aligned with profile system geometry).
Transparent root canvas (Mode A) matching Engineering Focus.
Contained code editor with fit-to-content padding and zero dead space.
Dual-mode output: Dark and Light theme variants.
All design tokens align strictly with Titanium Hacker theme.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from graphics import about_me_card

OUT = ROOT / 'assets' / 'sections'

def main():
    central = ROOT / 'design' / 'themes.json'
    theme = {}
    if central.exists():
        settings = json.loads(central.read_text(encoding='utf-8'))
        active = settings.get('active', 'titanium-hacker')
        theme = settings.get('presets', {}).get(active, {})

    OUT.mkdir(parents=True, exist_ok=True)
    dark_svg = about_me_card(theme, is_light=False)
    light_svg = about_me_card(theme, is_light=True)

    (OUT / 'about-me.svg').write_text(dark_svg, encoding='utf-8')
    (OUT / 'about-me-light.svg').write_text(light_svg, encoding='utf-8')
    print("Wrote assets/sections/about-me.svg and about-me-light.svg")

if __name__ == '__main__':
    main()
