# Day 10 – ROS 2 Action Goal Validation

## Objectives

* Improve the ROS 2 Action Client by allowing users to enter a custom target number.
* Implement goal validation using a goal callback.
* Learn how Action Servers decide whether to accept or reject incoming goals before execution.
* Understand how goal validation is applied in real-world robotics systems.

---

## What I Built

Today I enhanced my existing ROS 2 Action system by making it more dynamic and intelligent.

### Improvements Made

* Modified the Action Client to accept user input instead of using a hard-coded target number.
* Added a `goal_callback()` function to the Action Server.
* Configured the Action Server to validate every incoming goal before execution.
* Implemented goal rejection for invalid requests (negative target numbers).

This transformed my Action Server from simply executing every request to making decisions before starting a task.

---

## Workflow

```text
User Input
     │
     ▼
Action Client
     │
     ▼
Goal Request
     │
     ▼
Goal Callback
     │
 ┌───┴───────────┐
 │               │
 ▼               ▼
Accept        Reject
 │               │
 ▼               ▼
Execute      End Request
 │
 ▼
Feedback
 │
 ▼
Result
```

---

## Challenges Encountered

### Problem 1 – Indentation Error

**Error**

```
IndentationError: expected an indented block after function definition
```

**Cause**

While adding the `goal_callback()` function, I introduced an indentation error. Since Python uses indentation to define code blocks, the interpreter could not execute the file.

**Solution**

I replaced the affected section with a properly formatted implementation and rebuilt the package.

---

### Problem 2 – Goal Validation

Initially, the Action Server accepted every goal, including invalid values.

**Solution**

I implemented a goal callback that checks whether the requested target number is negative.

If the goal is valid:

* `GoalResponse.ACCEPT`

If the goal is invalid:

* `GoalResponse.REJECT`

---

## Testing

### Test 1

**Input**

```
Count Until: 5
```

**Result**

* Goal accepted
* Feedback published from 0 to 5
* Action completed successfully

---

### Test 2

**Input**

```
Count Until: -5
```

**Result**

* Goal rejected
* Execution never started
* Server displayed a warning indicating that negative goals are invalid

---

## Lessons Learned

Today I learned several important concepts about ROS 2 Actions.

* `goal_callback()` executes before `execute_callback()`.
* The Action Server can validate requests before beginning execution.
* `GoalResponse.ACCEPT` allows the Action Server to execute a task.
* `GoalResponse.REJECT` prevents execution entirely.
* User input makes software significantly more reusable than hard-coded values.
* Goal validation is an essential part of designing safe and reliable robotic systems.

---

## Real-World Reflection

Although today's project validates a simple counting task, the same principle is used in real robotics applications.

Examples include:

* Rejecting navigation goals outside a robot's mapped environment.
* Rejecting manipulation requests when an object cannot be reached.
* Rejecting tasks when the robot's battery level is too low.
* Rejecting unsafe or impossible commands before execution.

Today's implementation introduced me to one of the key safety mechanisms used in professional robotics software.

---

## Personal Reflection

Today's lesson helped me understand that robotics software is not just about executing commands—it is also about making intelligent decisions before acting.

By adding goal validation, I made my Action Server behave more like a real robotic system rather than a simple demonstration program.

This experience reinforced the importance of designing software that is robust, reusable, and capable of handling invalid requests gracefully.

