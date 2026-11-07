"""Render high-fidelity dark and light mode previews of Sections 06 and 07."""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = Path(r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f")

def main():
    for mode, bg in [("dark", "#070B0C"), ("light", "#FFFFFF")]:
        suffix = "-light" if mode == "light" else ""
        tw_cmd = (ROOT / "assets" / "headers" / f"render-technical-writing{suffix}.svg").read_text(encoding="utf-8")
        tw_head = (ROOT / "assets" / "writing" / f"header{suffix}.svg").read_text(encoding="utf-8")
        r1 = (ROOT / "assets" / "writing" / f"row-01{suffix}.svg").read_text(encoding="utf-8")
        r2 = (ROOT / "assets" / "writing" / f"row-02{suffix}.svg").read_text(encoding="utf-8")
        r3 = (ROOT / "assets" / "writing" / f"row-03{suffix}.svg").read_text(encoding="utf-8")

        atlas_hdr = (ROOT / "assets" / "headers" / f"render-contribution-atlas{suffix}.svg").read_text(encoding="utf-8")
        atlas_svg = (ROOT / "assets" / "contributions" / f"atlas-static{suffix}.svg").read_text(encoding="utf-8")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      margin: 0;
      padding: 30px;
      background: {bg};
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    .box {{ width: 1160px; }}
    a {{ display: block; text-decoration: none; width: 1160px; cursor: pointer; }}
  </style>
</head>
<body>
  <div class="box">{tw_cmd}</div>
  <div class="box">{tw_head}</div>
  <a href="https://medium.com/@phoenixarjun007/think-beyond-llms-choosing-the-right-model-for-the-right-job-6a24e3ef0bf3">{r1}</a>
  <a href="https://medium.com/@phoenixarjun007/git-at-agent-scale-what-anthropics-scion-really-teaches-us-fa7bcfa09ade">{r2}</a>
  <a href="https://medium.com/@phoenixarjun007/from-prompts-to-engineering-playbooks-why-i-built-agent-toolkit-efb3f6a7298e">{r3}</a>
  <div style="height: 16px;"></div>
  <div class="box">{atlas_hdr}</div>
  <div class="box">{atlas_svg}</div>
</body>
</html>"""

        tmp_dir = Path(tempfile.mkdtemp())
        tmp_html = tmp_dir / f"preview_{mode}.html"
        tmp_html.write_text(html_content, encoding="utf-8")
        out_png = out_dir / f"sections_06_07_{mode}_preview.png"

        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1260,1100",
            f"--screenshot={out_png}",
            str(tmp_html),
        ]
        subprocess.run(cmd, check=True)
        print("Generated", out_png)

if __name__ == "__main__":
    main()
