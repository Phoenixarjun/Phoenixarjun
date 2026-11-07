# GitHub Profile 2.0 — Realistic Logout Footer V2

**Replacement for the old neon-outline waving robot kit.**

The user approved a realistic white/silver robot with a glossy black smiling visor, neon-lime accents, and a raised waving hand. This kit isolates that subject into a **transparent PNG** and replaces the old outline mascot in the centered logout-card build. The **card headline types in the animated GIF**; the robot itself is a static realistic raised-hand pose.

## Files

- `assets/logout-footer/robot-realistic-transparent.png` — original robot cutout (RGBA)
- `assets/logout-footer/logout-card-static.png` — complete readable PNG fallback
- `assets/logout-footer/logout-card-animated.gif` — GitHub-compatible typewriter animation
- `assets/logout-footer/logout-terminal-separator.svg` — optional separator reference; reuse your repo's current terminal separator instead
- `scripts/build_logout_footer.py` — generator reading `content/logout-footer.json` and existing `design/themes.json`
- `content/logout-footer.json` — content configuration
- `docs/ANTIGRAVITY_LOGOUT_FOOTER_IMPLEMENTATION.md` — complete migration and integration prompt
- `previews/` — rendered checks
- `tests/test_logout_footer.py` — package-level validation

## Commands

```bash
python -m pip install "Pillow>=10,<13"
python scripts/build_logout_footer.py
python -m unittest discover -s tests -p 'test_logout_footer.py' -v
```

Extract at the root of the existing `Phoenixarjun/Phoenixarjun` repository. **Do not** replace your existing README, `design/themes.json`, or workflows. Integrate by editing the source README generator and render one shared `logout` separator above the card. When replacing the old kit, remove old vector-cartoon references only after verifying nothing else depends on them.

## Note on fidelity

The realistic robot is pixel-based generated artwork, not a path-perfect SVG; it is intentionally shipped as transparent PNG to preserve surface detail. The frame/text are programmatically generated and centrally themed. The GIF animates *only the headline*, not the robot's actual arm.
