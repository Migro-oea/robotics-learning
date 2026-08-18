# Day 48 – Proportional Distance Control

**Date:** 18 August 2026

## Objective

Upgrade MIGRO's existing closed-loop distance controller so that it no longer moves at a fixed speed throughout the entire movement.

The objective was to introduce proportional control, allowing MIGRO to adjust its forward velocity according to the remaining distance to its target.

The desired behaviour was:

```text
Far from target
      ↓
Move faster

Closer to target
      ↓
Move slower

Target reached
      ↓
Stop
```

This builds directly on the closed-loop distance controller developed during Day 47, where MIGRO successfully used odometry feedback to move approximately 1 metre and automatically stop. fileciteturn0file0L7-L13

---

## Starting Point

At the beginning of Day 48, MIGRO already had a working `distance_controller` node inside the existing:

```text
migro_core_001
```

package.

The Day 47 controller used:

```text
/diff_drive_controller/odom
```

as feedback and published:

```text
geometry_msgs/msg/TwistStamped
```

commands to:

```text
/diff_drive_controller/cmd_vel
```

The controller recorded MIGRO's starting position, calculated displacement, and stopped the robot when the target distance was reached. fileciteturn0file0L173-L213

The limitation was that the controller used a constant forward speed.

Therefore, the control behaviour was essentially:

```text
Distance < Target
       ↓
Move at fixed speed

Distance ≥ Target
       ↓
Stop
```

The goal for Day 48 was to make the speed respond to the current distance error.

---

## Why Proportional Control Was Added

A fixed-speed controller is useful as a first closed-loop implementation, but it does not consider how close MIGRO is to its target.

For example, if MIGRO is:

```text
0.8 m
```

away from a:

```text
1.0 m
```

target, it may be useful to move more slowly than when it is:

```text
0.1 m
```

from the starting position.

This creates a more natural control strategy:

```text
Large error
    ↓
Larger control response

Small error
    ↓
Smaller control response
```

The controller can therefore use the remaining distance as an indication of how strongly it should command the robot.

---

## Calculating the Control Error

The displacement calculation from Day 46 and Day 47 was retained.

The controller calculates:

```text
Δx = x - x₀
Δy = y - y₀
```

and then:

```text
distance = √(Δx² + Δy²)
```

The remaining distance to the target is then calculated as:

```text
error = target_distance - distance
```

For example:

```text
Target distance = 1.00 m
Current distance = 0.40 m
```

Therefore:

```text
error = 1.00 - 0.40
      = 0.60 m
```

The controller now has a direct measurement of how much distance remains before the target is reached.

---

## Introducing Proportional Control

The new controller uses the proportional control relationship:

```text
speed = Kp × error
```

where:

```text
Kp
```

is the proportional gain.

The controller was configured with:

```text
Kp = 0.8
```

For example, if:

```text
error = 0.10 m
```

then:

```text
speed = 0.8 × 0.10
      = 0.08 m/s
```

This means the commanded speed becomes smaller as the remaining error becomes smaller.

The control behaviour therefore becomes:

```text
Large error
    ↓
Higher speed

Small error
    ↓
Lower speed
```

This is the fundamental idea behind proportional control.

---

## Updating the Controller Parameters

The previous fixed-speed parameter was replaced with parameters for proportional control.

The controller now declares:

```python
self.declare_parameter('target_distance', 1.0)
self.declare_parameter('kp', 0.8)
self.declare_parameter('max_speed', 0.2)
self.declare_parameter('min_speed', 0.03)
```

These parameters allow the controller's behaviour to be adjusted without changing the core control logic.

### Target Distance

```text
target_distance = 1.0
```

Defines how far MIGRO should move from its starting position.

### Proportional Gain

```text
kp = 0.8
```

Determines how strongly the controller responds to the remaining distance error.

### Maximum Speed

```text
max_speed = 0.2
```

Limits the maximum velocity that can be commanded.

### Minimum Speed

```text
min_speed = 0.03
```

Prevents the controller from commanding an extremely small velocity while the target has not yet been reached.

---

## Enforcing the Speed Limit

The speed calculation was placed inside the movement function:

```python
def move_forward(self, distance, error):
```

The proportional speed is first calculated:

```python
speed = self.kp * error
```

The maximum speed is then enforced:

```python
speed = min(speed, self.max_speed)
```

This ensures that the proportional controller cannot command a velocity greater than the configured maximum.

The minimum speed is then enforced:

```python
if speed < self.min_speed:
    speed = self.min_speed
```

The final speed is assigned to the velocity command:

```python
msg.twist.linear.x = speed
```

The resulting control pipeline is:

```text
Error
  ↓
Kp × Error
  ↓
Calculated Speed
  ↓
Maximum Speed Limit
  ↓
Minimum Speed Limit
  ↓
TwistStamped
```

---

## Updating the Odometry Callback

The odometry callback was updated to calculate the control error.

After calculating displacement:

```python
dx = x - self.start_x
dy = y - self.start_y

distance = math.sqrt(
    dx ** 2 + dy ** 2
)
```

the controller calculates:

```python
error = self.target_distance - distance
```

