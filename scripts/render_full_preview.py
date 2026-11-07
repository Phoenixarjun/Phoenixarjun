import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f")

def render_preview(mode: str):
    is_light = (mode == "light")
    bg = "#ffffff" if is_light else "#0d1117"
    fg = "#1f2328" if is_light else "#c9d1d9"
    sub_color = "#57606a" if is_light else "#7A8C99"
    code_bg = "rgba(175,184,193,0.2)" if is_light else "rgba(110,118,129,0.2)"

    readme_text = (ROOT / 'README.md').read_text(encoding='utf-8')
    
    root_uri = ROOT.as_uri()
    readme_html = readme_text.replace('src="./', f'src="{root_uri}/')
    readme_html = readme_html.replace('srcset="./', f'srcset="{root_uri}/')
    readme_html = readme_html.replace('href="./', f'href="{root_uri}/')

    # For light mode testing, ensure light assets are explicitly loaded in the test page
    if is_light:
        for slug in ['concept', 'btn-github', 'btn-linkedin', 'btn-medium', 'btn-portfolio', 'footer', 'logout',
                     'open-developer-playground', 'connect-all', 'cat-engineering-stack', 'status-currently-building',
                     'ls-flagship-projects', 'inspect-engineering-focus', 'render-technical-writing', 'render-contribution-atlas',
                     'toolkit', 'atlas-static']:
            readme_html = readme_html.replace(f'/{slug}.svg', f'/{slug}-light.svg')
            readme_html = readme_html.replace(f'/{slug}-dark.svg', f'/{slug}-light.svg')
        for row in ['row-01', 'row-02', 'row-03', 'header']:
            readme_html = readme_html.replace(f'assets/writing/{row}.svg', f'assets/writing/{row}-light.svg')
        for proj in ['architecture-as-memory', 'promptnova', 'credflow']:
            readme_html = readme_html.replace(f'assets/projects/{proj}.svg', f'assets/projects/{proj}-light.svg')
        readme_html = readme_html.replace('agent-toolkit.svg', 'agent-toolkit-light.svg')
        readme_html = readme_html.replace('engineering-focus-dark.svg', 'engineering-focus-light.svg')

    html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    background: {bg};
    color: {fg};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 32px 20px;
    display: flex;
    justify-content: center;
  }}
  .markdown-body {{
    max-width: 960px;
    width: 100%;
  }}
  img {{
    max-width: 100%;
    display: inline-block;
    vertical-align: middle;
  }}
  p {{
    margin: 0 0 16px 0;
  }}
  sub {{
    color: {sub_color};
    font-size: 13px;
  }}
  code {{
    background: {code_bg};
    padding: 2px 4px;
    border-radius: 4px;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 12px;
  }}
  a {{
    text-decoration: none;
    color: inherit;
  }}
</style>
</head>
<body>
<div class="markdown-body">
{content}
</div>
</body>
</html>"""

    html = html_template.format(
        bg=bg, fg=fg, sub_color=sub_color, code_bg=code_bg, content=readme_html
    )

    tmp_html = out_dir / f"test_readme_{mode}.html"
    tmp_html.write_text(html, encoding="utf-8")

    out_png = out_dir / f"full_readme_{mode}_preview.png"
    tmp = tempfile.mkdtemp()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--force-prefers-color-scheme={mode}",
        f"--user-data-dir={tmp}",
        "--window-size=1040,5300",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"file:///{tmp_html.as_posix()}",
    ]
    subprocess.run(cmd, check=True)
    print(f"Rendered {mode} preview to: {out_png}")

    # Mobile rendering (viewport width 440px)
    mobile_png = out_dir / f"mobile_readme_{mode}_preview.png"
    mobile_cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--force-prefers-color-scheme={mode}",
        f"--user-data-dir={tmp}",
        "--window-size=440,6400",
        "--hide-scrollbars",
        f"--screenshot={mobile_png}",
        f"file:///{tmp_html.as_posix()}",
    ]
    subprocess.run(mobile_cmd, check=True)
    print(f"Rendered mobile {mode} preview to: {mobile_png}")

if __name__ == '__main__':
    render_preview("dark")
    render_preview("light")
