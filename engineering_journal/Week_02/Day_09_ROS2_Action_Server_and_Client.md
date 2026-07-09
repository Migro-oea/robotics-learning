# Day 09 – ROS 2 Action Server and Client

## Objectives

- Build a complete ROS 2 Action Server.
- Build a complete ROS 2 Action Client.
- Exchange Goals, Feedback and Results.
- Understand how Actions are used in real robotics systems.

---

## What I Built

Today I successfully implemented my first complete ROS 2 Action system.

The system consists of:

- A custom Action interface
- An Action Server
- An Action Client

The client sends a Goal to the server.

The server executes the task while continuously sending Feedback.

When execution finishes, the server returns a Result to the client.

---

## Workflow

Client

↓

Send Goal

↓

Server executes task

↓

Server sends Feedback

↓

Server returns Result

---

## Challenges Encountered

### Problem 1

The client executable could not be found.

Cause:

The executable had not been installed after updating `setup.py`.

Solution:

I performed a clean rebuild of the package using `colcon build` and sourced the workspace again.

---

### Problem 2

The server crashed with:

AttributeError:

CountUntil_Result has no attribute reached_number

Cause:

My Python code expected a field named `reached_number`, but my custom Action definition only contained:

- success
- message

Solution:

I updated both the Action Server and Action Client to use the correct fields defined inside the `.action` file.

---

## Lessons Learned

Today taught me several important concepts.

- The `.action` file acts as the communication contract between the Action Client and Action Server.

- Every field used inside Python must exist inside the Action definition.

- Actions are ideal for long-running tasks.

- Feedback allows progress to be monitored during execution.

- Client and Server are completely independent ROS nodes.

---

## Real World Reflection

Although today's example counted from 0 to 10, I now understand that the counting itself is not important.

The Action architecture is what matters.

The exact same structure could be used for:

- Robot Navigation
- Warehouse Robots
- Drone Missions
- Robotic Arms
- Autonomous Delivery Robots
- MIGRO in the future

Only the work performed by the server changes.

The communication pattern remains the same.

---

## Personal Reflection

Today was one of the most satisfying days since I started learning ROS.

The project initially failed due to interface mismatches, but debugging the problem taught me far more than if everything had worked on the first attempt.

I now have a much clearer understanding of how Action communication works inside ROS 2.