The target check is then performed.

If:

```text
distance >= target_distance
```

the robot is stopped.

Otherwise, the controller sends the current distance and error to:

```python
self.move_forward(distance, error)
```

This means the controller continuously updates its velocity based on the latest odometry feedback.

---

## Updated Movement Logic

The updated movement logic can be represented as:

```text
Receive Odometry
      ↓
Calculate Current Distance
      ↓
Calculate Error
      ↓
Is Target Reached?
   ├── Yes → Stop
   │
   └── No
        ↓
Calculate Proportional Speed
        ↓
Apply Maximum Speed Limit
        ↓
Apply Minimum Speed Limit
        ↓
Publish Velocity
```

This is a more complete feedback-control cycle than the fixed-speed implementation used previously.

---

## Controller Output

The controller's log output was also updated to show the control information.

The output now follows the structure:

```text
Moving... 0.40 / 1.00 m | Error: 0.60 m | Speed: 0.20 m/s
```

This provides three important pieces of information:

```text
Current distance
Remaining error
Commanded speed
```

This makes it easier to observe how the controller responds as MIGRO approaches its target.

---

## Understanding Speed Saturation

The maximum speed limit is important because proportional control can produce a large output when the error is large.

For example:

```text
Kp = 0.8
Error = 1.00 m
```

would produce:

```text
speed = 0.8 m/s
```

However, the configured maximum speed is:

```text
0.2 m/s
```

Therefore:

```text
Calculated speed = 0.8 m/s
Maximum speed = 0.2 m/s
Final speed = 0.2 m/s
```

The controller therefore saturates its output at the configured maximum.

This prevents large errors from producing unnecessarily high velocity commands.

---

## Understanding the Minimum Speed

A proportional controller naturally approaches zero output as the error becomes smaller.

For example:

```text
Error = 0.02 m
Kp = 0.8
```

would produce:

```text
speed = 0.016 m/s
```

The controller's minimum speed is:

```text
0.03 m/s
```

Therefore, while the target has not yet been reached, the controller will use:

```text
0.03 m/s
```

instead of an extremely small value.

This creates a practical lower bound for the robot's forward command.

The target detection logic still has priority, so once:

```text
distance >= target_distance
```

the robot receives a zero-velocity command.

---

## Testing the Updated Controller

The updated `distance_controller` was rebuilt and tested in the existing MIGRO Gazebo simulation.

The package was rebuilt using:

```bash
cd ~/robotics_ws
colcon build --packages-select migro_core_001
source install/setup.bash
```

The executable was then verified with:

```bash
ros2 pkg executables migro_core_001
```

The successful result included:

```text
migro_core_001 distance_controller
migro_core_001 hello_migro
migro_core_001 listener
```

This confirmed that the controller remained correctly registered as a ROS 2 executable.

---

## Running MIGRO

The existing Gazebo simulation was launched using:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 launch migro_description gazebo.launch.py
```

The simulation and required controllers started successfully.

The proportional distance controller was then started using:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 run migro_core_001 distance_controller
```

The controller successfully began receiving odometry and publishing velocity commands.

---

## Proportional-Control Test

MIGRO was tested with the proportional distance controller.

The controller used:

```text
Target distance = 1.00 m
Kp = 0.8
Maximum speed = 0.20 m/s
Minimum speed = 0.03 m/s
```

The robot successfully moved toward the target using the updated controller.

The controller adjusted the commanded speed according to the remaining distance error and automatically stopped when the target distance was reached.

The test was successful.

---

## Comparing Day 47 and Day 48

The difference between the two controllers can be represented as follows.

### Day 47 – Fixed-Speed Closed Loop

```text
Distance
    ↓
Is target reached?
    ├── No → Fixed Speed
    └── Yes → Stop
```

### Day 48 – Proportional Closed Loop

```text
Distance
    ↓
Calculate Error
    ↓
Kp × Error
    ↓
Adjust Speed
    ↓
Apply Speed Limits
    ↓
Move
    ↓
Target Reached?
    ├── No → Continue
    └── Yes → Stop
```

Day 48 therefore introduced continuous control of the robot's velocity rather than only using distance as a stopping condition.

---

## Understanding Proportional Gain

The proportional gain determines how strongly the controller reacts to the current error.

The relationship is:

```text
speed = Kp × error
```

For the same error:

```text
Higher Kp
    ↓
Higher commanded speed
```

while:

```text
Lower Kp
    ↓
Lower commanded speed
```

For example:

```text
Error = 0.20 m
```

With:

```text
Kp = 0.5
```

the calculated speed is:

```text
0.10 m/s
```

With:

```text
Kp = 1.0
```

the calculated speed is:

```text
0.20 m/s
```

This demonstrates why controller tuning is important.

---

## Why This Matters for Robotics

Proportional control is a fundamental concept in robotics.

The general control pattern is:

```text
Desired State
      ↓
Current State
      ↓
Calculate Error
      ↓
Controller
      ↓
Command
      ↓
Robot
      ↓
Feedback
      ↺
```

The same principle can be applied to:

