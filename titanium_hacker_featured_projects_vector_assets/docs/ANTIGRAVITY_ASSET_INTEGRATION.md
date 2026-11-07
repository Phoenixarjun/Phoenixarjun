# Featured Projects — Titanium Hacker assets and integration contract

## Status and scope

This bundle provides **vector recreations** of the three right-hand diagrams in the approved reference mockup. They are faithful to the visual vocabulary, shape hierarchy, lime highlights and content of that design, but are **not a pixel-for-pixel raster trace**. Everything is independent SVG markup, editable through the generator. The outer canvas of each illustration is **transparent**. Individual nodes retain intentional translucent charcoal surfaces.

Only these three featured projects are in scope, in this fixed order:

1. **Architecture-as-Memory** — architecture topology
2. **PromptNova** — intent/refine/evaluate/output
3. **CredFlow** — telecom billing, collection and dunning rules

Do not add Orchestrix, Vigilant, A1/AIVON or Agent Toolkit to Featured Projects. Agent Toolkit remains in *Currently Building*.

## Install

Extract this ZIP at the root of `Phoenixarjun/Phoenixarjun` on the `redesign/profile-v2` branch. The ZIP contains only additive paths under `assets/projects/`, `scripts/generate_featured_artwork.py`, `config/featured-art-theme-fallback.json`, `docs/`, and `previews/`. It **does not include or overwrite `README.md`, `README.v2.md`, `scripts/build.py`, or GitHub workflows**.

Then regenerate:

```bash
python scripts/generate_featured_artwork.py
```

The generator detects `design/themes.json` automatically and uses its active preset. The included `config/featured-art-theme-fallback.json` is strictly a fallback for running the assets outside the existing profile repository; do **not** treat it as a second authoritative design system.

Optional PNG previews require `cairosvg` and `Pillow`:

```bash
python -m pip install cairosvg Pillow
python scripts/generate_featured_artwork.py
```

SVG generation itself needs only the Python standard library.

## Assets

| File | Canvas | Role |
|---|---:|---|
| `assets/projects/illustrations/aam-topology.svg` | 710×236 | Architecture hierarchy on transparent canvas |
| `assets/projects/illustrations/promptnova-workflow.svg` | 710×236 | Prompt refinement and evaluation path |
| `assets/projects/illustrations/credflow-billing.svg` | 710×236 | Billing/collections workflow with dunning rule loop |
| `assets/projects/decor/header-dot-field.svg` | 328×144 | Sparse lime/steel header dots, transparent |
| `assets/projects/decor/triple-slashes.svg` | 116×34 | Three diagonal technical accents, transparent |
| `assets/projects/decor/featured-projects-terminal.svg` | 1160×52 | One transparent `ls --flagship-projects` header strip |
| `assets/projects/frames/project-row-frame.svg` | 1160×224 | Reusable chamfered pod with internal dark translucent surface and corner glows |

`previews/*-transparent.png` files are convenience **2× raster exports with alpha**, not replacements for the SVG source. The dark-background previews are reference-only and **must not** be used as transparent artwork.

## Exact palette and visual roles

The original mockup's dark-first Titanium Hacker theme is preserved:

- graphite base: `#0C0F10`
- interior surface: `#1B2328`
- raised surface: `#253139`
- steel border: `#42535C`
- signature lime accent: `#B6FF3B`
- soft text: `#EEF7EF`
- secondary data: `#8EADB6`
- muted text: `#A6B6B2`

Use the existing `design/themes.json` in the repository for centralized control. Avoid changing styles independently in each SVG. Bright lime is reserved for selected nodes, focused routes, corner accents and status points. Steel gray and off-white convey structure.

## Critical README rendering guidance

**Do not paste SVG source directly into GitHub Markdown**. GitHub will sanitize unsupported markup. Use external `.svg` images or composite the SVG content into a generated row asset and wrap it in a Markdown/HTML anchor.

**Do not embed illustrations via an SVG `<image href="other.svg">` reference** and assume GitHub will load those cross-file resources; SVG images served under restrictive image contexts can block secondary resources. The robust approach is to **inline the illustration's SVG elements into the generated row SVG** or rasterize the illustration at build time. If inlining, namespace shared SVG `id`s (`nodeFill`, `softGlow`, etc.) by project slug to prevent collisions.

For navigation, the **entire project row** should be linked from the README:

