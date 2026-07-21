# Day 20 – ROS 2 Integration Project

**Date:** July 21, 2026

---

## Objective

Combine ROS 2 Actions, Parameters, Launch Files, and Launch Arguments into a single configurable application that can be launched and customized without modifying the source code.

---

## What I Built

- Enhanced the existing ROS 2 Launch File to support multiple Launch Arguments.
- Added configurable node names for both the Action Server and Action Client.
- Passed the target number dynamically from the command line using Launch Arguments.
- Successfully launched the complete Action system with custom node names and parameter values.
- Verified that the Action Server and Action Client communicated correctly using the supplied configuration.

---

## Commands Used

Build the package:

```bash
cd ~/robotics_ws

colcon build --packages-select migro_action_001

source install/setup.bash
```

Launch with default configuration:

```bash
ros2 launch migro_action_001 count_until.launch.py
```

Launch with custom configuration:

```bash
ros2 launch migro_action_001 count_until.launch.py \
target_number:=15 \
server_name:=migro_server \
client_name:=migro_client
```

---

## Concepts Learned

Today I learned how Launch Files can configure an entire ROS application instead of simply starting nodes.

Using Launch Arguments, I was able to change:

- Target number
- Server node name
- Client node name

without modifying any Python source code.

This demonstrated how ROS separates application logic from deployment configuration.

---

## Key Takeaways

- Launch Arguments make ROS applications highly reusable.
- Multiple Launch Arguments can be combined within a single Launch File.
- Runtime configuration is preferred over hard-coded values.
- Professional ROS systems are designed to be configurable without changing the underlying code.

---

## Challenges

There were no major implementation issues.

The main challenge was understanding how Launch Arguments interact with Launch Configuration objects and how they are passed into individual nodes during startup.

After testing several launch configurations, I confirmed that the system behaved exactly as expected.

---

## Reflection

Today's project tied together everything I have learned throughout the Parameters and Launch Files module.

Instead of treating Actions, Parameters, and Launch Files as separate concepts, I now understand how they work together to build flexible and maintainable robotics software.

This feels much closer to how real robotic applications are deployed in industry.

---

## Module Completion

This project concludes my study of:

- ROS 2 Parameters
- Dynamic Parameters
- Launch Files
- Launch Arguments

I can now build configurable ROS applications that separate software logic from deployment settings.

---

## Next Steps

The next phase of my robotics journey will focus on robot coordinate systems, TF2, visualization with RViz, robot modeling using URDF, and simulation in Gazebo.
