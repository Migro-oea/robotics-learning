# Day 54 — Waypoint Navigation (Option 1)

## Objective
Close the outstanding near-zero initial error edge case, then bridge the
Day 53–55 roadmap gap by generalizing `goal_controller.py` to support
sequential multi-waypoint navigation instead of a single fixed goal.

## Technical Concepts
- Boundary/edge-case testing for state-machine transitions (near-zero error).
- Proportional control speed floor behavior at small error values.
- Dynamic goal computation from live odometry (`atan2`, `sqrt`) vs. fixed
  launch-time parameters.
- Python `return` semantics inside conditional branches — controlling exactly
  which code executes after a state transition.

## Implementation
- Removed `target_yaw` and `target_distance` as ROS 2 launch parameters.
- Added a hardcoded waypoint list (`self.waypoints`) of absolute (x, y) world
  coordinates, plus `self.waypoint_index` and `self.goal_initialized`.
- Added `set_goal_for_current_waypoint(current_x, current_y)`: computes
  heading/distance to the current waypoint from wherever the robot actually
  is, resets `start_x`/`start_y` to `None`, and resets `state = 'ROTATING'`.
- `odom_callback()` now calls this method once on the first odom message
  (`goal_initialized` flag) to set the initial goal, since goals can no
  longer be known at `__init__` time.
- `do_moving()`'s completion branch now increments `waypoint_index` and either
  calls `set_goal_for_current_waypoint()` again or terminates, instead of
  unconditionally setting `state = 'DONE'`.
- Fixed the startup log line, which referenced `target_yaw`/`target_distance`
  before either was known — replaced with a message reporting waypoint count.

## Code Changes
- `goal_controller.py`: parameter block, `__init__` state section, new
  `set_goal_for_current_waypoint()` method, `odom_callback()`, and the
  `DONE` branch of `do_moving()`.
- No changes to `do_rotating()`, `stop_robot()`, `normalize_angle()`, or the
  KeyboardInterrupt shutdown sequence — deliberately preserved as-is.

## Problems Encountered
- Initial design would have crashed on startup: `math.degrees(self.target_yaw)`
  in the startup log ran before `target_yaw` was ever set, since goal
  computation now happens on the first odom callback, not in `__init__`.
- First Gazebo run after editing showed old single-goal log output
  ("Target heading: 90.0 deg... Distance reached!... Goal complete.") despite
  the source file being correctly edited — traced to not having rebuilt with
  `colcon build` before running.

## Debugging Process
- Predicted the `None`-crash before running, by reasoning through execution
  order: `__init__` runs before any odom message can arrive, so any log line
  reading `target_yaw` at that point would fail. Fixed by rewording the log
  line to not depend on values not yet known.
- Traced the stale-log mismatch by comparing exact log phrasing against the
  actual source file — since neither "Target heading: 90.0 deg" nor "Goal
  complete." exist anywhere in the new code, concluded the binary hadn't been
  rebuilt. Confirmed by rebuilding with `colcon build --symlink-install`,
  re-sourcing, and re-running — new log phrasing appeared correctly.
- Manually traced the `DONE` branch's `return` statement to confirm that once
  `set_goal_for_current_waypoint()` resets state and pose tracking, no stale
  `speed`/`error` calculation from the just-completed leg can run afterward —
  confirmed the `return` fires before reaching that code, so the transition
  is clean.

## Testing
- Near-zero heading: spawned with error already inside tolerance (~1° off).
  Confirmed via log: "Heading reached" printed on the very first callback,
  no "Rotating..." line ever appeared, zero angular velocity published from
  `do_rotating()` before transition.
- Near-zero distance: set `target_distance = 0.003`. Confirmed speed pinned
  at `min_speed` (0.03 m/s) for all iterations, ~6 loop iterations to
  complete, clean termination — but exact overshoot magnitude could not be
  confirmed due to `.2f` log rounding hiding sub-centimeter values.
- Waypoint navigation: ran 3 hardcoded waypoints [(2,0), (2,2), (0,2)] in
  Gazebo. Confirmed each waypoint's target heading/distance was computed from
  the robot's actual current pose, not a fixed reference — most notably,
  waypoint 2's target distance came out to 2.07m rather than an expected
  2.00m, reflecting real accumulated overshoot from prior legs. All three
  waypoints completed in sequence; controller correctly stopped after the
  third with no attempted fourth iteration.

## Engineering Decisions
- Chose to extend the existing state machine (Option 1) rather than restructure
  around a waypoint abstraction (Option 2), despite MIGRO being a long-term
  project. Reasoning: with only one waypoint sequence tested, I don't yet have
  enough real usage to know what a clean reusable abstraction should look
  like — building first and refactoring later with evidence avoids premature
  abstraction and protects already-verified code.
- Chose a hardcoded Python list for waypoint input over YAML/launch params for
  this pass, to keep the change surgical — proving the state machine can chain
  goals correctly without also debugging a parameter-parsing layer at the
  same time.

## Lessons Learned
- `return` inside a conditional branch is what prevents stale-state logic
  (e.g. leftover `speed`/`error` from a just-completed leg) from executing
  after a transition — same principle already used in the ROTATING/MOVING
  boundary checks, now applied to waypoint advancement.
- Values that are computed dynamically (not known at `__init__`) must not be
  referenced in code that runs before they're set — startup logging is an
  easy place to miss this.
- A rebuilt-but-unverified assumption ("I edited the file, so it must be
  running the new code") is exactly the kind of thing that "predict before
  running" is meant to catch — matching actual log output against the source
  file caught a stale-binary issue immediately.

## Reflection
This session closed two separate threads that had been open across previous
sessions (near-zero initial error, and the Day 53–55 roadmap gap) in one
sitting, without touching any of the previously-verified control logic. The
overshoot in waypoint 2 turning out to be a real, computed number rather than
a round one was a small but genuinely convincing signal that the dynamic
goal-recompute logic works as intended, not just by coincidence.

## Next Step
- Distance-near-zero: increase log precision (e.g. `.4f`) if exact overshoot
  values are needed later; not currently blocking.
- Revisit Option 2 (waypoint abstraction refactor) once more waypoint patterns
  have been exercised — no immediate need.
- Resume internship application pipeline work (OIST deadline, resume) — this
  has not been touched in several sessions and remains the actual bottleneck
  outside of technical progress.
