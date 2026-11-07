#!/usr/bin/env python3
"""Verify all Featured Projects vector artwork is valid and truly transparent."""
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'assets/projects'
svg_files=sorted(P.rglob('*.svg'))
assert len(svg_files)==7, f'Expected 7 SVG files; got {len(svg_files)}'
for f in svg_files:
 root=ET.parse(f).getroot()
 assert root.tag.endswith('svg'),f'{f}: not SVG'
 assert root.attrib.get('viewBox'),f'{f}: missing viewBox'
 data=f.read_text()
 assert '<script' not in data.lower(),f'{f}: script forbidden'
 assert 'http://' not in data.replace('xmlns="http://www.w3.org/2000/svg"',''),f'{f}: external HTTP reference'
 assert '<image' not in data.lower(),f'{f}: should be fully vector'
 print('SVG valid:',f.relative_to(ROOT))
try:
 from PIL import Image
 for name in ['aam-topology','promptnova-workflow','credflow-billing']:
  f=ROOT/f'assets/projects/illustrations/{name}.png'
  im=Image.open(f).convert('RGBA')
  for pt in ((0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)):
   assert im.getpixel(pt)[3]==0, f'{name}: nontransparent corner {pt}'
  assert im.getbbox(),name+' is empty'
  print('Transparent PNG valid:',f.relative_to(ROOT))
 f=ROOT/'assets/projects/decor/header-dot-field.png'
 im=Image.open(f).convert('RGBA')
 assert all(im.getpixel(pt)[3]==0 for pt in [(0,0),(im.width-1,im.height-1)]), 'Dot grid corners not transparent'
 print('Transparent PNG valid:',f.relative_to(ROOT))
except ImportError:
 print('Pillow not installed, PNG alpha tests skipped')
print('PASS')
