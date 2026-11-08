# Firewall Defense — Game System, Mathematics and Balancing

## 1. Simulation

The engine is an ES module without browser dependencies. Its state evolves through `update(dt)` only when the phase is `wave`.

The browser uses a fixed timestep `h = 1/120 s` with a RAF accumulator. This decouples simulation and rendering rates, reduces collision variability, and enables deterministic tests. The 2× mode executes twice as many fixed steps per wall-clock time; it does not double the distance moved in a physics step.

When the tab is backgrounded during a wave, the UI pauses the game. The frame accumulator is clamped after slow frames to avoid an expensive catch-up burst.

## 2. Network geometry

Two immutable network paths are stored as ordered world-coordinate points. Every enemy stores `routeIndex` and scalar `distance` along its route.

For polyline segment `i`, length is:

```
L_i = sqrt((x_i-x_(i-1))² + (y_i-y_(i-1))²)
```

Given traveled distance `d`, subtract complete segment lengths until one remains, then linearly interpolate within that segment. The enemy's path position is not inferred from frame-to-frame image pixels.

There are 22 predefined build nodes, all outside both routes. A tower cannot obstruct the path, ensuring each attack is always navigable and the tower-defense strategy concerns placement and coverage, not accidental path-locking.

## 3. Projectile physics and collisions

Projectile trajectories home toward the target's current position. For each step, the bullet moves from `A` to `B`. The nearest point to circle center `C` on the segment is:

```
v = B - A
u = clamp(dot(C-A, v) / dot(v, v), 0, 1)
Q = A + u*v
hit = length(Q-C) <= (enemy radius + projectile tolerance)
```

A zero-length segment is handled explicitly. This *swept collision* is important at high projectile speeds; point-only collision tests can miss thin targets. The test suite compares the function to an independent closest-point implementation for 15,000 randomized scenarios, including tangencies.

This is intentional arcade interception physics; it does not simulate real network traffic, ballistics, or full rigid-body dynamics.

## 4. Target acquisition

A tower considers every alive enemy within its configured range, then prioritizes the largest `distance / routeLength` (the packet closest to reaching the core). For stealth packets, non-IDS targeting range is reduced to 43% of normal; IDS retains full range.

Towers:

- Firewall — homing single-target projectile, armor piercing.
- Rate Limiter — homing low-damage projectile, applies a 0.56 movement multiplier for 1.7 simulated seconds.
- Pulse Node — direct area damage to all packets within the pulse radius.
- IDS Scanner — instantaneous short beam chain, recognizes stealth and jumps to nearby unvisited enemies.

Upgrade levels boost damage, frequency or chain count, and effective range. Rank maximum is 3.

## 5. Enemies and credits

Enemies have health, speed, armor, shield (where applicable), and a core-leak penalty. Shield absorbs damage before health; armor reduces remaining damage but never below one point. Enemy health and speed scale as wave progression increases.

Start: 290 bandwidth credits and 20 core integrity. Costs: Firewall 95, Rate Limiter 110, Pulse Node 145, IDS 160. Eliminations grant enemy-specific credits; every eighth consecutive elimination grants +20; each cleared wave awards `65 + waveIndex*22` credits (0-indexed wave).

There are eight finite waves. The final wave includes a Titan with enhanced HP and shield. A loss is triggered at zero integrity. A win occurs only after wave 08 spawns completely and its surviving attackers are eliminated.

## 6. Balance evidence and limitations

A deterministic mixed-tower build script has been tested to clear all eight waves. A minimal single-tower build consistently loses. This demonstrates that the game has both feasible wins and possible losses; it is *not* proof of perfect or universal difficulty balancing.

Unresolved subjective tuning: best upgrade timing, balance between pulse and IDS at wave 7/8, relative weakness of a low-tier Rate Limiter, and perceived pacing on phones. Human playtesting can refine these without changing deterministic collision and accounting invariants.

## 7. Data and security

No APIs, tokens, calls to GitHub, analytics, or user accounts. High score uses localStorage (wrapped in try/catch for unavailable storage). No user-submitted HTML is rendered directly into the DOM; gameplay strings originate from static code.

The browser-only test harness is exposed only if URL contains `?test=1` or a test-only window flag is explicitly set before the main module loads. Do not rely on it for the production arcade.
