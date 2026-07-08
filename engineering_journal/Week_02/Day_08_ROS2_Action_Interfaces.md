# Day 08 – ROS 2 Action Interfaces

**Date:** July 8, 2026

## Objective

Today I learned how ROS 2 Actions are structured and created my first custom Action interface.

## Topics Covered

- ROS 2 Actions
- Goal, Feedback, and Result
- Custom `.action` files
- Interface packages
- `ament_cmake`
- Action generation pipeline

## Practical Work

- Created the `migro_interfaces` package.
- Added a custom `CountUntil.action` file.
- Updated `package.xml`.
- Updated `CMakeLists.txt`.
- Built the package using `colcon build`.
- Verified the generated Python classes.

## Key Concepts Learned

### Goal
Defines what the client wants the server to accomplish.

### Feedback
Provides progress updates while the action is running.

### Result
Returns the final outcome after the action completes.

## Why use a separate interface package?

Separating interfaces from implementation promotes:

- Reusability
- Decoupling
- Cleaner software architecture

## Reflection

Today helped me understand that Actions are more than just another ROS communication method—they combine long-running execution with continuous feedback and a final result. I also learned why professional ROS projects keep interfaces in their own package.

## Next Steps

- Create `migro_action_001`
- Build the Action Server
- Build the Action Client
- Execute my first custom Action