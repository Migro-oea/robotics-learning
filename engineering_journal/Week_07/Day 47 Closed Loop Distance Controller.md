# Day 47 – Closed-Loop Distance Controller

**Date:** 17 August 2026

## Objective

Build the first closed-loop movement controller for MIGRO.

The objective was to move beyond simply monitoring MIGRO's odometry and use that feedback to control the robot's movement.

A new ROS 2 node called `distance_controller` was created inside the existing `migro_core_001` package.

The controller commands MIGRO to move forward until the robot has travelled a specified displacement from its starting position, at which point it automatically stops.

The target distance for today's test was:

```text
1.00 metre
```

This introduced the fundamental closed-loop control pattern:

```text
Command
   ↓
Robot Movement
   ↓
Odometry Feedback
   ↓
Distance Calculation
   ↓
Control Decision
   ↓
New Command
   ↺
```

---

## Starting Point

At the beginning of Day 47, MIGRO already had a functional differential-drive simulation and odometry system.

The existing architecture consisted of:

```text
MIGRO
  ↓
Gazebo
  ↓
diff_drive_controller
  ↓
/diff_drive_controller/odom
```

Day 45 introduced odometry monitoring, while Day 46 extended that system to calculate MIGRO's displacement from its starting position.

However, the calculated distance was only being reported.

The robot still depended on an external command to determine when it should stop.

The objective of Day 47 was therefore to use the same odometry information as **feedback for an actual controller**.

---

## Why Closed-Loop Control Was Needed

A simple robot movement command could instruct MIGRO to move forward at a fixed speed for a fixed amount of time.

For example:

```text
Move forward
for 5 seconds
```

However, this is an open-loop approach.

The controller does not know whether MIGRO actually travelled the desired distance.

Changes in:

* Simulation conditions
* Robot speed
* Wheel behaviour
* Controller response
* Starting conditions

could affect the final position.

A better approach is to continuously observe the robot's state and use that information to determine whether the objective has been achieved.

Therefore, instead of:

```text
Move for a fixed amount of time
        ↓
Stop
```

MIGRO now uses:

```text
Move
 ↓
Measure position
 ↓
Calculate displacement
 ↓
Is target reached?
 ├── No → Continue
 └── Yes → Stop
```

This is the foundation of closed-loop control.

---

## Controller Architecture

The new architecture is:

```text
                 ┌─────────────────────┐
                 │   Distance Goal     │
                 │      1.00 m         │
                 └──────────┬──────────┘
                            ↓
                  distance_controller
                            ↓
                       TwistStamped
                            ↓
                 diff_drive_controller
                            ↓
                         MIGRO
                            ↓
                         Odometry
                            │
                            └──────────────→
                              Feedback
```

The controller continuously receives odometry information and compares MIGRO's current position against the position recorded when the controller started.

---

## Creating the Distance Controller

The new node was created inside the existing:

```text
migro_core_001
```

package.

No new ROS 2 package was created because the existing package already provides a suitable location for basic robot-control nodes.

The new file is:

```text
migro_core_001/
├── __init__.py
├── hello_migro.py
├── listener.py
└── distance_controller.py
```

This keeps the project structure simple while allowing the controller to build upon the ROS 2 concepts already implemented.

---

## Controller Inputs and Outputs

The controller uses two important pieces of information.

### Input

Odometry from:

```text
/diff_drive_controller/odom
```

with message type:

```text
nav_msgs/msg/Odometry
```

### Output

Velocity commands using:

```text
geometry_msgs/msg/TwistStamped
```

The commands are sent to the differential-drive controller.

The forward movement command sets:

```text
linear.x > 0
```

while:

```text
angular.z = 0
```

keeps the robot travelling straight.

When the target is reached, both velocities are set to zero.

---

## Recording the Starting Position

When the controller begins, it records MIGRO's current position.

The starting position is represented by:

```text
start_x
start_y
```

