# Engineering Focus — Visual Specification

This spec accompanies the generated, editable SVGs and the user-supplied screenshot in `references/`.

## Content model

**Hierarchy:** section-command → heading/subtitle → 3 primary pillar pods → enabling-practices heading → 3 slim practice pills.

The three pillars are **Applied AI Systems**, **Backend Engineering**, and **Distributed & Reliable Platforms**; enabling practices are **Automation**, **Observability**, and **Production Engineering**. The last category is not a fourth equal pillar. Do not add statistics or additional project claims.

## Dimensions & layout

- Root assembled artboard: `1280×765` (`viewBox="0 0 1280 765"`)
- Command band: `20,14` to `1260,86`
- Heading band: `20,105` to `1260,207`
- Pods: x 20, 447, 874; y 226; width 386; height 353
- Pod title baselines: 422,456 in global coordinates
- Underline y: global 483
- Description baselines: global 513,536,559
- Practice subheading line y: 628
- Practice pills y: 672..738; x 23,452,880

SVG layout coordinates are **not** CSS pixels after embedding. At a rendered README width of 900px all dimensions scale by 900/1280 ≈ 0.703. Text sizes must be selected for clarity at that scale.

## Colors

`#0C0F10` graphite, `#1B2328` charcoal surface, `#42535C` steel, `#B6FF3B` lime accent, `#EEF7EF` off-white text; secondary muted steel/aqua gradient allowed. The script uses root `design/themes.json` if present; fallback tokens in `config/theme.json` are used otherwise.

## Pod specifications

| Element | Detail |
|---|---|
| Outline | chamfered technical path; ~1.8px neutral steel |
| Accent | fine lime upper-left trim + sharp lower-right glowing elbow |
| Fill | near-black gradient, not uniform neon fill |
| Icon | floating 3D-style isometric geometry with metallic face gradients |
| Icon size | 190×155 inside main pod |
| Heading | bold sans, 30px, two lines centered |
| Underline | ~48×4px bright accent |
| Description | 19px mono, 3 lines, muted text |
| Padding | ≥22px on all sides, including text descent |

## Contrast & rendering

The main SVG is offered in a self-contained dark variant for GitHub light/dark mode and an alpha-transparent variant for custom dark hosts. Every individual SVG icon and reusable frame retains true transparency. Primary asset should be the dark version until GitHub previews confirm readability.

## Motion

**No motion is requested for Engineering Focus.** The animated typewriter and halftone reveal belong to the identity hero, not this section. Keeping this second section static avoids visual noise and improves accessibility and render predictability.

## Shared separator concept

`naresh@github:~$ engineering-focus` with a thin neutral steel rule; this is a recurring motif for later sections, but only the current Engineering Focus separator is included in this bundle. Future command names should be produced with the same typography/spacing but different command strings.
