# Integration quickstart — existing Phoenixarjun/Phoenixarjun repository

The package **contains no `README.md`, no `README.v2.md` and no `.github/workflows`**. Its ZIP can be extracted into the project root without overwriting those files. It adds namespaced SVG assets, content JSON, a generator script, reference screenshots and documentation.

## Commands

```bash
# From the root of your cloned Phoenixarjun/Phoenixarjun repository
python scripts/build_engineering_focus.py
python -m unittest discover -s tests -p 'test_assets.py' -v
```

A fresh run updates the supplied SVGs. PNG previews are included; they can be regenerated with Inkscape:

```bash
inkscape assets/engineering-focus/engineering-focus-dark.svg \
  --export-filename=assets/engineering-focus/previews/engineering-focus-dark-preview.png \
  --export-width=1280
```

If `design/themes.json` is already present from the earlier starter, the generator inherits its **active preset**. Use that central file to change colors across sections; never edit generated SVG colors directly. If that file is absent, `config/theme.json` supplies the Titanium Hacker fallback.

## README snippet

Place the snippet from `examples/README_SECTION_SNIPPET.md` after the hero and before Flagship Projects in the **draft** README (typically `README.v2.md`). The command and heading are already painted into the SVG. Remove any older Markdown `## Engineering focus` block; do not duplicate it.

> **If you use `python scripts/build.py`** from the earlier starter, its `build_readme()` function regenerates `README.v2.md` from scratch. Have Antigravity integrate this new image into `build_readme()` to avoid losing it on regeneration. The detailed instructions for that are in `ANTIGRAVITY_IMPLEMENTATION.md`.

## Why two full-section SVGs?

- `engineering-focus-dark.svg`: self-contained dark background, suitable for GitHub dark **and** light themes; this is the safest primary asset.
- `engineering-focus-transparent.svg`: transparent outside its own section bands/pods; useful when hosted within a known dark container. On GitHub light theme, the alpha gaps expose the page background.

All six **standalone icon assets** and both **frame assets** have genuinely transparent canvas backgrounds. They can be embedded separately or reused when assembling future designs.

## Priorities

1. Confirm the rendered imagery matches the supplied screenshot at ~900px README width.
2. Do not add a global outer frame; the hero already owns that treatment.
3. Use the three core pillars, not six equal subjects.
4. Confirm no leakage of future flagship projects or private details.
5. Keep `README.md` live state unchanged until approved.
