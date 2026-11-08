# Antigravity Integration Specification — Titanium Hacker Arcade / Game 04

## Your mission

You are integrating a **completed independent game package** into a future five-game GitHub Pages arcade. You must **not** replace or overwrite the existing Game 01 Packet Breaker, Game 02 Circuit Pinball, or Game 03 Runtime Rush. The games are intentionally decoupled until the shared arcade hub is built.

Repository under consideration: `Phoenixarjun/Phoenixarjun`, development branch `redesign/profile-v2`.

## 0. Read first

Inspect the existing repository, `.github/workflows/`, Pages publishing source, `README.md`, and `scripts/build.py`. Understand the current Pages setup before modifying anything. The user has not authorized an automatic commit, merge, or deployment.

### Files delivered

The authoritative editable game consists of `index.html`, `style.css`, `src/engine.mjs`, `src/renderer.js`, `src/main.js`.

`standalone.html` is a portable offline *generated artifact*; don't edit it by hand. Run `python build_standalone.py` after changes. The `tests/` directory contains Node and optional browser regression suites. `assets/` contains real screenshots, a gameplay GIF, and a cover image, not an illustrated fake.

## 1. Integration target

Use an independent future publishing path:

```text
docs/
  arcade/
    index.html                   # arcade selector, NOT INCLUDED YET
    packet-breaker/
    circuit-pinball/
    runtime-rush/
    firewall-defense/
      index.html
      style.css
      src/
        engine.mjs
        renderer.js
        main.js
      assets/
        arcade-cover.png
        firewall-defense-gameplay.gif
    stack-overflow/            # Game 05, pending
```

Do not use `docs/runner.html` or overwrite its existing content. Do not place all games' global CSS/JS into one directory; each game is an isolated relative-path mini application.

### Copying

Use the included exporter, with an explicit destination:

```
python scripts/export_to_profile.py /path/to/Phoenixarjun --dry-run
python scripts/export_to_profile.py /path/to/Phoenixarjun
```

The exporter copies only into `docs/arcade/firewall-defense/` and refuses to overwrite existing files unless explicitly called with `--force`. It does not edit the profile README or enable Pages.

## 2. Preserve theme and component isolation

Palette:

- Base `#0C0F10`, deep canvas `#070B0C`
- Surface `#1B2328`, Steel `#42535C`
- Accent lime `#B6FF3B`, text `#EEF7EF`
- Accent-only supporting lights: cyan for south route, amber pulse, violet IDS.

No Bootstrap, external fonts, analytics, or new application framework is needed. The game uses semantic HTML, CSS, and Canvas. It is **2.5D vector visualization** of a tactical board, not true 3D. Do not market it as a physically accurate network simulator.

Keep the overall source style distinct from the other games but share future arcade hub typography and link navigation.

## 3. Mechanics that must remain intact

- Two simultaneous attack routes; 22 permitted build nodes.
- Four upgradeable tower types, each with distinct effects.
- Eight escalating waves, including stealthed, armored, shielded and final Titan packets.
- Independent game simulation fixed at 120 Hz.
- Distance-based route interpolation and swept segment-circle bullet hits.
- Resource accounting, resale values, wave rewards, core integrity, scoring.
- Pause/resume, 1×/2×, keyboard shortcuts, pointer/touch placement, audio toggle.
- Mobile board can scroll horizontally inside its container without page-level horizontal overflow.
- Optional local best-score persistence; no remote analytics or login.

Do not turn this into a scripted click-through. The player must choose tower placements and upgrades, and weak choices must genuinely risk failure.

## 4. README embedding: later arcade hub

The README cannot run JavaScript games directly. When the five-game arcade is deployed, the GitHub profile's Developer Playground section should show a simple **Arcade Hub** preview linked to the deployed selector, rather than the old `System Runner` card.

Do not put five full game canvases into README. Do not invent a Pages URL until the publishing source and live deploy have been checked. A likely URL after a verified `docs` Pages setup will be:

`https://phoenixarjun.github.io/Phoenixarjun/arcade/firewall-defense/`

This is a *candidate*, not an availability claim.

Do not change `README.md` or `scripts/build.py` in this Game 04 integration until the shared arcade design is finalized.

## 5. Preflight and tests

```
node --test tests/engine.test.mjs
python build_standalone.py
python tests/browser_smoke.py  # optional Chromium/Playwright
```

Use `python -m http.server 8000` from the game directory for local HTTP testing; open `http://localhost:8000/index.html`.

Verify on real browsers, including touch-capable mobile where available:

1. Place all four types on different nodes, not on paths.
2. Click a built tower and upgrade it twice; third upgrade must be refused.
3. Sell a tower; bandwidth credit refund must match its investment.
4. Deploy wave and observe packets on both routes; towers must fire.
5. Confirm armor, shields, stealth, slow and beam chaining at higher waves.
6. Pause, resume, 2× speed, sound toggle, local high scores, Help dialog.
7. Lose with underpowered build; win with a calculated mixed-tower strategy.
8. Run mobile tap and horizontal board scroll test.
9. Refresh and verify no broken relative paths.
10. Report any different behavior in Safari, WebKit, or slower mobiles rather than claiming it was tested if it wasn't.

## 6. User-approval boundary

Do not commit, push, activate GitHub Pages, replace the current README Developer Playground, or remove the old System Runner automatically. Only prepare an additive integration and report actual status. Keep Game 01, 02 and 03 source folders independent. Game 05 will be added later.

## Final report

Provide changed file list, actual test commands/results, deployment status, playable local path, any mobile limitations, and the exact verified live URL only if it genuinely exists.
