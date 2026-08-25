# Day 52 — Combining Distance and Heading Control

## Goal
Combine the Day 51 heading controller and the earlier distance controller
into a single behavior: rotate to face a target heading, then drive a
target distance.

## Problem identified before implementation
`distance_controller.py` and `heading_controller.py` both publish to
`/diff_drive_controller/cmd_vel`. Running them as two independent nodes
would mean both odometry callbacks fire on every odom message, each
publishing a `TwistStamped` that overwrites the other. Twist messages are
not additive — whichever node's callback runs last "wins" for that cycle,
with no guaranteed ordering. This would produce non-deterministic,
flickering behavior rather than coordinated motion.

## Architecture decision
Considered three options:
1. Sequential state machine (single node)
2. Two nodes + external coordinator managing handoff
3. Two nodes + mux/arbitration node

Rejected (3): a mux solves concurrent-command arbitration, which isn't
the actual problem here — heading and distance control are sequential
tasks, not concurrent behaviors competing for the same actuator.

Rejected (2): moves the coordination problem into inter-node signaling
(service/topic-based handoff) without a clear benefit at this stage, and
doesn't scale cleanly to repeated per-waypoint sequencing needed for
Days 56–57.

Chosen (1): single node, internal state machine (`ROTATING` → `MOVING` →
`DONE`). One publisher, one odom subscriber, state decides which control
logic runs each cycle. No possibility of command collision since only
one code path publishes per callback.

## Implementation notes
- New node: `goal_controller.py`
- Merges parameters from both prior controllers (`target_yaw`,
  `kp_angular`, `max_angular_speed`, `heading_tolerance`,
  `target_distance`, `kp_linear`, `max_speed`, `min_speed`)
- Key correction vs. naive merge: `start_x`/`start_y` for distance
  tracking are captured on **entry into `MOVING`**, not at node startup.
  This ensures distance is measured from the robot's post-rotation pose,
  not its pose at node initialization.
- `heading_controller.py` and `distance_controller.py` left untouched —
  new node is additive, not a replacement, in case either is needed
  standalone later.

## Status
Implementation complete, added to `setup.py` entry_points. Build
verified clean (`colcon build --packages-select migro_core_001`,
no errors).

## Test 1 — baseline (target_yaw=90.0 deg, target_distance=1.0 m)
Pre-flight checks confirmed before running the controller:
- `/diff_drive_controller/odom` publishing correctly (robot at rest,
  position ~(0,0,0))
- `/diff_drive_controller/cmd_vel` type confirmed as
  `geometry_msgs/msg/TwistStamped`, one subscriber (diff drive
  controller), zero publishers prior to running goal_controller
  (confirms no competing node was mid-publishing)

Ran:
```
ros2 run migro_core_001 goal_controller --ros-args \
  -p target_yaw:=90.0 -p target_distance:=1.0
```

Observed in Gazebo: robot rotated in place first (no translation
during this phase), then drove straight forward with no further
rotation, then stopped cleanly with no drift or twitch after
completion.

Logged transition points:
```
Heading reached. Yaw: 88.0 deg | Error: 2.0 deg. Switching to MOVING.
Distance reached! Distance: 1.00 m. Goal complete.
```

Heading transition occurred exactly at the 2.0 deg tolerance boundary
(as configured via `heading_tolerance` param) — confirms the ROTATING
→ MOVING transition condition (`abs(error_degrees) <= heading_tolerance`)
is firing correctly, not early or late. Distance transition landed
exactly at the 1.00 m target, confirming MOVING → DONE fires correctly
and `start_x`/`start_y` capture-on-entry logic measured distance from
the correct (post-rotation) starting pose.

No cmd_vel collision observed — single publisher throughout, consistent
with the single-node/single-publisher design.

## Outstanding (not yet tested)
- Only one test case run (single target_yaw, single target_distance).
  Have not yet tested: negative/large-angle headings, wraparound cases
  near ±180 deg, short-distance targets, or behavior if the robot
  starts already near the target heading (does ROTATING skip near-
  instantly without issue).
- Have not verified behavior under KeyboardInterrupt mid-state
  (does `stop_robot()` in `finally` correctly halt the robot from
  either ROTATING or MOVING state).

## Next session
- Run remaining test cases (large angle, wraparound, near-zero initial
  error) — same rigor as Day 51's four-test suite
- Then proceed to Day 56–57: waypoint navigation (loop this state
  machine over multiple target poses)