```html
<a href="https://github.com/Phoenixarjun/architecture-as-memory">
  <img src="./assets/projects/featured/architecture-as-memory.svg"
       alt="Architecture-as-Memory — architecture visual and project summary; opens GitHub repository"
       width="100%" />
</a>
```

`featured/architecture-as-memory.svg` is the **row composite** that Antigravity will generate using the supplied stand-alone visual. The included SVGs are components, not drop-in replacements for the existing full-width row images. The `View on GitHub ↗` button is a **painted CTA in the SVG**, but the **outer `<a>` makes it actually clickable**.

## Full implementation instructions for Antigravity

1. Inspect the current branch's `README.md`, `README.v2.md`, `content/projects.json`, `design/themes.json`, `scripts/build.py`, and `scripts/graphics.py`.
2. Keep the existing section order. Change **only Featured Projects** (Section 03). Preserve Hero and Engineering Focus.
3. Use the reference image `featured_projects_neon_graphite_showcase.png` supplied by the user for geometry and spacing. These SVGs are the approved **project-specific right-side art**.
4. Retain exactly **three** horizontal full-width project rows: AAM, PromptNova, CredFlow.
5. For each row: number at left (`01`, `02`, `03`), bold name, 2–3 readable description lines, 4–7 **curated verified** technologies, a project-specific visual on the right, and an obvious bottom-right `View on GitHub ↗` label.
6. Use the transparent `project-row-frame.svg` as a geometry reference: bevelled corners, thin steel outline, top-left short lime segment, small bottom-right lime glow. The frame has intentional translucent internal surface; never render an opaque rectangle behind the whole section.
7. Place each 710×236 illustration into the right-side visual region, preserving aspect ratio. It was drawn larger than the screenshot to stay crisp on high-density displays. Do not simply stretch it horizontally to fill the container.
8. Use only one command-style separator, **`naresh@github:~$ ls --flagship-projects`**. `featured-projects-terminal.svg` is available, but the repository may already generate this header; don't duplicate it.
9. The `header-dot-field.svg` and `triple-slashes.svg` are **optional header decorations**. Compose them selectively at low opacity. Don't add a second decorative strip if it causes repetition or clutter.
10. Integrate by updating the authoritative functions in `scripts/build.py` and `scripts/graphics.py`. **Never rely on hand edits to generated `README.md`**, because regeneration would overwrite them.
11. Preserve approved descriptions and project names; do not invent metrics, seniority or deployment claims. CredFlow is a *monolithic* telecom application; AAM is *local-first* tooling.
12. Keep project visuals replaceable through metadata (e.g. `visual_asset` field in each entry of `content/projects.json`). New featured projects can point to other generated visuals in the future without requiring a rewrite of the entire section layout.
13. Do **not** use CSS, JavaScript or iframe interactions inside the README. All visuals are self-contained images and all links are outer native anchors.
14. Render the final README on **GitHub dark and light modes**. Dark design is the brand, but light mode needs reasonable contrast. If necessary use a deliberate contained dark surface or a `(prefers-color-scheme: light)` alternate; don't make transparent off-white text float unsupported on white.
15. Validate at desktop README width (~850px) and mobile. If 2–3 lines become unreadable at mobile scale, provide a mobile-specific version or keep the descriptions as accessible native Markdown rather than shrinking type indefinitely.
16. Inspect visual boundaries, image transparency, text alignment, no broken glyphs, no duplicate links and working GitHub targets. Do not commit or push without permission.

## Future replacement strategy

Keep this profile's data and artwork **decoupled**. Each project record should have `slug`, `name`, `description`, `technologies`, `github_url` (or existing `url`), and `visual_asset`. Content should be independently curated; artwork should be referenced by path.

The generator currently includes three named functions: `aam()`, `promptnova()`, `credflow()`. When featured projects change, create a new visual function, update the project-to-visual mapping, regenerate, and leave the row shell untouched.

## Acceptance checks

- SVGs parse as XML without missing resources.
- SVG outer backgrounds are transparent (RGBA alpha = 0 at canvas corners).
- All 3 visuals are distinctive, accurate, and legible.
- `header-dot-field.svg` is independent and has a transparent background.
- The signature lime is `#B6FF3B` and structural metallic colors derive from the palette.
- Exactly 3 featured projects, correct order, links to corresponding repositories.
- Existing Hero, Engineering Focus and other README sections are unchanged.
- Rebuilding retains every approved change.

The references are concept art and do not constitute proofs of implementation quality. Test the rendered output, not just the source.
