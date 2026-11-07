# ANTIGRAVITY IMPLEMENTATION — GITHUB PROFILE 2.0 / REALISTIC LOGOUT FOOTER V2

## 0. Mission, source of truth, and boundaries

You are updating the existing GitHub profile repository `Phoenixarjun/Phoenixarjun` on its `redesign/profile-v2` development branch. This is a replacement asset kit for the **final Logout Footer** only, immediately after the existing **Connect All** section. Treat the supplied realistic transparent robot PNG as the source of truth for its appearance. It is reconstructed from the user's approved realistic illustration; **do not recreate the old line-art robot** and do not substitute an emoji or stock mascot.

Approved content, exact copy:

- Existing terminal-style separator: `naresh@github:~$ logout`
- Headline: **Thanks for stopping by.** (not "shopping")
- Four lines: `Built with curiosity`, `Driven by systems`, `Always learning`, `Always shipping`
- Final terminal label: `// Session Closed //`
- **No** GitHub, LinkedIn, Medium, Portfolio, or other links repeated here.
- **No** new projects, skills, identity claims, stats, or unrelated UI.

Identity and color system already established elsewhere:

- Professional identity: **AI Systems Engineer** (footer need not repeat it)
- Theme: **Titanium Hacker**, from `design/themes.json` (do not create another global theme configuration)
- Base graphite `#070B0C`, surface `#1B2328`, steel `#42535C`, accent lime `#B6FF3B`, text `#EEF7EF` are the existing default values. The build script reads the active theme and makes them configurable.

## 1. Updated asset package contents

| Path | Role | GitHub README-ready? |
|---|---|---|
| `assets/logout-footer/robot-realistic-transparent.png` | Original isolated *realistic* raised-hand robot, real RGBA transparency | Yes, standalone if needed |
| `assets/logout-footer/logout-card-static.png` | High-resolution full card with the exact robot and completed headline | Yes, static alternative |
| `assets/logout-footer/logout-card-animated.gif` | Card with **frame-by-frame typewriter effect** and readable hold | **Yes, recommended primary README asset** |
| `assets/logout-footer/logout-terminal-separator.svg` | Standalone separator reference; prefer the existing centralized separator generator | Yes, fallback only |
| `scripts/build_logout_footer.py` | Source renderer for the frame, text, GIF, and static card | Local/CI generation |
| `content/logout-footer.json` | Single content source (no separate colors) | Build input |
| `previews/readme-footer-preview.png` | Visual check of separator + static card | QA only |
| `previews/typing-frames.png` | Six animation states as a contact sheet | QA only |
| `previews/robot-on-dark.png` | Robot against theme surface, for cutout inspection | QA only |
| `previews/logout-card-static-preview.png` | Standard-width visual check | QA only |
| `tests/test_logout_footer.py` | Package-level structural and animation tests | CI/local |

### SVG versus PNG fidelity

**The new realistic robot is a transparent PNG, intentionally.** It is not a mathematically traced vector SVG. Rasterizing the photoreal reference preserves its metallic detail, glossy visor, lime edge lighting, facial features, and raised fingers. Claiming a fully editable, path-based SVG duplicate would be misleading. The card framing, typography, and graphic rules are reproducible in code; the mascot is a replaceable photographic/CG raster asset.

The robot is **in a raised-hand/waving pose**, but the new v2 animation moves only the text. Do not simulate an articulated arm movement by rotating the entire robot PNG. A future realistic wave would require separately modeled layers or a properly rigged animation, which is outside this task.

## 2. Inspect and integrate safely

Before editing, inspect the actual repository:

- Current branch, `git status`, `README.md`, and any alternate draft README.
- `scripts/build.py` and related graphics helpers, especially the **one** shared `section_terminal_header()` or equivalent function.
- `design/themes.json` and existing theme resolution.
- The current Connect All section and the old Logout Footer implementation if present.
- Existing `.github/workflows/` and any build commands.

**Do not overwrite** `README.md`, `README.v2.md`, `design/themes.json`, or `.github/workflows/*` from a ZIP; this ZIP deliberately excludes them. Modify the authoritative generator/template instead of only editing generated README markup. Preserve all existing sections and links.

If the previous footer kit has been integrated, explicitly replace references to its old **outline** assets:

- Old `robot-wave-static.svg`, `robot-wave-animated.svg`, `robot-wave.gif` are legacy cartoon imagery, not the new robot.
- Old `logout-card-static.svg` is legacy cartoon artwork, not the new card.
- The filename `logout-card-animated.gif` is retained for compatibility; after extraction, regenerate it using the new script and inspect it.
- Remove old cartoon assets only after verifying no other references depend on them, and explain any deletions in the change report.

## 3. Asset build

Requirements: **Python 3.10+** and Pillow 10+.

From the repository root, after extracting this kit:

```bash
python -m pip install "Pillow>=10,<13"
python scripts/build_logout_footer.py --repo-root .
python -m unittest discover -s tests -p 'test_logout_footer.py' -v
```

This builder uses the packaged transparent robot. It does **not** download icons, request GitHub access, read `.env`, or require any API token. It loads the active theme from `design/themes.json` if present; otherwise it uses the packaged Titanium Hacker defaults.

Expected outputs:

- `assets/logout-footer/logout-card-static.png`
- `assets/logout-footer/logout-card-animated.gif`
- `assets/logout-footer/logout-terminal-separator.svg`
- New QA images in `previews/`

Do not replace this builder with a new incompatible SVG portrait generator.

## 4. Exact composition

