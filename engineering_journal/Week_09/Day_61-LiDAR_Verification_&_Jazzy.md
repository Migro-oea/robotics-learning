# Day 61 — LiDAR Verification & Jazzy `diff_drive_controller` Breaking Change

## Objective
Resolve the suspected LiDAR `frame_id`/TF mismatch flagged on Day 59, complete the LiDAR obstacle ranging test, and integrate a fix for teleop-to-controller communication into the launch file.

## Technical Concepts
- TF2 frame tree structure and `tf2_echo`/`view_frames` as ground-truth verification tools (vs. trusting stale notes)
- ROS 2 DDS type matching: publisher/subscriber type hashes must match exactly or no connection is established, with no explicit error at the publisher
- `ros2_control`'s `diff_drive_controller` breaking API change (Iron → Jazzy): `use_stamped_vel` and plain `Twist` support were removed entirely; `TwistStamped` is now mandatory
- `colcon`'s three-copy build model (`src/` → `build/` → `install/`) and the recurring failure mode of testing against a stale `install/` copy or a still-running process from before a rebuild

## Implementation
- Verified TF tree via `ros2 run tf2_tools view_frames`: confirmed `lidar_link` is correctly parented under `base_link`, matching `/scan`'s reported `frame_id`. The Day 59 mismatch note did not reflect the current build state — closed as a non-issue.
- Diagnosed teleop → controller communication failure via layered isolation (`/cmd_vel` existence → topic type inspection → node identification) rather than guessing at a fix.
- Root-caused via `ros2 param list /diff_drive_controller`: `use_stamped_vel` is absent from the node's declared parameter schema entirely (not merely unset), while every other `controllers.yaml` parameter loaded correctly — ruling out a stale-file or wrong-path theory.
- Confirmed via web search against the official `diff_drive_controller` changelog and Iron→Jazzy migration docs: non-stamped `Twist` support was removed in this controller version; `~/cmd_vel` now requires `TwistStamped`.
- Installed `ros-jazzy-twist-stamper` and wired it into `gazebo.launch.py` as a standing `Node()` entry, remapping `/cmd_vel` (plain `Twist`) → `/diff_drive_controller/cmd_vel` (`TwistStamped`), so any future `Twist`-publishing node (teleop, nav stack) works without a manual per-run remap.
- Ran the LiDAR obstacle ranging test: drove the robot toward a box in the world and confirmed a coherent cluster of finite range readings (~2.45 m, 12 contiguous points with smooth angle-to-angle continuity) against a background of `.inf` — consistent with a flat surface return, not noise.

## Code Changes
- `migro_description/launch/gazebo.launch.py`: added `twist_stamper` `Node()` block (package `twist_stamper`, executable `twist_stamper`, remaps `cmd_vel_in`→`/cmd_vel`, `cmd_vel_out`→`/diff_drive_controller/cmd_vel`, `frame_id` param set to `base_link`), included in the final `LaunchDescription` list.

## Problems Encountered
1. Suspected LiDAR TF mismatch (Day 59 holdover) — investigated, found already resolved.
2. Teleop produced no robot movement, no errors.
3. `ros2 topic echo` on `/scan` and `/diff_drive_controller/cmd_vel` initially misread due to terminal focus mixup (keystrokes landing in the wrong terminal) and YAML array truncation in `echo` output.
4. `ros2 param get` initially targeted the wrong node path (`/controller_manager/diff_drive_controller` instead of `/diff_drive_controller`).
5. After wiring `twist_stamper` into the launch file, it didn't appear in `ros2 node list` despite the code being correctly present in the built `install/` copy and working standalone via `ros2 run`.

## Debugging Process
- Diagnosed the movement failure by isolating each layer of the pipeline in sequence (teleop publish → topic existence → subscriber count → message type) rather than modifying code speculatively.
- Confirmed the true message-type mismatch (`Twist` vs `TwistStamped`) directly from `ros2 topic info -v`, which shows both endpoint types explicitly.
- Ruled out a stale-build theory for the missing `use_stamped_vel` parameter by diffing `src/`, `build/`, and `install/` copies of `controllers.yaml` (identical) before concluding the parameter was removed from the controller's schema upstream — verified against the package's own changelog rather than assumed.
- For the final `twist_stamper`-not-appearing issue: verified the executable name via `ros2 pkg executables`, verified the launch file edit was present in `install/` via `grep`, verified the node worked standalone via direct `ros2 run` — isolating the fault to the *running* launch session being stale, not the code. A full process kill (`pkill`) and relaunch resolved it.

## Testing
- `tf2_echo` confirmed stable `base_link` → `lidar_link` static transform after initial cold-start poll.
- `/scan` obstacle test: finite range cluster (~2.45 m) confirmed against a known obstacle in the world.
- Post-fix: `ros2 node list | grep twist_stamper` confirmed `/twist_stamper` running; teleop drove the robot with zero manual remap flags, using only the launch file.

## Engineering Decisions
- Chose `twist_stamper` (external package) over a hand-written conversion node for today, given time constraints and to avoid introducing unnecessary custom code for a well-solved problem; flagged writing an in-house version as a future option if more control is needed.
- Remapped `twist_stamper`'s output directly to `/diff_drive_controller/cmd_vel` rather than scoping the fix to teleop only, so the launch file is a systemic fix and any future `Twist`-publishing node (e.g. a Nav2 planner) works without modification.

## Lessons Learned
- A running ROS 2 process does not pick up source or launch-file changes until it is killed and relaunched — `colcon build` alone is not sufficient; this bit twice in one session (once with `controllers.yaml`, again with the `twist_stamper` integration).
- `ros2 param list <node>` is the correct tool to distinguish "parameter loaded with wrong value" from "parameter never declared by this version of the node" — checking declared parameters against a package's own changelog is more reliable than assuming YAML content is authoritative.
- `ros2 topic info -v` showing multiple message types on one topic name is a direct, load-bearing signal of a publisher/subscriber type mismatch — worth checking early in any "nothing happens, no errors" debugging session.

## Reflection
Most of today's time went into isolating a silent failure (no movement, no errors) down to a single-line root cause in an upstream package's breaking API change — a good example of why guessing at fixes wastes more time than methodically checking each layer of the pipeline in order.

## Next Steps
- Add `twist_stamper` as an `<exec_depend>` in `migro_description/package.xml` (not yet done — deferred due to session time)
- Close the `goal_handle.abort()` fix in `navigate_to_waypoint_server.py` (still open from Day 58/59)
- Clean up duplicate `/ros_gz_bridge` node names by giving each `parameter_bridge` instance a unique `name:=` in the launch file (deferred, non-blocking)
- Continue Step 5 (Sensors): IMU next
- ML/DL gap assessment (Step 12 prerequisite) still unaddressed
