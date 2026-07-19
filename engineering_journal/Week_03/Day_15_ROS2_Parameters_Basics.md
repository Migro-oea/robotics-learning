# Day 15 – ROS 2 Parameters Basics

**Date:** July 15, 2026

---

## Objective

Learn how ROS 2 Parameters work and understand why they are preferred over hard-coded values for configuring robot behavior.

---

## What I Built

- Created a new ROS 2 Python package:
  - `migro_parameters_001`
- Built my first ROS 2 Parameter node.
- Declared a configurable parameter named `robot_name`.
- Retrieved the parameter value inside the node.
- Successfully changed the parameter from the terminal without modifying the source code.

---

## Commands Used

Create package:

```bash
ros2 pkg create --build-type ament_python migro_parameters_001
```

Run with default parameter:

```bash
ros2 run migro_parameters_001 parameter_node
```

Run with a custom parameter:

```bash
ros2 run migro_parameters_001 parameter_node --ros-args -p robot_name:=Atlas
```

---

## Concepts Learned

Today I learned that ROS 2 Parameters allow a node's behavior to be configured without changing its source code.

Instead of writing:

```python
robot_name = "MIGRO"
```

I declared a parameter:

```python
self.declare_parameter("robot_name", "MIGRO")
```

and retrieved its value using:

```python
self.get_parameter("robot_name").value
```

I also learned that parameter values can be overridden directly from the command line.

---

## Key Takeaways

- Parameters separate configuration from implementation.
- The same software can behave differently depending on parameter values.
- Parameters improve software reusability and maintainability.
- Professional ROS applications rely heavily on Parameters instead of hard-coded values.

---

## Challenges

No major issues occurred during today's practical.

The main challenge was understanding the purpose of Parameters rather than simply learning the syntax.

---

## Reflection

Today's lesson helped me understand why Launch Files and Parameters are commonly used together.

Previously, my Action Client relied on keyboard input using `input()`. I now understand that replacing user input with Parameters makes the node configurable and suitable for automated launches.

This reinforced an important software engineering principle:

**Configuration should be separated from code whenever possible.**

---

## Next Steps

Tomorrow I will continue learning ROS 2 Parameters by exploring runtime parameter changes and dynamic configuration before integrating Parameters into my Action project.
