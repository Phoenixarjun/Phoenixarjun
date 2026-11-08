# Add Packet Breaker to GitHub Profile 2.0

**Target:** `Phoenixarjun/Phoenixarjun`, on the development branch `redesign/profile-v2`. Do **not** blindly overwrite the existing Pages site, README generator, or old `docs/runner.html`.

## A. Export the playable game

1. Back up or commit your profile's current state locally before integration.
2. Unzip this package to a local workspace.
3. In this game's directory, optionally run `node --test tests/physics.test.mjs`.
4. Export only its browser runtime to your GitHub profile checkout:

```bash
node scripts/export-pages.mjs --target "/path/to/Phoenixarjun"
```

This writes the game under `docs/packet-breaker/` and replaces only files inside that dedicated directory. It never changes `docs/runner.html`, `README.md`, unrelated games, or `.github/workflows`.

Alternatively, manually copy `index.html`, `style.css`, `dist/game.bundle.js`, and `assets/favicon.svg` into the same `docs/packet-breaker/` hierarchy.

## B. Confirm GitHub Pages settings

Check whether the public profile repo uses Pages from the default branch's `/docs` folder, or a separate Actions deployment artifact. Scheduled updates and Pages may behave differently on the development branch. Do not claim the game is live until a deployed build can be visited in a browser.

If Pages serves `docs/` at the repo's base path, the expected destination will be:

`https://phoenixarjun.github.io/Phoenixarjun/packet-breaker/`

**This is a prospective URL, not a verified deployment.** If the repository uses another Pages source or custom domain, obtain its actual URL instead.

## C. Change Section 08 *in the generator*

Review `scripts/build.py` and its `build_readme()` implementation. Replace the old System Runner link and copy with Packet Breaker, updating the header generator to use:

`naresh@github:~$ play --packet-breaker`

Add an accessible section heading (`Developer Playground`) and a concise descriptor (`Packet Breaker — keep the packet alive. Break the bottlenecks.`). The README's clickable image should be a locally stored screenshot or GIF.

Example Markdown-compatible HTML (only once the site is verified):

```html
<p align="center">
  <a href="https://phoenixarjun.github.io/Phoenixarjun/packet-breaker/">
    <img src="./assets/playground/packet-breaker-preview.gif"
         alt="Play Packet Breaker: a neon arcade brick-breaker with real ball physics and power-ups"
         width="100%" />
  </a>
</p>
```

Copy this ZIP's `assets/packet-breaker-gameplay.gif` to `assets/playground/packet-breaker-preview.gif`, or use the static preview PNG if its animation is too heavy. Keep the link on the enclosing `<a>` element because embedded README images cannot run click handlers or JavaScript.

When updating the command or section headline, modify the source generator too. Otherwise running the current profile build can restore the old System Runner content.

## D. Integration checklist

- All internal asset URLs remain relative to the game directory (`./dist/` and `./assets/`).
- The game opens locally from `index.html` and works as an ordinary static Pages app.
- No tokens, `.env`, private source files or unwanted project data are copied into the public game directory.
- README still contains exactly one Section 08 and one play link.
- The Play link points to an **accessible** public page, not a predicted or placeholder location.
- The old `docs/runner.html` and its existing users are not broken by this migration.
- Confirm keyboard, pointer, touch, pause, restart, game-over and sound controls on the deployed page.
- Visual style follows Titanium Hacker; if the global palette changes in future, update game CSS tokens accordingly.

## E. Public-repository implications

The deployed game uses public HTML, CSS and JavaScript, so visitors can view its implementation. This is expected for an open public profile and is separate from the GitHub README image assets.
