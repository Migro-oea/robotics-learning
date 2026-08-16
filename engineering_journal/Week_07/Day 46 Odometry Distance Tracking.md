# Day 46 – Odometry Distance Tracking

**Date:** 12 August 2026

## Objective

Extend MIGRO's existing odometry monitoring system so that the robot can calculate and report its displacement from its starting position.

The previous day focused on reading and interpreting odometry data such as position, orientation, and velocity. Today, the objective was to go one step further by using the odometry data to derive a useful measurement: the distance between MIGRO's current position and its starting position.

---

## Starting Point

At the beginning of Day 46, MIGRO already had a working differential-drive control system.

The existing architecture consisted of:

```text
Keyboard Teleoperation
        ↓
Diff Drive Controller
        ↓
Wheel Joints
        ↓
Gazebo
        ↓
MIGRO
```

MIGRO was publishing odometry through `/diff_drive_controller/odom` using `nav_msgs/msg/Odometry`.

A custom ROS 2 node called `odom_monitor` was already monitoring:

- X position
- Y position
- Yaw
- Linear velocity
- Angular velocity

The purpose of Day 46 was to extend this functionality.

---

## Why Distance Tracking Was Added

Simply displaying the current X and Y coordinates is useful, but it does not immediately communicate how far MIGRO has moved away from its starting position.

For example, if MIGRO reports:

```text
x = 1.20 m
y = 0.50 m
```

it is useful to also know the magnitude of its displacement from where monitoring began.

Therefore, the odometry monitor was extended to calculate the distance between the starting position and the current position.

This introduced a simple example of transforming raw robot-state data into more meaningful information.

---

## Calculating Distance From the Starting Position

The first odometry position received by the monitor is stored as the starting position.

The starting coordinates are represented as:

```text
x₀
y₀
```

When a new odometry message is received, the current position is:

```text
x
y
```

The displacement along each axis is calculated using:

```text
Δx = x - x₀
Δy = y - y₀
```

The magnitude of the displacement is then calculated using the Euclidean distance formula:

```text
distance = √(Δx² + Δy²)
```

This gives the straight-line displacement between MIGRO's starting position and its current position.

---

## Modifying `odom_monitor.py`

The existing `odom_monitor.py` node was extended to store MIGRO's starting position.

Two variables were added:

```python
self.start_x = None
self.start_y = None
```

When the first odometry message is received, the current position is saved:

```python
if self.start_x is None:
    self.start_x = x
    self.start_y = y
```

This establishes the reference position for the rest of the monitoring session.

The node then calculates the current displacement from that reference position.

---

## Updated Distance Calculation

The current position is compared with the starting position:

```python
dx = x - self.start_x
dy = y - self.start_y
```

The distance from the starting position is then calculated:

```python
distance_from_start = math.sqrt(
    dx ** 2 + dy ** 2
)
```

The result is reported in metres.

This allows the monitor to provide an additional measurement without changing the underlying differential-drive controller.

---

## Updated Odometry Monitor Output

The monitor now reports:

- Current X position
- Current Y position
- Distance from starting position
- Yaw
- Linear velocity
- Angular velocity

The output follows the structure:

```text
Position: x=... m, y=... m |
Distance from start=... m |
Yaw=... deg |
Linear=... m/s |
Angular=... rad/s
```

This makes it easier to observe MIGRO's state during simulation and testing.

---

## Building the Updated Package

After modifying the odometry monitor, the `migro_teleop` package was rebuilt.

The following commands were used:

```bash
cd ~/robotics_ws
colcon build --packages-select migro_teleop
source install/setup.bash
```

The package built successfully.

The available executables were verified with:

```bash
ros2 pkg executables migro_teleop
```

The result showed:

```text
migro_teleop keyboard_teleop
migro_teleop odom_monitor
```

This confirmed that both the keyboard teleoperation node and the odometry monitor remained available after the modification.

---

## Launching MIGRO

