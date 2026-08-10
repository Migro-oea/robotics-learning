# Day 41 – Automating MIGRO Controller Startup

**Date:** 9 August 2026

---

## Objective

Complete the Gazebo control setup for MIGRO and eliminate the need to manually load and activate ROS 2 controllers every time the simulation starts.

---

## Work Completed

Today, I continued debugging the MIGRO Gazebo simulation and its `ros2_control` integration.

The main issue was that the `controller_manager` was running, but the controllers were not automatically loaded or activated when Gazebo started. This meant that I previously had to manually load and activate the controllers from the terminal before I could control MIGRO.

I verified that the required ROS 2 control packages were installed, including:

* `ros2_control`
* `ros2_controllers`
* `diff_drive_controller`
* `gz_ros2_control`

I also verified that MIGRO's generated URDF contained the required `ros2_control` configuration and that the `gz_ros2_control` Gazebo plugin was being loaded correctly.

---

## Gazebo Clock Debugging

Another issue encountered was the warning:

```text
No clock received, using time argument instead!
Check your node's clock configuration (use_sim_time parameter)
and if a valid clock source is available
```

I investigated the simulation clock and discovered that Gazebo was publishing its clock on:

```text
/world/migro_world/clock
```

while ROS 2 was expecting:

```text
/clock
```

I therefore added a `ros_gz_bridge` clock bridge to the Gazebo launch file so that the Gazebo simulation clock is made available to ROS 2.

The relevant bridge connects:

```text
Gazebo: /world/migro_world/clock
        ↓
ROS 2: /clock
```

I also verified that `use_sim_time` was enabled for the relevant ROS 2 nodes.

---

## Automatic Controller Startup

I modified the Gazebo launch file to automatically spawn:

* `joint_state_broadcaster`
* `diff_drive_controller`

A startup delay was added to allow Gazebo and `controller_manager` to initialize before the controller spawners attempt to connect.

As a result, I no longer need to manually run commands such as:

```bash
ros2 control load_controller joint_state_broadcaster
```

or:

```bash
ros2 control load_controller diff_drive_controller
```

The controllers now start automatically when I launch the simulation.

---

## Verification

After restarting Gazebo and launching MIGRO, I verified that both controllers were active:

```text
joint_state_broadcaster   active
diff_drive_controller     active
```

I also verified the relevant ROS 2 topics:

```text
/clock
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/dynamic_joint_states
/joint_states
```

The hardware interfaces showed that the four wheel velocity command interfaces were available and claimed by the differential drive controller.

---

## Final Functional Test

I sent a velocity command to the differential drive controller:

```text
linear.x = 0.2 m/s
angular.z = 0.0 rad/s
```

MIGRO responded to the command and physically moved in Gazebo.

However, MIGRO moved **backward instead of forward**.

This confirms that the complete ROS 2 → controller → `ros2_control` → Gazebo → wheel joint control pipeline is functioning, but the wheel rotation direction needs to be corrected.

---

## Problem Remaining

The remaining issue is the direction/sign of the wheel joints.

The current configuration causes a positive forward velocity command to rotate the wheels in the direction that moves MIGRO backward.

This will be investigated and corrected in the next session by checking the wheel joint axes, wheel orientation, and controller configuration.

---

## Key Learning

Today I learned that a successful `ros2_control` setup requires more than defining wheel joints and command interfaces.

The complete control chain is:

```text
ROS 2 /cmd_vel
      ↓
diff_drive_controller
      ↓
controller_manager
      ↓
ros2_control hardware interfaces
      ↓
gz_ros2_control
      ↓
Gazebo wheel joints
      ↓
MIGRO movement
```

I also learned the importance of bridging simulation time from Gazebo to ROS 2 when using `use_sim_time`.

Most importantly, MIGRO's simulation is now much more efficient to use because the required controllers are automatically started when Gazebo launches.

---

## Status

**Day 41 completed.**

MIGRO is now successfully controllable through the ROS 2 differential drive controller.

**Next session:** Correct the wheel rotation direction and verify forward, backward, and rotational movement.


