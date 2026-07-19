# Day 16 – Dynamic ROS 2 Parameters

**Date:** July 16, 2026

---

## Objective

Learn how to modify ROS 2 Parameters while a node is running and understand how dynamic configuration improves robot flexibility.

---

## What I Built

- Built a Dynamic Parameter Node.
- Declared a configurable `robot_name` parameter.
- Created a timer that continuously reads the current parameter value.
- Successfully changed the parameter while the node was running.
- Verified that the node immediately reflected the updated value without restarting.

---

## Commands Used

Run the node:

```bash
ros2 run migro_parameters_001 dynamic_parameter_node
```

List available parameters:

```bash
ros2 param list
```

Read the current parameter:

```bash
ros2 param get /dynamic_parameter_node robot_name
```

Modify the parameter during runtime:

```bash
ros2 param set /dynamic_parameter_node robot_name Atlas
```

---

## Concepts Learned

Today I learned that ROS 2 Parameters can be modified while a node is actively running.

Unlike hard-coded variables, Parameters allow software behavior to change without stopping the node, rebuilding the package, or modifying the source code.

This enables robots to adapt to changing conditions in real time.

---

## Key Takeaways

- Parameters are not just variables; they are runtime configuration tools.
- Dynamic Parameters allow robots to change behavior while executing tasks.
- Nodes can continuously read updated parameter values.
- Parameters improve flexibility, maintainability, and scalability.

---

## Challenges

No major implementation issues occurred.

The main challenge was understanding how ROS continuously updates parameter values during node execution.

---

## Reflection

Watching the node immediately change from:

```
Robot Name: MIGRO
```

to

```
Robot Name: Atlas
```

without restarting the node was one of the biggest learning moments so far.

It demonstrated the power of runtime configuration and showed why Parameters are heavily used in professional robotics systems.

Today's lesson reinforced an important engineering principle:

**Robot behavior should be configurable without modifying source code whenever possible.**

---

## Next Steps

Tomorrow I will integrate Parameters into my ROS 2 Action Client, replacing keyboard input and making the application fully compatible with Launch Files.