This position becomes the reference point for the controller.

The robot does not need to start at the world origin.

For example, if MIGRO begins at:

```text
x₀ = 1.0 m
y₀ = 0.0 m
```

and later reaches:

```text
x = 2.0 m
y = 0.0 m
```

its displacement is approximately:

```text
1.0 m
```

rather than 2.0 m.

This allows the controller to operate relative to the robot's starting position.

---

## Calculating Displacement

The same displacement calculation developed during Day 46 was reused.

The change in position is:

```text
Δx = x - x₀
Δy = y - y₀
```

The displacement magnitude is calculated using:

```text
distance = √(Δx² + Δy²)
```

In Python:

```python
dx = x - self.start_x
dy = y - self.start_y

distance = math.sqrt(
    dx ** 2 + dy ** 2
)
```

The resulting value represents the robot's straight-line displacement from the controller's starting position.

---

## Target Detection

The controller was configured with a target distance:

```text
1.00 m
```

Each time a new odometry message is received, the calculated distance is compared with the target.

The decision logic is:

```text
distance < target
      ↓
Continue moving
```

or:

```text
distance >= target
      ↓
Stop robot
```

This means that the robot does not rely on a predetermined movement duration.

Instead, the robot's measured state determines when the movement should end.

---

## Moving MIGRO Forward

While the target has not been reached, the controller publishes a forward velocity command.

The important velocity values are:

```text
linear.x = forward speed
angular.z = 0.0
```

This instructs the differential-drive controller to move MIGRO forward without intentionally rotating.

The controller also reports the current progress.

Conceptually, the output follows:

```text
Moving... 0.00 / 1.00 m
Moving... 0.05 / 1.00 m
Moving... 0.20 / 1.00 m
...
Moving... 0.95 / 1.00 m
```

---

## Automatically Stopping MIGRO

When the calculated displacement reaches the target, the controller publishes a zero-velocity command.

The stop command contains:

```text
linear.x = 0.0
angular.z = 0.0
```

The controller then marks the movement as finished and reports that the target has been reached.

The expected behaviour is:

```text
Target reached! Distance: ~1.00 m
```

This prevents the robot from continuing to move after reaching its objective.

---

## Adding the ROS 2 Executable

The new controller was added to the existing `setup.py` entry points.

The package originally contained executables for:

```text
hello_migro
listener
```

The new executable was added:

```text
distance_controller = migro_core_001.distance_controller:main
```

The final executable list therefore contains:

```text
hello_migro
listener
distance_controller
```

No existing executables were removed.

---

## Building the Package

The updated package was rebuilt using:

```bash
cd ~/robotics_ws
colcon build --packages-select migro_core_001
source install/setup.bash
```

The package built successfully.

The available executables were then checked with:

```bash
ros2 pkg executables migro_core_001
```

The result confirmed:

```text
migro_core_001 distance_controller
migro_core_001 hello_migro
migro_core_001 listener
```

This verified that the new controller was correctly registered with ROS 2.

---

## Launching MIGRO

MIGRO was launched using the existing Gazebo simulation:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 launch migro_description gazebo.launch.py
```

The simulation loaded successfully and the required controllers became active.

---

## Running the Distance Controller

The controller was then started in a separate terminal:

```bash
cd ~/robotics_ws
source install/setup.bash
ros2 run migro_core_001 distance_controller
```

The controller successfully began monitoring MIGRO's odometry and publishing movement commands.

---

## Closed-Loop Movement Test

The controller was tested with a target distance of:

```text
1.00 m
```

MIGRO began moving forward.

Unlike the previous keyboard teleoperation tests, no manual stop command was required.

The controller continuously calculated MIGRO's displacement and compared it with the target.

Once the target was reached, the controller automatically published a zero-velocity command.

The observed behaviour was:

```text
Controller starts
      ↓
Starting position recorded
      ↓
MIGRO moves forward
      ↓
