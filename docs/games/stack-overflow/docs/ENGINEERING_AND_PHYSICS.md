# Stack Overflow — Physics, progression and rendering notes

## Design intention

A satisfying, repeatable precision game with a clear input → consequence loop. Unlike the packet-breaker and pinball games, this experience is about timing, momentum, structural constraints, and managing loss of platform width. These are real game rules, not a static animation. The visual representation is an isometric-looking 2.5D Canvas surface; the physics is a deliberately constrained vertical-plane simulation.

## Physical units and integration

The world uses pixel-equivalent units: canvas width 1040, height 680; one block layer is 34 high. Physics updates at a fixed `dt=1/120 s`, not variable display frame durations. Falling acceleration is `G=1450 units/s²`; horizontal acceleration due to wind is a stage-dependent signed value, typically between ±0 and ±112 units/s².

During released fall, semi-implicit position integration is equivalent to constant-acceleration kinematics over one fixed step:

```
vy_new = vy_old + g * dt
x_new = x_old + vx_old * dt + 0.5 * wind * dt²
y_new = y_old + 0.5 * (vy_old + vy_new) * dt
vx_new = vx_old + wind * dt
```

When the new bottom reaches the supporting top, the solver interpolates contact time within the timestep and reconstructs horizontal position at that time, avoiding overshoot/penetration in the 120Hz integrator. `impactTime` also exposes a closed-form prediction for the visual ghost target:

```
t_contact = (-vy + sqrt(vy² + 2*g*distance)) / g
x_predict = x + vx * t_contact + 0.5 * wind * t_contact²
```

This model does **not** approximate rotational tumbling or elastic collisions. Those would add computational complexity without clear gameplay value for a precision stacker.

## Landing and trimming

Represent two rectangles by horizontal `(center x, width w)` intervals:

```
left  = max(xA - wA/2, xB - wB/2)
right = min(xA + wA/2, xB + wB/2)
overlap = max(0, right - left)
```

A landing fails if `overlap < 24` or `overlap < 0.18 * incomingWidth`. Otherwise, the supported server's new width becomes exactly the overlap; its center becomes the overlap midpoint. This models overhang trimming without inventing platform capacity. Perfect placement within 7 units snaps to the center and repairs at most 2 units up to the configured maximum platform width. This makes perfect execution rewarding without eliminating mistakes.

## Stability and tower collapse

For every support interface `i`, compute center of mass of all stacked blocks above it; mass is proportional to block width (all layers have equal height and density):

```
centerMass(i) = sum(width[j] * x[j]) / sum(width[j]) for j > i
```

If this center falls outside the footprint of the supporting block, stability for that joint becomes 0 and the tower fails. This produces a causal structural reason for failure in addition to missing the block outright, but remains intentionally simple: there are no rotational inertia terms or deformable constraints.

## Difficulty schedule

| Sector | Begins at incoming layer | Scan speed | Wind amplitude |
| --- | ---: | ---: | ---: |
| Bootstrap | 1 | 230 | 0 |
| Load Balance | 5 | 275 | 35 |
| Distributed Core | 10 | 330 | 63 |
| High Availability | 16 | 388 | 85 |
| Hyperscale | 23 | 445 | 112 |

An additional capped speed bonus of 2.7 units/second per level increases challenge gradually. Wind direction and magnitude are derived from a seeded PRNG so simulations remain testable. After reaching Hyperscale, players continue in endless mode rather than hitting a fixed victory screen.

## Timing and difficulty

The moving block travels from one side of the arena to the other and reflects at screen bounds. Releasing the block preserves 13% of its horizontal velocity; a small amount of release momentum means a player must aim for the *projected landing*, not simply the block's current position. Holding Focus reduces scan velocity to 34% while consuming a finite buffer.

A browser high score is saved locally, not uploaded. There are no accounts, tracking pixels, external requests, or backend services.

## Rendering

Draw scene in Canvas at 2× logical resolution, scaled to browser width. The renderer provides engineered server fronts, top bevels, oblique side facets, rack indicators, parallax grid, projected guide, HUD overlays, exhaust particles, and a camera that follows the rising tower. The physics positions remain in logical world space; camera transform is applied only during drawing.

## Validation performed

`tests/physics.test.mjs` covers collision geometry, predicted trajectory, trimming, perfect placement, insufficient overlap, stability, seeded repeatability, wall scan bounds, high-speed contact, game-over, focus, pause-in-flight, sector boundaries, 25 successful placements, unattended simulation, and 10,000 randomized overlaps.

`tests/browser_smoke.py` covers actual page interactions, pause/resume, Shift/focus, dropping and scoring, ten-layer stack, sector change, loss, restart, help, touch input and mobile overflow. It uses Chromium to render the actual HTML/Canvas UI. These tests do not replace human balancing or testing across every phone browser.
