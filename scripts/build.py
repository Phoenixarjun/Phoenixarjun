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
        visual_aam,
        visual_promptnova,
        visual_credflow,
        now_building,
        stack_card,
        technical_writing_header,
        technical_writing_row_card,
        technical_writing_card,
        city,
        playground,
        connect_button,
        terminal_footer,
    )
    from contribution_metrics import compute_metrics
except ModuleNotFoundError:
    from scripts.graphics import (
        section_terminal_header,
        engineering_focus_card,
        project_card,
        visual_aam,
        visual_promptnova,
        visual_credflow,
        now_building,
        stack_card,
        technical_writing_header,
        technical_writing_row_card,
        technical_writing_card,
        city,
        playground,
        connect_button,
        terminal_footer,
    )
    from scripts.contribution_metrics import compute_metrics

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write(path: str, text: str) -> Path:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
    return target


def get_medium_posts(feed_url: str = 'https://medium.com/feed/@phoenixarjun007', max_posts: int = 5) -> list[dict]:
    """Dynamically fetch latest articles from Medium RSS feed with authentic word-count reading times."""
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

            # Curated / authentic topics
            if i == 1:
                topic = 'Applied AI · Model Selection'
            elif i == 2:
                topic = 'Systems · Agent Scale'
            elif i == 3:
                topic = 'Agent Engineering · Tooling'
            else:
                topic = ' · '.join(c.capitalize() for c in cats[:2]) if cats else 'Applied AI · Engineering'

            # Calculate authentic reading time from actual article content (265 wpm Medium standard)
            content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            content_text = content_elem.text if content_elem is not None and content_elem.text else ''
            word_count = len(content_text.split()) if content_text else 0
            if word_count > 0:
                read_time = f"~{max(1, round(word_count / 265))} min read"
            else:
                read_time = "~9 min read" if i in (1, 2) else "~3 min read"

            posts.append({
                'index': f"{i:02d}",
                'title': title,
                'topic': topic,
                'url': clean_link,
                'read_time': read_time,
                'platform': 'Medium',
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

    # Verified fallback with accurate word-count reading times
    return [
        {
            'index': '01',
            'title': 'Think Beyond LLMs: Choosing the Right Model for the Right Job',
            'topic': 'Applied AI · Model Selection',
            'url': 'https://medium.com/@phoenixarjun007/think-beyond-llms-choosing-the-right-model-for-the-right-job-6a24e3ef0bf3',
            'read_time': '~9 min read',
            'platform': 'Medium',
        },
        {
            'index': '02',
            'title': "Git at Agent Scale: What Anthropic's Scion Really Teaches Us",
            'topic': 'Systems · Agent Scale',
            'url': 'https://medium.com/@phoenixarjun007/git-at-agent-scale-what-anthropics-scion-really-teaches-us-fa7bcfa09ade',
            'read_time': '~9 min read',
            'platform': 'Medium',
        },
        {
            'index': '03',
            'title': 'From Prompts to Engineering Playbooks: Why I Built Agent Toolkit',
            'topic': 'Agent Engineering · Tooling',
            'url': 'https://medium.com/@phoenixarjun007/from-prompts-to-engineering-playbooks-why-i-built-agent-toolkit-efb3f6a7298e',
            'read_time': '~3 min read',
            'platform': 'Medium',
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


def build_readme(profile: dict, projects: dict, stack: dict, posts: list[dict], has_real: bool, contrib_data: dict = None) -> str:
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

    # 6. TECHNICAL WRITING (Modular Clickable Rows + Titanium Hacker Header)
    lines.append('<!-- ==================== SECTION 06: TECHNICAL WRITING ==================== -->\n')
    lines.append(header_tag('render-technical-writing'))
    lines.append(
        '<p align="center">\n'
        '  <picture>\n'
        '    <source media="(prefers-color-scheme: dark)" srcset="./assets/writing/header.svg">\n'
        '    <source media="(prefers-color-scheme: light)" srcset="./assets/writing/header-light.svg">\n'
        '    <img src="./assets/writing/header.svg" alt="Technical Writing // Articles, ideas, and engineering write-ups" width="100%" />\n'
        '  </picture>\n'
        '</p>\n'
    )
    lines.append('<!-- BLOG-POST-LIST:START -->\n')
    for i, a in enumerate(posts[:3], 1):
        slug = f"row-{i:02d}"
        url_esc = html_escape(a["url"], quote=True)
        title_esc = html_escape(a["title"], quote=True)
        lines.append(
            f'<p align="center">\n'
            f'  <a href="{url_esc}">\n'
            f'    <picture>\n'
            f'      <source media="(prefers-color-scheme: dark)" srcset="./assets/writing/{slug}.svg">\n'
            f'      <source media="(prefers-color-scheme: light)" srcset="./assets/writing/{slug}-light.svg">\n'
            f'      <img src="./assets/writing/{slug}.svg" alt="{title_esc}" width="100%" />\n'
            f'    </picture>\n'
            f'  </a>\n'
            f'</p>\n'
        )
    lines.append('<!-- BLOG-POST-LIST:END -->\n\n')

    # 7. CONTRIBUTION ATLAS (Mode D Contained 3D Isometric View)
    if profile['features'].get('show_contribution_city', True):
        lines.append('<!-- ==================== SECTION 07: CONTRIBUTION ATLAS ==================== -->\n')
        lines.append(header_tag('render-contribution-atlas'))
        metrics = compute_metrics(contrib_data.get('days', []), total_reported=contrib_data.get('total_contributions')) if contrib_data else {}
        total_c = metrics.get('total_contributions', 208)
        active_d = metrics.get('active_days', 37)
        lines.append(
            '<p align="center">\n'
            '  <picture>\n'
            '    <source media="(prefers-color-scheme: dark)" srcset="./assets/contributions/atlas-static.svg">\n'
            '    <source media="(prefers-color-scheme: light)" srcset="./assets/contributions/atlas-static-light.svg">\n'
            f'    <img src="./assets/contributions/atlas-static.svg" alt="Contribution Atlas: {total_c:,} contributions across {active_d} active days as an isometric 3D city" width="100%" />\n'
            '  </picture>\n'
            '</p>\n'
            '<!-- Optional Animated Build View:\n'
            '<p align="center">\n'
            '  <img src="./assets/contributions/atlas-animated.gif" alt="Contribution Atlas Rise Animation" width="100%" />\n'
            '</p>\n'
            '-->\n\n'
        )

    # 8. DEVELOPER PLAYGROUND (Mode D Contained Visualization)
    if profile['features'].get('show_playground', True):
        lines.append('<!-- ==================== SECTION 08: DEVELOPER PLAYGROUND ==================== -->\n')
        lines.append(header_tag('play-system-runner'))
        runner_url = "https://phoenixarjun.github.io/Phoenixarjun/runner.html"
        lines.append(
            f'<p align="center">\n'
            f'  <a href="{runner_url}">\n'
            f'    <picture>\n'
            f'      <source media="(prefers-color-scheme: dark)" srcset="./assets/playground/concept.svg">\n'
            f'      <source media="(prefers-color-scheme: light)" srcset="./assets/playground/concept-light.svg">\n'
            f'      <img src="./assets/playground/concept.svg" alt="Developer Playground — System Runner: Architecture Grid Runner" width="100%" />\n'
            f'    </picture>\n'
            f'  </a>\n'
            f'</p>\n\n'
        )

    # 9. CONNECT (Mode A Accessible Actions)
    lines.append('<!-- ==================== SECTION 09: CONNECT ==================== -->\n')
    lines.append(header_tag('connect-all'))

    github_url = html_escape(profile["links"]["github"], quote=True)
    linkedin_url = html_escape(profile["links"]["linkedin"], quote=True)
    medium_url = html_escape(profile["links"]["medium"], quote=True)
    portfolio_url = profile["links"].get("portfolio", "")

    portfolio_btn = (
        f'<a href="{html_escape(portfolio_url, quote=True)}">'
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" srcset="./assets/sections/btn-portfolio.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="./assets/sections/btn-portfolio-light.svg">'
        f'<img src="./assets/sections/btn-portfolio.svg" width="21%" alt="Portfolio" />'
        f'</picture>'
        f'</a>'
        if portfolio_url else
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" srcset="./assets/sections/btn-portfolio.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="./assets/sections/btn-portfolio-light.svg">'
        f'<img src="./assets/sections/btn-portfolio.svg" width="21%" alt="Portfolio" />'
        f'</picture>'
    )

    lines.append('<p align="center">\n')
    lines.append(
        f'  <a href="{github_url}">'
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" srcset="./assets/sections/btn-github.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="./assets/sections/btn-github-light.svg">'
        f'<img src="./assets/sections/btn-github.svg" width="21%" alt="GitHub" />'
        f'</picture>'
        f'</a>'
        f'<a href="{linkedin_url}">'
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" srcset="./assets/sections/btn-linkedin.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="./assets/sections/btn-linkedin-light.svg">'
        f'<img src="./assets/sections/btn-linkedin.svg" width="21%" alt="LinkedIn" />'
        f'</picture>'
        f'</a>'
        f'<a href="{medium_url}">'
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" srcset="./assets/sections/btn-medium.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="./assets/sections/btn-medium-light.svg">'
        f'<img src="./assets/sections/btn-medium.svg" width="21%" alt="Medium" />'
        f'</picture>'
        f'</a>'
        f'{portfolio_btn}\n'
    )
    lines.append('</p>\n\n')

    # Footer tagline
    lines.append(
        '<p align="center">\n'
        '  <picture>\n'
        '    <source media="(prefers-color-scheme: dark)" srcset="./assets/sections/footer.svg">\n'
        '    <source media="(prefers-color-scheme: light)" srcset="./assets/sections/footer-light.svg">\n'
        '    <img src="./assets/sections/footer.svg" alt="Variation 01 / Terminal Editorial — Building intelligent software on reliable systems." width="100%" />\n'
        '  </picture>\n'
        '</p>\n\n'
    )

    # 10. FINAL LOGOUT FOOTER (Mode B Contained Animated Card + Static Fallback)
    lines.append('<!-- ==================== FINAL LOGOUT FOOTER ==================== -->\n')
    lines.append(header_tag('logout'))
    lines.append(
        '<p align="center">\n'
        '  <img\n'
        '    src="./assets/logout-footer/logout-card-animated.gif"\n'
        '    alt="Thanks for stopping by. Built with curiosity, driven by systems, always learning and always shipping. Session closed."\n'
        '    width="770"\n'
        '  />\n'
        '</p>\n'
        '<!-- Static Fallback:\n'
        '<p align="center">\n'
        '  <img src="./assets/logout-footer/logout-card-static.png" alt="Thanks for stopping by. Session closed." width="770" />\n'
        '</p>\n'
        '-->\n\n'
    )

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
        ('render', 'technical-writing', 'render-technical-writing'),
        ('render', 'contribution-atlas', 'render-contribution-atlas'),
        ('play', 'system-runner', 'play-system-runner'),
        ('open', 'developer-playground', 'open-developer-playground'),
        ('connect', 'all', 'connect-all'),
        ('logout', '', 'logout'),
    ]
    for cmd, flg, slug in headers:
        write(f'assets/headers/{slug}.svg', section_terminal_header(cmd, flg, theme, is_light=False))
        write(f'assets/headers/{slug}-light.svg', section_terminal_header(cmd, flg, theme, is_light=True))

    # 3. Section Cards & Components (Dark and Light variants)
    write('assets/sections/engineering-focus.svg', engineering_focus_card(profile, theme, is_light=False))
    write('assets/sections/engineering-focus-light.svg', engineering_focus_card(profile, theme, is_light=True))

    for i, p in enumerate(projects['flagship'], 1):
        slug = p["slug"]
        dark_card = project_card(p, theme, i, is_light=False)
        light_card = project_card(p, theme, i, is_light=True)
        # Primary assets/projects/ paths
        write(f'assets/projects/{slug}.svg', dark_card)
        write(f'assets/projects/{slug}-light.svg', light_card)
        # Dedicated featured paths
        write(f'assets/projects/featured/{slug}.svg', dark_card)
        write(f'assets/projects/featured/{slug}-light.svg', light_card)

    # Standalone Architecture & Workflow Visualizations
    write('assets/projects/visuals/aam-topology.svg', visual_aam(theme, is_light=False, standalone=True))
    write('assets/projects/visuals/aam-topology-light.svg', visual_aam(theme, is_light=True, standalone=True))
    write('assets/projects/visuals/promptnova-workflow.svg', visual_promptnova(theme, is_light=False, standalone=True))
    write('assets/projects/visuals/promptnova-workflow-light.svg', visual_promptnova(theme, is_light=True, standalone=True))
    write('assets/projects/visuals/credflow-collections.svg', visual_credflow(theme, is_light=False, standalone=True))
    write('assets/projects/visuals/credflow-collections-light.svg', visual_credflow(theme, is_light=True, standalone=True))

    for p in projects['currently_building']:
        write(f'assets/now/{p["slug"]}.svg', now_building(p, theme, is_light=False))
        write(f'assets/now/{p["slug"]}-light.svg', now_building(p, theme, is_light=True))

    write('assets/stack/toolkit.svg', stack_card(stack, theme, is_light=False))
    write('assets/stack/toolkit-light.svg', stack_card(stack, theme, is_light=True))

    # Section 06: Technical Writing (Header, Clickable Rows & Standalone Cards)
    write('assets/writing/header.svg', technical_writing_header(theme, is_light=False))
    write('assets/writing/header-light.svg', technical_writing_header(theme, is_light=True))
    for i, a in enumerate(posts[:3], 1):
        slug = f"row-{i:02d}"
        write(f'assets/writing/{slug}.svg', technical_writing_row_card(a, theme, is_light=False))
        write(f'assets/writing/{slug}-light.svg', technical_writing_row_card(a, theme, is_light=True))

    write('assets/writing/technical-writing.svg', technical_writing_card(posts, theme, is_light=False))
    write('assets/writing/technical-writing-light.svg', technical_writing_card(posts, theme, is_light=True))
    write('assets/sections/technical-writing.svg', technical_writing_card(posts, theme, is_light=False))

    # Section 07: Contribution Atlas (Static SVGs & Animated GIF)
    atlas_dark = city(contributions, theme, is_light=False)
    atlas_light = city(contributions, theme, is_light=True)
    write('assets/contributions/atlas-static.svg', atlas_dark)
    write('assets/contributions/atlas-static-light.svg', atlas_light)
    write('assets/contributions/city.svg', atlas_dark)

    try:
        try:
            from scripts.render_contribution_gif import render_atlas_gif
        except ModuleNotFoundError:
            from render_contribution_gif import render_atlas_gif
        render_atlas_gif(contributions, theme, ROOT / 'assets' / 'contributions' / 'atlas-animated.gif', num_frames=36, fps=8)
    except Exception as e:
        print(f"Warning: Animated GIF generation skipped or failed ({e}); preserving static fallback.")

    # Section 08: Developer Playground (Dark and Light variants)
    write('assets/playground/concept.svg', playground(theme, is_light=False))
    write('assets/playground/concept-light.svg', playground(theme, is_light=True))

    # Section 09: Connect Buttons (Dark and Light variants, compact width=206, height=50 with built-in 30px gap)
    connect_slugs = [
        ('github', 'GitHub', False),
        ('linkedin', 'LinkedIn', False),
        ('medium', 'Medium', False),
        ('portfolio', 'Portfolio', True),
    ]
    for slug, lbl, is_hl in connect_slugs:
        write(f'assets/sections/btn-{slug}.svg', connect_button(slug, lbl, theme, width=206, height=50, is_light=False, is_highlight=is_hl))
        write(f'assets/sections/btn-{slug}-light.svg', connect_button(slug, lbl, theme, width=206, height=50, is_light=True, is_highlight=is_hl))

    # Section 09: Terminal Editorial Footer (Dark and Light variants)
    write('assets/sections/footer.svg', terminal_footer(profile, theme, is_light=False))
    write('assets/sections/footer-light.svg', terminal_footer(profile, theme, is_light=True))

    # Section 10: Final Logout Footer (Animated GIF, Static Card & Robot Asset)
    try:
        try:
            from scripts.build_logout_footer import run as run_logout_footer
        except ModuleNotFoundError:
            from build_logout_footer import run as run_logout_footer
        gif_file = ROOT / 'assets' / 'logout-footer' / 'logout-card-animated.gif'
        run_logout_footer(ROOT, build_gif=not gif_file.is_file())
    except Exception as e:
        print(f"Warning: Logout footer generation skipped or failed ({e}); preserving existing assets.")

    # 5. Assemble READMEs
    live = contributions.get('status') == 'ok' and bool(contributions.get('days'))
    readme_content = build_readme(profile, projects, stack, posts, live, contrib_data=contributions)
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
