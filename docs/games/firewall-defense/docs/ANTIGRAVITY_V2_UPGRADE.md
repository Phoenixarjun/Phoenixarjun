# Integration: Firewall Defense 2.0 (update the EXISTING game)

## Intent

The user already has Firewall Defense installed among five independent games. **Do not create a sixth game, new folder beside it, or duplicate arcade entry.** Update the current Firewall Defense implementation in its existing folder only. Nothing in the wider GitHub profile, its README generation, other arcade games, or shared navigation needs changing.

## Confirm integration location

The source package is supplied in `firewall-defense-titanium/`. Inspect your real GitHub profile repository to locate the actual installed Firewall Defense directory (possibly `docs/games/firewall-defense/` or `docs/arcade/firewall-defense/`). Do not assume either path. Confirm that the existing `src/engine.mjs`, `src/main.js`, `src/renderer.js`, `style.css` and `index.html` still match the original version or inspect differences before proceeding.

## Files to merge into the existing game

- `src/engine.mjs` — existing simulation extended to 30 waves, six towers, abilities, bosses and endless mode.
- `src/main.js` — existing HUD and controls extended; old game loops retained.
- `src/renderer.js` — added beam, muzzle, freeze, boss and shield effects.
- `style.css` — scoped additional Command Protocol styles, no reset of original layout.
- `index.html` — one Command Protocol strip, updated labels/help, continue endless button.
- `tests/engine.test.mjs`, `tests/browser_smoke.py` — expanded regression tests.
- `build_standalone.py` — unchanged original exporter; regenerate standalone.html from edited source.
- `arcade-manifest.json` — updated game description only; **keep the existing launcher references**.

Keep any additional shared arcade navigation code that Antigravity already added. In particular, **do not overwrite existing header-only customizations** with an old `index.html`; merge only the V2 sections into it.

## Quick diff review

`docs/FIREWALL_V2_SOURCE.patch` shows exactly what changed relative to the original 8-wave ZIP. Review this diff to resolve any merge conflicts in an integrated game. Do not apply a patch without first checking that the target tree matches its base.

## Commands

```bash
npm test
python build_standalone.py
python tests/browser_smoke.py
```

The browser test requires Python Playwright and an installed system Chromium; on Windows, configure its Chromium path or run an equivalent Playwright browser test using your local browser.

## Important behavior changes

- Wave progress now reads **01 / 30**, not **01 / 08**. After wave 30 the player can restart or opt into Endless Mode.
- Tower hotkeys are **1–6**, abilities **E/O/Q**.
- The two new weapon modules are *Scatter Cannon* (triple-shot) and *Rail Lance* (piercing beam).
- Ability buttons are enabled only during active waves when affordable and off cooldown.
- The original 290 starting credits and 20 integrity remain unchanged. The existing local high-score storage key remains unchanged.
- Original gameplay GIF may show legacy balance or fewer tower types; use the supplied updated preview asset if present.

## Do not change

- No changes to README / GitHub profile sections.
- No changes to Packet Breaker, Pinball, Runtime Rush or Stack Overflow.
- Do not rename old launch paths or change GitHub Pages setup.
- Do not make up test results or claim deployment.
- Do not push / merge / deploy without explicit user approval.

## Acceptance

The existing game opens, all six towers can be selected and built, EMP/Overclock/Shield each work and spend credits, the six milestone bosses appear, a solid strategy can clear 30 waves, an unprotected core can be lost, original pause/speed/restart still work, mobile has no page overflow, and the Games hub still launches Firewall Defense at its original URL.
