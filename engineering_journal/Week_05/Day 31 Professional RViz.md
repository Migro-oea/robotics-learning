# Day 31 – Professional RViz Launch System

**Date:** 31 July 2026

## Objective

Improve the MIGRO visualization workflow by creating a professional launch system that automatically loads the robot model and RViz configuration without requiring manual setup.

---

## Activities Completed

- Created a custom RViz configuration file (`migro.rviz`) for the MIGRO robot.
- Saved the RViz layout inside the `rviz` directory of the `migro_description` package.
- Updated `display.launch.py` to automatically load the saved RViz configuration during launch.
- Improved the package structure to follow standard ROS 2 conventions.
- Updated `setup.py` to automatically install:
  - Launch files
  - URDF files
  - RViz configuration files
  - Mesh directory
- Used `glob()` to make the installation process scalable for future files.
- Rebuilt the `migro_description` package using `colcon build`.
- Sourced the updated workspace.
- Successfully launched MIGRO using a single launch command.
- Verified that RViz now:
  - Opens automatically
  - Loads the saved layout
  - Displays the robot without manual configuration
  - Loads the TF tree correctly
  - Uses the saved RViz settings

---

## Commands Practiced

```bash
colcon build --packages-select migro_description

source install/setup.bash

ros2 launch migro_description display.launch.py
```

---

## Key Lessons Learned

- Professional ROS packages should automatically configure RViz through launch files.
- RViz layouts can be saved and reused using `.rviz` configuration files.
- The `setup.py` file determines which resources are installed with a package.
- Using Python's `glob()` function allows launch files, URDFs, RViz configurations, and meshes to be installed automatically without modifying `setup.py` every time new files are added.
- Separating launch files, robot descriptions, RViz configurations, and meshes results in a cleaner and more maintainable package structure.
- A professional launch system improves development speed by eliminating repetitive manual configuration.

---

## Challenges Encountered

- Understanding how ROS installs package resources during the build process.
- Ensuring that the RViz configuration was copied into the installed package.
- Updating the launch file so that RViz automatically loads the correct configuration.

---

## Outcome

MIGRO can now be launched with a single command while automatically loading the robot model and RViz configuration. The visualization workflow now follows professional ROS 2 development practices and provides a solid foundation for future Xacro conversion and Gazebo simulation.

---

## Next Steps

- Convert the robot description from URDF to Xacro.
- Modularize the robot description using reusable macros.
- Prepare MIGRO for Gazebo simulation.
- Begin implementing differential-drive robot modelling.
