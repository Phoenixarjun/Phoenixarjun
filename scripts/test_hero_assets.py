"""Validation suite for one-time portrait reveal and Titanium Hacker hero V4."""
from pathlib import Path
from PIL import Image, ImageChops
import xml.etree.ElementTree as ET
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/generated/hero'

def test():
    for n in ('hero-static.svg','hero-vector-halftone.svg','portrait-halftone.svg',
              'wave-terrain.svg','right-architecture.svg','three-slashes.svg'):
        p=OUT/n
        assert p.is_file() and p.stat().st_size > 100,(n,'missing/empty')
        root=ET.parse(p).getroot()
        assert root.attrib.get('viewBox'),n
    print('PASS 6 SVGs parse and have viewBoxes')
    s=(OUT/'hero-static.svg').read_text()
    assert 'data:image/png;base64,' in s,'photographic SVG should be self-contained'
    assert '<script' not in s
    for text in ('Naresh B A','AI Systems Engineer','Software Engineer @ Prodapt','Chennai, India'):
        assert text in s
    for marker in ('signal-terrain','right-circuit-visual','lower-right-slashes','photographic-portrait'):
        assert marker in s
    print('PASS faithful static content, embedded photo, right art, wave and slashes')
    h=(OUT/'hero-vector-halftone.svg').read_text()
    assert '<image' not in h and h.count('<circle ')>4000
    print('PASS vector-only halftone alternative')
    im=Image.open(OUT/'hero-preview.png').convert('RGBA')
    assert im.size==(1600,740) and im.getpixel((0,0))[3]==0
    assert Image.open(OUT/'hero-static.png').size==(1600,740)
    print('PASS static alpha, geometry and PNG fallback')
    gif=Image.open(OUT/'hero-animated.gif')
    assert gif.n_frames>=20
    assert gif.size[0]>=1000
    assert gif.info.get('loop') == 0, 'GIF should include Netscape repeat-loop extension (loop=0)'
    count=0
    for j in range(gif.n_frames):
        gif.seek(j);count+=gif.info.get('duration',0)
    assert 3500<count<7000,(count,'unexpected duration')
    gif.seek(0);start=gif.convert('RGB').copy()
    gif.seek(gif.n_frames-1);end=gif.convert('RGB').copy()
    face_box=(65,100,410,450)
    v=np.asarray(ImageChops.difference(start.crop(face_box),end.crop(face_box)).convert('L'))
    assert (v>25).sum()>8000,'Portrait does not change in reveal area'
    assert ImageChops.difference(start,end).getbbox()
    print('PASS GIF one-time play,',gif.n_frames,'optimized frames, total',round(count/1000,2),'seconds; portrait reveals')
    assert (OUT/'hero-animated.gif').stat().st_size<8_000_000
    print('PASS GIF size')

if __name__=='__main__':test()
