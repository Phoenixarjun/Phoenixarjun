# Quality assurance — Packet Breaker v1

## Automated physics checks (passed)

Command: `node --test tests/physics.test.mjs`

**17 passing test cases**, including:
- High-speed swept collision against front/top faces with no tunneling.
- Direction away from object results in no collision.
- Exact rounded-corner contact normal and rejection of a near-corner false positive.
- Paddle reflection geometry and limiting projectile speed.
- Wall intersection and reflection.
- **10,000 deterministic randomized sweeps** with finite and normalized contact information.

## Browser smoke checks (passed)

Command: `python tests/browser_smoke.py` with Playwright and a local Chrome/Chromium installation.

- Initial menu rendered and internal game state initialized.
- INITIALIZE RUN → READY.
- Mouse/tap or Space → PLAYING.
- Score increases after a brick is hit.
- Pause and resume controls work.
- Sound toggle works.
- 390px touch viewport has no horizontal overflow; tapping launches a packet.
- No uncaught JavaScript page errors in observed sessions.

## Longer play simulation

A desktop browser run advanced from three lives through brick collisions, score changes, packet loss, and the GAME OVER state. No runtime errors occurred. Another traced run with predictive paddle movement repeatedly bounced the ball without losing lives, which verifies that successful defensive play is possible and that paddle collisions register at high speed.

## Export safety (passed)

The optional Pages exporter was exercised against a temporary mock profile repository. It copied the game into `docs/packet-breaker/`, preserving the existing `README.md` and `docs/runner.html` exactly.

## Visual checks

Generated desktop menu and gameplay screenshots, an animated gameplay preview GIF, and a 390px mobile screenshot. The dark surfaces, lime accents, metal brick facets, ball trails, controls, HUD, overlay, and responsive layout were reviewed.

## Not claimed

- The full five-stage campaign and endless mode have not been playtested to completion by multiple humans.
- Game feel, difficulty, and power-up balancing have not been user-acceptance tested.
- A public GitHub Pages URL has not been verified or deployed.
- The visuals are **2.5D Canvas**, not a real-time WebGL 3D scene. This was chosen to prioritize reliable collisions and smooth play rather than heavy 3D dependencies.
