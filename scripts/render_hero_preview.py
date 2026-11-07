import subprocess
import tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def render_preview():
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    svg_file = ROOT / "assets" / "generated" / "hero" / "hero-static.svg"
    out_png = ROOT / "assets" / "generated" / "hero" / "hero-preview.png"
    
    # HTML wrapper to force exact 1280x420 viewport with no margins
    html_content = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ width: 1280px; height: 420px; overflow: hidden; background: #070B0C; }}
    img {{ display: block; width: 1280px; height: 420px; }}
  </style>
</head>
<body>
  <img src="file:///{svg_file.as_posix()}" width="1280" height="420" />
</body>
</html>"""
    
    wrapper_html = ROOT / "previews" / "hero_render_wrapper.html"
    wrapper_html.write_text(html_content, encoding='utf-8')
    
    tmp = tempfile.mkdtemp()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={tmp}",
        "--window-size=1280,420",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"file:///{wrapper_html.as_posix()}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if wrapper_html.is_file():
        wrapper_html.unlink()
    if out_png.is_file():
        im = Image.open(out_png)
        print("Success! Rendered hero-preview.png with size:", im.size)
        # If size has any extra window chrome padding, crop or resize to exact 1280x420
        if im.size != (1280, 420):
            im = im.crop((0, 0, min(1280, im.width), min(420, im.height)))
            im = im.resize((1280, 420), Image.Resampling.LANCZOS)
            im.save(out_png)
            print("Adjusted to exact (1280, 420).")
    else:
        print("Render failed. Stderr:", res.stderr)

if __name__ == '__main__':
    render_preview()
