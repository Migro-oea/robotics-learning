# Day 59 — LIDAR Sensor Integration

## Objective

Add a 2D LIDAR sensor to MIGRO, verify that it publishes correctly through the ROS 2 / Gazebo Sim bridge, and confirm it produces accurate range readings against a known obstacle. This work followed the Days 57–63 revision cycle and marked the start of Step 5 (Sensors) on the roadmap. The session spanned two sittings, split by a late-night pause.

## Technical Concepts

Gazebo Sim (Harmonic-era, `gz-sim`) replaces classic Gazebo's plugin architecture. Sensors are defined inside a `<gazebo>` block in the URDF using SDF elements, but the plugin alone does not guarantee a working sensor. Three separate layers have to line up: the SDF sensor definition itself, the world's system plugins (which determine whether rendering and sensing are active at all), and the `ros_gz_bridge`, which is a completely separate process responsible for translating Gazebo Transport topics into ROS 2 topics. None of these layers reports failure loudly if another layer is missing. A `<sensor>` tag with no `Sensors` system plugin in the world simply produces nothing, with no error.

A second concept that came up repeatedly: `ros2 pkg` resources — xacro files, world files, and launch files — are read by `get_package_share_directory()` from the installed share directory, not from source. Editing a source file and relaunching does nothing until `colcon build` has actually copied the change into `install/`. This applied uniformly across every file type touched today, not just the URDF.

## Implementation

Four files were modified or created:

- `properties.xacro` — added LIDAR mount properties (`lidar_radius`, `lidar_height`, `lidar_x`, `lidar_y`, `lidar_z`), positioned front-center and on top of the chassis so a full 360° horizontal sweep is not blocked by the robot's own body.
- `lidar.xacro` (new) — defines `lidar_link`, a fixed joint to `base_link`, and a `<gazebo>` block containing a `gpu_lidar` sensor: 360 samples over a full circle, range 0.12–10.0 m.
- `migro.world.sdf` — added four explicit system plugins (`Physics`, `Sensors`, `SceneBroadcaster`, `UserCommands`). The world had none defined before, and while physics and scene broadcasting were apparently active by some Gazebo default, sensor rendering was not.
- `gazebo.launch.py` — added a `lidar_bridge` node bridging `/scan` from `gz.msgs.LaserScan` to `sensor_msgs/msg/LaserScan`.

A static test box (0.5 × 0.5 × 1.0 m) was later added to the world file, placed two meters in front of the robot's spawn point, to provide a known obstacle for verifying range accuracy.

2D LIDAR was chosen over 3D after some back-and-forth. Nav2's standard costmap and SLAM Toolbox both consume `LaserScan` messages directly; a 3D LIDAR publishes `PointCloud2` and would need an additional `pointcloud_to_laserscan` node to be useful for the same purpose. Most indoor differential-drive robots at this stage of complexity — TurtleBot being the obvious reference point — use 2D LIDAR for exactly this reason. 3D remains a reasonable extension once the 2D navigation stack is working, not a starting point.

## Code Changes

The `<sensor>` block in `lidar.xacro`:

```xml
<gazebo reference="lidar_link">
  <sensor name="lidar_sensor" type="gpu_lidar">
    <pose>0 0 0 0 0 0</pose>
    <topic>scan</topic>
    <gz_frame_id>lidar_link</gz_frame_id>
    <update_rate>10</update_rate>
    <always_on>true</always_on>
    <visualize>true</visualize>
    <lidar>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.12</min>
        <max>10.0</max>
        <resolution>0.01</resolution>
      </range>
    </lidar>
  </sensor>
</gazebo>
```

The `lidar_bridge` node in `gazebo.launch.py`:

```python
lidar_bridge = Node(
    package="ros_gz_bridge",
    executable="parameter_bridge",
    arguments=[
        "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
    ],
    output="screen",
)
```

## Problems Encountered

Several distinct issues surfaced, mostly one layer deep from the last:

