# Antigravity Implementation Brief — Engineering Focus / Titanium Hacker

**Copy this entire document into Antigravity as the implementation request.** The accompanying ZIP is a self-contained source package, not only a design image. Inspect its generator, SVGs, configuration, and reference screenshots before editing your existing GitHub profile repository.

## 0. Mission / Scope

You are a senior SVG graphics engineer, GitHub README specialist, visual designer, and Python tooling maintainer. Your assignment is to integrate **one and only one section — Engineering Focus** — immediately after the already-approved Identity/Hero in the existing `Phoenixarjun/Phoenixarjun` GitHub profile repository.

**Do not rebuild the hero. Do not invent new sections. Do not reveal private/unreleased projects. Do not alter the existing employer name, identity, or other public claims. Do not add social links, GitHub stats, animations, or project cards inside Engineering Focus.**

The result must look like a natural continuation of the existing README, *not a second full-screen hero card*. There is one command-line separator, a section heading, three premium micro-pods, then a slim three-item practice row. The section is a single compositional flow; the individual pillar pods have their own frames but the entire section must not acquire another thick enclosing frame.

## 1. Files included with the supplied ZIP

After extracting the ZIP into the root of your existing GitHub profile repo, you should find:

```text
config/
  theme.json                         # FALLBACK ONLY: existing design/themes.json wins
  engineering_focus.json             # canonical text/label source
scripts/
  build_engineering_focus.py         # stdlib-only deterministic SVG generator
assets/engineering-focus/
  engineering-focus-dark.svg         # default: dark self-contained README asset
  engineering-focus-transparent.svg  # alpha-transparent section variant
  section-command.svg                # reusable transparent-viewport command strip
  icons/
    applied-ai-systems.svg
    backend-engineering.svg
    distributed-reliable-platforms.svg
    automation.svg
    observability.svg
    production-engineering.svg
  frames/
    pillar-pod.svg
    practice-pill.svg
  previews/
    engineering-focus-dark-preview.png
    engineering-focus-transparent-preview.png
    engineering-focus-at-readme-width.png
    engineering-focus-light-mode-preview.png
    icon-contact-sheet.png
references/
  engineering-focus-reference.png
  titanium-hacker-palette-reference.png
docs/
  ANTIGRAVITY_IMPLEMENTATION.md      # this brief
  README_INTEGRATION.md
  DESIGN_SPECIFICATION.md
  QUALITY_CHECKLIST.md
examples/
  README_SECTION_SNIPPET.md
```

Treat the actual SVG outputs as the **editable structural reference**, and the attached PNG screenshot as the *look/feel reference*. They are close, engineered recreations rather than a claim of pixel-identical vector extraction of the screenshot. Prefer pixel-level visual parity to gratuitous new details, but prioritize alignment and readability at typical README widths.

## 2. Fixed visual system — do not improvise other colors

### Canonical five swatches from the approved Titanium Hacker palette

