# Design system: Titanium Hacker

## Positioning

A mature engineering console rather than a gaming or stock cyberpunk dashboard. The same profile identity should remain coherent with a violet developer portfolio and a blue professional portfolio, while being distinguishable at first glance.

- Primary character: graphite/charcoal, steel neutral, restrained citron-lime.
- Components: editorial whitespace; technical line work; understated panels; readable copy.
- Avoid: excessive glows, vast badge collections, fake telemetry, five equal-weight job titles, metrics without sources.

## Centralized tokens

Every generated SVG reads the **selected** palette in `design/themes.json`. Palette keys:

| Token | Meaning |
| --- | --- |
| `base` | canvas / outer darkness |
| `surface` | principal cards |
| `surface2` | raised surfaces and capsules |
| `stroke` | borders / wires / non-primary diagram edges |
| `accent` | primary signal — use sparingly |
| `secondary` | secondary signal / alternate data |
| `text` | high-contrast headings |
| `muted` | descriptions and labels |

Default palette: `#0C0F10`, `#1B2328`, `#253139`, `#42535C`, `#B6FF3B`, `#8EADB6`, `#EEF7EF`, `#A6B6B2`.

**Accessibility:** inspect text contrast after any palette change. Avoid very small 10px typography in the final image, because GitHub will scale assets on mobile. SVGS use inline paint values rather than CSS variables because they are loaded as images by GitHub.

## Composition

1. Hero: large name + one stable specialty + reliable systems tagline, decorative topology.
2. Engineering focus: readable Markdown first.
3. Flagships: full-width illustrated cards linking to real repositories.
4. Currently building: intentionally isolated from flagships.
5. Stack: six curated domains, no irrelevant badge dump.
6. Writing: three articles.
7. Contribution atlas: 12 isometric month districts with bar height determined by contributions.
8. Playground: optional and hidden until functional.
9. Connect: simple footer.

## Contribution scaling

For `count > 0`, the current generator maps count to block height:

`height_px = min(49, max(4, 7 * log2(count + 1)))`

This is logarithmic rather than linear, to keep sparse days visible beside spikes. Counts remain derived from GitHub's daily contribution values, and the source is stated in the graphic. The geometry is isometric SVG, not a real 3D engine. Additional interactivity would require a website outside GitHub's README renderer.

## Copy and claims

Always separate official employer title from professional specialization. Do not use job search language, open-to-work calls to action, invented adoption statistics, fabricated performance numbers, or nonpublic work claims. Keep project descriptions traceable to repositories and verifiable demonstrations.
