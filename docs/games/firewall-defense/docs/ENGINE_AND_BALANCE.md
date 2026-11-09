# Firewall Defense 2.0 — Simulation, Weapons and Balance

## What changed

The existing `src/engine.mjs` remains the authoritative deterministic simulation. The existing Canvas renderer, HUD, board coordinates, two routes, 22 pads, high-score key and original four towers remain. Version 2 extends them rather than replacing the game.

- **30 authored waves** arranged into six acts of five waves; boss events at waves 5, 10, 15, 20, 25 and 30.
- **Six weapon types:** Firewall, Rate Limiter, Pulse Node, IDS Scanner, Scatter Cannon and Rail Lance.
- **Five upgrade levels** per tower (up from three).
- **Three paid tactical protocols:** EMP, Overclock and Core Shield. Each has a simulation-time cooldown.
- New threat behaviors: Swarm, Splitter, Jammer, Regenerator, Sentinel and Overseer.
- Optional endless waves unlocked by clearing the 30-wave campaign.

## Simulation invariants

The game still uses a fixed simulation step `h=1/120s`. Rendering occurs independently. The frame loop caps catch-up steps and automatically pauses when the tab loses visibility. The `speed` setting multiplies the number of simulation steps executed per wall second, not the physics speed in an individual step.

Enemies advance by arc-length along one of two fixed polylines. Each placement pad is off the route. Target acquisition prioritizes normalized route progress within the tower's engagement radius; stealth can only be engaged at full distance by IDS.

Projectiles use a segment-to-circle test to prevent tunneling at high speeds: 

```
u = clamp(dot(C - A, B - A) / ||B - A||², 0, 1)
Q = A + u * (B - A)
hit = ||Q - C|| <= targetRadius + tolerance
```

For a zero-length segment, `u=0`. The tests include 15,000 randomized independent comparisons.

## Shot and weapon mathematics

### Existing weapons

- **Firewall:** one homing shot; armor piercing (`pierce=4`); direct hit.
- **Rate Limiter:** one lower-damage homing shot, then `speed × 0.56` for 1.7 simulation seconds.
- **Pulse Node:** radial instantaneous hit inside a level-dependent circle; all nearby alive enemies can be damaged.
- **IDS Scanner:** chain beams through unique nearby targets; sees stealth at full range.

### Added weapons

- **Scatter Cannon:** launches three separate homing shots per volley. Where multiple targets exist, they are distributed across distinct nearby enemies. Otherwise the three shots converge on the same target from slightly separated muzzle origins. Each projectile has independent collision and damage accounting.
- **Rail Lance:** computes a vector from the tower to its leading target and extends a finite beam for its full effective range. An enemy is hit only if the beam segment intersects its radius (plus tolerance). Up to `3 + floor(level/2)` aligned targets receive decreasing damage (`base × levelBoost × 0.81^penetrationIndex`). This is not an unlimited map-wide beam.

### Upgrades

`upgradeCost = round(baseCost × (0.7 + 0.43 × (currentLevel - 1)^1.25))`

For projectile weapons, `damage = baseDamage × (1 + 0.34 × (level - 1))` and firing cooldown is divided by `1 + 0.10 × (level - 1)`. Level 5 is the cap. Other weapons preserve their per-type mechanics (pulse radius, IDS chain count, piercing beam capacity).

## Abilities and cooldowns

| Protocol | Cost | Cooldown | Effect |
| --- | ---: | ---: | --- |
| EMP Freeze | 120 CR | 52s | Stops currently active enemies for 2.7 simulation seconds |
| Overclock | 155 CR | 62s | Future tower shots reload 1.8× faster for 7 simulation seconds |
| Core Shield | 135 CR | 58s | Adds 7 points of absorptive shielding, to a cap of 14 |

Abilities can activate **only while a wave is active** and after validating both affordability and cooldown. Cooldowns progress in simulation time, so pause does not consume them. EMP requires at least one current enemy. Core Shield consumes a charge for each point of would-be core damage before any reduction in integrity. Shield never raises the base 20 integrity value.

## Wave and enemy scaling

Thirty wave profiles are explicitly authored in `WAVES`; the last element includes the **Overseer**. A wave appends its boss only if its `boss` field is set. Extra Splitter children are counted as active enemies and must also be cleared to complete a wave.

```
healthMultiplier(i) = 1 + 0.10 i + 0.0032 i²
speedMultiplier(i) = 1 + min(0.42, 0.016 i)
spawnInterval(i, r) = max(0.19, 0.76 exp(-0.042 i)) + 0.11 r
```

Here `i` is the zero-based wave index and `r` is a seeded uniform random value `[0,1)`. There is no negative or zero spawn interval. Boss units additionally have larger base health/shield, armor and leak penalties. A Jammer temporarily disables adjacent towers; Regenerators restore some health without exceeding their maximum; Splitters create two Swarm units after death.

At wave completion, the bonus is `70 + 19i` credits, plus the normal rewards from destroyed enemies. The game still starts with 290 CR and 20 core integrity. Selling returns 65% of invested credits.

Endless mode uses the same simulation rules with deterministic generated wave profiles; enemy counts are capped at 85 plus a boss. It is optional after completing the campaign.

## Verification

- 27 deterministic Node tests, including weapons, ability affordability/cooldowns, 30-wave winnability, enemy effects, endless transition, defeat, and randomized geometry.
- Chromium desktop and mobile smoke tests for original gameplay and new superpower buttons; no page-wide mobile overflow observed.
- A demonstrably funded mixed-arms build can complete 30 waves; a minimal single-tower strategy loses. These checks establish playability boundaries, **not** perfect difficulty balance.

**Design limits:** The engine models arcade network defense, not real packets or real-world physics. An interactive player should still playtest wave pacing, large enemy waves, mobile ergonomics and the subjective power of Scatter Cannon/Rail Lance before deployment.
