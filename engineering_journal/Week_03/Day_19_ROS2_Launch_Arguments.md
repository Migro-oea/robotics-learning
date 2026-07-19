# Day 19 – ROS 2 Launch Arguments

**Date:** July 19, 2026

---

## Objective

Learn how to make ROS 2 Launch Files configurable using Launch Arguments, allowing the same Launch File to be reused with different parameter values.

---

## What I Built

- Modified the existing Launch File to support Launch Arguments.
- Declared a launch argument named `target_number`.
- Connected the Launch Argument to the Action Client parameter.
- Successfully launched the Action Server and Action Client using different target values without modifying any source code.
- Verified that the Action Client received the parameter value supplied from the command line.

---

## Commands Used

Launch with the default value:

```bash
ros2 launch migro_action_001 count_until.launch.py
```

Launch with a custom value:

```bash
ros2 launch migro_action_001 count_until.launch.py target_number:=25
```

---

## Concepts Learned

Today I learned how Launch Arguments make Launch Files reusable.

Instead of editing the Launch File every time a different parameter is needed, Launch Arguments allow configuration values to be supplied directly from the command line.

This makes deployment much more flexible and scalable.

---

## Key Takeaways

- Launch Arguments make Launch Files reusable.
- Parameters can receive values directly from Launch Arguments.
- The same Launch File can support many different robot configurations.
- Launch Arguments reduce code duplication and improve maintainability.

---

## Challenges

No major implementation issues occurred.

The primary learning challenge was understanding the relationship between:

- Launch Arguments
- Launch Configuration
- ROS Parameters

Once these concepts were connected, the overall launch process became much clearer.

---

## Reflection

Today's lesson showed me how professional robotics applications avoid hard-coded configuration values.

Rather than editing Python files for every new robot configuration, Launch Arguments allow software behavior to change at startup while keeping the application itself unchanged.

This approach improves scalability and makes ROS applications easier to deploy across multiple robots.

---

## Next Steps

Tomorrow I will complete the Parameters and Launch Files module by building a small integration project that combines Actions, Parameters, Launch Files, and Launch Arguments into a single ROS 2 application.
