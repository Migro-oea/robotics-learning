# Day 22 – TF2 Broadcaster and Coordinate Frames

**Date:** 22 July 2026

## Objective

The objective of today's lesson was to understand the fundamentals of the TF2 framework in ROS 2 by creating my first Transform Broadcaster. The goal was to learn how robots describe the position and orientation of different components using coordinate frames.

---

## Activities Performed

- Created a new ROS 2 Python package named `migro_tf2_001`.
- Configured the package dependencies in `package.xml`.
- Implemented a TF2 Broadcaster using `TransformBroadcaster`.
- Created a `TransformStamped` message to represent a transform.
- Defined the parent frame (`base_link`) and child frame (`camera_link`).
- Configured the translation of the camera frame to be 0.5 meters above the robot base.
- Assigned the identity quaternion to represent zero rotation.
- Built and sourced the package successfully.
- Executed the broadcaster node.
- Verified the transform using the `tf2_echo` tool.
- Learned how TF2 continuously broadcasts transforms between coordinate frames.

---

## Challenges Encountered

Initially, I expected both `/tf` and `/tf_static` topics to appear. After further investigation, I learned that the current implementation uses a Dynamic Transform Broadcaster, which continuously publishes on `/tf`. Static transforms are published differently using a Static Transform Broadcaster.

Another challenge involved verifying whether the broadcaster was publishing correctly. Although `/tf` existed, `ros2 topic echo /tf` did not immediately display messages. I verified successful broadcasting using `ros2 topic hz /tf` and `tf2_echo`, confirming that the transform was being published correctly.

---

## Lessons Learned

Today I learned:

- The purpose of the TF2 framework.
- The difference between Parent Frames and Child Frames.
- The ROS coordinate convention:
  - X → Forward
  - Y → Left
  - Z → Up
- How robots describe spatial relationships using transforms.
- The structure of a `TransformStamped` message.
- The role of `TransformBroadcaster`.
- Why dynamic transforms are published continuously.
- The difference between Dynamic and Static Transform Broadcasters.
- How to verify transforms using `tf2_echo`.

---

## Commands Used

```bash
cd ~/robotics_ws/src

ros2 pkg create --build-type ament_python migro_tf2_001

colcon build --packages-select migro_tf2_001

source install/setup.bash

ros2 run migro_tf2_001 tf_broadcaster

ros2 node list

ros2 topic list

ros2 topic hz /tf

ros2 run tf2_ros tf2_echo base_link camera_link
```

---

## Reflection

Today's lesson introduced one of the most important concepts in robotics: coordinate transformations. I now understand how different robot components maintain spatial relationships through TF2. Successfully broadcasting and verifying my first transform was another major milestone in my robotics engineering journey and strengthened my understanding of how robots perceive their physical structure.
