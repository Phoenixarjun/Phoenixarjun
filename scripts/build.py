"""Build self-contained GitHub-compatible SVG assets and README.v2.md / README.md.

Adheres strictly to Titanium Hacker design specifications and unified rendering:
- Standardized reference width (1160px) and transparent root canvases (Mode A)
- Dual-mode Dark/Light theme switching via GitHub-supported <picture> syntax
- Intentional contained surfaces for cards and HUD modules (Mode B & Mode D)
- Standalone animated hero panel (Mode C)
- Clean, accessible native Markdown links for Technical Writing (no duplicate SVG)
- Theme centralization strictly flowing from design/themes.json
"""
from __future__ import annotations

import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from html import escape as html_escape

try:
    from graphics import (
        section_terminal_header,
        engineering_focus_card,
        project_card,
        now_building,
        stack_card,
        technical_writing_card,
        city,
        playground,
        connect_button,
    )
except ModuleNotFoundError:
    from scripts.graphics import (
        section_terminal_header,
        engineering_focus_card,
        project_card,
        now_building,
        stack_card,
        technical_writing_card,
        city,
        playground,
        connect_button,
    )

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write(path: str, text: str) -> Path:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
    return target


def get_medium_posts(feed_url: str = 'https://medium.com/feed/@phoenixarjun007', max_posts: int = 5) -> list[dict]:
    """Dynamically fetch latest articles from Medium RSS feed with local caching."""
    try:
        req = urllib.request.Request(
            feed_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            content = resp.read()
        root = ET.fromstring(content)
        items = root.findall('./channel/item')
        posts = []
        for i, item in enumerate(items[:max_posts], 1):
            title = item.find('title').text.strip() if item.find('title') is not None else ''
            link = item.find('link').text.strip() if item.find('link') is not None else ''
            clean_link = link.split('?')[0] if '?' in link else link
            cats = [c.text for c in item.findall('category') if c.text]
            topic = ' · '.join(c.capitalize() for c in cats[:2]) if cats else 'Applied AI · Engineering'
            posts.append({
                'index': f"{i:02d}",
                'title': title,
                'topic': topic,
                'url': clean_link,
            })
        if posts:
            cache_file = ROOT / 'data' / 'blog_cache.json'
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps({'status': 'ok', 'posts': posts}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            return posts
    except Exception:
        pass

    # Read from cache if network fails
    cache_file = ROOT / 'data' / 'blog_cache.json'
    if cache_file.is_file():
        try:
            return json.loads(cache_file.read_text(encoding='utf-8')).get('posts', [])
        except Exception:
            pass

    # Safe initial fallback
    return [
        {
            'index': '01',
            'title': 'Think Beyond LLMs: Choosing the Right Model for the Right Job',
            'topic': 'Applied AI · Model selection',
            'url': 'https://medium.com/@phoenixarjun007/think-beyond-llms-choosing-the-right-model-for-the-right-job-6a24e3ef0bf3',
        },
        {
            'index': '02',
            'title': "Git at Agent Scale: What Anthropic's Scion Really Teaches Us",
            'topic': 'Agent engineering · Git',
            'url': 'https://medium.com/@phoenixarjun007/git-at-agent-scale-what-anthropics-scion-really-teaches-us-fa7bcfa09ade',
        },
        {
            'index': '03',
            'title': 'From Prompts to Engineering Playbooks: Why I Built Agent Toolkit',
            'topic': 'Developer tooling · Engineering playbooks',
            'url': 'https://medium.com/@phoenixarjun007/from-prompts-to-engineering-playbooks-why-i-built-agent-toolkit-efb3f6a7298e',
        },
    ]


def header_tag(slug: str) -> str:
    """Return GitHub-compliant <picture> tag for dark/light terminal command separators."""
    return (
        f'<p align="center">\n'
        f'  <picture>\n'
        f'    <source media="(prefers-color-scheme: dark)" srcset="./assets/headers/{slug}.svg">\n'
        f'    <source media="(prefers-color-scheme: light)" srcset="./assets/headers/{slug}-light.svg">\n'
        f'    <img src="./assets/headers/{slug}.svg" width="100%" />\n'
        f'  </picture>\n'
        f'</p>\n'
    )


def build_readme(profile: dict, projects: dict, stack: dict, posts: list[dict], has_real: bool) -> str:
    lines = []
    lines.append('<!-- GENERATED FILE: edit content/*.json or design/themes.json, then run python scripts/build.py. -->\n\n')

    # 1. HERO IDENTITY (Mode C: Independent Cyber Card)
    lines.append('<!-- ==================== SECTION 01: IDENTITY / HERO ==================== -->\n')
    lines.append('<!-- Regenerate hero assets: python scripts/generate_hero_svg.py && python scripts/render_hero_gif.py -->\n')
    lines.append('<p align="center">\n  <img src="./assets/generated/hero/hero-animated.gif" alt="Naresh B A — AI Systems Engineer" width="100%" />\n</p>\n\n')
    lines.append('<!-- Fallback:\n<p align="center">\n  <img src="./assets/generated/hero/hero-static.svg" alt="Naresh B A — AI Systems Engineer" width="100%" />\n</p>\n-->\n\n')

    # 2. ENGINEERING FOCUS (Mode A Transparent Canvas with Mode B Contained Pods)
    lines.append('<!-- ==================== SECTION 02: ENGINEERING FOCUS ==================== -->\n')
    lines.append('<!-- PROFILE:ENGINEERING-FOCUS:START -->\n')
    lines.append(header_tag('inspect-engineering-focus'))
    lines.append('<p align="center">\n')
    lines.append('  <picture>\n')
    lines.append('    <source media="(prefers-color-scheme: dark)" srcset="./assets/engineering-focus/engineering-focus-dark.svg">\n')
    lines.append('    <source media="(prefers-color-scheme: light)" srcset="./assets/engineering-focus/engineering-focus-light.svg">\n')
    lines.append('    <img src="./assets/engineering-focus/engineering-focus-dark.svg"\n')
    lines.append('         alt="Engineering Focus: Applied AI Systems, Backend Engineering, Distributed and Reliable Platforms; enabling practices Automation, Observability, and Production Engineering."\n')
    lines.append('         width="100%" />\n')
    lines.append('  </picture>\n')
    lines.append('</p>\n')
    lines.append('<!-- PROFILE:ENGINEERING-FOCUS:END -->\n\n')

    # 3. FLAGSHIP PROJECTS (Mode A Transparent Outer Rows with Mode B Architecture Previews)
    lines.append('<!-- ==================== SECTION 03: FLAGSHIP PROJECTS ==================== -->\n')
    lines.append(header_tag('ls-flagship-projects'))
    for p in projects['flagship']:
        slug = p["slug"]
        lines.append(
            f'<p align="center">\n'
            f'  <a href="{html_escape(p["url"], quote=True)}">\n'
            f'    <picture>\n'
            f'      <source media="(prefers-color-scheme: dark)" srcset="./assets/projects/{slug}.svg">\n'
            f'      <source media="(prefers-color-scheme: light)" srcset="./assets/projects/{slug}-light.svg">\n'
            f'      <img src="./assets/projects/{slug}.svg" alt="{html_escape(p["name"], quote=True)}" width="100%" />\n'
            f'    </picture>\n'
            f'  </a>\n'
            f'</p>\n'
        )
    lines.append('\n')

    # 4. CURRENTLY BUILDING (Mode B Contained HUD Surface)
    lines.append('<!-- ==================== SECTION 04: CURRENTLY BUILDING ==================== -->\n')
    lines.append(header_tag('status-currently-building'))
    for p in projects['currently_building']:
        slug = p["slug"]
        lines.append(
            f'<p align="center">\n'
            f'  <a href="{html_escape(p["url"], quote=True)}">\n'
            f'    <picture>\n'
            f'      <source media="(prefers-color-scheme: dark)" srcset="./assets/now/{slug}.svg">\n'
            f'      <source media="(prefers-color-scheme: light)" srcset="./assets/now/{slug}-light.svg">\n'
            f'      <img src="./assets/now/{slug}.svg" alt="{html_escape(p["name"], quote=True)}" width="100%" />\n'
            f'    </picture>\n'
            f'  </a>\n'
            f'</p>\n'
        )
    lines.append('\n')

    # 5. ENGINEERING STACK (Mode A Transparent Terminal Matrix)
    lines.append('<!-- ==================== SECTION 05: ENGINEERING STACK ==================== -->\n')
    lines.append(header_tag('cat-engineering-stack'))
    lines.append(
        '<p align="center">\n'
        '  <picture>\n'
        '    <source media="(prefers-color-scheme: dark)" srcset="./assets/stack/toolkit.svg">\n'
        '    <source media="(prefers-color-scheme: light)" srcset="./assets/stack/toolkit-light.svg">\n'
        '    <img src="./assets/stack/toolkit.svg" alt="Engineering Stack" width="100%" />\n'
        '  </picture>\n'
        '</p>\n\n'
    )

    # 6. TECHNICAL WRITING (Deduplicated: Native Accessible Markdown Links only)
    lines.append('<!-- ==================== SECTION 06: TECHNICAL WRITING ==================== -->\n')
    lines.append(header_tag('read-technical-writing'))
    lines.append('<!-- BLOG-POST-LIST:START -->\n')
    for a in posts:
        lines.append(f'- **[{html_escape(a["title"])}]({html_escape(a["url"], quote=True)})**\n')
    lines.append('<!-- BLOG-POST-LIST:END -->\n\n')

    # 7. CONTRIBUTION ATLAS (Mode D Contained Visualization)
    if profile['features'].get('show_contribution_city', True):
        lines.append('<!-- ==================== SECTION 07: CONTRIBUTION ATLAS ==================== -->\n')
        lines.append(header_tag('render-contribution-atlas'))
        lines.append('<p align="center"><img src="./assets/contributions/city.svg" alt="Contribution Atlas" width="100%" /></p>\n\n')

    # 8. DEVELOPER PLAYGROUND (Mode D Contained Visualization)
    if profile['features'].get('show_playground', True):
        lines.append('<!-- ==================== SECTION 08: DEVELOPER PLAYGROUND ==================== -->\n')
        lines.append(header_tag('open-developer-playground'))
        lines.append('<p align="left"><sub>A little personality, without distracting from the engineering.</sub></p>\n')
        lines.append('<p align="center"><img src="./assets/playground/concept.svg" alt="Developer Playground" width="100%" /></p>\n\n')

    # 9. CONNECT (Mode A Accessible Actions)
    lines.append('<!-- ==================== SECTION 09: CONNECT ==================== -->\n')
    lines.append(header_tag('connect-all'))
    lines.append('<p align="center">\n')
    lines.append(f'  <a href="{html_escape(profile["links"]["github"], quote=True)}"><img src="./assets/sections/btn-github.svg" height="44" alt="GitHub" /></a> &nbsp;\n')
    lines.append(f'  <a href="{html_escape(profile["links"]["linkedin"], quote=True)}"><img src="./assets/sections/btn-linkedin.svg" height="44" alt="LinkedIn" /></a> &nbsp;\n')
    lines.append(f'  <a href="{html_escape(profile["links"]["medium"], quote=True)}"><img src="./assets/sections/btn-medium.svg" height="44" alt="Medium" /></a> &nbsp;\n')
    lines.append('  <img src="./assets/sections/btn-portfolio.svg" height="44" alt="Portfolio (soon)" />\n')
    lines.append('</p>\n\n')

    # Footer tagline
    lines.append('<p align="center">\n')
    lines.append(f'  <sub>{html_escape(profile["tagline"])}</sub><br/>\n')
    lines.append('  <sub><code>VARIATION 01 / TERMINAL EDITORIAL</code></sub>\n')
    lines.append('</p>\n')

    return ''.join(lines)


def build(theme_override=None, save=False):
    settings = read('design/themes.json')
    key = theme_override or settings['active']
    if key not in settings['presets']:
        raise ValueError(f'Unknown theme: {key}; valid: {", ".join(settings["presets"])}')
    if save:
        settings['active'] = key
        write('design/themes.json', json.dumps(settings, indent=2, ensure_ascii=False) + '\n')
    theme = settings['presets'][key]

    profile = read('content/profile.json')
    projects = read('content/projects.json')
    stack = read('content/stack.json')
    contributions = read('data/contributions.json')

    # Fetch blog posts directly from Medium RSS (no static writing.json)
    posts = get_medium_posts(
        feed_url=f"https://medium.com/feed/@{profile['github_username'].lower()}" if not profile.get('links', {}).get('medium') else profile['links']['medium'].replace('https://medium.com/', 'https://medium.com/feed/'),
        max_posts=5,
    )

    # 1. Engineering Focus Section Assets (Dual-mode 1160px SVGs)
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_engineering_focus.py')], check=True)

    # 2. Section Header Dividers (Dual-mode Dark and Light variants)
    headers = [
        ('inspect', 'engineering-focus', 'inspect-engineering-focus'),
        ('ls', 'flagship-projects', 'ls-flagship-projects'),
        ('status', 'currently-building', 'status-currently-building'),
        ('cat', 'engineering-stack', 'cat-engineering-stack'),
        ('read', 'technical-writing', 'read-technical-writing'),
        ('render', 'contribution-atlas', 'render-contribution-atlas'),
        ('open', 'developer-playground', 'open-developer-playground'),
        ('connect', 'all', 'connect-all'),
    ]
    for cmd, flg, slug in headers:
        write(f'assets/headers/{slug}.svg', section_terminal_header(cmd, flg, theme, is_light=False))
        write(f'assets/headers/{slug}-light.svg', section_terminal_header(cmd, flg, theme, is_light=True))

    # 3. Section Cards & Components (Dark and Light variants)
    write('assets/sections/engineering-focus.svg', engineering_focus_card(profile, theme, is_light=False))
    write('assets/sections/engineering-focus-light.svg', engineering_focus_card(profile, theme, is_light=True))

    for i, p in enumerate(projects['flagship'], 1):
        write(f'assets/projects/{p["slug"]}.svg', project_card(p, theme, i, is_light=False))
        write(f'assets/projects/{p["slug"]}-light.svg', project_card(p, theme, i, is_light=True))

    for p in projects['currently_building']:
        write(f'assets/now/{p["slug"]}.svg', now_building(p, theme, is_light=False))
        write(f'assets/now/{p["slug"]}-light.svg', now_building(p, theme, is_light=True))

    write('assets/stack/toolkit.svg', stack_card(stack, theme, is_light=False))
    write('assets/stack/toolkit-light.svg', stack_card(stack, theme, is_light=True))

    # Backward compatibility for any external references
    write('assets/sections/technical-writing.svg', technical_writing_card(posts, theme, is_light=False))
    write('assets/contributions/city.svg', city(contributions, theme))
    write('assets/playground/concept.svg', playground(theme))

    # 4. Connect Buttons
    write('assets/sections/btn-github.svg', connect_button('GitHub', theme))
    write('assets/sections/btn-linkedin.svg', connect_button('LinkedIn', theme))
    write('assets/sections/btn-medium.svg', connect_button('Medium', theme))
    write('assets/sections/btn-portfolio.svg', connect_button('Portfolio (soon)', theme))

    # 5. Assemble READMEs
    live = contributions.get('status') == 'ok' and bool(contributions.get('days'))
    readme_content = build_readme(profile, projects, stack, posts, live)
    write('README.v2.md', readme_content)
    write('README.md', readme_content)

    print(f'Built full Variation 01 layout with theme: {key} (Medium blog feed: live, contributions: {"live" if live else "sample"})')
    return key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', help='Render a specific preset')
    parser.add_argument('--save-theme', action='store_true')
    parser.add_argument('--skip-previews', action='store_true')
    args = parser.parse_args()
    build(args.theme, args.save_theme)


if __name__ == '__main__':
    main()
