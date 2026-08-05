# Day 36 – Successfully Spawning MIGRO into Gazebo

**Date:** August 5, 2026  
**Duration:** Evening Session

---

# Objective

Today's objective was to transition MIGRO from a robot that could only be visualized in RViz to a robot that could exist inside a physics simulation using Gazebo Sim.

---

# Tasks Completed

- Verified that Gazebo Sim was correctly installed and accessible using the `gz` command.
- Created a dedicated `gazebo.launch.py` launch file for the `migro_description` package.
- Configured the launch file to:
  - Launch Gazebo Sim.
  - Start `robot_state_publisher`.
  - Spawn MIGRO from the `robot_description` topic.
- Built the updated package using `colcon build`.
- Sourced the workspace and launched the simulation successfully.
- Spawned MIGRO into Gazebo for the first time.

---

# Challenges Encountered

### 1. Gazebo Installation Issues

Initially, the Gazebo command (`gz`) was unavailable because the required Gazebo packages were not fully installed.

After troubleshooting the package repositories and verifying the OSRF package source, Gazebo was installed correctly and became accessible.

---

### 2. Root Link Inertia Warning

During launch, the following warning appeared:

```
The root link base_link has an inertia specified in the URDF,
but KDL does not support a root link with an inertia.
```

After investigation, I learned that this is a common warning when the robot's root link contains inertia properties.

This does not prevent Gazebo from simulating the robot correctly.

The recommended long-term solution is to introduce a `base_footprint` link above `base_link`.

---

### 3. EGL Graphics Warnings

Gazebo also produced several EGL-related warnings associated with the graphics driver.

Despite these warnings, Gazebo rendered correctly and MIGRO spawned successfully, so the warnings were determined to be non-blocking.

---

# Lessons Learned

Today reinforced several important robotics concepts:

- Gazebo does not automatically know about a robot—it receives the robot description through ROS.
- `robot_state_publisher` publishes the robot model to the `robot_description` topic.
- The `ros_gz_sim create` executable listens to this topic and creates the robot inside Gazebo.
- Launch files make it possible to start multiple ROS nodes in the correct order with a single command.
- Simulation requires more than a robot model—it also requires proper communication between ROS and Gazebo.

---

# Result

✅ Gazebo launches successfully.

✅ MIGRO is successfully spawned into Gazebo.

✅ The robot appears correctly with:

- Chassis
- Four wheels
- Camera
- Collision geometry

This marks MIGRO's first successful deployment inside a physics simulation environment.

---

# Next Steps

For the next session, I will begin transforming MIGRO from a static simulated robot into a controllable mobile robot by:

- Adding proper wheel joints.
- Integrating `ros2_control`.
- Configuring a Differential Drive Controller.
- Driving MIGRO using `/cmd_vel`.

---

# Reflection

Today was one of the biggest milestones in my robotics journey so far.

Seeing MIGRO move from RViz visualization into an actual simulation environment made the project feel significantly more real.

The robot is no longer just a collection of links and visuals—it now exists inside a simulator capable of supporting future sensing, control, and autonomous behaviors.

This milestone lays the foundation for everything that follows, including robot control, perception, navigation, and machine learning.
