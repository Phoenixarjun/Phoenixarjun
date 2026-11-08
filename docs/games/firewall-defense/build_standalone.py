"""Produce a one-file offline game; inline only first-party sources, no network calls."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.html').read_text(encoding='utf8')
css=(ROOT/'style.css').read_text(encoding='utf8')
modules=[]
for name in ('engine.mjs','renderer.js','main.js'):
    source=(ROOT/'src'/name).read_text(encoding='utf8')
    source=re.sub(r'^import\s+.*?\s+from\s+[\'"].*?[\'"].*?;\s*$', '', source,flags=re.MULTILINE)
    source=re.sub(r'^export\s+(?=(?:const|class|function))','',source,flags=re.MULTILINE)
    modules.append('// SOURCE: '+name+'\n'+source)
html=html.replace('<link rel="stylesheet" href="./style.css" />', '<style>\n'+css+'\n</style>')
html=html.replace('<script type="module" src="./src/main.js"></script>', '<script type="module">\n'+'\n'.join(modules)+'\n</script>')
assert '<script type="module">' in html and 'src="./src/' not in html
(ROOT/'standalone.html').write_text(html,encoding='utf8')
print('standalone written:', (ROOT/'standalone.html').stat().st_size, 'bytes')
