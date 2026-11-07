import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f")

def render_html_to_png(html_content: str, out_png: Path, width: int = 1200, height: int = 800):
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

def main():
    # 1. Section 04 Dark & Light
    for is_light, mode in [(False, "dark"), (True, "light")]:
        suffix = "-light" if is_light else ""
        bg_col = "#ffffff" if is_light else "#0d1117"
        h_s4 = (ROOT / 'assets' / 'headers' / f'status-currently-building{suffix}.svg').as_uri()
        s4 = (ROOT / 'assets' / 'now' / f'agent-toolkit{suffix}.svg').as_uri()
        html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>* {{ margin:0; padding:0; box-sizing:border-box; }} body {{ background:{bg_col}; padding:32px; width:1200px; }} img {{ display:block; margin-bottom:16px; width:100%; }}</style>
</head><body>
<img src="{h_s4}" />
<img src="{s4}" />
</body></html>"""
        render_html_to_png(html, out_dir / f"section_04_currently_building_{mode}.png", width=1200, height=360)

    # 2. Section 05 Dark & Light
    for is_light, mode in [(False, "dark"), (True, "light")]:
        suffix = "-light" if is_light else ""
        bg_col = "#ffffff" if is_light else "#0d1117"
        h_s5 = (ROOT / 'assets' / 'headers' / f'cat-engineering-stack{suffix}.svg').as_uri()
        s5 = (ROOT / 'assets' / 'stack' / f'toolkit{suffix}.svg').as_uri()
        html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>* {{ margin:0; padding:0; box-sizing:border-box; }} body {{ background:{bg_col}; padding:32px; width:1200px; }} img {{ display:block; margin-bottom:16px; width:100%; }}</style>
</head><body>
<img src="{h_s5}" />
<img src="{s5}" />
</body></html>"""
        render_html_to_png(html, out_dir / f"section_05_engineering_stack_{mode}.png", width=1200, height=520)

    # 3. Combined Sections 04 + 05 Dark & Light (matches user reference image)
    for is_light, mode in [(False, "dark"), (True, "light")]:
        suffix = "-light" if is_light else ""
        bg_col = "#ffffff" if is_light else "#0C0F10"
        h_s4 = (ROOT / 'assets' / 'headers' / f'status-currently-building{suffix}.svg').as_uri()
        s4 = (ROOT / 'assets' / 'now' / f'agent-toolkit{suffix}.svg').as_uri()
        h_s5 = (ROOT / 'assets' / 'headers' / f'cat-engineering-stack{suffix}.svg').as_uri()
        s5 = (ROOT / 'assets' / 'stack' / f'toolkit{suffix}.svg').as_uri()
        html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>* {{ margin:0; padding:0; box-sizing:border-box; }} body {{ background:{bg_col}; padding:24px; width:1200px; }} img {{ display:block; margin-bottom:16px; width:100%; }}</style>
</head><body>
<img src="{h_s4}" />
<img src="{s4}" />
<img src="{h_s5}" />
<img src="{s5}" />
</body></html>"""
        render_html_to_png(html, out_dir / f"sections_04_05_{mode}_preview.png", width=1200, height=780)

if __name__ == "__main__":
    main()

