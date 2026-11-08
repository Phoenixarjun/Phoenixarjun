# Engineering notes: Packet Breaker physics and gameplay

## 1. Simulation model

The gameplay simulation uses a **fixed timestep** `dt = 1 / 120` seconds, independent of the display's requestAnimationFrame rate. The accumulator clamps individual display-frame gaps to 50 ms and processes a maximum of nine physics steps per frame to avoid the spiral of death after inactivity. Canvas rendering occurs once per browser animation frame.

World coordinates remain `W = 1000, H = 680`. CSS scales the canvas while pointer coordinates are converted back to logical game coordinates using `getBoundingClientRect()`. Pixel density may rise to 2× for crisp output, but the physics geometry is unchanged.

## 2. Continuous collision detection

For a moving ball of radius r at initial centre P, moving by displacement V over the current substep, determine the earliest first-contact time `t ∈ [0,1]` against walls, the paddle, and each live brick.

For a rectangle, test four **face regions** with their r-offset planes, plus four **corner circles**. Corner intersections solve:

`|P + tV − C|² = r²`

where C is a rectangle corner. For the quadratic `a t² + b t + c = 0`, use the smallest admissible root:

`a = V·V`

`b = 2 (P−C)·V`

`c = |P−C|² − r²`

`t = (-b − sqrt(b²−4ac)) / (2a)`

A corner hit must lie outside both adjacent rectangle faces (its quarter circle), and the incoming velocity must be directed *into* the surface: `V·N < 0`. This avoids false hits at empty square corner regions that occur with naive inflated AABB checks.

On contact, move precisely to first contact, then reflect the velocity `V' = V − 2(V·N)N`. Nudge the position outward by a small epsilon to avoid repeated zero-time hits. Decrease the time remaining in that substep and process possible additional contacts. When the paddle is hit from above, compute a fresh outgoing angle instead of a specular reflection.

The game has a bounded speed and minimum vertical movement to prevent infinite near-horizontal trajectories. Collision iteration is capped per simulation substep; speeds are low enough relative to brick dimensions for the cap to be safe in normal play.

## 3. Paddle control

A hit near the middle sends the ball mostly upward. Hits near the edge steer it outward. The signed hit offset is:

`u = clamp((ball.x − paddle.x) / (paddle.width/2), −1, 1)`

The outgoing angle is approximately:

`θ = clamp(1.08u + clamp(paddleVelocity/1250,−.12,.12), −1.08, 1.08)`

Velocity then becomes `(speed sin θ, −speed cos θ)` with a minimum horizontal speed to avoid stationary columns. **The paddle has finite maximum movement speed** rather than instantly teleporting, making timing and anticipation meaningful.

## 4. Ball dynamics

Starting speeds increase by stage, from 425 to 550 logical pixels/s. The practical cap grows gently with stage; paddle rebounds add about 0.8% momentum up to the cap. The minimum vertical ratio reduces horizontal-lock exploits.

The ball's trail is rendered independently of physics. Particle effects never affect collisions. Brick explosions destroy nearby blocks using radial proximity, whereas other bricks lose HP per hit. Explosion damage affects the score but doesn't spawn recursively explosive chains.

## 5. Controls and accessibility

- Mouse/touch moves a paddle target, clamped inside the arena.
- Keyboard arrow keys or A/D move the target at a fixed rate.
- Space or click/tap launches a waiting packet.
- P/Escape pause/resume, and browser blur automatically pauses a run.
- Reduced motion limits decorative particle volume and disables CSS transitions/animations.
- Sound uses user-gesture-triggered Web Audio oscillators and can be switched off at any time.

## 6. Reproducibility and trust

Level layouts have deterministic pseudo-random generation seeded by stage, while drops and visual particles are randomized in play. The physics math is in `src/physics.mjs` and tested by `tests/physics.test.mjs`, including 10,000 randomized sweeps.

There are no accounts, network calls, external dependencies, ads, or telemetry. The only persisted state is an optional best score in browser local storage.
