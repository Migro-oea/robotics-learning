# Day 51 — Heading Controller Tuning

**Objective:** Study the effect of proportional gain, max angular velocity, and heading tolerance on the heading controller's convergence behavior, overshoot, and saturation dynamics — verified through controlled Gazebo tests.

## Parameters at test time
- `kp_angular = 1.0` (default)
- `max_angular_speed = 0.5` rad/s
- `heading_tolerance = 2.0°`

## Test 1 — Small-angle baseline (Kp=1.0, target 25°)
Converged in ~3.0s. Fully monotonic approach, no saturation (error × Kp stayed under `max_angular_speed` the entire run), no oscillation. Settled at 23.0° (2.0° error, at tolerance boundary).

## Test 2 — Large-angle saturation test (Kp=1.0, target 170°)
Converged in ~7.9s. Angular speed held at the 0.5 rad/s cap from error=147° down to error≈27.8°, matching the predicted saturation-exit threshold of `max_angular_speed / kp_angular ≈ 28.6°`. Decelerated smoothly afterward, no overshoot. Settled at 168.0° (2.0° error).

## Test 3 — Gain variation (Kp=2.0, target ~20° turn crossing back)
Converged in ~6.2s. Saturation-exit threshold shifted to ≈13.7°, matching the predicted `0.5/2.0 = 14.3°`. Even with doubled gain and a shorter deceleration window, no overshoot occurred — settled cleanly at 21.9° (1.9° error).

**Key finding:** No overshoot was observed at either gain tested, despite Test 3 deliberately compressing the deceleration window. This suggests the simulated differential-drive system has enough inherent damping (physical inertia, `gz_ros2_control` velocity smoothing) that pure proportional gain in the 1.0–2.0 range doesn't destabilize heading control. The instability boundary (if one exists in a reasonable gain range) wasn't found in this session — worth revisiting if a future controller (e.g. combined distance+heading) behaves unexpectedly.

## Test 4 — Wraparound verification (170° → -170° target)
`normalize_angle()` uses `atan2(sin(angle), cos(angle))`, which correctly maps any angle into `(-π, π]`. Live test confirmed this: commanding a turn from 168° to -170° produced a smooth ~20° short-path rotation, not a ~340° long-path rotation. Error stayed continuous and small (~10° → ~2°) directly through the +180°/-180° yaw crossing, with no discontinuity or spike. Settled at -172.0° (2.0° error).

## Saturation-exit threshold relationship (derived and confirmed)

        saturation_exit_threshold = max_angular_speed / kp_angular
        
Verified at two gain values (1.0 → 28.6°, 2.0 → 14.3°), both matching observed log data within rounding.

## Concepts reinforced
- Proportional controller saturation and its effect on convergence time vs. stability
- The `atan2(sin, cos)` pattern for angle normalization, and why it's more robust than modulo-based wrapping
- The importance of verifying control logic under real boundary conditions (wraparound), not just static code review

## Outcome
Heading controller behavior is now quantitatively understood across gain and angle-magnitude variations, and wraparound handling is verified correct in simulation. Closing Day 51.
