# GitHub Profile 2.0 — Titanium Hacker Starter Kit

This is a **safe, copy-and-paste starter kit** for the **existing** public `Phoenixarjun/Phoenixarjun` GitHub profile repository.

**Important:** The ZIP deliberately contains **no `README.md` and no `.github/` directory**. Your current README and existing workflows remain untouched when you merge the contents of this ZIP into your repository.

## What is already included?

- Complete **nine-section content architecture**, with a first-pass draft of the actual README in `README.v2.md`.
- Generated SVG artwork for the hero, three **current public** flagship projects (AAM, PromptNova, CredFlow), Agent Toolkit, engineering stack, contribution city, and optional playground concept.
- Central theme tokens and four switchable theme presets, with `titanium-hacker` active.
- A contribution city generator with upright isometric blocks.
- Official GitHub GraphQL contribution fetcher; **it is not populated with real data yet**.
- An HTML comparison page at `previews/compare-themes.html`.
- Local tests and example automation (not automatically activated).

All output is based on plain Python (3.10+) and SVG. No pip install, hosted illustration service, paid templates or paid APIs required.

## Install safely in your existing repository

```bash
# If you do not already have a local clone:
git clone https://github.com/Phoenixarjun/Phoenixarjun.git
cd Phoenixarjun

# Make a review branch, not a direct change to main:
git switch -c redesign/profile-v2
```

Now extract this ZIP **to your repository root** and merge its directories. It does not include `README.md` or `.github/workflows`, so these files are unaffected.

```bash
python scripts/build.py
python scripts/validate.py
python -m unittest discover -s tests -v
```

Review `README.v2.md`, all images under `assets/`, and `previews/compare-themes.html`. The SVG assets are already included in the ZIP, so you can inspect the generated output even before running Python.

**When and only when you approve the full design** (on your review branch):

```bash
# Linux/macOS:
cp README.v2.md README.md
# Windows PowerShell:
# Copy-Item README.v2.md README.md
```

Commit and test the GitHub rendering on the branch; merge into your default branch only after review.

## Change theme centrally

Change one value in `design/themes.json`:

```json
"active": "titanium-hacker"
```

Available choices:

- `titanium-hacker` — default
- `midnight-circuit`
- `aurora-grid`
- `obsidian-vermilion`

Regenerate **every SVG asset and the README preview** with:

```bash
python scripts/build.py
```

Or select and persist a new preset without editing JSON:

```bash
python scripts/build.py --theme midnight-circuit --save-theme
```

To test a theme temporarily without saving it:

```bash
python scripts/build.py --theme aurora-grid
```

The switch changes the generated output. To revert, just run the build again using the saved active theme.

> This is asset-level theming. GitHub itself controls surrounding page colors. Avoid using unsupported HTML/CSS/JavaScript inside the README.

## Contribution city and real GitHub data

The included contribution city is explicitly labeled **SAMPLE DATA / NOT LIVE**. No real contribution count was guessed or copied from a screenshot.

When you are ready, authenticate with a token that has the necessary read permissions. For local development:

```bash
# Linux/macOS (example; do not commit token):
export GH_TOKEN="<your GitHub token>"
python scripts/fetch_contributions.py
python scripts/build.py
```

```powershell
# Windows PowerShell:
$env:GH_TOKEN = "<your GitHub token>"
python scripts/fetch_contributions.py
python scripts/build.py
```

Use the least-permissive credential that can read the required contribution data. GitHub determines which contributions are visible or authorized; the script does not access repository code. `data/contributions.json` will then contain day/count pairs. Avoid checking this generated file into a public repository if it includes counts you don't want publicly represented.

`automation/profile-refresh.example.yml` is an **inactive template**. To enable later, review and copy it manually into `.github/workflows/profile-v2-refresh.yml`, with repo workflow permissions as appropriate. It uses `GITHUB_TOKEN`; verify it can read the desired contribution data on your account. If not, configure a separate least-privilege token as a secret and adapt the workflow.

## Update content without redesigning assets

| What changes? | Edit |
| --- | --- |
| Name, tagline, links, section visibility | `content/profile.json` |
| Flagship projects and currently building | `content/projects.json` |
| Technology groupings | `content/stack.json` |
| Featured articles | `content/writing.json` |
| All palette colors | `design/themes.json` |
| Hero/project/stack graphic layout | `scripts/graphics.py` |
| README section ordering and Markdown | `scripts/build.py` |
| Contribution city geometry and scaling | `scripts/graphics.py` (`city` and `_tower`) |
| GitHub contribution API access | `scripts/fetch_contributions.py` |

**Do not add unreleased/private projects to content files until they are ready to be public.** These files will eventually live in a public repository.

## Important current boundaries

- AAM, PromptNova and CredFlow are the **current initial flagship selection**.
- Agent Toolkit is separate under **Currently building**.
- The third future flagship has **not** been selected in this public starter kit.
- No future unreleased systems are included or hinted at here.
- Your portfolio link is intentionally empty until its new public URL is ready.
- LeetCode integration is excluded for now.
- Playground is disabled in `content/profile.json` until a working game exists.
- Production metrics and confidential employer/client details are intentionally excluded.

## Build status

Run `python scripts/validate.py` and `python -m unittest discover -s tests -v`. The ZIP ships with generated SVGs, so build success isn't dependent on external APIs.

The initial visual layouts are **starter designs, not final approved artwork**. This modular architecture is meant for section-by-section improvement.
