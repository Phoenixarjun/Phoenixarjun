# Circuit Pinball — Physics and Design Notes

## Coordinate system and fixed-step integration

The game uses a 760×1080 logical coordinate system, with +x to the right and +y downward. Canvas device-pixel scaling does **not** affect collision math. `requestAnimationFrame` supplies wall-clock elapsed time, but the simulation advances in fixed 1/120-second steps. An accumulator runs up to 7 steps per rendered frame and drops the remainder if the tab returns after a long pause; this prioritizes predictable motion and avoids runaway CPU.

For each active ball and substep `h`, the semi-implicit update is:

```
vy <- vy + g*h                   // g = +760 px/s²
v  <- v*exp(-0.021*h)           // tiny linear drag
p  <- p + v*h
```

A per-ball substep count is chosen from movement speed: `max(1, ceil(|v|*dt/4.6))`, capped at 9. A speed cap of 1860 px/s guards against pathological impulses. This is an intentional *arcade approximation*, not full rigid-body motion with angular momentum.

## Collision geometry

For a finite segment `A→B` and point `P`, the nearest point is:

```
t = clamp(dot(P-A, B-A) / dot(B-A, B-A), 0, 1)
Q = A + t(B-A)
```

A ball of radius `r` intersects the segment when `|P-Q| < r`. The normal is `(P-Q) / |P-Q|` except in a degenerate zero-distance case, where a safe normal is constructed from the segment. Contact correction moves the ball outside the segment.

For a stationary wall, with normal `n` and restitution `e`, let `vn = dot(v,n)`. If `vn < 0`, apply the normal impulse:

```
v <- v - (1+e)*vn*n
```

The moving-surface case first computes relative velocity `vrel = v - vsurface`. The same impulse uses `dot(vrel,n)`. This enables flippers to add real mechanical energy when rotating upward rather than being ordinary static bounce pads.

**Static continuous collision helpers:** `sweepCircleCircle` solves the quadratic `|(p+vt)-c|²=(r+R)²`, selecting the earliest nonnegative impact time; `sweepCircleSegment` checks the two parallel capsule sides and both endpoint caps. They are directly tested, while the interactive engine uses tight displacement substeps and contact correction for static objects.

## Flipper geometry

Flippers are two capsules with moving centerlines. Let `O` be the pivot, `L` the bat length, and `θ` its angle:

```
Tip = O + L*(cos θ, sin θ)
```

The contact-point surface velocity for angular speed `ω` at point `C` is:

```
vsurface = ω × (C - O) = (-ω*(Cy-Oy), ω*(Cx-Ox))
```

The left flipper rotates from `.34 rad` down to `-.57 rad` raised; the right is its mirror from `π-.34` to `π+.57`. The bat angles move at a controlled maximum of 16 rad/s while raised and 11 rad/s while returning. Each contact check samples five positions along the bat's angular sweep so fast flipper motion does not miss small balls.

**Playability correction:** the two resting flippers have a real center opening. An early prototype used overly long overlapping bats, causing passive no-input survival. The final shorter bats, weaker passive restitution, and inward gravity-fed behavior permit natural drainage while active raises provide strong upward strikes. A 42-second no-input simulated session reached game-over with three actual drains (duration can vary because collisions include minor randomized interactions).

## Gameplay and scoring

- Reactor bumpers: 175 base points, with multiplicative score modifiers and bounded combo scaling. Bumpers can temporarily energize the ball, as in arcade pinball.
- Firewall target plates: 350 base points. Bank completion: 2200 base points and a multiplier increase.
- Spinner: 100 base points and short sound/particle feedback.
- Two completed banks: triggers two additional balls when an active ball exists, subject to a 5-ball simultaneous limit.
- Extra balls: begin at 50,000 score, then higher thresholds; banked lives are capped at 5.
- Ball saver: 9 seconds after launch, one rescue for the current ball only. Once consumed, rescuing/relaunching does not rearm the saver until the next genuinely lost life.
- Tilt: heat increases with nudge and cools gradually; sufficiently rapid nudges lock flippers for 3.6 seconds.
- Target-bank respawn: disabled targets remain down 1.45 seconds before the next bank appears. This also prevents immediate double scoring as a ball remains in the target's physical space.

## What is and is not simulated

The geometry, gravity, collisions, flipper angular motion, and scoring are calculated and interactive. Lighting, reflections, PCB lines, 3D-looking surfaces, and sound effects are presentation effects. They do not claim physical accuracy of full 3D rolling, rotational spin, surface friction, cabinet mechanics, or ball-to-ball rigid-body collision. Multiball packets have independent trajectories; they do not physically collide with each other in this version.

## Verification and limitations

The test suite checks wall normals, degenerate segments, endpoint caps, moving contact restitution, TOI boundaries, angular flipper direction, ball speed limits, and 20,000 randomized collision cases. Browser tests exercise actual controls and game state. Human playtesting remains required for difficulty and satisfaction, especially for multiball and unusually long sessions.
