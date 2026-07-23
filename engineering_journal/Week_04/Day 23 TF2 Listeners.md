# Day 23 – TF2 Listeners: Receiving Coordinate Transforms

**Date:** 22 July 2026

---

# Objective

To understand the purpose of TF2 listeners, learn how to retrieve coordinate transforms between robot frames, and observe how independent ROS 2 nodes communicate through the TF2 system.

---

# Activities Performed

- Created a new ROS 2 node named `tf_listener.py`.
- Implemented a **TF2 Buffer** to store incoming transforms.
- Created a **TransformListener** to receive transform data from the TF2 network.
- Used the `lookup_transform()` method to obtain the position of `camera_link` relative to `base_link`.
- Retrieved and displayed the translation values (`x`, `y`, and `z`) from the received transform.
- Added the listener executable to the `setup.py` file.
- Rebuilt the package using `colcon build`.
- Sourced the workspace after rebuilding.
- Verified that both `tf_broadcaster` and `tf_listener` executables were successfully registered using:

```bash
ros2 pkg executables migro_tf2_001
```

- Executed the broadcaster and listener simultaneously in separate terminals.
- Observed the listener continuously receiving transform updates published by the broadcaster.
- Confirmed that modifying the broadcaster's translation values resulted in updated coordinates being displayed by the listener.

---

# Challenges Encountered

Initially ensured that the listener executable was properly registered in `setup.py` and verified successful package installation before attempting to execute the node.

---

# Solutions Applied

- Added the listener executable to the `console_scripts` section of `setup.py`.
- Rebuilt the package using:

```bash
colcon build --packages-select migro_tf2_001
```

- Sourced the workspace:

```bash
source install/setup.bash
```

- Verified the available executables before launching the nodes.

---

# Knowledge Gained

Today I learned that a **TF2 Listener** continuously retrieves coordinate transforms published by TF broadcasters instead of communicating directly with another node. I also learned the importance of **target** and **source** frames when requesting transforms and understood how TF2 enables different robot components to maintain a common understanding of spatial relationships.

---

# Commands Used

```bash
ros2 run migro_tf2_001 tf_broadcaster

ros2 run migro_tf2_001 tf_listener

ros2 pkg executables migro_tf2_001

colcon build --packages-select migro_tf2_001

source install/setup.bash
```

---

# Files Created / Modified

- `migro_tf2_001/tf_listener.py`
- `setup.py`

---

# Key Concepts Learned

- TF2 Listener
- TF2 Buffer
- TransformListener
- `lookup_transform()`
- Target Frame
- Source Frame
- Coordinate Frames
- Dynamic Transforms
- Transform Communication
- TF2 Architecture

---

# Reflection

Today's lesson demonstrated how robots determine the positions of different components without requiring direct communication between software modules. Understanding TF2 listeners provides the foundation for advanced robotics applications such as robot navigation, object manipulation, autonomous perception, and motion planning, where accurate coordinate transformations are essential.
