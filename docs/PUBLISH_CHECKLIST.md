# Release checklist

- [ ] All generated claims have been reviewed; official role and professional identity distinguished.
- [ ] Check employer confidentiality — no customer data, proprietary diagrams, internal counts or unapproved metrics.
- [ ] Confirm exact public project repos, names, and links.
- [ ] Confirm LinkedIn URL and Medium URLs.
- [ ] The initial full README is readable and loads in GitHub light and dark themes.
- [ ] Verify SVG layout at 320px viewport as well as desktop.
- [ ] Run `python scripts/build.py` and `python scripts/validate.py`.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Contribution city data is **real** or the clearly labeled sample preview is intentionally acceptable for review only.
- [ ] Playground is not enabled without functional game.
- [ ] Review the Git diff: `README.md`, current workflows, any private files are unchanged until approval.
- [ ] Manually copy `README.v2.md` to `README.md` on the review branch when ready.
- [ ] Check image links in the branch GitHub renderer; merge only after approval.
- [ ] If enabling automation, review its permissions and generated file changes first.
