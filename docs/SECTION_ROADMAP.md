# Section-by-section improvement roadmap

All sections have a functioning starter asset or Markdown structure. These are the detailed visual decisions to refine during review.

| Order | Section | Design criteria | Acceptance test |
| --- | --- | --- | --- |
| 1 | Hero | Readable identity, restrained industrial motif, focused links | At mobile GitHub width, name and specialty remain clear |
| 2 | Engineering focus | Three evidenced capabilities; no false seniority | Claims match actual work/projects |
| 3 | Flagships | 3 differentiated project cards, strong narrative, working links | Names, visuals and technical claims accurate |
| 4 | Currently building | Visually distinct from flagship section | Only public, active projects shown |
| 5 | Stack | Low-noise skill matrix, 4-6 meaningful domains | No irrelevant technology/badge padding |
| 6 | Technical writing | 3 select articles; direct links | URLs and titles validated |
| 7 | Contribution city | Upright 3D-like towers from true daily counts | Authenticated fetch, date placement, zero-day handling and color scaling tested |
| 8 | Playground | Functional external experience, concise GIF teaser | Works on desktop/mobile; not falsely presented as embedded GitHub game |
| 9 | Connect | Domain, socials and closing identity | All visible links point to correct public pages |

## Planned content releases

- Phase 1: current verified public work only.
- Phase 2: portfolio URL when public; verify link and change `show_portfolio`.
- Phase 3: public flagship selection can be replaced by editing `content/projects.json`.
- Future work should not appear prematurely in public content files, graphics, or commit messages.

## Decision principle

Visual novelty must support hiring signal, not replace it. A good README should let an engineer identify your specialization and inspect meaningful evidence within the first two screenfuls.
