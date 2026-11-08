# ANTIGRAVITY — Stack Overflow Game 05 Integration Specification

## Context and scope

The GitHub profile belongs to `Phoenixarjun/Phoenixarjun` and currently uses the **Titanium Hacker** theme. The user plans a five-game arcade featuring Packet Breaker, Circuit Pinball, Runtime Rush, Firewall Defense and **Stack Overflow**. This package is **Game 05 only**; do not merge code from different games prematurely, overwrite a working arcade or change the public README before the user approves the unified arcade selector.

Treat this package as the authoritative implementation of Stack Overflow. Preserve its independent deployability and game mechanics, and reuse its look/feel in the eventual arcade hub.

## Existing package

- `index.html`: modular production entry (loads `style.css`, `src/main.js`).
- `style.css`: responsive Titanium Hacker interface with engineering telemetry.
- `src/physics.mjs`: fixed-step game engine, deterministic staged difficulty, rectangular landing, kinematics, center-of-mass stability.
- `src/renderer.js`: 2.5D server tower in Canvas, scan target, floor, effects.
- `src/main.js`: sound, keyboard/pointer/touch, UI, focus, persistence.
- `standalone.html`: complete offline single HTML with source embedded. May be opened directly.
- `build_standalone.py`: deterministic build from the modular files.
- `arcade-manifest.json`: portable information for the future game selector.
- `assets/arcade-cover.png`: actual game screenshot formatted as a cover, not generated art.
- `assets/stack-overflow-gameplay.gif`: captured actual gameplay frames.
- `tests/physics.test.mjs`: physics and simulation tests.
- `tests/browser_smoke.py`: Chromium interactive test covering desktop/mobile.
- `docs/ENGINEERING_AND_PHYSICS.md`: documented formulas and simplified physics model.
- `scripts/export_to_profile.py`: conservative exporter.

## Visual contract

Central palette (do not improvise independent theme): graphite `#0C0F10`, deep canvas `#070B0C`, steel `#42535C`, surface `#1B2328`, neon lime `#B6FF3B`, off-white `#EEF7EF`; supporting aqua `#80D8C7` and subdued metal tones are allowed. The page already follows this direction. The game uses UI panels, a glowing moving block, isometric-looking server blocks, a signal-grid arena, HUD metrics and a compact terminal footer.

Use a mono font stack for technical labels and a readable UI sans stack for headings. Keep functionality and readability ahead of visual effects. Do not add Three.js, GSAP, physics engines, external APIs, third-party fonts or trackers as prerequisites unless they materially improve the game and are separately approved.

## Gameplay contract

The game is a precision server-stacking arcade, not a visually static puzzle. A moving layer scans left/right. `Space`, click or tap commits a drop. Once released, the block falls with constant gravity and a small amount of horizontal drift from release momentum and sector-dependent wind. The supported overlap remains as the new platform; overhang is visually trimmed. Too little contact or failed stack support ends the run. Centered perfect drops add bonus points, recharge focus, and restore a small amount of platform width. Increasing difficulty is driven by scan speed, wind, and narrowing width. There are five sectors followed by an endless challenge.

Controls:

| Action | Desktop | Touch |
| --- | --- | --- |
| Start | Start button | Start button |
| Drop | Space / click board / drop button | Tap board / drop button |
| Precision focus | Hold Shift / hold Focus button | Hold Focus button |
| Pause | P / pause button | Pause button |
| Restart | R / restart button | Restart button |

No social accounts or backend needed. Scores are local to the visitor's browser. There is no global ranking or data collection.

## Mandatory pre-integration checks

1. Inspect the existing `Phoenixarjun/Phoenixarjun` repo and current published Pages source (`docs` directory, root, or Actions artifact). Do not assume the Pages configuration.
2. Check all existing `docs/arcade/` files. Avoid overwriting same-name assets or routes.
3. Check README generator `scripts/build.py` and existing Developer Playground path; do not hand-edit generated files that will be overwritten.
4. Check the actual active theme preset and any shared arcade UI design tokens; map game CSS tokens if centralized theming is planned, but preserve working standalone mode.
5. Run `node --test tests/physics.test.mjs` (Node 20+ is sufficient). Build standalone and compare generated assets.
6. Review the game in desktop and mobile browsers; check keyboard, pointer, touch, pause during drop, restart, scoring, game over, and no JS console errors.

## Safe initial export

From this folder, to inspect the copying plan:

```bash
python scripts/export_to_profile.py /path/to/local/Phoenixarjun
```

When the target is confirmed clean and the existing Pages configuration is correct:

```bash
python scripts/export_to_profile.py /path/to/local/Phoenixarjun --apply
```

That copies only this game's public files to `docs/arcade/stack-overflow/`. It does **not** edit the root README, workflows, Pages settings, other games, or existing profile graphics. It refuses to replace an already-populated target directory. For a GitHub Pages site published from the repository's `docs/` folder, the expected eventual path is:

`https://phoenixarjun.github.io/Phoenixarjun/arcade/stack-overflow/`

This URL is conditional on Pages configuration and deployment; verify it before displaying it in the profile.

If Pages publishes through a workflow, include the files in the workflow's published artifact instead of assuming a `docs` folder is automatically published.

## Future shared arcade (do NOT implement without instruction)

Eventually create a shared landing page with five distinct choices: Packet Breaker, Circuit Pinball, Runtime Rush, Firewall Defense, Stack Overflow. Read each game's manifest and use its real poster/screenshot, description, and controls. Give users a real **Play** link, not a static interaction disguised as a button. Keep games isolated in `docs/arcade/<slug>/` so one game's scripts and CSS do not affect the others.

Only after the five-game selector is built and tested should `README.md` change its Developer Playground section to point to the unified arcade rather than an individual game. Make this change in its authoritative generator as well.

## Functional acceptance tests

- A new session starts and a server module moves across the top.
- A real user can drop through keyboard, mouse and touch input.
- A correctly aligned drop lands and increases score and layer count.
- Off-center overlap trims unsupported width accurately.
- A miss causes game over and the overlay offers replay.
- Pausing during a committed drop freezes the drop and resumes correctly.
- Holding Shift/Focus reduces movement speed and consumes a finite meter.
- Stage progression changes scan velocity and wind pressure.
- Score and personal best remain local (no server calls).
- GIF shows actual gameplay, not a fake screenshot of buttons.
- All paths resolve when published via the selected GitHub Pages source.
- Browser canvas resizing creates no horizontal scroll on mobile.
- Readme/profile sections, personal data, `.env`, tokens, and other games remain unchanged.

## Final deliverable report

Report files copied, tests run, any failure found, actual Pages deployment path, desktop/mobile results, and whether the shared arcade selector has been touched. Do not claim the game is deployed or the public URL works until it has been opened successfully. Do not push, commit, change deployment settings, or rewire the profile README without authorization.