The native card artboard is **940 × 300** units, displayed centered at an approximate maximum rendered width of **760–780 CSS pixels** on GitHub desktop. It must scale down proportionally on mobile. Do not stretch to fill the entire README width if that would turn a compact footer into another giant hero.

### Main card

- Outer canvas: transparent corners; intentional dark solid surface **inside** the bevelled card.
- Frame path: eight-point chamfered corners, thin steel outline, localized top-left and bottom-right lime edge highlights.
- No thick neon outline around the entire perimeter.
- Small three-dot window indicator across the top, a fine interior rule, and a short separator above the closing label.
- Reuse the central color theme for frame/text/lighting. The robot's lime highlights are baked into the raster and will not automatically recolor if the theme changes.
- No repeated GitHub terminal command **inside** the card; the command separator belongs immediately above it.

### Left visual

- Use `robot-realistic-transparent.png` exclusively for the mascot.
- Render without changing aspect ratio or cropping its raised fingers, head, or chest symbol.
- Maintain a little padding around the head/hand.
- Target source card region is approximately x=35–313 and y=53–293.
- The original pose is static; never rotate the entire raster to counterfeit a wave.

### Right identity farewell

- A thin steel vertical rule begins near x=325, below the top status strip.
- Large headline starts near x=351, y=79, size around 32 source pixels, bold and legible.
- Text **must be exactly** `Thanks for stopping by.`
- Keep `Thanks for ` off-white and `stopping by.` lime.
- Add a narrow lime blinking cursor immediately after the currently revealed characters.
- Four principles form a readable **vertical list**, starting around y=144, spaced by approximately 27 units.
- Use simple triangular lime bullets or library icons if desired; don't pack oversized icon panels into the compact layout.
- Closing label `// Session Closed //` centered at the bottom, below a subtle rule.

## 5. Typewriter timing and GIF requirements

The README must not depend on JavaScript, React, CSS keyframes, client-side SVG animation, or scroll triggers. GitHub README rendering sanitizes runtime interactivity. **Use the generated GIF.**

The packaged generator currently uses:

- 46 frames, nominal 105 ms each (~4.8 seconds total, actual playback dependent on GIF viewers).
- First ~0.3 seconds: initial cursor and empty headline.
- Next ~2.4 seconds: character-by-character appearance.
- Remaining frames: complete headline held on screen; cursor gently blinks.
- The robot remains perfectly stable in its original raised-hand pose.
- Frame count, first/last wording, and readable hold must be visually tested before publishing.

Important: GIF encoders may coalesce identical frames when optimizing. Compare frames by decoding the output rather than asserting an exact frame count.

### Static fallback

`logout-card-static.png` must show the full completed headline, full four principles, and `// Session Closed //`. It is the accessible, no-motion alternative. Do not publish an empty first GIF frame as the only fallback.

## 6. Integrate with the existing README generator

**First** use the current shared terminal-separator generator, with the command `logout` (or the existing syntax that produces `naresh@github:~$ logout`); do not add a second nearly-identical generator if one exists.

**Then** insert the centered animated card. Example GitHub-compatible Markdown/HTML:

```html
<!-- Final Logout Footer: one shared terminal separator above this image -->
<p align="center">
  <img
    src="./assets/logout-footer/logout-card-animated.gif"
    alt="Thanks for stopping by. Built with curiosity, driven by systems, always learning and always shipping. Session closed."
    width="770"
  />
</p>
```

For a static image substitute:

```html
<p align="center">
  <img src="./assets/logout-footer/logout-card-static.png"
       alt="Thanks for stopping by. Session closed." width="770" />
</p>
```

Do not embed both versions visibly at once. Some custom HTML or image sizing behaviors may vary in GitHub's mobile viewport; inspect the **actual GitHub-rendered branch README** and adjust width if needed. If the build produces a Markdown image rather than an HTML image, preserve equivalent centering and responsive constraints where possible.

In `scripts/build.py`, wire the step to rebuild the footer assets **before** final README assembly if the pipeline is responsible for artwork generation. The build must remain idempotent: repeated executions don't duplicate the footer, social buttons, or section header. Avoid regenerating GIF on every README view; GIF is an artifact committed or generated in CI.

## 7. Quality and validation

Run the provided package tests, then validate against the *actual* repository:

1. Robot RGBA alpha has transparent pixels around its silhouette (not a white rectangular matte).
2. The visual preserves the exact premium robot likeness—metal shell, glossy dark visor, glowing smiling eyes, single raised hand, chest code symbol.
3. GIF visibly types the headline over multiple unique frames; complete phrase is held long enough to read.
4. Four principles use the approved exact phrases and are not duplicated elsewhere in the footer.
5. The logout separator appears exactly once, and the card appears exactly once, **after** Connect All.
6. The footer does not repeat social links and does not accidentally restore cartoon line-art files.
7. Rendering is acceptable in GitHub dark and light UI themes.
8. The card is compact and centered at desktop width, with no horizontal overflow on mobile.
9. All paths are local repository paths; no fragile external CDN.
10. No secrets, private project names, or tokens are embedded.
11. The central theme configuration is not overwritten.
12. Existing hero, engineering focus, featured projects, writing, atlas, and developer playground remain untouched.

### Required report

After integrating, report exactly which source files changed, which generated assets were replaced, whether any obsolete robot assets were removed, GIF duration and dimensions, validation results, and any remaining constraints. Show the rendered README preview.

**Do not commit, push, merge, or activate publishing workflows without the user's authorization.**

## 8. Final implementation instruction

**Use the packaged realistic transparent robot PNG and pre-rendered typing GIF, preserve the `logout` terminal separator, render one compact closing card after Connect All, and stop.** Do not reinvent another style or modify earlier sections.
