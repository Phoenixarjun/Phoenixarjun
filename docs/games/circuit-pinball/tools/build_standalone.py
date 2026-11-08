#!/usr/bin/env python3
"""Create one offline-playable HTML file by embedding local CSS and JS (no build deps)."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf-8')
css=(root/'style.css').read_text(encoding='utf-8')
html=html.replace('  <link rel="stylesheet" href="style.css" />',f'  <style>\n{css}\n  </style>')
html=html.replace('  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />','')
for name in ['physics','audio','render','game']:
    script=(root/f'src/{name}.js').read_text(encoding='utf-8')
    html=html.replace(f'  <script src="src/{name}.js"></script>',f'  <script>\n{script}\n  </script>')
(root/'standalone.html').write_text(html,encoding='utf-8')
print(f"Created standalone.html ({(root/'standalone.html').stat().st_size} bytes)")
