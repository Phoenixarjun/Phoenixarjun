import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f")

# Build dual-theme preview HTMLs
def render_mode_preview(mode: str, bg_color: str, text_color: str, out_png: Path):
    is_light = (mode == "light")
    hero_uri = (ROOT / 'assets' / 'generated' / 'hero' / 'hero-animated.gif').as_uri()
    
    # Headers
    h_ef = (ROOT / 'assets' / 'headers' / f'inspect-engineering-focus{"-light" if is_light else ""}.svg').as_uri()
    h_proj = (ROOT / 'assets' / 'headers' / f'ls-flagship-projects{"-light" if is_light else ""}.svg').as_uri()
    h_now = (ROOT / 'assets' / 'headers' / f'status-currently-building{"-light" if is_light else ""}.svg').as_uri()
    
    # Content SVGs
    ef_svg = (ROOT / 'assets' / 'engineering-focus' / f'engineering-focus-{"light" if is_light else "dark"}.svg').as_uri()
    p1 = (ROOT / 'assets' / 'projects' / f'architecture-as-memory{"-light" if is_light else ""}.svg').as_uri()
    p2 = (ROOT / 'assets' / 'projects' / f'promptnova{"-light" if is_light else ""}.svg').as_uri()
    p3 = (ROOT / 'assets' / 'projects' / f'credflow{"-light" if is_light else ""}.svg').as_uri()
    now_svg = (ROOT / 'assets' / 'now' / f'agent-toolkit{"-light" if is_light else ""}.svg').as_uri()

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: {bg_color};
  color: {text_color};
  width: 920px;
  margin: 0 auto;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
.container {{
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}}
img {{
  width: 100%;
  display: block;
}}
h2 {{
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  opacity: 0.6;
  margin-bottom: 8px;
}}
</style>
</head>
<body>
<div class="container">
  <h2>Simulated GitHub {mode.capitalize()} Mode ({bg_color})</h2>
  <img src="{hero_uri}" alt="Hero" />
  <img src="{h_ef}" alt="Header" />
  <img src="{ef_svg}" alt="Engineering Focus" />
  <img src="{h_proj}" alt="Flagship Projects Header" />
  <img src="{p1}" alt="Architecture as Memory" />
  <img src="{p2}" alt="PromptNova" />
  <img src="{p3}" alt="CredFlow" />
  <img src="{h_now}" alt="Currently Building Header" />
  <img src="{now_svg}" alt="Agent Toolkit" />
</div>
</body>
</html>"""

    tmp_html = ROOT / "previews" / f"github_{mode}_preview.html"
    tmp_html.write_text(html, encoding="utf-8")
    tmp = tempfile.mkdtemp()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={tmp}",
        "--window-size=940,2400",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"file:///{tmp_html.as_posix()}",
    ]
    subprocess.run(cmd, check=True)
    if tmp_html.is_file():
        tmp_html.unlink()
    print(f"Rendered {mode} preview to:", out_png)

if __name__ == '__main__':
    render_mode_preview("dark", "#0d1117", "#c9d1d9", out_dir / "github_dark_mode_preview.png")
    render_mode_preview("light", "#ffffff", "#1f2328", out_dir / "github_light_mode_preview.png")
