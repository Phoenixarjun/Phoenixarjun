# RUNTIME RUSH — Game 03 / Titanium Hacker Arcade

**One packet. Three lanes. Endless infrastructure failure. Keep the request alive.**

Runtime Rush is a self-contained browser game: a glowing 3D data sphere races through a futuristic infrastructure tunnel, switching lanes, jumping over corrupted services, ducking beneath security beams, and collecting energy shards. It has a different gameplay loop and visual design from Packet Breaker and Circuit Pinball.

## Play locally

- **Fastest:** open `standalone.html` in a modern browser. Everything is in one HTML file; no network, API keys, npm packages, or web server are required.
- **Editable developer version:** `python -m http.server 8000`, then visit `http://localhost:8000/`. The modular `index.html` loads relative CSS and ES modules, so it needs HTTP(S) in browsers that block local file ES modules.

## Controls

| Input | Action |
|---|---|
| `A` / `←` | Shift one lane left |
| `D` / `→` | Shift one lane right |
| `Space` / `W` / `↑` | Jump |
| `S` / `↓` | Slide below overhead beam |
| `P` / `Esc` | Pause/resume |
| `M` | Toggle synthesized sound |
| `Enter` | Start / resume / retry |
| Swipe left/right/up/down | Move, jump, slide on touch surfaces |
| On-screen directional buttons | Mobile accessibility |

**Gameplay:** survive with 3 integrity points while distance and speed increase. Low barriers must be jumped, overhead scanners must be slid under, and core blocks require dodging or well-timed jumping. Energy shards increase score and combos; shields absorb one impact and overclock capsules temporarily slow the simulation to give you reaction time. The generator always leaves at least one unblocked lane per pattern row. There are five named speed sectors, followed by continued endless play.

## Technology

- **Native WebGL 3D renderer**, with real perspective camera, 3D meshes, shading, tunnel geometry, sphere and pickup meshes; no Three.js or other third-party runtime needed.
- **Perspective Canvas2D fallback** activates automatically if WebGL is unavailable (for example, restricted cloud browsers). Gameplay is fully functional in both renderers; fallback is 2.5D.
- **120Hz fixed-step simulation** independent of frame rate; physically integrated ballistic jumping, continuous obstacle-plane crossing, deterministic procedural level generation, lane easing, slide timing, invulnerability, damage, power-ups, and score accumulation.
- Responsive typography/UI, mobile controls, synthetic Web Audio, local high scores, accessible buttons and reduced-motion styling.
- Everything runs in the browser: no backend, network calls, analytics, login, or credentials.

## Repo contents

- `index.html` — editable game interface and semantic HTML
- `style.css` — Titanium Hacker visuals and responsive layout
- `src/game.js` — input, states, UI, simulation loop
- `src/physics.mjs` — pure deterministic physics and obstacles
- `src/renderer.js` — native WebGL 3D renderer
- `src/fallback.js` — perspective Canvas2D fallback renderer
- `src/audio.js` — optional audio synthesis
- `standalone.html` — offline one-file build
- `tests/physics.test.mjs` — focused physics unit tests
- `tests/scenarios.mjs` — idle / safe-run / deterministic replay stress tests
- `tests/browser_smoke.py` — desktop/mobile Chromium smoke test
- `tools/build_standalone.py` — rebuild offline HTML
- `tools/export_to_profile.py` — safe Pages export (dry-run by default)
- `arcade.manifest.json` — future five-game launcher manifest
- `docs/PHYSICS_AND_DESIGN.md` — formulas, game system and limitations
- `docs/ANTIGRAVITY_INTEGRATION.md` — future deployment instructions

## Rebuild and tests

```bash
python tools/build_standalone.py
node --test tests/physics.test.mjs
node tests/scenarios.mjs
python tests/browser_smoke.py  # optional: Python Playwright and Chromium
```

**Verification note:** physics tests and browser fallback tests ran in the development environment. Its headless Chromium has WebGL disabled, so the actual hardware WebGL renderer still requires verification in a GPU-enabled browser before deployment. Automated physics tests do not replace manual difficulty and device playtesting.

## Future profile integration

This package remains **Game 03**, independent of the two games already built. Proposed future public path (only if Pages is correctly configured to publish `docs/`):

`https://phoenixarjun.github.io/Phoenixarjun/arcade/runtime-rush/`

That address is **not claimed to be deployed or working**. Read `docs/ANTIGRAVITY_INTEGRATION.md`; run the dry-run exporter first, then perform actual published-URL verification. Do **not** modify GitHub README or Pages settings until the arcade hub is ready.
