"""Build self-contained GitHub-compatible SVG assets and README.v2.md.

By design, this script NEVER writes README.md or changes .github/workflows.
Everything is free, deterministic (except live GitHub contribution fetch), and
uses Python's standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from html import escape as html_escape

try:
    from graphics import hero, project_card, now_building, stack_card, city, playground
except ModuleNotFoundError:
    from scripts.graphics import hero, project_card, now_building, stack_card, city, playground

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def write(path, text):
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(text,encoding='utf-8')
    return target


def md_escape(text):
    return str(text).replace('|','\\|').replace('[','\\[').replace(']','\\]')


def section_header(s,sub=None):
    return f'## {s}\n\n'+(sub+'\n\n' if sub else '')


def img(src,alt):
    return f'<p align="center"><img src="{html_escape(src,quote=True)}" alt="{html_escape(alt,quote=True)}" width="100%" /></p>\n\n'


def build_readme(profile,projects,stack,writing,has_real):
    lines=[]
    lines.append('<!-- GENERATED FILE: edit content/*.json or design/themes.json, then run python scripts/build.py. -->\n')
    lines.append('<!-- Preview only. Existing README.md is deliberately untouched. -->\n\n')
    lines.append('<!-- Regenerate hero assets: python scripts/generate_hero_svg.py && python scripts/render_hero_gif.py -->\n')
    lines.append('<p align="center">\n  <img src="./assets/generated/hero/hero-animated.gif" alt="Naresh B A — AI Systems Engineer" width="100%" />\n</p>\n\n')
    lines.append('<!-- Fallback:\n<p align="center">\n  <img src="./assets/generated/hero/hero-static.svg" alt="Naresh B A — AI Systems Engineer" width="100%" />\n</p>\n-->\n\n')
    links=profile['links']
    nav=[('GitHub',links['github']),('LinkedIn',links['linkedin']),('Medium',links['medium'])]
    if profile['features'].get('show_portfolio') and links.get('portfolio'):
        nav.append(('Portfolio',links['portfolio']))
    lines.append('<p align="center">'+' &nbsp;·&nbsp; '.join(f'<a href="{html_escape(url,quote=True)}">{html_escape(label)}</a>' for label,url in nav)+'</p>\n\n')
    lines.append('---\n\n')
    lines.append(section_header('Engineering focus'))
    lines.append(profile['overview']+'\n\n')
    for pillar in profile['engineering_pillars']:
        lines.append(f'- **{md_escape(pillar["title"])}:** {md_escape(pillar["description"])}\n')
    lines.append('\n---\n\n')
    lines.append(section_header('Flagship projects','Selected public projects with engineering-focused write-ups.'))
    for p in projects['flagship']:
        lines.append(f'<a href="{html_escape(p["url"],quote=True)}"><img src="assets/projects/{p["slug"]}.svg" alt="{html_escape(p["name"],quote=True)} project showcase" width="100%" /></a>\n\n')
        lines.append(f'**[{md_escape(p["name"])}]({p["url"]})** · {md_escape(p["category"])}\n\n')
    lines.append('---\n\n')
    lines.append(section_header('Currently building','Active, evolving work — separate from the flagship portfolio.'))
    for p in projects['currently_building']:
        lines.append(f'<a href="{html_escape(p["url"],quote=True)}"><img src="assets/now/{p["slug"]}.svg" alt="{html_escape(p["name"],quote=True)} currently building" width="100%" /></a>\n\n')
        lines.append(f'**[{md_escape(p["name"])}]({p["url"]})** · {md_escape(p["status"])}\n\n')
    lines.append('---\n\n')
    lines.append(section_header('Engineering toolkit'))
    lines.append(img('assets/stack/toolkit.svg','Engineering domains and technologies'))
    lines.append('---\n\n')
    lines.append(section_header('Technical writing','Selected articles about designing, building, and evaluating software systems.'))
    for a in writing['featured']:
        lines.append(f'- **[{md_escape(a["title"])}]({a["url"]})** — {md_escape(a["topic"])}\n')
    lines.append('\n---\n\n')
    if profile['features'].get('show_contribution_city'):
        lines.append(section_header('Contribution atlas'))
        lines.append(img('assets/contributions/city.svg','Isometric GitHub contribution city'))
        if not has_real:
            lines.append('> Design preview only — the graphic uses clearly labeled sample geometry until GitHub contribution data has been fetched.\n\n')
        lines.append('---\n\n')
    if profile['features'].get('show_playground'):
        lines.append(section_header('Developer playground'))
        lines.append(img('assets/playground/concept.svg','System Runner concept — game not yet implemented'))
        lines.append('> Concept only. Add a working GitHub Pages link before enabling this section.\n\n')
        lines.append('---\n\n')
    lines.append(section_header('Connect'))
    lines.append(f'**Building intelligent software on reliable systems.**\n\n')
    lines.append(' &nbsp;·&nbsp; '.join(f'[{label}]({url})' for label,url in nav)+'\n\n')
    lines.append(f'<sub>{md_escape(profile["name"])} · {md_escape(profile["location"])}</sub>\n')
    return ''.join(lines)


def build(theme_override=None,save=False,previews=True):
    settings=read('design/themes.json')
    key=theme_override or settings['active']
    if key not in settings['presets']:
        raise ValueError(f'Unknown theme: {key}; valid: {", ".join(settings["presets"])}')
    if save:
        settings['active']=key
        write('design/themes.json',json.dumps(settings,indent=2,ensure_ascii=False)+'\n')
    theme=settings['presets'][key]
    profile=read('content/profile.json')
    projects=read('content/projects.json')
    stack=read('content/stack.json')
    writing=read('content/writing.json')
    contributions=read('data/contributions.json')
    write('assets/hero/identity.svg',hero(profile,theme))
    for i,p in enumerate(projects['flagship'],1):
        write(f'assets/projects/{p["slug"]}.svg',project_card(p,theme,i))
    for p in projects['currently_building']:
        write(f'assets/now/{p["slug"]}.svg',now_building(p,theme))
    write('assets/stack/toolkit.svg',stack_card(stack,theme))
    write('assets/contributions/city.svg',city(contributions,theme))
    write('assets/playground/concept.svg',playground(theme))
    live=contributions.get('status')=='ok' and bool(contributions.get('days'))
    write('README.v2.md',build_readme(profile,projects,stack,writing,live))
    if previews:
        make_previews(settings,profile)
    print(f'Built README.v2.md + SVG assets with theme: {key} (contributions: {"live" if live else "sample preview"})')
    return key


def make_previews(settings,profile):
    swatch_labels=['base','surface','stroke','accent','text']
    cards=[]
    for key,t in settings['presets'].items():
        file=f'previews/heroes/{key}.svg'
        write(file,hero(profile,t))
        samples=''.join(f'<span class="swatch"><i style="background:{t[k]}"></i><code>{t[k]}</code></span>' for k in swatch_labels)
        cards.append(f'<article><h2>{html_escape(t["name"])}</h2><p>{html_escape(t["description"])}</p><div class="swatches">{samples}</div><img src="heroes/{key}.svg" alt="{html_escape(t["name"])} preview" /></article>')
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GitHub Profile V2 · Theme Comparison</title><style>
    :root{color-scheme:dark;font-family:Inter,Segoe UI,Arial,sans-serif;background:#0e1012;color:#eef3f0}
    *{box-sizing:border-box}body{max-width:1370px;margin:0 auto;padding:28px}h1{font-size:clamp(26px,4vw,46px);margin:0 0 8px}header p,article p{color:#abb8b2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(520px,100%),1fr));gap:20px;margin-top:34px}
    article{border:1px solid #35403b;border-radius:16px;padding:20px;background:#171c1a}article h2{margin:0;font-size:22px}article img{width:100%;border-radius:12px;margin-top:16px}
    .swatches{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.swatch{display:grid;gap:6px}.swatch i{display:block;width:54px;height:30px;border-radius:5px;border:1px solid #607068}.swatch code{color:#aebcb4;font-size:10px}
    footer{color:#8ca097;margin-top:32px;font-size:13px}</style></head><body><header><h1>GitHub Profile · Theme Comparison</h1><p>Change the active theme in <code>design/themes.json</code>, or run <code>python scripts/build.py --theme midnight-circuit --save-theme</code>.</p></header><main>'''+''.join(cards)+'''</main><footer>SVG graphics are generated from the same centralized palette configuration.</footer></body></html>'''
    write('previews/compare-themes.html',html)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme',help='Render a specific preset without changing the saved default')
    parser.add_argument('--save-theme',action='store_true',help='Persist --theme to design/themes.json')
    parser.add_argument('--skip-previews',action='store_true')
    args=parser.parse_args()
    if args.save_theme and not args.theme:
        parser.error('--save-theme requires --theme')
    build(args.theme,args.save_theme,not args.skip_previews)

if __name__=='__main__':
    main()
