# Day 58 — SIGINT Fix in navigate_to_waypoint_server.py

## Objective

Day 61's deep dive into the action server had surfaced a real bug: the SIGINT
handling that works correctly in `goal_controller.py` was never properly
ported to `navigate_to_waypoint_server.py`. Today's goal was to fix it and
confirm, with an actual Gazebo test, that the robot stops when the server is
interrupted mid-goal.

## Technical Concepts

The core concept here is that `KeyboardInterrupt` only unblocks whatever call
is directly blocked on the signal — it does not reach into every thread a
process happens to be running. `goal_controller.py` uses `rclpy.spin()` on a
single thread, so Ctrl+C interrupts the exact call that's blocking, and
everything downstream in `finally` runs on that same thread with no
coordination problem.

`navigate_to_waypoint_server.py` is different. It uses a
`MultiThreadedExecutor`, and the actual control loop inside
`execute_callback` runs on a separate worker thread, dispatched there because
the action server was configured with a `ReentrantCallbackGroup`. Ctrl+C
interrupts `executor.spin()` on the main thread only. The worker thread,
sitting in `time.sleep()` inside its own `while` loop, has no way of knowing
anything happened, and its exit condition — `rclpy.ok()` — doesn't flip to
`False` until after `rclpy.shutdown()`, which by then is the very last line
of the main thread's teardown. So the loop kept running commands into Gazebo
for however long the teardown took.

The fix for this class of problem is a `threading.Event`: a flag that is safe
to set from one thread and read from another without a lock, used here purely
as a shutdown signal rather than for passing data.

## Implementation

Added `self._shutdown_event = threading.Event()` to `__init__`. The
`execute_callback` loop condition became
`while rclpy.ok() and not self._shutdown_event.is_set():`, so the worker
thread checks the flag once per iteration — at 20 Hz, that's a maximum
latency of 50ms between the flag being set and the loop noticing.

`main()`'s `finally` block now sets the event as its very first action,
before touching the subscription or the node itself, followed by a short
`time.sleep(0.1)` — two loop periods — to give the worker thread room to see
the flag and finish its own iteration cleanly before the publisher it depends
on gets destroyed underneath it.

There was a second issue in the same area, smaller but worth fixing at the
same time: the code path that runs after the `while` loop exits — meant to
handle exactly this kind of interrupted shutdown — built a result message but
never actually called `stop_robot()`. Even a correctly-detected shutdown
would have left whatever velocity command was last published still active.
That line was added to the fallback path.

## Code Changes

- `navigate_to_waypoint_server.py`:
  - `import threading` added
  - `self._shutdown_event = threading.Event()` added to `__init__`
  - loop condition in `execute_callback` updated to check the event
  - fallback path (after the `while` loop) now calls `self.stop_robot()`
    before returning
  - `main()`'s `finally` block sets the event and sleeps briefly before the
    existing teardown sequence (destroy subscription, grace-period spin,
    destroy node, shutdown)
- `goal_controller.py`: untouched. Its single-threaded spin model doesn't
  have this problem, so there was nothing to change there.

## Problems Encountered

The most useful problem today was actually procedural, not technical: my
first attempt at testing this ended with the machine getting shut down
before the Ctrl+C test ran. That produced zero data — not a failed test, just
no test. It would have been easy to write the journal entry as though the
fix were confirmed, since the code review made it look obviously correct. I
did not do that, and reran the whole test properly once I was back at the
machine.

## Debugging Process

Rebuilt with `colcon build --packages-select migro_core_001`, confirmed a
clean finish. Grepped the file for `_shutdown_event` afterward, specifically
to confirm the edits had actually survived to disk before trusting the build
output — worth doing after any session that ends in an unclean shutdown.

Launched Gazebo, started the action server in a second terminal, and sent a
goal three meters out from a third terminal using
`ros2 action send_goal ... --feedback`, which streams `distance_remaining`
and `current_state` as the goal progresses. Let the feedback confirm the
robot had actually reached MOVING and was underway, then switched to the
server's terminal and hit Ctrl+C there — not the terminal running the goal
client, and not closing any windows.

## Testing

The server logged:

```
[INFO] Received goal: x=3.00, y=0.00
[INFO] Heading reached. Error: -0.0 deg. Switching to MOVING.
[INFO] Starting distance tracking from: x=0.00, y=-0.00
^C[WARN] Goal state not set, assuming aborted. Goal ID: [...]
```

The goal client reported `Result: success: false`, final position around
x=2.86 (out of a 3.0m target), and `Goal finished with status: ABORTED`. In
Gazebo, the robot stopped immediately on the Ctrl+C — not a slow drift, not a
few extra commands trickling through, an immediate stop.

That confirms the primary objective. The `threading.Event` is reaching the
worker thread, the worker thread is noticing it within roughly one loop
period, and it's calling `stop_robot()` before the node gets torn down.

The `WARN` line is a secondary finding, not a failure. `rclpy`'s action
server machinery expects the goal to end in an explicit terminal state —
succeeded, canceled, or aborted — set through `goal_handle`. The fallback
path publishes a stop command and returns a result, but never calls
`goal_handle.abort()`, so `rclpy` falls back to marking it aborted on my
behalf and logs a warning about it. The end state is the correct one, but it
happened by rclpy's default rather than by an explicit decision in the code.
That's a one-line fix — `goal_handle.abort()` before the return — left for a
future session rather than made tonight, given the time available.

## Engineering Decisions

Chose to verify with a real Ctrl+C in the server's own terminal rather than
accept the earlier shutdown-interrupted attempt as sufficient. A terminal
closing or a machine shutting down kills the process outright and skips the
exact code path being tested, so it would have told me nothing about whether
the fix works.

Decided not to chase the `goal_handle.abort()` gap in this session. The
primary risk — a robot that keeps moving in a real environment after a
supposed stop — is closed. The remaining issue is about how cleanly the
action server reports its own internal state, which matters for correctness
but not for safety, and is a small enough change to do properly rather than
rushed.

## Lessons Learned

`KeyboardInterrupt` in Python is not a broadcast. It interrupts one specific
blocking call, on the thread that owns it. Any additional thread — worker
threads inside a `MultiThreadedExecutor`, background threads spun up
manually, anything with its own loop — needs an explicit, thread-safe
shutdown mechanism if the program is expected to shut down as a coordinated
whole. `goal_controller.py`'s SIGINT handling worked without an `Event`
specifically because it never had a second thread. The moment
`navigate_to_waypoint_server.py` introduced one, that assumption quietly
stopped being true, and the bug sat there until the mid-motion Ctrl+C test on
Day 61 actually exercised it.

The other lesson is smaller but keeps coming up: a build succeeding and code
looking correct on review are not the same as a behavior being verified.
Today's first attempt would have made a fine journal entry if I hadn't
caught that the test itself never ran.

## Reflection

This was a short session, and most of the code had already been reasoned
through structurally before tonight — what changed today was seeing it
actually work in Gazebo instead of just following the logic on paper. The
gap between "this should work" and "the robot stopped, confirmed by watching
it happen" is exactly the gap the project's verification principle exists to
close, and today was a small, direct example of why that principle earns its
keep even under time pressure.

## Next Steps

- Add `goal_handle.abort()` to the fallback path in `execute_callback`, to
  replace rclpy's default aborted-state fallback with an explicit one
- Day 62: honest gap assessment — name CV/ML/DL as uncovered by the Days
  57–63 revision cycle
- Day 63: mock interview, LinkedIn post
- After the revision cycle closes: roadmap Steps 5–8 (Sensors, Perception,
  Localization, Navigation), building on the action-server pattern now
  confirmed working under interruption
