# Antigravity — Runtime Rush / Game 03 Integration Guide

## Mission and scope

Integrate **Runtime Rush** as an independent Game 03 into the future developer arcade inside `Phoenixarjun/Phoenixarjun`, currently worked on in the `redesign/profile-v2` branch. Packet Breaker and Circuit Pinball are separate completed packages. Firewall Defense and Stack Overflow are still planned; do not create false playable links for them.

**Do not edit the profile README, hero, project content, other games, GitHub Actions, Pages configuration, or deployment settings during initial copying. No push, commit, merge, or automatic deployment.**

## Package inventory

- `index.html`, `style.css`, `src/physics.mjs`, `src/renderer.js`, `src/fallback.js`, `src/audio.js`, `src/game.js`: full editable standalone implementation.
- `standalone.html`: one-file playable offline build with scripts and styling inlined.
- `assets/favicon.svg`: custom vector icon.
- `previews/`: real browser screenshot previews and gameplay animation where provided.
- `tests/physics.test.mjs`, `tests/scenarios.mjs`, `tests/browser_smoke.py`: physics and interaction checks.
- `tools/build_standalone.py`: deterministic local HTML export.
- `tools/export_to_profile.py`: defensive dry-run exporter.
- `arcade.manifest.json`: registry candidate for future game selector.
- `docs/PHYSICS_AND_DESIGN.md`: mathematical model, constraints and test details.

## Exact design intent

Runtime Rush is a high-contrast panoramic sci-fi **3D infrastructure tunnel**, not a brick breaker or pinball table. It must retain its own visual identity while reusing Titanium Hacker colors and terminal design language. Navigation and game overlay: one packet/sphere traveling through three lanes, procedural architectural corridor, glowing infrastructure gantries, hazard blocks, low barriers, sliding security gates and floating energy orbs. Right-side telemetry panel, HUD, sector progression, compact responsive control deck, source code wholly local.

**Theme values:** graphite `#0C0F10`, deep `#070B0C`, steel `#42535C`, surface `#1B2328`, neon lime `#B6FF3B`, text `#EEF7EF`. Red/amber danger and aqua signal indicators are semantic exceptions. Preserve style design, do not replace artwork with AI-generated flat backgrounds.

## Step 1 — Run and validate independently

1. Extract package outside the profile repository.
2. Open `standalone.html` in Chrome/Firefox/Edge, or serve the modular app using `python -m http.server 8000` and visit `http://localhost:8000/`.
3. Check a **GPU-enabled** browser: the WebGL 3D renderer should launch; if unavailable, the Canvas2D perspective fallback should take over without blocking play. Report which backend was tested.
4. Confirm left/right lane inputs move in the same direction as the key pressed (the world +Z camera reverses world X).
5. Test jump/slide timing, low-barrier clearance, overhead-beam collision, core-block collision, energy pickup, shield absorption, overclock, scoring, sectors, high score, life loss and retry.
6. Run `node --test tests/physics.test.mjs` and `node tests/scenarios.mjs`.
7. Run `python tests/browser_smoke.py` if Python Playwright and Chromium are installed. This test uses an in-memory standalone page to support environments restricting localhost and records mobile/desktop screenshots.
8. Manually test sound and mobile touch gestures on a real device. Automated checks do not prove perfect balance.

## Step 2 — Copy the game into the correct Pages source

Read the repo's actual Pages settings and existing publish workflow before choosing a location. If the Pages source is `docs/` on the published branch, a safe candidate destination is:

```
Phoenixarjun/
  docs/
    arcade/
      runtime-rush/
        index.html
        style.css
        assets/favicon.svg
        src/game.js
        src/physics.mjs
        src/renderer.js
        src/fallback.js
        src/audio.js
```

Use the provided exporter for a **dry run** first:

```
python tools/export_to_profile.py --profile-repo /path/to/Phoenixarjun
```

After reviewing that output, and only with authorization:

```
python tools/export_to_profile.py --profile-repo /path/to/Phoenixarjun --apply
```

The exporter refuses overwrites and never touches README.md or workflows. If Pages uses an Actions artifact or different directory, adapt the output location based on verified configuration. Use relative imports and asset paths; never assume `/` root on a project Pages site.

## Step 3 — Verify deployed candidate URL (do not assume it works)

A potential project-Pages URL, **only if `docs/` publishing is activated on the appropriate branch**, is:

`https://phoenixarjun.github.io/Phoenixarjun/arcade/runtime-rush/`

Do **not** add this URL to README or shared arcade menu until it actually returns the playable game with all JS, CSS and favicon loading, and a completed playthrough works. Avoid a second conflicting Pages workflow. The existing `docs/runner.html` game is a legacy experiment and should not be deleted as part of this source copy.

## Step 4 — Future unified five-game hub (separate task)

Use `arcade.manifest.json` to register the game only when published and tested. Its manifest ID is `runtime-rush`. Build a future arcade selector with five distinguishable games; only deployed ones should have working launch controls:

1. Packet Breaker (existing separate package)
2. Circuit Pinball (existing separate package)
3. Runtime Rush (this package)
4. Firewall Defense (planned)
5. Stack Overflow (planned)

Keep each game scoped under its own path and localStorage key. Do not share mutable physics state or globals across games. A future README Developer Playground should link to the verified arcade hub, not an outdated direct System Runner page; **that is a later approved change, not part of this package**.

## Security / quality acceptance

- No API calls, external fonts, CDN scripts, trackers or telemetry.
- No `.env`, tokens or sensitive data in deployed Pages assets.
- Correct WebGL or Canvas fallback mode.
- No console errors on play/retry/pause/mobile.
- 120Hz fixed-step simulation and swept obstacle-plane collision.
- Guaranteed at least one open lane per obstacle pattern, with reasonable advance warning.
- UI responsive at 390px width, no horizontal overflow.
- Fully working keyboard, touch, pointer gestures and sound toggling.
- Safe launcher/deployment URL, absolute URLs only after verification.
- Prior 2 games and existing GitHub profile content remain untouched.
- No commit, push, merge or deploy without explicit approval.

## Final report

List files added, commands/tests **actually run**, rendering backend tested (GPU vs fallback), gameplay scenarios, approximate file sizes, mobile screenshots, pending real-device tests, Pages deployment status and exact public URL if *verified live*. Do not claim a perfect/photoreal 3D physics simulation; this is a polished arcade runner with native WebGL geometry, a robust simulation layer and a 2.5D fallback.
