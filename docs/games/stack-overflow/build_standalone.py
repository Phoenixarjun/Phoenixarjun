from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
p=(ROOT/'src/physics.mjs').read_text()
r=(ROOT/'src/renderer.js').read_text()
m=(ROOT/'src/main.js').read_text()
r=re.sub(r'^import .*?;\s*$', '',r,flags=re.M)
m=re.sub(r'^import .*?;\s*$', '',m,flags=re.M)
source='\n\n'.join((re.sub(r'\bexport (?=(const|function|class)\b)','',p),re.sub(r'\bexport (?=(const|function|class)\b)','',r),m))
html=(ROOT/'index.html').read_text()
html=html.replace('<link rel="stylesheet" href="./style.css" />', f'<style>\n{(ROOT/"style.css").read_text()}\n</style>')
html=html.replace('<script type="module" src="./src/main.js"></script>', '')
html=html.replace('</body>',f'<script>\n{source}\n</script>\n</body>')
assert '<script type="module"' not in html
assert not re.search(r'\bimport \{',source)
(ROOT/'standalone.html').write_text(html)
print('standalone bytes',len(html))
