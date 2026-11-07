"""Validate local content references, palette tokens and generated SVG syntax."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

def load(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))

def validate():
    themes=load('design/themes.json')
    assert themes['active'] in themes['presets']
    for key,t in themes['presets'].items():
        for token in ('base','surface','surface2','stroke','accent','secondary','text','muted'):
            color=t[token]
            assert len(color)==7 and color[0]=='#' and all(c in '0123456789abcdefABCDEF' for c in color[1:]),(key,token,color)
    profile=load('content/profile.json'); projects=load('content/projects.json')
    assert profile['github_username']=='Phoenixarjun'
    assert 1<=len(projects['flagship'])<=4
    names=[p['slug'] for p in projects['flagship']+projects['currently_building']]
    assert len(set(names))==len(names),'Duplicate project slug'
    for p in projects['flagship']+projects['currently_building']:
        url=urlsplit(p['url'])
        assert url.scheme=='https' and url.netloc=='github.com' and url.path.strip('/'), p
    content=(ROOT/'README.v2.md').read_text(encoding='utf-8')
    assert 'assets/hero/identity.svg' in content
    assert len(content)<500*1024
    for filename in (ROOT/'assets').rglob('*.svg'):
        ET.parse(filename)
        assert filename.stat().st_size<1024*1024
    for filename in (ROOT/'previews/heroes').rglob('*.svg'):
        ET.parse(filename)
    for folder in ('hero','projects','now','stack','contributions','playground'):
        assert list((ROOT/'assets'/folder).glob('*.svg'))
    # This starter is designed to be extracted into an EXISTING profile repo.
    # README.md and .github/workflows may legitimately be present there.
    # The generator only emits README.v2.md; live-file preservation is checked
    # by the integration smoke test instead of forbidding existing files.
    print('PASS: themes, source data, SVGs and rendered README preview')

if __name__=='__main__':
    validate()