Odometry updates
      ↓
Distance increases
      ↓
Distance reaches target
      ↓
Zero velocity published
      ↓
MIGRO stops automatically
```

This confirmed that the closed-loop control system was functioning correctly.

---

## Verifying the Odometry Topic

An initial attempt was made to inspect:

```text
/odom
```

However, ROS 2 reported that this topic was not being published.

The available topics were then inspected using:

```bash
ros2 topic list | grep -E "odom|joint|tf"
```

The result included:

```text
/diff_drive_controller/odom
/dynamic_joint_states
/joint_state_broadcaster/transition_event
/joint_states
/tf
/tf_static
```

This confirmed that MIGRO's odometry was being published through:

```text
/diff_drive_controller/odom
```

rather than the generic `/odom` topic.

---

## Verifying the Odometry Message

The correct topic was inspected using:

```bash
ros2 topic echo /diff_drive_controller/odom --once
```

The message was successfully received.

Important fields included:

```text
header:
  frame_id: odom

child_frame_id: base_link
```

The odometry also contained position information:

```text
position:
  x: ...
  y: ...
  z: 0.0
```

and velocity information:

```text
linear:
  x: ...
```

The final observed velocity was effectively zero:

```text
linear.x ≈ 0
angular.z ≈ 0
```

This was consistent with MIGRO having stopped after reaching its target.

---

## Understanding the Feedback Loop

The most important concept introduced today was the feedback loop.

The controller does not simply send a command and assume that MIGRO followed it.

Instead:

```text
Controller
    ↓
Velocity Command
    ↓
MIGRO
    ↓
Odometry
    ↓
Controller
```

The robot's measured state returns to the controller.

The controller then uses this information to determine whether another movement command is required.

This is fundamentally different from a purely open-loop system.

---

## Open-Loop vs Closed-Loop Control

### Open-Loop

An open-loop controller might behave like:

```text
Command forward velocity
        ↓
Wait 5 seconds
        ↓
Stop
```

The controller does not verify how far the robot actually travelled.

### Closed-Loop

The new controller behaves like:

```text
Command forward velocity
        ↓
Read odometry
        ↓
Calculate displacement
        ↓
Compare against target
        ↓
Target reached?
   ├── No → Continue
   └── Yes → Stop
```

The second approach uses feedback to determine the next action.

This pattern is fundamental to autonomous robotics.

---

## Important Engineering Limitation

Today's controller is a **basic closed-loop distance controller**, not yet a sophisticated feedback controller such as a PID controller.

The controller currently uses the measured distance primarily as a stopping condition.

It does not continuously adjust the forward velocity based on the size of the distance error.

For example, it does not yet implement:

```text
error = target_distance - current_distance
```

followed by proportional velocity control.

That will be a natural future improvement.

---

## Why This Matters for Robotics

Closed-loop control is one of the foundations of autonomous robotic systems.

A robot cannot reliably perform useful autonomous behaviours by simply issuing commands.

It needs to:

1. Observe its state.
2. Compare its current state with a desired state.
3. Determine whether an objective has been achieved.
4. Take an appropriate action.
5. Observe the result.
6. Repeat the process.

Today's implementation demonstrates this principle in a simple form.

The desired state is:

```text
Displacement = 1.00 m
```

The observed state comes from:

```text
/diff_drive_controller/odom
```

The controller compares the two and decides whether MIGRO should continue moving or stop.

---

## Updated MIGRO Architecture

After Day 47, MIGRO's basic control architecture can be represented as:

```text
                 Desired State
                    1.00 m
                      ↓
              Distance Controller
                      ↓
                TwistStamped
                      ↓
            diff_drive_controller
                      ↓
                  MIGRO
                      ↓
                  Odometry
                      ↓
       /diff_drive_controller/odom
                      ↓
              Distance Calculation
                      │
                      └──────────────→
                            Feedback
