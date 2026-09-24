# Day 60 — Camera Sensor Integration

## Objective

Add a camera sensor to MIGRO following the same simulation → verification pattern used for LiDAR (Day 59): Xacro link/joint → Gazebo sensor plugin → `ros_gz_bridge` → ROS 2 topic → `cv_bridge` subscriber → visual confirmation.

## Technical Concepts

- **ROS optical frame convention**: camera images use z-forward, x-right, y-down, which differs from URDF's x-forward, z-up convention. Requires a dedicated `camera_link_optical` frame with a fixed rotation joint (`rpy = -pi/2, 0, -pi/2`).
- **gz-sim sensor architecture (Gazebo Harmonic)**: sensors publish on Gazebo Transport, not directly onto ROS 2 topics. A `ros_gz_bridge` `parameter_bridge` node is required to bridge each topic into the ROS 2 graph.
- **`<optical_frame_id>`**: a gz-sim camera sensor tag that separates *where the sensor is physically attached/rendered from* from *what frame_id the output image reports*. Attaching the `<sensor>` tag itself to a rotated link does not just relabel the frame — it physically redirects the render.
- **Near-clip planes**: any sensor geometry (including the sensor's own housing) positioned at or behind the `<near>` distance renders as degenerate/solid fill.
- **NumPy ABI compatibility**: compiled ROS Python extensions (e.g. `cv_bridge`'s `cv_bridge_boost`) are built against a specific NumPy ABI; a shadowing user-level NumPy of a different major version causes a segfault, not a clean error.
- **colcon build vs. source**: without `--symlink-install`, `install/` is a copy of `src/`, not a live reference — edits to `src/` don't affect a running or even a freshly-launched node until rebuilt.

## Implementation

- Added `camera_link` (visual/collision/inertial box) and `camera_joint` (fixed, parented to `base_link`) in `camera.xacro`.
- Added `camera_link_optical` (empty link) and `camera_optical_joint` (fixed, rotation only) for ROS frame convention.
- Added a `gz-sim` `<sensor type="camera">` block: 640×480, 30 Hz, `horizontal_fov = 1.089` rad, near/far clip 0.05/10.0.
- Added `camera_bridge` (`parameter_bridge`) to `gazebo.launch.py`, bridging `/camera/image_raw` (`sensor_msgs/Image`) and `/camera/camera_info` (`sensor_msgs/CameraInfo`).
- Wrote `camera_viewer.py` in `migro_core_001`: subscribes to `/camera/image_raw`, converts with `cv_bridge.imgmsg_to_cv2(desired_encoding="bgr8")`, displays via `cv2.imshow`.
- Added an explicit `<light type="directional" name="sun">` and `<scene>` block to `migro.world.sdf` (previously undefined — relying on renderer defaults).
- Gave `ground_plane` and `test_box` explicit `<material>` definitions (previously undefined).

## Code Changes

- `migro_description/urdf/camera.xacro` — camera link/joint, optical frame, sensor block (final: sensor attached to `camera_link`, not `camera_link_optical`, with `<optical_frame_id>`)
- `migro_description/urdf/properties.xacro` — `camera_length/width/height`, `camera_x/y/z` (final: `camera_x = chassis_length/2 + camera_length/2`, protruding forward of chassis; `camera_z` derived from `lidar_z` for guaranteed clearance)
- `migro_description/worlds/migro.world.sdf` — added `sun` light, `<scene>` block, materials for `ground_plane` and `test_box`
- `migro_description/launch/gazebo.launch.py` — added `camera_bridge` node, added to `LaunchDescription([...])`
- `migro_core_001/migro_core_001/camera_viewer.py` — new file
- `migro_core_001/setup.py`, `package.xml` — entry point and dependencies (`cv_bridge`, `sensor_msgs`)

## Problems Encountered

1. **`camera_bridge` defined but not launched** — `Node()` object created but never added to the final `LaunchDescription([...])` list.
2. **NumPy 2.x/1.x ABI mismatch** — user-level `pip` install of NumPy 2.4.2 shadowed the NumPy 1.x `cv_bridge` was compiled against, causing a segfault on first image callback.
3. **`pip install --user` blocked by PEP 668** — Ubuntu 24.04's externally-managed-environment protection required `--break-system-packages`.
4. **Camera embedded in chassis geometry** — `camera_x = 0.0` placed the sensor at the chassis's horizontal center (inside the 0.5m-long box), not at its edge.
5. **Missing comma between two bridge arguments** — adjacent Python string literals silently concatenated into one invalid topic spec, so `parameter_bridge` created neither topic.
6. **Stale `install/`** — edited `src/` files (launch file, then later xacro) without rebuilding; `ros2 launch` kept running the old copy from `install/`.
7. **LiDAR/camera vertical overlap** — both sensors' z-heights were computed independently with only ~2.5cm separation, LiDAR occluding the camera.
8. **Camera housing self-occlusion** — the optical frame's local offset placed the sensor exactly at the camera box's own front face (flush, zero clearance), inside the near-clip threshold.
9. **Camera flush-mounted to chassis, zero standoff** — `camera_x` formula placed the housing's front face exactly coplanar with the chassis front face, not protruding beyond it.
10. **No world lighting/materials defined** — `migro.world.sdf` had no `<light>` and no `<scene>`; `ground_plane` and `test_box` had no `<material>`, producing ambiguous renderer-default colors.
11. **Root cause: sensor attached to rotated link** — the `<sensor>` tag was attached to `camera_link_optical` (rotated for ROS convention), which physically redirected the Gazebo render ~90° off the robot's true forward axis, independent of all geometry fixes above.

## Debugging Process

Worked outward from the ROS side inward to the render side, using layer-isolation at each step rather than guessing:

- `ros2 topic list` / `gz topic -l` to separate "Gazebo publishing" from "ROS 2 bridge working."
- `ros2 topic hz` to confirm a steady publish rate, not just topic existence.
- `ros2 run tf2_ros tf2_echo <parent> <child>` used repeatedly as ground truth for actual computed position/rotation, instead of reasoning from `${...}` formulas alone.
- `ros2 run tf2_tools view_frames` to confirm the real TF tree (`odom → base_link → camera_link → camera_link_optical`) and correct parent link names.
- `rqt_image_view` used specifically to isolate whether a symptom was in the render/scene layer or the `cv_bridge`/`camera_viewer.py` layer — confirmed identical output in both, ruling out the ROS-side pipeline entirely.
- Wrote a standalone `cv_bridge` pixel-inspector script (`inspect_camera.py`) to save `/tmp/camera_frame.png` and print raw BGR samples along the center row/column — screenshots via `rqt`/OS were being cropped/scaled and were misleading.
- Systematically eliminated candidate causes with real evidence: chassis embedding (fixed, confirmed via TF), LiDAR occlusion (fixed, confirmed via TF), missing lighting (fixed, added sun), self-occlusion (fixed, confirmed via TF, `[0.05, 0, 0.025]` local offset), shadow casting (disabled, no change — ruled out), image transpose/encoding (confirmed `640×480`, correct array shape — ruled out), ground plane finite-size edge (confirmed `100×100`, camera nowhere near edge — ruled out).
- User's own empirical observation — that rotating the displayed image 90° in `rqt_image_view` produced a correctly-framed scene — was the decisive clue pointing at a render-direction bug rather than a geometry bug.
- Explicit primary-color materials (red `test_box`, distinct background/ground colors) used to make ambiguous gray-on-gray renders diagnostically unambiguous.

## Testing

- `ros2 topic hz /camera/image_raw` — confirmed steady ~26–29 Hz publish rate at multiple points.
- `ros2 topic echo /camera/camera_info --once` — confirmed correct intrinsics (640×480, centered principal point, no distortion).
- `tf2_echo` checks at every geometry change to verify actual computed transforms against expected values before checking the image.
- Final verification: `rqt_image_view` at 0° rotation showing `test_box` (red) large, centered, directly ahead, with a correctly horizontal horizon (blue sky / gray ground) — confirmed against the Gazebo GUI's independent orbit view for consistency.

## Engineering Decisions

- Chose `<optical_frame_id>` over keeping the sensor attached to the rotated link — preserves both a physically correct render direction and ROS-convention frame labeling for downstream consumers, rather than trading one off for the other.
- Kept `camera_link_optical` and its joint in place after the fix (not deleted) — still required as a genuine TF frame for any future 3D vision math.
- Derived `camera_z` from `lidar_z` (rather than an independent formula) so vertical clearance between the two sensors is guaranteed by construction, not by manually tuned constants.
- Added explicit `<scene>` and `<material>` definitions to the world file as a standing practice, not just a one-off diagnostic — ambiguous renderer defaults cost significant debugging time and have no downside to fixing permanently.
- Did not bridge `camera_info` initially, then added it once needed — correctly deferred until required rather than bridging speculatively.

## Lessons Learned

- Attaching a `<sensor>` tag to a rotated link in gz-sim redirects the physical render, not just the frame_id — this is a non-obvious trap with no geometry-side symptoms, and applies to any future optical sensor (depth camera, stereo pair).
- A symptom that stays visually identical across many real, confirmed geometry changes is itself diagnostic — it means the bug is likely independent of the geometry being changed, not that the fixes are ineffective.
- Screenshots through rqt/OS tools get cropped and scaled in ways that mislead pixel-level diagnosis; a raw pixel-sample script is a more reliable tool for this class of bug.
- `install/` staleness is a repeat failure mode worth solving structurally (`--symlink-install`) rather than re-catching manually each time.
- World-level lighting and materials should be defined explicitly from the start — relying on renderer defaults removes a diagnostic anchor when something else goes wrong later.

## Reflection

This was the longest single-symptom debugging session so far — many real, individually necessary fixes (chassis embedding, LiDAR spacing, lighting, self-occlusion, world materials) were made along the way without resolving the core symptom, which took discipline to keep separating "did this fix something real" from "did this fix the actual bug." The eventual root cause was a layer beneath where all the geometry reasoning was happening, and was only found by taking the user's own empirical observation (0° vs. 270°) seriously as data rather than continuing to guess from formulas. Layer-isolation tools (`gz topic -l` vs `ros2 topic list` vs `rqt_image_view` vs full stack) were the actual turning point — they ruled out entire categories of explanation in single commands rather than one geometry guess at a time.

## Next Steps

- Bridge `camera_info` is in place — worth exercising once actual computer vision work starts (Step 9).
- Adopt `colcon build --symlink-install` workspace-wide to remove the install/src staleness failure mode going forward.
- Continue Step 5 (Sensors) revision cycle — camera sensor now complete and verified end-to-end.
