# Day 53 — goal_controller.py Edge Case Testing

## Objective
Close out the three outstanding edge cases identified for `goal_controller.py`:
large-angle/wraparound, near-zero initial error, and KeyboardInterrupt mid-state.

## Wraparound — Verified ✅
Deliberately forced a wraparound by setting `target_yaw:=-175.0` while the robot's
actual yaw (carried over from a prior test) was ~177°. Raw difference was -352°,
outside the valid (-180°, 180°] range.

`normalize_angle()` correctly collapsed this to +8° error, and the robot took the
short path (a small positive nudge) instead of spinning ~352° the long way.
Confirms `normalize_angle()` — validated in isolation on Day 51 — behaves correctly
when called live inside `do_rotating()`'s control loop.

## KeyboardInterrupt Mid-State — Bug Found, Fixed, Verified ✅
Initial testing showed the robot continuing to move indefinitely after Ctrl+C,
regardless of which state (ROTATING or MOVING) it was interrupted in. Root cause
turned out to be two distinct, stacked bugs:

**Bug 1 — Context torn down before shutdown logic runs.**
`rclpy.init()` installs its own SIGINT handler by default, which tears down the
rclpy context asynchronously as soon as Ctrl+C is pressed — racing against my own
`try/except KeyboardInterrupt/finally` block. By the time `finally` ran,
`stop_robot()`'s publish call was failing silently against an already-invalid
context (confirmed via explicit exception logging: `Failed to publish: publisher's
context is invalid`).

**Fix:** disabled rclpy's built-in signal handler so only my own exception handling
controls shutdown:
```python
rclpy.init(args=args, signal_handler_options=rclpy.signals.SignalHandlerOptions.NO)
```

**Bug 2 — Grace-period loop re-triggering the state machine.**
After fixing Bug 1, `stop_robot()` succeeded, but the robot still kept moving.
The `spin_once()` grace-period loop I'd added (meant to give the zero-velocity
publish time to actually leave the DDS buffer before `destroy_node()`) was itself
processing incoming odometry messages, re-triggering `odom_callback()` →
`do_rotating()`/`do_moving()`, which republished a nonzero velocity command right
after the stop — undoing the fix within the same shutdown sequence.

**Fix:** destroy the odometry subscription before entering the grace-period loop,
so `spin_once()` can only flush the outgoing stop command with nothing left to
regenerate motion:
```python
node.destroy_subscription(node.odom_sub)
```

**Verification:** re-tested interrupting mid-ROTATING at high angular speed
(~0.5 rad/s) — robot stopped immediately in Gazebo, no further motion. Debug
logging confirmed clean execution order: `stop_robot() completed` → no further
state-machine callbacks → `spin_once loop complete` → `shutdown complete`.

## Near-Zero Initial Error — Still Open ⚠️
Only observed incidentally (heading started at 2.0° error and transitioned to
MOVING immediately) — not a deliberate test. Carrying forward as outstanding.

## Key Learning
Publishing in ROS 2 is fire-and-queue, not fire-and-confirmed — `publish()` hands
a message to DDS asynchronously and returns before transmission completes.
Anything requiring guaranteed delivery before shutdown needs the executor kept
alive briefly afterward, but that grace period itself can have side effects
(reprocessing other pending callbacks) that need to be explicitly guarded against,
not just the publish itself.

## Commit
`Fix KeyboardInterrupt leaving robot with stale cmd_vel`

## Next Steps
- Deliberately test near-zero initial error
- Decide on Days 53–55 structure / bridge to waypoint navigation (Days 56–57)
