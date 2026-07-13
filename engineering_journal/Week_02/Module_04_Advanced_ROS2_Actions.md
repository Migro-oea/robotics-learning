# Module 04 – Advanced ROS 2 Actions

## Objective

Complete the ROS 2 Actions module by building a fully functional Action Server and Action Client capable of:

* Accepting and rejecting goals
* Publishing feedback
* Returning results
* Handling goal cancellation
* Understanding how Actions are used in real robotic systems

---

# Concepts Learned

During this module I learned the complete lifecycle of a ROS 2 Action.

An Action follows this sequence:

1. Client sends a goal.
2. Server validates the goal.
3. Goal is accepted or rejected.
4. Server executes the long-running task.
5. Feedback is continuously published.
6. Client can request cancellation at any time.
7. Server returns a final result.

I also learned that an Action may finish in three different ways:

* **Succeeded** – The task completed successfully.
* **Cancelled** – The task was intentionally stopped.
* **Aborted** – The task failed unexpectedly.

---

# What I Built

### Goal Validation

Implemented a `goal_callback()` to validate incoming requests before execution.

The Action Server now rejects invalid goals, such as negative target numbers.

---

### Goal Cancellation

Implemented a `cancel_callback()` to accept cancellation requests from the client.

The server continuously checks whether cancellation has been requested during execution and stops safely when necessary.

---

### Action Client Improvements

Updated the Action Client to:

* Accept user input instead of using a hard-coded value.
* Receive continuous feedback from the server.
* Automatically request cancellation after a short delay.
* Display the final Action result.

---

# Testing

## Valid Goal

Input:

```text
20
```

Result:

* Goal accepted
* Feedback published continuously
* Client requested cancellation
* Server stopped execution safely
* Cancellation result returned successfully

---

## Invalid Goal

Input:

```text
-5
```

Result:

* Goal rejected
* Execution never started
* Warning displayed on the server

---

# Key Concepts Understood

I now understand the responsibilities of each callback.

### goal_callback()

Determines whether the Action Server should accept or reject an incoming goal.

### execute_callback()

Executes the long-running task after a goal has been accepted.

### cancel_callback()

Handles cancellation requests and allows the Action Server to stop execution safely.

Separating these callbacks keeps the Action Server responsive and easier to maintain.

---

# Real-World Applications

I learned that the same Action architecture is used in real robotic systems.

Examples include:

* Autonomous Mobile Robots (AMRs)
* Warehouse robots
* Robot manipulators
* Delivery robots
* Autonomous vehicles

In these systems, Actions are commonly used for navigation, manipulation, package delivery, docking, inspection, and other long-running tasks.

---

# Lessons Learned

* Topics are designed for continuous communication.
* Services are designed for quick request-response interactions.
* Actions are designed for long-running tasks that require feedback and cancellation.

I also learned that not every robot manages multiple goals the same way.

Depending on the application, a robot may:

* Reject new goals
* Queue goals
* Cancel the current goal and execute a higher-priority task
* Execute multiple goals concurrently

The chosen strategy depends on the robot's hardware capabilities and mission requirements.

---

# Reflection

This module helped me understand why ROS 2 provides three communication mechanisms instead of one.

Before this module, Actions felt like a more complicated version of Services.

After implementing goal validation, feedback, cancellation, and studying real-world robotics examples, I now understand that Actions solve a completely different class of problems.

Completing this module has given me a much deeper appreciation of how professional robotic systems manage long-running tasks safely and efficiently.

---

## Next Module

**Module 05 – ROS 2 Launch Files**

The next step is to learn how to launch multiple ROS nodes together using launch files, making robotics applications easier to deploy and manage.
