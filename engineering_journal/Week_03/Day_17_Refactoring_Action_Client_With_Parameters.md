# Day 17 – Refactoring the ROS 2 Action Client with Parameters

**Date:** July 17, 2026

---

## Objective

Refactor the ROS 2 Action Client by replacing manual keyboard input with configurable ROS 2 Parameters, making the node suitable for automated execution and Launch Files.

---

## What I Built

- Removed the use of Python's `input()` function from the Action Client.
- Declared a configurable parameter named `target_number`.
- Retrieved the parameter value using the ROS 2 Parameter API.
- Added logging to display the target number before sending the goal.
- Successfully sent goals using both the default parameter value and a custom parameter supplied from the command line.

---

## Commands Used

Run with the default parameter:

```bash
ros2 run migro_action_001 count_until_action_client
```

Run with a custom parameter:

```bash
ros2 run migro_action_001 count_until_action_client --ros-args -p target_number:=12
```

---

## Concepts Learned

Today I learned that ROS 2 Parameters can be used to configure Action Clients without relying on keyboard input.

Instead of asking the user for a value using:

```python
target = int(input("Count Until: "))
```

I replaced it with:

```python
self.declare_parameter("target_number", 5)

target = self.get_parameter("target_number").value
```

This makes the Action Client configurable, reusable, and compatible with Launch Files.

---

## Key Takeaways

- Parameters are a better alternative to manual user input.
- Launch Files work best with configurable nodes.
- Production ROS applications avoid interactive terminal input.
- Parameters improve automation and scalability.

---

## Challenges

No major implementation issues occurred.

The main challenge was understanding how to redesign an Action Client to use Parameters instead of keyboard input while preserving the existing Action workflow.

---

## Reflection

Today's lesson connected several ROS concepts together.

Topics taught me continuous communication.

Services taught me request-response communication.

Actions introduced long-running tasks.

Today I learned how Parameters allow these nodes to become configurable without changing their source code.

This made the Action Client feel much closer to what would be used in a real robotics application.

---

## Next Steps

Tomorrow I will integrate Parameters into ROS 2 Launch Files so both the Action Server and Action Client can be started automatically with predefined configuration values.