```

This is the first clear implementation of a feedback-controlled behaviour in MIGRO.

---

## ROS 2 Concepts Practiced

### Nodes

A new ROS 2 node called:

```text
distance_controller
```

was created.

### Publishers

The node publishes:

```text
geometry_msgs/msg/TwistStamped
```

commands to control MIGRO's movement.

### Subscribers

The node subscribes to:

```text
/diff_drive_controller/odom
```

to receive robot-state feedback.

### Odometry

The controller uses:

```text
nav_msgs/msg/Odometry
```

to obtain MIGRO's estimated position.

### Feedback

Odometry provides the feedback required for the controller to make movement decisions.

### Control Logic

The node compares measured displacement with a desired target and changes its output accordingly.

### Package Executables

The new node was registered as a ROS 2 executable through `setup.py`.

---

## What Was Learned

Today's work reinforced several important robotics concepts:

* A robot controller can use odometry as feedback.
* Robot movement can be controlled using measured state rather than time alone.
* Displacement can be used as a simple control objective.
* ROS 2 subscribers can provide feedback to a control node.
* ROS 2 publishers can provide movement commands.
* A controller can automatically stop a robot when a target condition is satisfied.
* Closed-loop systems continuously connect robot actions with robot-state measurements.
* The correct ROS topic must be identified rather than assuming a generic topic name.
* `nav_msgs/msg/Odometry` provides both position and velocity information.
* A basic closed-loop controller provides a foundation for more advanced control algorithms.

---

## Day 47 Outcome

By the end of Day 47, MIGRO successfully had:

* ✅ A new `distance_controller` ROS 2 node
* ✅ A configurable target distance
* ✅ Starting-position tracking
* ✅ Odometry feedback
* ✅ Displacement calculation
* ✅ Forward velocity control
* ✅ Automatic stopping
* ✅ `TwistStamped` command publishing
* ✅ Successful package build
* ✅ Successful executable registration
* ✅ Successful Gazebo integration
* ✅ Successful 1-metre movement test
* ✅ Automatic stopping after reaching the target
* ✅ Verified `/diff_drive_controller/odom` feedback
* ✅ Confirmed near-zero velocity after stopping

---

## Engineering Significance

Day 46 transformed odometry into useful information:

```text
Odometry
    ↓
Distance Calculation
    ↓
Reported Robot State
```

Day 47 took the next step:

```text
Odometry
    ↓
Distance Calculation
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

This is a major conceptual transition in MIGRO's development.

The robot is no longer simply being commanded and observed.

It is beginning to **observe its own state and use that state to determine its behaviour**.

This is the foundation upon which more advanced autonomous behaviours can be built.

---

## Next Direction

The current controller uses a simple target-reached condition:

```text
distance >= target
        ↓
STOP
```

A natural next step is to introduce a proper control error:

```text
error = target_distance - current_distance
```

and use that error to influence the robot's velocity.

This can eventually lead to:

```text
Target
  ↓
Error Calculation
  ↓
Controller
  ↓
Velocity Command
  ↓
Robot
  ↓
Odometry
  ↺
```

More advanced control techniques such as proportional or PID control can then be explored.

This progression will move MIGRO from basic threshold-based control toward more robust robotic motion control.

---

## Summary

Day 47 marked MIGRO's first successful closed-loop movement controller.

A new `distance_controller` node was added to the existing `migro_core_001` package. The controller records MIGRO's starting position, receives odometry from `/diff_drive_controller/odom`, calculates displacement, and commands the robot to move forward until the specified target distance is reached.

The controller was successfully built, registered as a ROS 2 executable, launched in Gazebo, and tested.

MIGRO moved approximately one metre and then stopped automatically without requiring manual intervention.

The most important engineering lesson from today was the difference between commanding a robot and **controlling a robot using feedback**.

Day 47 therefore represents an important milestone in MIGRO's progression toward autonomous robotic behaviour.

