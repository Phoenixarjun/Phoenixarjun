# ANTIGRAVITY IMPLEMENTATION REQUEST — Packet Breaker // Developer Playground

You are acting as a senior browser-game engineer, frontend specialist, gameplay physics reviewer, and GitHub README maintainer.

**Objective:** Replace the currently unsatisfying `System Runner / Architecture Grid Runner` section of my GitHub Profile 2.0 with the provided fully playable **Packet Breaker** arcade game, preserving Titanium Hacker visual branding. Integrate the public game as a GitHub Pages static site and keep an animated or static preview linked from my GitHub README.

**Repository:** `Phoenixarjun/Phoenixarjun`, branch `redesign/profile-v2`.

## Non-negotiable principles

1. **Reuse the supplied implementation rather than recreate it from an image.** Audit `index.html`, `style.css`, `src/game.js`, `src/physics.mjs`, `dist/game.bundle.js`, `scripts/build.mjs`, tests and screenshots.
2. **Do not rebuild other profile sections.** Preserve approved Hero, Engineering Focus, Featured Projects, Currently Building, Engineering Stack, Technical Writing, Contribution Atlas, Connect All and Logout Footer.
3. **Never claim an unverified Pages URL is live.** Inspect the actual Pages source and browser-test the resulting link.
4. **A GitHub README cannot run a JavaScript arcade game.** It must show a normal image/GIF which opens the published game via an anchor.
5. **No automatic deployment or commit** without my explicit approval.

## Phase 1 — Play and inspect supplied source

- Open `index.html`; no npm install is required to play the prebuilt output.
- Click **INITIALIZE RUN**, then click/tap the arena or press Space to launch.
- Test arrow/A-D controls, mouse movement, touch, pause, resume, reset, sound toggle, best score, losing lives, stage changes, and post-victory endless mode.
- Confirm all stage layouts are viable and all destructible bricks can be hit.
- Study `docs/GAME_DESIGN_AND_PHYSICS.md` before changing collision calculations.

## Phase 2 — Physics verification

- Run `node --test tests/physics.test.mjs` (17 tests, including 10,000 randomized swept circle cases).
- The game runs physics at a fixed 120 Hz, with exact swept-circle face/corner collision tests, paddle-angle steering, clamped velocity, and per-frame iteration cap.
- Physics must not depend on frame rate. Do not switch to naïve position-update collision tests that permit tunneling.
- Add regression tests for any physics bug discovered. If editing source, run `node scripts/build.mjs` and verify the generated `dist/game.bundle.js` is updated.
- Be conservative about adding heavyweight Three.js/GSAP dependencies: the existing 2.5D solution is an intentional performance/reliability decision, not an unfinished 3D game.

## Phase 3 — Titanium Hacker design verification

Global palette: base `#0C0F10`, deep `#070B0C`, surface `#1B2328`, steel `#42535C`, lime `#B6FF3B`, text `#EEF7EF`.

Keep the metallic brick bevels, responsive dark HUD, glowing packet trails, particle impacts, paddle reflections, power-up capsules, accessible controls, and floating score effects. Preserve clear typography. No unrelated cyan/purple palette. Retain graceful offline fallback fonts (no font files should be committed).

The page is deliberately a **playable 2.5D arcade**, not a nonfunctional 3D illustration. Focus on responsive playability before considering optional shader polish.

## Phase 4 — Export to the existing Pages source

Read `docs/GITHUB_PAGES_AND_README.md`.

1. Inspect existing profile repo Pages settings and the old `docs/runner.html`.
2. Run `node scripts/export-pages.mjs --target "<local checkout of Phoenixarjun>"` or copy browser files manually to `docs/packet-breaker/`.
3. Confirm **only** that new directory was changed by the exporter.
4. Check whether Pages publishes `docs/` from the intended branch or via a build artifact.
5. Preview/test the game at the actual deployed URL before making the profile link visible.

## Phase 5 — README integration

Edit the authoritative `scripts/build.py` to regenerate Section 08 as:

- Shared transparent separator: `naresh@github:~$ play --packet-breaker`
- Heading: `Developer Playground`
- Label: `Packet Breaker`
- Description: `Keep the packet alive. Break the bottlenecks.`
- Clickable `assets/playground/packet-breaker-preview.gif` (provided in assets) with a real validated Pages URL.

Do not duplicate Section 08 or leave the obsolete architecture-grid game as the main game. Do not assume embedding `<canvas>` in README.md will work. Preserve the other eight sections and their URLs.

If the game isn't deployed yet, prepare the section change but avoid linking to a dead Pages URL; mention what remains to be activated.

## Phase 6 — Test and report

Run physics tests and UI smoke tests after integration. Review desktop, narrow desktop, 390px mobile and tablet. Confirm no horizontal overflow, canvas input coordinates match CSS scaling, and taps on touchscreens don't scroll the canvas while playing.

Report all changed files, any new deployed address, Pages publishing mode, exact tests executed/results, screenshot of the rendered game, screenshot of the GitHub README preview, and unresolved issues. Do not claim the full 5-stage campaign was manually playtested unless it truly was.

**Completion criterion:** A visitor clicks an attractive Packet Breaker preview on GitHub, lands on a functioning arcade game, immediately understands the paddle/ball controls, can score points and lose, can play multiple levels and try again, and sees a consistently branded experience with no unnecessary setup.