| Token | Hex | Purpose |
|---|---|---|
| `base` | `#0C0F10` | background graphite |
| `surface` | `#1B2328` | pod interiors, steel-charcoal depth |
| `steel` (existing theme's `stroke`) | `#42535C` | neutral hairlines, linework |
| `accent` | `#B6FF3B` | selectively glowing corner trims, feature highlights |
| `text` | `#EEF7EF` | primary text |

These five are *mandatory*. Secondary subdued metal/aqua colors may be derived from the selected theme's `secondary` or fallback (`#80D8C7`, `#B8C8BE`) for icon face sheen and descriptions. Do not change lime to yellow-green, turquoise, rainbow, violet, etc. Lime must not cover large backgrounds. Use steel-gray borders and accents on select corners. Avoid saturated glow behind text and avoid glassmorphism blur over entire cards.

### Single source of truth

Your existing starter likely has `design/themes.json` with `active` and `presets`. The supplied `scripts/build_engineering_focus.py` **automatically reads that file when present**. It reads the active preset and maps `stroke → steel`, `secondary → icon face sheen`, `muted → muted text`, while deriving dark/raised surfaces from the palette. The bundled `config/theme.json` is only for previewing the section standalone when that central theme file is absent.

**Do not create a second permanent active-theme toggle.** If the repo already has a centralized palette loader, reuse it or extend it. A subsequent `python scripts/build.py --theme midnight-circuit --save-theme` followed by `python scripts/build_engineering_focus.py` should recolor the section consistently. You may wire the second script into the existing build pipeline, but do not overwrite the existing theme presets.

## 3. Exact user-approved textual structure

Keep all labels and wording editable in `config/engineering_focus.json`. Use the following visible content (small refinements require user sign-off):

**Command separator:**

```text
naresh@github:~$ engineering-focus ─────────────────────────────────────
```

Use mono type. The username/prompt is lime, command off-white. The long rule is a thin muted-steel line with an unobtrusive lime endpoint. This separator is inside the exported section SVG; do not duplicate a textual command line in `README.md` directly above it.

**Section heading:**

```text
Engineering Focus
Primary engineering pillars, supported by key engineering practices.
```

Engineering in off-white; Focus in lime. A short slim lime vertical stroke on its left. Do not add a huge second terminal shell or a tab-like top header around the entire section.

**Three primary pillars, left to right:**

1. **Applied AI Systems** — `Building practical AI workflows, agents, and intelligent software.`
2. **Backend Engineering** — `Designing APIs, services, data flows, and scalable backend systems.`
3. **Distributed & Reliable Platforms** — `Building event-driven, scalable, and observable platforms.`

**Practice strip:**

`// Enabling Practices` with three aligned low-height outlined pods:

- `Automation`
- `Observability`
- `Production Engineering`

**Information architecture:** these are **three focus pillars supported by three practices**, *not six equal disciplines*. The design must convey that difference. Do not split reliability from platforms into a fourth card. Do not add expertise meters, years, percentages, personal claims, or private project names.

## 4. Exact master SVG geometry (all pixels are in viewBox coordinates)

The included generator exports `viewBox="0 0 1280 765"`. Keep a responsive image ratio; do not rely on viewport-relative CSS, scripts, or browser APIs.

Reference major placements:

| Element | Bounding box / position | Styling |
|---|---|---|
| Command bar | `x=20, y=14, w=1240, h=72` | near-black flat band, **no outer hero frame** |
| Prompt prefix | `x≈57, y≈63` | 25px mono, lime |
| Command name | `x≈341, y≈63` | 25px mono, off-white |
| Separator rule | `x≈618..1230, y≈53` | 1.5px steel line |
| Heading area | `x=20, y=105, w=1240, h=102` | dark background for GitHub light-mode legibility |
| Heading accent | `x=39, y=123, w=5, h=60` | lime |
| Heading | `x=63, y≈153` | 44px bold sans; Focus lime |
| Subtitle | `x=65, baseline≈188` | 23px regular secondary |
| First pillar | `x=20, y=226, w=386, h=353` | chamfered technical frame |
| Second pillar | `x=447, y=226, w=386, h=353` | identical |
| Third pillar | `x=874, y=226, w=386, h=353` | identical |
| Primary icon zone | ~`190×155` inside each pod; offset from pod origin `(+100,+14)` | custom isometric vector art |
| Titles | ~pod `x=193`; baselines `196`, `230` | 30px bold, centered |
| Mini underline | pod `(169,257)` length `48` height `4` | bright lime |
| Descriptions | pod `x=193`; baselines `287,310,333` | 19px monospace, centered, muted |
| Practice heading | `x=20,y=607` | no extra large block frame |
| Practice strip | three frames at `(23,672), (452,672), (880,672)` | 66px high, slim chamfers |

### Geometric pod frame

Each pillar has a chamfered near-rectangle. Use a path equivalent to:

```svg
<path d="M 24 2 H 350 L 384 34 V 319 L 351 351 H 2 V 22 Z"
      fill="url(#pod)" stroke="url(#edgeGrad)" stroke-width="1.8" />
```

- Top-left small bevel **lit with a short lime L-shaped line**.
- Top border is delicate steel, not pure green.
- Bottom-right has a precisely localized lime-light corner stroke; use a blurred duplicate of the same path for glow, and a sharp 3–4px stroke above it.
- Bottom-left and right-side edges are mostly dark steel.
- Corner glow must not flood the entire pod or create a neon outline around all four sides.
- Interior uses `surfaceDeep → deep` subtle gradient, ideally translucent-looking against charcoal.
- Keep all three pods visually identical; only contents differ.

#### Suggested local glow strategy

```svg
<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="5" />
</filter>
<!-- soft glow behind identical crisp stroke -->
<path d="M 281 351 H 351 L 384 319" stroke="#B6FF3B"
      stroke-width="9" filter="url(#glow)" opacity="0.8" fill="none" />
<path d="M 281 351 H 351 L 384 319" stroke="#B6FF3B"
      stroke-width="3.8" fill="none" />
```

Do not use filters with massive uncontrolled radii. Three repeated local filters are acceptable; large full-screen Gaussian blurs are not.

## 5. Custom vector icon engineering

**No icon CDN or externally-hosted dependency is necessary.** Six separate SVGs already exist in `assets/engineering-focus/icons/`. They use editable geometry and alpha transparency, not hardcoded bitmap crops or screenshot screenshots. They inherit centrally generated colors when rebuilt.

### Pillar 1: Applied AI Systems

A floating stack of three diamond/isometric plates. Top plate looks like a model chip, with `AI` centered in lime. Metal side facets and soft low-opacity lime underglow. Wide silhouette; no cartoon brain, robots, or unrelated sparkles. Intended to express layered AI applications on reliable computing infrastructure.

### Pillar 2: Backend Engineering

A floating angled code console / implementation tile showing a `< / >` or equivalent code glyph. Use an angled front plane, a small steel base, thin lime key edges, subtle plane shading. Distinct from the AI chip; not merely a re-colored square badge.

### Pillar 3: Distributed & Reliable Platforms

Three isometric nodes/cubes with a larger upper node and two lower peers. Draw three faces per cube; top face in muted aquamarine/steel, left face in dark steel, right face with sparing lime edge. If adding connecting lines, keep them very faint to avoid distraction.

### Enabling-practice icons

- Automation: 10-tooth outlined gear, circular hole; about 40px apparent size.
- Observability: small chart/telemetry viewport with a rising trend.
- Production Engineering: layered stack/plates icon; distinguish it from applied AI with no central AI mark.

**Transparency requirement:** all six individual icon assets and reusable frames must have alpha-transparent canvases (i.e., no full-viewBox `<rect>` fill). Gradients apply only to vector artwork. Export PNG previews with actual alpha to verify. For the *assembled* section, deliver both transparent and self-contained dark-background versions so the latter reads correctly in GitHub's light and dark UI themes.

## 6. Typography / hierarchy

- Heading: Inter/Arial-compatible heavy sans; 44px in master canvas.
- Pillar titles: 30px heavy sans; center-aligned; two lines.
- Body text: 19px JetBrains Mono/Consolas fallback; center-aligned in exactly three short lines.
- Command: 25px monospace, command white and shell lime.
- Practice heading: 27px sans and leading `//` in mono lime.
- Practice labels: 24px sans, except `Production Engineering` 21px so it never collides with its left icon.

Keep descriptions as written above. Use balanced line breaks from `config/engineering_focus.json` to avoid auto-wrapping inconsistencies in standalone SVG.

### Glyph safety

Do not embed external font URLs in the SVG. Do not ship font binaries. Use installed/system-font fallbacks; if a more deterministic final asset is required, optionally convert SVG text to paths for a *separate* non-editable distribution copy while preserving the editable source.

## 7. Background and transparency strategy

1. `engineering-focus-transparent.svg` must have transparent viewBox outside the independent section elements. Validate its RGBA corner pixel has alpha=0.
2. `engineering-focus-dark.svg` should have graphite background `#0C0F10` over the canvas so GitHub **light mode** never renders white/light text on a white page.
3. Individual pods are **always dark** independent visual objects.
4. The full section **must not** be surrounded by one heavy card border. The hero is the first big card; subsequent README sections use open editorial flow. The dark-background version is an image backing plane, not another prominent card frame.
5. Render the card with **both** black/near-black host and light host preview backgrounds to evaluate contrast.

## 8. Exact implementation steps — existing repository

1. Ensure the working branch is `redesign/profile-v2`, or create a new feature branch such as `feat/engineering-focus` from that branch.
2. Examine the current repository tree; never assume a pristine clone. Preserve `README.md`, `README.v2.md`, `scripts/build.py`, existing hero assets, and `.github/workflows/` unless a targeted integration edit is necessary.
3. Merge the supplied package files into the repo by adding/merging folders, not replacing whole existing directories. The supplied package deliberately does **not** include `README.md` or workflow files.
4. Detect `design/themes.json`. If present, use the selected preset and do not modify its definitions unless absolutely necessary. The supplied generator already handles this.
5. Run `python scripts/build_engineering_focus.py` from the repo root. This creates the assembled SVGs, six transparent icons, separator, and reusable frames.
6. Open and compare `assets/engineering-focus/previews/engineering-focus-dark-preview.png` and the reference screenshot. Render a fresh preview from the new SVG after any modifications.
7. Edit the *generator* for all visual refinements; don't hand-edit generated SVGs and lose changes on regeneration.
8. Insert the single section asset after Identity/Hero and before Flagship Projects. If the existing README has a textual Engineering Focus section, **replace that section** rather than duplicating it.
9. If an existing `scripts/build.py` regenerates `README.v2.md`, update `build_readme()` to include the Engineering Focus image instead of its old list of bullets, and call the section generator within its build step. Otherwise subsequent builds will undo the manual integration. Do not modify unrelated sections.
10. Keep the default README published state unchanged until review: prefer updating `README.v2.md` on the feature branch. If asked to update the live profile `README.md`, do so only after preview and approval.
11. Validate assets with the included `tests/test_assets.py` and `python scripts/build_engineering_focus.py`. Open a GitHub rendered preview or draft PR; SVG browser rendering alone is not proof of GitHub's renderer.
12. Stage only expected files and inspect diffs for secrets or private references before commit. Do not add tokens, `.env`, internal company screenshots, or private repository details.

### Integration snippet (one image, no duplicates)

```md
<!-- PROFILE:ENGINEERING-FOCUS:START -->
<p align="center">
  <img src="./assets/engineering-focus/engineering-focus-dark.svg"
       alt="Engineering Focus: Applied AI Systems, Backend Engineering, Distributed and Reliable Platforms; enabling practices Automation, Observability, and Production Engineering."
       width="100%" />
</p>
<!-- PROFILE:ENGINEERING-FOCUS:END -->
```

The SVG **already contains the heading and terminal command separator**, so do **not** place another `## Engineering Focus` immediately above it. Verify no other Engineering Focus section remains below.

## 9. Rendering, SVG correctness and GitHub constraints

- Profile READMEs allow ordinary Markdown and `<img>` but are **not arbitrary webapps**. Do not add JavaScript to the README, inline `<script>`, canvas, interactive CSS, or React components.
- Prefer **static inline-image-linked SVG** for this section, with PNG preview fallback if you detect a rendering issue.
- Ensure all SVG documents have a correct `xmlns`, `viewBox`, valid XML, and no external network resources.
- Avoid `foreignObject`, external image references, embedded base64 photographs, dynamically fetched CSS, or unsupported browser APIs.
- Icons are source graphics; assembled section may be a single SVG image for reliable exact layout in GitHub.
- Test at intrinsic width 1280, README-scaled width around 850–900, and smaller 600px widths. If tiny text becomes unreadable at mobile sizes, simplify descriptions or add optional alternate assets; do not shrink font below legibility.
- Verify all 3 pillars fit on one line each in the visual card layout and all practice labels remain fully within bounds. Keep the three-line descriptions away from the bottom border; previous rendering required explicit adjustment here.
- The card logo icons should remain recognizable at README width. Some simplified line details may be lost after scaling—prioritize clear silhouette.

## 10. Quality bar and acceptance tests

The work is complete only when:

- [ ] The exact three pillars and three practices are shown.
- [ ] `naresh@github:~$ engineering-focus` is above the section title.
- [ ] The whole section is part of the README flow, not another giant hero card.
- [ ] All five canonical color swatches remain unchanged.
- [ ] Each custom icon has its own valid transparent SVG.
- [ ] Framing has restrained steel borders with localized lime bevel/corner glows.
- [ ] Titles, descriptions, and practice labels have no clipping/overlap.
- [ ] The look remains recognizable against both GitHub dark and light themes.
- [ ] `design/themes.json` remains the central source when present.
- [ ] The generator is deterministic and takes editable content from `config/engineering_focus.json`.
- [ ] The output uses no remote assets and no paid dependency.
- [ ] Existing live `README.md` / `.github/workflows` remain intact until explicitly approved.
- [ ] The hero is not duplicated.
- [ ] The Engineering Focus heading and command separator appear **once**.
- [ ] README preview is checked visually at real reading size, not only by zooming into a screenshot.
- [ ] A final summary of touched files and preview screenshots is provided for review.

## 11. Explicit anti-goals

- No extra skill badges, technologies, languages, certifications, statistics, achievements, or employment history.
- No extra fourth/fifth pillar; reliability belongs with Distributed & Reliable Platforms.
- No visual change to Identity/Hero, Flagship Projects, Currently Building, Engineering Stack, Writing, Contribution Atlas, Playground, Footer.
- No separate 3D HTML page, JavaScript game, or GitHub Action for this single section.
- No changes to published `README.md` without user's approval.
- No invisible labels, clipped text, inconsistent theme colors, or overly bright card backgrounds.

**Execute the integration and produce the finished Engineering Focus assets and a verified README preview. Do not stop at a description of what should be done.**
