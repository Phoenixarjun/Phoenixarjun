import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f")

def render_html_to_png(html_content: str, out_png: Path, width: int = 1000, height: int = 1200):
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_html = tmp_dir / "preview.html"
    tmp_html.write_text(html_content, encoding="utf-8")
    user_data = tmp_dir / "chrome_user"
    user_data.mkdir()
    
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={user_data}",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"file:///{tmp_html.as_posix()}",
    ]
    subprocess.run(cmd, check=True)
    try:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception:
        pass
    print("Rendered:", out_png.name)

def render_individual_cards():
    for slug in ["architecture-as-memory", "promptnova", "credflow"]:
        svg_dark = (ROOT / 'assets' / 'projects' / f'{slug}.svg').as_uri()
        html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: #0d1117;
  padding: 32px;
  width: 960px;
  margin: 0 auto;
}}
img {{
  width: 100%;
  display: block;
}}
</style>
</head>
<body>
  <img src="{svg_dark}" alt="{slug}" />
</body>
</html>"""
        render_html_to_png(html, out_dir / f"{slug}-preview.png", width=980, height=300)

def render_section_03(mode: str, bg_color: str, text_color: str):
    is_light = (mode == "light")
    h_proj = (ROOT / 'assets' / 'headers' / f'ls-flagship-projects{"-light" if is_light else ""}.svg').as_uri()
    p1 = (ROOT / 'assets' / 'projects' / f'architecture-as-memory{"-light" if is_light else ""}.svg').as_uri()
    p2 = (ROOT / 'assets' / 'projects' / f'promptnova{"-light" if is_light else ""}.svg').as_uri()
    p3 = (ROOT / 'assets' / 'projects' / f'credflow{"-light" if is_light else ""}.svg').as_uri()

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: {bg_color};
  color: {text_color};
  width: 940px;
  margin: 0 auto;
  padding: 32px 24px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
.container {{
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}}
img {{
  width: 100%;
  display: block;
}}
</style>
</head>
<body>
<div class="container">
  <img src="{h_proj}" alt="Header" />
  <img src="{p1}" alt="Architecture as Memory" />
  <img src="{p2}" alt="PromptNova" />
  <img src="{p3}" alt="CredFlow" />
</div>
</body>
</html>"""
    render_html_to_png(html, out_dir / f"section_03_featured_projects_{mode}.png", width=960, height=960)

if __name__ == '__main__':
    render_individual_cards()
    render_section_03("dark", "#0d1117", "#c9d1d9")
    render_section_03("light", "#ffffff", "#1f2328")

