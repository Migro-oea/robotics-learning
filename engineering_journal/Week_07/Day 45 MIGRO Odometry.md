# Day 45 – MIGRO Odometry Monitoring

**Date:** 11 August 2026

---

## Objective

Build on MIGRO's successful keyboard teleoperation system by introducing a software component capable of reading and interpreting the robot's odometry.

The goal for today was to move beyond simply commanding MIGRO and begin allowing software to observe and report the robot's state.

---

## Background

During the previous days, MIGRO's differential-drive control system was successfully integrated with Gazebo and `ros2_control`.

The control pipeline had reached the following state:

```text
Keyboard
    ↓
keyboard_teleop
    ↓
TwistStamped
    ↓
/diff_drive_controller/cmd_vel
    ↓
diff_drive_controller
    ↓
ros2_control
    ↓
Wheel joints
    ↓
Gazebo
    ↓
MIGRO