MIGRO was launched using the existing Gazebo launch file:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 launch migro_description gazebo.launch.py
```

This launch process starts the required simulation components, including:

- Gazebo
- MIGRO
- Robot State Publisher
- Gazebo/ROS 2 clock bridge
- `gz_ros2_control`
- Joint State Broadcaster
- Differential Drive Controller

The controllers were confirmed to become active.

---

## Starting the Odometry Monitor

The updated odometry monitor was started in a separate terminal:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 run migro_teleop odom_monitor
```

The node successfully connected to:

```text
/diff_drive_controller/odom
```

and began reporting MIGRO's state.

The monitor continued to provide readable updates at approximately one-second intervals.

---

## Starting Keyboard Teleoperation

Keyboard teleoperation is a separate ROS 2 executable and is not automatically started by the Gazebo launch file.

Therefore, it was started separately:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 run migro_teleop keyboard_teleop
```

Once started, MIGRO responded correctly to keyboard commands.

The three-terminal workflow was:

```text
Terminal 1
Gazebo + MIGRO
        ↓
Controllers
```

```text
Terminal 2
odom_monitor
        ↓
/diff_drive_controller/odom
```

```text
Terminal 3
keyboard_teleop
        ↓
/diff_drive_controller/cmd_vel
        ↓
MIGRO
```

---

## Testing Forward Movement

MIGRO was commanded to move forward using the keyboard teleoperation system.

The forward command was:

```text
W
```

MIGRO moved successfully in Gazebo.

The odometry monitor responded with updated X and Y position values.

As MIGRO moved away from the starting position, the reported distance from start also increased.

This confirmed that the new calculation was being performed correctly.

---

## Testing the Stop Command

After moving MIGRO, the robot was stopped using:

```text
SPACE
```

The odometry monitor showed the linear velocity returning to approximately:

```text
Linear = 0.00 m/s
```

The angular velocity also returned to approximately:

```text
Angular = 0.00 rad/s
```

This confirmed that adding distance tracking did not interfere with the existing velocity monitoring.

---

## Testing Rotation

MIGRO was rotated using the keyboard teleoperation controls.

The yaw value reported by the odometry monitor changed as MIGRO rotated.

This confirmed that the quaternion-to-yaw conversion implemented during Day 45 continued to work correctly.

The distance-from-start calculation also remained active while the robot changed orientation.

---

## Understanding Displacement vs Total Distance

An important concept reinforced during this implementation is that the new value represents **displacement from the starting position**, not the total distance travelled by the robot.

For example, if MIGRO moves:

```text
1 m forward
```

and then:

```text
1 m backward
```

it can return close to its original position.

The monitor would then report approximately:

```text
Distance from start = 0.00 m
```

even though MIGRO actually travelled approximately 2 metres.

Therefore:

### Displacement

Displacement describes the change in position between the starting point and the current point.

### Total Distance Travelled

Total distance travelled represents the complete path length followed by the robot.

The implementation completed today measures **displacement from the starting position**.

This distinction will become increasingly important when working with navigation and path planning.

---

## Why This Matters for Robotics

The ability to calculate displacement from odometry is useful for higher-level robotic behaviors.

Robot software can eventually use position information to determine:

- Whether the robot has reached a target
- How far the robot is from a waypoint
- Whether the robot has moved sufficiently
- Whether the robot has deviated from a desired position
- Whether a navigation goal has been reached
- How the robot's current state compares with a desired state

This creates a bridge between low-level robot control and higher-level navigation.

---

## Updated MIGRO Architecture

After today's work, MIGRO has both a command path and a feedback path.

### Command Path

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
Wheel Joints
    ↓
Gazebo
    ↓
MIGRO Movement
```

### Feedback Path

