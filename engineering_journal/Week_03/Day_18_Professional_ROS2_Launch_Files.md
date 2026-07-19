# Day 18 – Professional ROS 2 Launch Files

**Date:** July 18, 2026

---

## Objective

Learn how to automate the startup of multiple ROS 2 nodes using Launch Files and configure node parameters during launch.

---

## What I Built

- Created a professional ROS 2 Launch File for the Action package.
- Configured the Launch File to start both the Action Server and Action Client automatically.
- Passed the `target_number` parameter directly from the Launch File to the Action Client.
- Updated `setup.py` to install the Launch File correctly with the package.
- Successfully launched the complete Action system using a single command.

---

## Commands Used

Build the package:

```bash
colcon build --packages-select migro_action_001

source install/setup.bash
```

Launch the complete system:

```bash
ros2 launch migro_action_001 count_until.launch.py
```

---

## Concepts Learned

Today I learned that Launch Files allow multiple ROS 2 nodes to be started together using a single command.

Instead of manually opening multiple terminals and launching each node individually, the Launch File coordinates the startup sequence automatically.

I also learned that Launch Files can pass Parameters directly to nodes during startup, making applications easier to configure and deploy.

---

## Key Takeaways

- Launch Files automate node startup.
- One Launch File can start multiple ROS nodes simultaneously.
- Parameters can be supplied directly from Launch Files.
- Launch Files improve scalability and reduce deployment errors.
- Launch Files must be installed through `setup.py` before ROS can discover them.

---

## Challenges

Initially, ROS reported:

```
file 'action.launch.py' was not found
```

I traced the issue to the package installation process and corrected the Launch File installation in `setup.py`.

After rebuilding the package, the Launch File executed successfully.

---

## Reflection

Today's lesson made my project feel much closer to a professional robotics application.

Previously I needed multiple terminals to start my Action Server and Action Client.

Now, the complete system starts automatically using one command.

This experience reinforced the importance of automation and proper software organization in robotics engineering.

---

## Next Steps

Tomorrow I will learn Launch Arguments so the Launch File itself can be configured from the command line without modifying the source code.
