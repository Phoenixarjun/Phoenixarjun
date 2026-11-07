import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
hero = (ROOT / 'assets' / 'generated' / 'hero' / 'hero-animated.gif').as_uri()
header = (ROOT / 'assets' / 'headers' / 'inspect-engineering-focus.svg').as_uri()
ef = (ROOT / 'assets' / 'engineering-focus' / 'engineering-focus-dark.svg').as_uri()

html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#070B0C; color:#EEF7EF; width:900px; padding:20px; font-family:sans-serif; }}
.wrapper {{ display:flex; flex-direction:column; gap:16px; align-items:center; }}
img {{ width:100%; display:block; }}
</style>
</head>
<body>
<div class="wrapper">
  <img src="{hero}" />
  <img src="{header}" />
  <img src="{ef}" />
</div>
</body>
</html>"""

tmp_html = ROOT / 'previews' / 'blend_preview.html'
tmp_html.write_text(html, encoding='utf-8')
tmp = tempfile.mkdtemp()
out_png = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f\seamless-blend-preview.png")
cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    f"--user-data-dir={tmp}",
    "--window-size=920,1500",
    "--hide-scrollbars",
    f"--screenshot={out_png}",
    f"file:///{tmp_html.as_posix()}"
]
subprocess.run(cmd, check=True)
if tmp_html.is_file():
    tmp_html.unlink()
print("Rendered seamless blend preview to:", out_png)

