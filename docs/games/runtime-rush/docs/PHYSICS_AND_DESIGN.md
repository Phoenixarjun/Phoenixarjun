# Runtime Rush: physics, rendering, level generation

## Simulation axes and units

The camera sits behind the vehicle, facing down the tunnel's **world +Z** axis. Visual left-to-right movement follows screen space: `LANE_X=[+3.05,0,-3.05]` because the conventional right-handed camera facing world +Z reverses world X on screen. All world distances use arbitrary metres and seconds consistently; no claim of physically measured full-scale vehicle speeds.

The simulation uses a fixed `1/120 second` timestep, with frame time clamped at 50ms and an update budget to avoid runaway catch-up after tab switching. At each tick:

- Speed `v(d) = clamp(22+d/140, 22,46)` metres/second, reduced temporarily by 28% for overclock pickup.
- Distance `d_{n+1}=d_n + v*Δt`.
- Lane position approaches target exponentially: `x_{n+1}=x_target+(x_n-x_target)*exp(-13.5*Δt)`.
- Vertical motion uses `v_y <- v_y - 21.8*Δt`; `y <- y+v_y*Δt`, with a ground constraint at `PLAYER_RADIUS=0.68`.
- Initial jump velocity is `9.7 m/s`, gravity is `21.8 m/s²`, giving a peak jump of `v²/(2g)≈2.158m` and flight duration `2v/g≈0.89s`. This is a stylized arcade jump, not a realistic physical network packet.
- Slide duration is `.72s`. A sliding ball has a smaller effective vertical collision radius for overhead gates.

## Collision checks

Instead of relying on a single frame's Z position, a hazard at progress `s` triggers when the interval `[oldDistance,newDistance]` crosses its collision plane `s-halfDepth`. Interpolation at crossing time determines the vehicle's X and Y. This **swept plane** model prevents missed obstacles under ordinary high speed/time stepping, though it is not a full swept sphere versus arbitrary moving mesh solver. Lateral and vertical checks are performed at crossing. A 1.8-second post-impact grace period prevents repeated damage from immediately adjacent hazards.

Distinct hazards:
- Core block height ~1.67: change lane or high jump.
- Low barrier height ~0.87: jump.
- Overhead beam extends below standing top radius (1.36), but above sliding top radius (1.13): slide.

## Procedural safety

Every pattern chooses one of 3 lanes as a reserved open lane and adds at most two blocking hazard objects on other lanes. Future pattern rows are spaced by 30–39m. At maximum speed 46m/s, the minimum interval is approximately 0.65s; the lane change filter can shift from far-left to far-right (two inputs) in that interval with appropriately early decisions. The level is **feasible**, though reckless or late input can still lose.

Obstacles are seeded with `mulberry32` for deterministic simulation. Collectibles may appear in the open lane. Five named sectors are triggered at 0,450,900,1350,1800m; sector 5 continues indefinitely after that point.

## Scoring and state

- Base distance points: 1.4 point/metre, accumulated fractionally to prevent loss from per-tick rounding.
- Safe obstacle avoidance: 20 points, plus near-miss bonus 45.
- Energy pickup: 150 plus combo multipliers.
- Shields: absorb one damage event (with temporary i-frames).
- Time-dilation capsules: lower speed for seven seconds.
- Sector milestone bonuses: 300×sector.
- High score: localStorage, without online telemetry.
- A failed collision reduces integrity from 3 to 0 and enters game-over state.

## Rendering design

**Primary:** Native WebGL, perspective projection, a custom GLSL lighting/fog shader and procedural cube, sphere, and torus meshes. Tunneled walls and gantries are extruded 3D geometry. Each frame streams only model matrices/colors and reuses cached mesh buffers. Backface geometry is wound outward. Camera uses a right-handed look-at matrix. There is no Three.js dependency.

**Fallback:** Canvas2D software perspective projection, sorted faceted surfaces, fog, emissive outlines and shaded player sphere; plays the exact same deterministic simulation. The fallback is not a claim of full native GPU 3D. It exists for environments where `getContext('webgl')` and `getContext('webgl2')` fail.

Titanium Hacker tokens: base `#0C0F10`, deep `#070B0C`, steel `#42535C`, surface `#1B2328`, accent `#B6FF3B`, text `#EEF7EF`; red and amber are only for hazards. No external fonts, services, image downloads or CDNs.

## Accessibility and known limitations

The actual gameplay is visual and timing-dependent; screen-reader-only play is not supported. All main buttons have labels or visible controls, and reduced-motion CSS is supplied. Mobile tap/swipe controls are included. The automated browser environment has WebGL disabled: the software fallback was tested, while the GPU renderer requires an additional smoke test in a GPU-enabled local browser. No rigid-body dynamic obstacles, track branching, networked multiplayer, or online leaderboard are claimed. Difficulty and high-performance graphics on older mobile devices require human playtesting.
