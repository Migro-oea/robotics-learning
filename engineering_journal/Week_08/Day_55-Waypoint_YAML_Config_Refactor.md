# Day 55

## Objective
Refactor `goal_controller.py` to load waypoints from an external YAML config file instead of a hardcoded Python list, without changing any runtime behavior. This decouples waypoint data from code, making it editable without a rebuild-and-redeploy cycle, and follows standard ROS 2 package conventions for external configuration.

## Technical Concepts
- **ROS 2 parameter system vs. plain file I/O**: ROS 2 nodes have a built-in parameter server (`declare_parameter`/`get_parameter`) that makes values introspectable and live-tunable via `ros2 param get/set`. This carries real overhead in setup and is designed for scalar/array runtime tuning knobs, not structured nested data. Since live-tuning waypoints was not a requirement (edit-file-and-relaunch is the accepted workflow), bypassing the parameter system entirely in favor of a plain YAML file read with `yaml.safe_load()` was the correct architectural choice — no parameter registration, no CLI override machinery, just a Python object read from disk.
- **`ament_index_python.packages.get_package_share_directory`**: resolves a package's installed share directory regardless of the working directory the node is launched from. This is the standard ROS 2 mechanism for locating installed non-code resources (config, launch files, meshes, etc.) and avoids fragile relative-path assumptions.
- **`setup.py` `data_files` install step**: Python ROS 2 packages must explicitly declare which non-Python files get installed into the package's share directory via `data_files` in `setup.py`. A source-tree file (e.g. `config/waypoints.yaml`) is invisible to `get_package_share_directory` after a clean build unless this entry exists.

## Implementation
Three changes, done in order:
1. Created `config/waypoints.yaml` in the package source tree, containing the same 3 waypoints previously hardcoded in `goal_controller.py`.
2. Updated `setup.py` to add a `data_files` entry installing `config/*.yaml` into the package's share directory, using `glob` so future YAML files are picked up automatically.
3. Updated `goal_controller.py` to resolve the installed YAML path via `get_package_share_directory`, load it with `yaml.safe_load()`, and convert the resulting list of `{x, y}` dicts into the same list of `(x, y)` tuples the rest of the state machine already expects.

## Code Changes
**`config/waypoints.yaml`** (new file):
```yaml
waypoints:
  - {x: 2.0, y: 0.0}
  - {x: 2.0, y: 2.0}
  - {x: 0.0, y: 2.0}
```

**`setup.py`**: added `import os`, `from glob import glob`, and one new `data_files` entry:
```python
(os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
```

**`goal_controller.py`**: added `import os`, `import yaml`, `from ament_index_python.packages import get_package_share_directory`. Replaced the hardcoded `self.waypoints = [...]` list with:
```python
pkg_share = get_package_share_directory('migro_core_001')
waypoints_path = os.path.join(pkg_share, 'config', 'waypoints.yaml')

with open(waypoints_path, 'r') as f:
    waypoints_data = yaml.safe_load(f)

self.waypoints = [
    (wp['x'], wp['y']) for wp in waypoints_data['waypoints']
]
```
No other lines in `goal_controller.py` changed — `waypoint_index`, `goal_initialized`, `target_yaw`, `target_distance`, and the entire state machine were left untouched.

## Problems Encountered
1. An early `setup.py` edit was incomplete — the `import os` / `from glob import glob` lines were added, but the new `data_files` tuple itself was never actually inserted into the list. `colcon build` succeeded regardless (Python packages have no compile step to catch this), and the config file did not appear in the install space until the missing tuple was added.
2. Momentary confusion about whether `colcon build` needed to be re-run in a second terminal before `ros2 run` — clarified that `colcon build` updates the shared install space once, and the actual per-terminal requirement is sourcing (`source ~/robotics_ws/install/setup.bash`), not rebuilding.

## Debugging Process
When `ls` on the expected install path failed, first ruled out a typo in the checked path (the original failing command was missing the `share/migro_core_001` segment), then re-ran the correct path. When that also came up empty despite a "successful" build, went back to the actual `setup.py` source with `cat` rather than assuming the earlier edit had been applied — this immediately showed the `data_files` list still only had the original two entries. Fixing that and rebuilding resolved it, confirmed by `ls` showing `waypoints.yaml` present in the install directory.

## Testing
1. Verified `config/waypoints.yaml` parses correctly with a standalone `yaml.safe_load()` check before ever touching `goal_controller.py`, confirming the exact dict structure expected downstream.
2. Verified the installed file's presence via `ls` on the install share path after each build.
3. Ran the full node in Gazebo end-to-end and captured the log output for the complete 3-waypoint run.
4. Cross-checked logged waypoint coordinates and target headings/distances against the original hardcoded values:
   - Waypoint 0: (2.00, 0.00), heading -0.0°, distance 2.00 m — matches.
   - Waypoint 1: (2.00, 2.00), heading 90.0°, distance 2.00 m — matches.
   - Waypoint 2: (0.00, 2.00), heading 180.0°, distance 2.07 m — matches expected overshoot self-correction (recomputed from actual post-waypoint-1 odometry, consistent with Day 54 behavior).
5. Confirmed "All waypoints complete." at the end of the run with no errors.

## Engineering Decisions
- Chose plain-file YAML loading over ROS 2 parameters after explicitly confirming the live-tuning use case (`ros2 param set`) was not needed. This avoided the awkward parallel-array shape (`waypoint_x: [...]`, `waypoint_y: [...]`) that ROS 2's flat parameter type system would have forced, in favor of a natural nested `{x, y}` structure.
- Chose to let the node crash loudly (unhandled exception) if `waypoints.yaml` is missing or malformed, rather than silently falling back to a default waypoint list. A missing config file is a real deployment error that should surface immediately, not be masked.
- Used `glob('config/*.yaml')` in `setup.py` instead of hardcoding the filename, so future config files are installed automatically without further `setup.py` edits.

## Lessons Learned
- `colcon build` succeeding is not proof that a source edit was actually applied correctly — Python packages have no compilation step, so a build can "succeed" even when the intended code change never happened. The only real verification is re-reading the actual file content or observing the runtime behavior.
- Rebuilding is a workspace-wide, one-time operation per change; sourcing (`setup.bash`) is the per-terminal requirement. Conflating these two easily leads to unnecessary rebuilds or, in the earlier case, confusion about which was missing.

## Reflection
This was a clean "zero behavior change" refactor — the value was in decoupling configuration from code, not in changing what the robot does. The one real bug (incomplete `setup.py` edit) was caught early because of the habit of verifying at the file-system level (`ls` on the install path) rather than trusting a successful build message, which matches the broader principle of never closing out a test without direct log-or-filesystem-level confirmation.

## Next Step
YAML/launch-param sourcing for waypoints is now complete. Next up per the roadmap: continue exercising more waypoint patterns before considering the Option 2 waypoint-abstraction class, and/or begin scoping the deep learning and RL ramp-up needed for roadmap steps 9 and 12.
