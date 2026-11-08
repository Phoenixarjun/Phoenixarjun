# ANTIGRAVITY — Circuit Pinball Implementation & Future Arcade Integration

## Mission

Integrate the enclosed **Circuit Pinball** game as an independent playable unit in the existing GitHub profile repository. This is **game 02 of a proposed five-game arcade**. Packet Breaker is game 01 and must remain untouched. The other three games are not built yet and must not be represented as working.

**Repository:** `Phoenixarjun/Phoenixarjun`
**Development branch:** `redesign/profile-v2`
**Canonical branding:** Titanium Hacker: graphite `#0C0F10`, surface `#1B2328`, steel `#42535C`, lime `#B6FF3B`, text `#EEF7EF`.

## What is already supplied (do not recreate from a screenshot)

- Full working `index.html` and `style.css`.
- Four separate, readable JS sources: `src/physics.js`, `src/render.js`, `src/audio.js`, `src/game.js`.
- One-file standalone build `standalone.html`.
- Native SVG favicon and genuine browser-captured gameplay preview images/GIF.
- 18 Node physics tests plus desktop/mobile Chromium integration tests and scenario tests.
- Physics formulas, geometry rationale, control mapping, test results, and packaging scripts.
- `arcade.manifest.json` for discovery by a future games menu.

Read `README.md` and `docs/PHYSICS_AND_DESIGN.md` before making code changes.

## Exact scope

This task is **not** approval to modify the published GitHub profile, redesign the existing Packet Breaker, change Pages settings, commit, or deploy anything automatically. Review the repository state and existing Pages source first.

### Phase 1 — Validate locally

1. Extract this pack outside the profile repository.
2. Open `standalone.html` locally, or serve `index.html` from a static HTTP server.
3. Test desktop at 1440×900 and mobile at 390×844.
4. Confirm 120-Hz physics loop, normal startup, charge/release, two flippers, bumper/target scoring, nudge/tilt, multiball, pause/resume, sound toggle, and natural life loss.
5. Run `node --test tests/physics.test.cjs`.
6. If Python + Playwright + Chromium are available, run `python tests/browser_smoke.py` and `python tests/gameplay_scenarios.py`. These tests load a self-contained in-memory document, requiring no public network access.
7. Inspect console errors and playtest manually. Do not claim all difficulty levels are perfectly balanced on the strength of unit tests alone.

### Phase 2 — Additive source copy

Suggested destination:

```text
docs/
  arcade/
    circuit-pinball/
      index.html
      style.css
      assets/favicon.svg
      src/physics.js
      src/render.js
      src/audio.js
      src/game.js
```

Use the included safe-copy script as a planning aid:

```bash
python tools/export_to_profile.py --profile-repo /path/to/Phoenixarjun
# After reviewing the output:
python tools/export_to_profile.py --profile-repo /path/to/Phoenixarjun --apply
```

The script refuses overwrites by default and **never** touches README, Workflows, Packet Breaker, or any other section. Adjust the destination only if the existing Pages site uses a different source structure.

### Phase 3 — Pages inspection

1. Determine whether GitHub Pages publishes the default branch, `/docs`, or a GitHub Actions artifact.
2. Determine the active profile repository's URL prefix; do not guess it.
3. In `/docs` publishing mode, the candidate game URL is typically:
   `https://phoenixarjun.github.io/Phoenixarjun/arcade/circuit-pinball/`
4. Confirm the deployed `index.html`, `style.css`, and `src/` resources respond successfully. Relative paths must continue to resolve in a subdirectory.
5. Verify browser rendering and controls on the **real** deployed URL before linking it in README.
6. Do not add a second Pages deployment workflow if one already exists.
7. Never expose GitHub API tokens or `.env` files to Pages.

### Phase 4 — Future five-game hub (NOT part of this delivery)

The user plans a future unified arcade launcher where visitors can choose from five games. When enough games are independently stable, create an arcade hub under `docs/arcade/index.html` that reads an approved manifest list and offers real entry points. Proposed series:

1. Packet Breaker — already built, existing independent package.
2. Circuit Pinball — this package.
3. Runtime Rush — planned, not yet built.
4. Firewall Defense — planned, not yet built.
5. Stack Overflow — planned, not yet built.

Do not create dead links, fictional game previews, or playable-looking buttons for unfinished games. An arcade menu should include only games that are tested and published. Only then replace the README's existing System Runner preview with a verified arcade launcher URL and an appropriate multi-game showcase design. Preserve the README's section order.

### Future interface contract

Use each game's scoped folder with its own entry point, assets, localStorage keys, CSS, and JS. Avoid global styles leaking into the hub by navigating to separate pages or containing each game in a sandboxed iframe if needed. Preserve game-specific controls and avoid overriding browser shortcuts when focus is outside a game. Do not share mutable physics code across unrelated games just to reduce file count.

The package exposes a deliberately small, compatible manifest:

```json
{
  "id":"circuit-pinball",
  "title":"Circuit Pinball",
  "entrypoint":"./index.html",
  "category":"Physics Arcade"
}
```

Any future hub must resolve paths relative to the deployed location, not the original development directory.

## Acceptance checks

- New game deploys and plays independently.
- Score, controls, bumper/collision behavior, extra lives, tilt and game-over function.
- No console errors on real Chrome desktop and mobile.
- No horizontal overflow at typical mobile widths.
- README, Hero, Engineering Focus, project cards, blog list, Contribution Atlas, Connect All and logout card remain untouched.
- Existing Packet Breaker folder and launcher remain unchanged.
- All game code is inside its own scoped directory with relative paths.
- No APIs, permissions, tracking, external fonts or external asset requirements.
- No secrets, token values or `.env` committed.
- Source, renderer and tests remain editable and maintainable.
- No commit, merge, push or Pages deployment without explicit permission.

## Final delivery report

List exact files copied/edited, tests actually run, screenshots, actual deployed URL if published, unresolved issues and any performance findings. Report gameplay as a **2D physics simulation with 2.5D lighting and metallic surfaces**; do not claim a true rigid-body 3D pinball engine. Human playtesting is still needed to finalize difficulty.