```text
MIGRO Movement
      ↓
Wheel Movement
      ↓
diff_drive_controller
      ↓
/diff_drive_controller/odom
      ↓
odom_monitor
      ↓
┌─────────────────────────────┐
│ Position                    │
│ Yaw                         │
│ Linear Velocity             │
│ Angular Velocity            │
│ Distance From Start         │
└─────────────────────────────┘
```

This gives MIGRO a complete basic command-and-feedback loop.

---

## Engineering Significance

The main progression from the previous day is that the system is beginning to transform raw robot-state information into meaningful information.

Previously:

```text
Odometry → Display Values
```

Today:

```text
Odometry
    ↓
Extract Position
    ↓
Compare With Starting Position
    ↓
Calculate Displacement
    ↓
Report Useful Robot State
```

This is an important pattern in robotics software engineering.

Robotic systems frequently take raw measurements and process them into information that can be used by:

- Controllers
- Navigation systems
- Planners
- State estimators
- Decision-making systems
- Autonomous behaviors

The `odom_monitor` node is a simple implementation of this principle.

---

## ROS 2 Concepts Practiced

### Nodes

The `odom_monitor` program runs as a ROS 2 node.

### Topics

The node receives robot state information through:

```text
/diff_drive_controller/odom
```

### Subscribers

The node subscribes to the odometry topic and processes incoming messages.

### Message Types

The node works with:

```text
nav_msgs/msg/Odometry
```

### Data Processing

Instead of simply displaying raw values, the node performs calculations on incoming data.

### Robot State

The node extracts position, orientation, and velocity information from the robot's state.

### Feedback

The robot's movement generates state information that can be observed by other software components.

---

## What Was Learned

Today's work reinforced several important robotics concepts:

- Odometry provides an estimate of a robot's position, orientation, and movement over time.
- X and Y coordinates describe MIGRO's estimated location relative to the odometry frame.
- Displacement describes the change in position relative to a reference position.
- The magnitude of displacement can be calculated from X and Y differences using the Euclidean distance formula.
- ROS 2 nodes can transform raw message data into higher-level information.
- A robot needs information about its state in order to make informed decisions about its next action.

---

## Day 46 Outcome

By the end of Day 46, MIGRO successfully had:

- ✅ Working Gazebo simulation
- ✅ Working robot controllers
- ✅ Working keyboard teleoperation
- ✅ Working differential-drive control
- ✅ Working odometry
- ✅ Working odometry monitor
- ✅ Position monitoring
- ✅ Yaw monitoring
- ✅ Linear velocity monitoring
- ✅ Angular velocity monitoring
- ✅ Starting-position tracking
- ✅ Distance-from-start calculation
- ✅ Successful forward movement test
- ✅ Successful stop test
- ✅ Successful rotation test
- ✅ Successful rebuild of the `migro_teleop` package

---

## Next Direction

MIGRO currently follows this basic cycle:

```text
Human
  ↓
Command
  ↓
Robot
  ↓
Odometry
  ↓
Robot State
```

The long-term objective is to develop:

```text
Robot State
     ↓
Perception
     ↓
Decision Making
     ↓
Motion Command
     ↓
Robot
     ↓
New Robot State
     ↺
```

This will eventually form the foundation for autonomous navigation and intelligent robotic behavior.

The work completed today brings MIGRO one step closer to that architecture.

---

## Summary

Day 46 extended MIGRO's existing odometry monitoring system by adding displacement tracking.

The robot now records its starting position and calculates how far its current position is from that reference point.

This was implemented by storing the initial X and Y coordinates, calculating the change along each axis, and applying the Euclidean distance formula.

The updated system was successfully built and tested alongside MIGRO's Gazebo simulation, differential-drive controller, keyboard teleoperation system, and odometry monitor.

The most important engineering lesson from today was that robot software does not have to simply consume raw sensor or state data. It can process that information into meaningful quantities that can later support navigation, planning, control, and autonomous decision-making.

Day 46 therefore represents another step in the progression of MIGRO from a manually controlled simulated robot toward an autonomous robotic system.