1. **Wrong filename assumption.** The main URDF file is `migro.urdf.xacro`, not `migro_urdf.xacro`. An early xacro parse command was run against a path that did not exist.
2. **Stray nested install directory.** A duplicate `install/` folder existed inside `src/migro_description/`, left over from a colcon build likely run from the wrong working directory at some point. It was not in use, but worth flagging as clutter in the source tree.
3. **Missing `Sensors` system plugin.** The world file had no `<plugin>` declarations at all. Physics and scene broadcasting appeared to work anyway, but sensor rendering did not — `/scan` never appeared on `gz topic -l` until this was added explicitly.
4. **`lidar_bridge` defined but never launched.** The node object existed in the Python file, syntactically correct, but was never added to the final `LaunchDescription([...])` list. This is the same category of mistake as the earlier SIGINT fix being written into notes before it existed in code — a change that looks complete but was never actually wired in.
5. **Wrong SDF element for frame naming.** `<frame_id>` was tried first, based on pattern-matching from ROS conventions, and had no effect. The SDF parser silently ignored it rather than raising an error. The correct element, confirmed against the SDFormat spec and Gazebo's own migration documentation, is `<gz_frame_id>`.
6. **Stale running instance.** After adding a test box to the world file, `/scan` still returned no detections. The Gazebo process had been running continuously since before the edit; the world file is only read once, at launch.
7. **Terminal truncation produced a false negative.** `ros2 topic echo` truncates long arrays for display, inserting a literal `'...'` marker. Every manual inspection of the `ranges` array during this session was reading only the first third of 360 values — which, given the angle convention (`-π` to `π`), happened to be the rear-facing beams. The forward-facing beams, where the box actually was, were never visible in the truncated output.

## Debugging Process

Each problem was chased down with a direct check rather than an assumption: `find` to locate the real file paths, `gz topic -l` to confirm what Gazebo was actually publishing before touching the ROS side, `ros2 node list` to prove whether the bridge node process existed at all, and `ps aux` to check whether Gazebo had actually restarted after an edit. The `frame_id` mistake was resolved by searching Gazebo's own issue tracker and documentation rather than guessing a second time.

The final and most stubborn issue — the truncated array — was only caught by writing a small standalone rclpy subscriber (`check_scan.py`) that reads the `LaserScan` message object directly, bypassing the CLI's text formatting entirely. It reported all 360 beams, 18 of them finite, with a minimum range of 1.550 m at index 180.

## Testing

The 1.550 m reading was checked against expected geometry: the box's near face sits at world x = 1.75 m (center at x = 2.0, half-width 0.25 m), and the LIDAR is mounted 0.2 m forward of `base_link`. Expected distance is 1.75 − 0.2 = 1.55 m, matching the measured value exactly.

TF was also verified independently. `lidar_link` appears as a static child of `base_link` in `view_frames`, and `tf2_echo odom lidar_link` returns a consistent world-frame position of (0.2, 0.0, 0.375), matching the property values defined in `properties.xacro`.

## Engineering Decisions

System plugins were added explicitly to the world file rather than left to whatever implicit defaults Gazebo was applying. Two of the four plugins (`Physics`, `SceneBroadcaster`) may already have been active by default, but relying on undocumented default behavior is not something to build on going forward, particularly once more sensors and controllers depend on the same world.

The `<gz_frame_id>` fix was applied directly to the sensor definition rather than through a separate remapping node, keeping the frame naming consistent with the rest of the TF tree at the source rather than patching it downstream.

## Lessons Learned

The install-versus-source distinction in ROS 2 is not specific to URDF files. It applies to world files and launch files as well, and `get_package_share_directory()` is the mechanism responsible in every case. Any edit to a package resource needs a rebuild before it can be observed as taking effect, and unverified success at one step should not be assumed to carry forward automatically to the next.

SDF element names are not something to infer from ROS conventions or adjacent frameworks. `frame_id` is a reasonable guess and was wrong; `gz_frame_id` is correct, and the only way to know that with confidence was checking the spec directly.

Command-line tools built for human readability, such as `ros2 topic echo`, are not reliable instruments for verifying data correctness once arrays get large. A dedicated, minimal script reading the message object directly removed all ambiguity in a way that repeated attempts at parsing truncated terminal output could not.

## Reflection

The session was paused close to midnight, with battery and sleep both running low, at a point where the LIDAR appeared broken. It resumed the next day, and the actual state turned out to be that the sensor had already been working correctly since the `gz_frame_id` fix — every problem after that point was a failure to observe the data correctly, not a failure of the implementation. Stopping when tired rather than pushing through a false negative was the right call; a few more hours spent debugging a working system for the wrong reason would not have been time well spent.

## Next Steps

Camera sensor plugin is next, building on the existing mechanical mount already present in `camera.xacro`. IMU after that. Once all three sensors are verified, the Sensors step (5) closes out and Step 6 (Perception/Computer Vision) becomes the next real milestone — the point where the CV/DL skills gap named earlier in the roadmap starts to matter directly.
