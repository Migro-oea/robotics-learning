# Day 49 – Heading Controller Design

**Date:** 22 August 2026

*Extending closed-loop control from one axis to two — and learning why rotation is harder than it looks.*

## Objective

Extend MIGRO's closed-loop control from linear motion to angular motion — apply the same proportional-control pattern already proven in `distance_controller` to heading/rotation.

## What I Worked On

Designed and implemented `heading_controller.py` inside `migro_core_001`, mirroring the architecture of the existing distance controller for consistency: subscribe to odometry, compute error, publish a velocity command. The real work here wasn't the proportional math — it was handling angle wraparound correctly, which linear control never has to deal with.

## Technical Implementation

- **Quaternion-to-yaw conversion:** MIGRO only rotates about the z-axis, so the full quaternion-to-Euler formula reduces to `yaw = atan2(2·qw·qz, 1 − 2·qz²)`. Used this simplified planar form instead of a general TF2 transform, keeping the node lightweight and the math explicit.
- **Angle normalization:** Wrote `normalize_angle()` using `atan2(sin(θ), cos(θ))` to keep heading error within [−180°, 180°]. Without this, naive subtraction (`target − current`) can produce a 350° error when the real shortest turn is −10°, causing the robot to spin the long way around.
- **Proportional control:** `angular_speed = Kp × error`, clamped to `max_angular_speed`, stopping once error is within `heading_tolerance` — the same `error → scaled command → clamp → tolerance` structure as the distance controller, applied to the angular axis.
- **Parameters exposed:** `target_yaw` (90°), `kp_angular` (1.0), `max_angular_speed` (0.5 rad/s), `heading_tolerance` (2.0°) — all runtime-tunable ROS 2 parameters.

## Testing & Debugging

Design and implementation only on this day — integration and verification followed on Day 50.

## What I Learned

Proportional control generalizes cleanly from linear to angular motion — the feedback structure doesn't change. What changes is the domain: angles wrap around, distances don't. Getting the normalization right up front avoided a class of bug (spinning the long way to a target) that wouldn't show up until tested with a heading close to the wraparound boundary.

## Result / Outcome

`heading_controller.py` written and functionally complete, but not yet integrated — not registered in `setup.py`, not built, not tested in Gazebo.

## Next Step

Register the node as an executable, rebuild the package, and verify heading control in Gazebo — closing the loop from design to working system.

---

*Note: this entry was written on Day 50 while integrating the controller. The code was implemented on 22 August but not documented at the time — logging it now to keep the engineering record accurate.*
