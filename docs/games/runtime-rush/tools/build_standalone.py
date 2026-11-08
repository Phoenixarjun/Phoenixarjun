#!/usr/bin/env python3
"""Produce one portable offline standalone.html; no network dependencies."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text()
css=(ROOT/'style.css').read_text()
sources=[]
for name in ('physics.mjs','renderer.js','fallback.js','audio.js','game.js'):
    text=(ROOT/'src'/name).read_text()
    text=re.sub(r'^import\s+.+?from\s+[\'"].+?[\'"].*?;\s*$', '',text,flags=re.M)
    text=re.sub(r'\bexport\s+(?=(?:const|let|function|class)\b)','',text)
    sources.append('// === '+name+' ===\n'+text)
html=html.replace('<link rel="icon" href="./assets/favicon.svg" type="image/svg+xml">','')
html=html.replace('<link rel="stylesheet" href="./style.css">','<style>\n'+css+'\n</style>')
html=html.replace('<script type="module" src="./src/game.js"></script>','<script>\n'+ '\n'.join(sources) +'\n</script>')
assert '<script type="module"' not in html
assert 'src="./src/' not in html
assert 'href="./style.css"' not in html
out=ROOT/'standalone.html'
out.write_text(html,encoding='utf-8')
print(f'Generated {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)')
