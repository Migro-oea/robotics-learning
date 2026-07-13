# Day 14 – First ROS 2 Launch File

## Objective

Learn how ROS 2 Launch Files simplify the process of starting multiple nodes by creating a single launch script that automatically launches both the Action Server and Action Client.

---

# Concepts Learned

Today I learned that a ROS 2 Launch File is a Python script used to start one or more ROS nodes with a single command.

Instead of manually opening multiple terminals and running each node individually, a Launch File allows ROS to launch an entire application automatically.

The entry point of every Launch File is the `generate_launch_description()` function, which returns a `LaunchDescription` containing one or more `Node` actions.

---

# What I Built

### Created My First Launch File

I created my first ROS 2 Launch File:

```text
count_until.launch.py
```

The Launch File starts:

* CountUntil Action Server
* CountUntil Action Client

using a single command.

---

### Updated Package Installation

I modified the package's `setup.py` file to install the Launch File alongside the package so ROS 2 could locate it when using the `ros2 launch` command.

---

### Successfully Built the Package

After updating the package configuration, I rebuilt the package successfully using `colcon build` and sourced the workspace.

---

# Testing

I launched the application using:

```bash
ros2 launch migro_action_001 count_until.launch.py
```

The Action Server started successfully, confirming that the Launch File was correctly discovered and executed by ROS 2.

---

# Challenge Encountered

The Action Client did not continue as expected.

After investigating, I discovered that the client waits for keyboard input using Python's `input()` function.

Since Launch Files are designed to launch autonomous background processes rather than interactive programs, the client could not receive terminal input when launched automatically.

This helped me understand an important design principle in ROS 2.

---

# Key Concepts Understood

I learned that Launch Files are responsible for starting and coordinating nodes, but they are not intended for programs that depend on manual keyboard interaction.

This naturally introduced the need for ROS 2 Parameters.

Instead of requesting values using `input()`, professional ROS applications typically receive configuration values through Parameters or other ROS communication mechanisms.

This allows Launch Files to start complete robotic systems without requiring user interaction.

---

# Lessons Learned

* Launch Files reduce startup complexity by launching multiple nodes with one command.
* Every Launch File uses the `generate_launch_description()` function.
* The `Node` action defines which package and executable ROS should launch.
* Package installation must include the Launch File for ROS to discover it.
* Interactive nodes are not ideal for Launch Files.
* ROS 2 Parameters provide a better way to configure nodes than using Python's `input()`.

---

# Reflection

Although the Launch File did not fully automate the application because of the client's use of keyboard input, today's lesson helped me understand an important aspect of professional ROS software design.

Rather than seeing this as a failure, I now understand why Launch Files and Parameters are commonly used together in real robotic systems.

This experience also showed me that writing working code is only part of robotics software engineering; designing software that is scalable, configurable, and easy to deploy is equally important.

---

## Next Steps

Tomorrow I will learn ROS 2 Parameters and update the Action Client to receive configuration values without relying on keyboard input.

This will allow the Launch File to start the complete application automatically using a single command.

