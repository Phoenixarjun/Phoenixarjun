import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
svg_file = ROOT / "assets" / "engineering-focus" / "engineering-focus-dark.svg"
out_png = ROOT / "assets" / "engineering-focus" / "previews" / "engineering-focus-dark-preview.png"

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1280px; height:765px; overflow:hidden; background:#070B0C; }}
img {{ display:block; width:1280px; height:765px; }}
</style></head><body><img src="file:///{svg_file.as_posix()}" width="1280" height="765"/></body></html>"""

tmp_html = ROOT / "previews" / "ef_render.html"
tmp_html.write_text(html, encoding='utf-8')
tmp = tempfile.mkdtemp()
cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    f"--user-data-dir={tmp}",
    "--window-size=1280,765",
    "--hide-scrollbars",
    f"--screenshot={out_png}",
    f"file:///{tmp_html.as_posix()}"
]
subprocess.run(cmd, check=True)
if tmp_html.is_file():
    tmp_html.unlink()
print("Rendered fresh preview PNG to:", out_png)