- Position control
- Velocity control
- Heading control
- Joint control
- Waypoint tracking
- Mobile robot navigation
- Path following

The Day 48 implementation is simple, but it introduces the fundamental relationship between error and control output.

---

## ROS 2 Concepts Practiced

### Parameters

The controller now uses configurable parameters for:

```text
target_distance
kp
max_speed
min_speed
```

### Subscribers

The controller continues subscribing to:

```text
/diff_drive_controller/odom
```

using:

```text
nav_msgs/msg/Odometry
```

### Publishers

The controller continues publishing:

```text
geometry_msgs/msg/TwistStamped
```

commands.

### Feedback

Odometry provides the current robot state required to calculate the control error.

### Control Logic

The node transforms the difference between the desired distance and current distance into a velocity command.

### Closed-Loop Control

The controller now follows:

```text
Desired Distance
      ↓
Current Distance
      ↓
Error
      ↓
Proportional Controller
      ↓
Velocity Command
      ↓
MIGRO
      ↓
Odometry
      ↺
```

---

## What Was Learned

Today's work reinforced several important robotics and control concepts:

* A controller can use the difference between a desired state and the current state to generate a control response.
* Proportional control produces an output based on the magnitude of the current error.
* Increasing proportional gain increases the response to a given error.
* Controller outputs can be limited using maximum and minimum bounds.
* Robot velocity can be dynamically adjusted using odometry feedback.
* A fixed-speed closed-loop controller can be upgraded into a proportional controller without changing the robot's hardware or simulation.
* ROS 2 parameters make controller behaviour configurable.
* The controller can continuously react to changes in the robot's measured state.
* Speed limiting is important when converting control error into physical movement commands.

---

## Day 48 Outcome

By the end of Day 48, MIGRO successfully had:

- ✅ Working Gazebo simulation
- ✅ Working differential-drive controller
- ✅ Working odometry feedback
- ✅ Working closed-loop distance controller
- ✅ Configurable target distance
- ✅ Configurable proportional gain
- ✅ Configurable maximum speed
- ✅ Configurable minimum speed
- ✅ Control-error calculation
- ✅ Proportional velocity calculation
- ✅ Maximum speed enforcement
- ✅ Minimum speed enforcement
- ✅ Automatic target detection
- ✅ Automatic stopping
- ✅ Successful package rebuild
- ✅ Successful executable verification
- ✅ Successful proportional-control test

---

## Updated MIGRO Architecture

After Day 48, the control architecture can be represented as:

```text
                 Desired Distance
                        ↓
                 Distance Error
                        ↓
                Proportional Control
                        ↓
                  Speed Limiting
                        ↓
                 TwistStamped
                        ↓
              diff_drive_controller
                        ↓
                     MIGRO
                        ↓
                    Odometry
                        ↓
              Current Distance
                        ↓
                  Distance Error
                        ↺
```

MIGRO has now progressed from simply using odometry to stop at a target toward using odometry to continuously influence its movement command.

---

## Engineering Significance

Day 47 established the basic closed-loop control pattern:

```text
Odometry
    ↓
Distance
    ↓
Control Decision
    ↓
Movement Command
    ↓
Robot
    ↓
Odometry
    ↺
```

Day 48 extended that architecture:

```text
Odometry
    ↓
Distance
    ↓
Error
    ↓
Proportional Controller
    ↓
Variable Velocity
    ↓
Robot
    ↓
Odometry
    ↺
```

This is an important progression because the controller is no longer simply asking:

```text
"Have I reached the target?"
```

It is now also asking:

```text
"How much should I move based on how far I am from the target?"
```

That distinction is an important step toward more sophisticated motion-control systems.

---

## Next Direction

The current controller uses:

```text
error = target_distance - current_distance
```

and:

```text
speed = Kp × error
```

The next progression can investigate controller tuning and more advanced motion control.

Possible future directions include:

```text
Proportional Distance Control
            ↓
Controller Tuning
            ↓
Heading Control
            ↓
Waypoint Navigation
            ↓
Position-Based Navigation
            ↓
Path Following
            ↓
Autonomous Navigation
```

Different `Kp` values can be tested to understand their effect on:

- Response speed
- Stability
- Overshoot
- Settling behaviour
- Positioning accuracy

This will provide a practical foundation for understanding more advanced controllers such as PID-based systems.

---

## Summary

Day 48 upgraded MIGRO's closed-loop distance controller from a fixed-speed controller into a basic proportional controller.

The controller now calculates the remaining distance to the target and uses that error to determine the robot's forward velocity.

The proportional relationship:

```text
speed = Kp × error
```

allows MIGRO to respond more strongly when it is far from the target and reduce its commanded speed as it approaches the target.

Maximum and minimum speed limits were also introduced to keep the commanded velocity within the configured operating range.

The updated controller was successfully rebuilt, verified as a ROS 2 executable, and tested in the Gazebo simulation.

The most important engineering lesson from Day 48 was that feedback can be used not only to determine **when a robot should stop**, but also to determine **how strongly the robot should respond while moving toward its objective**.

Day 48 therefore represents another step in MIGRO's progression from basic closed-loop movement toward more sophisticated autonomous control.
