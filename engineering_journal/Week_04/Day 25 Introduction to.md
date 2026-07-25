# Day 25 – Introduction to URDF (Unified Robot Description Format)

**Date:** 25 July 2026

---

# Objective

To understand the fundamentals of URDF (Unified Robot Description Format), learn how robots are represented in ROS 2, distinguish between links and joints, and create the first robot description for MIGRO.

---

# Activities Performed

- Studied the purpose of URDF and why every robot requires a robot description before visualization or simulation.
- Learned that URDF is an XML-based format used to describe a robot's physical structure.
- Understood the relationship between **TF2** and **URDF**:
  - URDF describes **what** the robot is.
  - TF2 describes **where** each robot component is.
- Learned the concept of a **Link**, representing a rigid physical part of a robot.
- Learned the concept of a **Joint**, representing the connection between two links.
- Studied the three most common joint types:
  - Fixed Joint
  - Revolute Joint
  - Prismatic Joint
- Discussed practical examples of each joint type:
  - Camera mounted on a robot (Fixed)
  - Robot elbow (Revolute)
  - Telescopic arm or forklift mechanism (Prismatic)
- Created a new ROS 2 package named:

```text
migro_description
```

- Created the standard directory structure for robot description packages:

```text
launch/
meshes/
rviz/
urdf/
```

- Created the first robot description file:

```text
urdf/migro.urdf
```

- Added the robot declaration:

```xml
<robot name="migro">
```

- Created the first robot link:

```xml
<link name="base_link"/>
```

- Added the first sensor link:

```xml
<link name="camera_link"/>
```

- Connected both links using a **Fixed Joint**.

- Learned the purpose of the `<origin>` tag and how it specifies the position and orientation of a child link relative to its parent.

- Understood that:

```xml
<origin xyz="0 0 0.5"/>
```

places the camera **0.5 meters above** the robot base.

- Compared URDF positioning with the TF2 transforms implemented in previous lessons.

---

# Challenges Encountered

Initially misunderstood the purpose of `base_link`, assuming it was a container holding all other robot components instead of being a physical rigid body itself.

---

# Solutions Applied

Clarified that every physical component of a robot is represented by its own **Link**, while **Joints** connect links together. Understood that `base_link` represents the robot's chassis rather than a container for other links.

---

# Knowledge Gained

Today I learned that URDF serves as the blueprint of a robot by defining every physical component and the joints connecting them. I now understand the difference between Links and Joints, the purpose of Fixed, Revolute, and Prismatic joints, and how URDF complements TF2 by describing the robot's physical structure while TF2 manages coordinate transformations during runtime.

---

# Files Created

```text
migro_description/
├── launch/
├── meshes/
├── rviz/
├── urdf/
│   └── migro.urdf
├── package.xml
├── setup.py
└── setup.cfg
```

---

# Key Concepts Learned

- URDF
- Robot Description
- XML
- Link
- Joint
- Fixed Joint
- Revolute Joint
- Prismatic Joint
- Parent Link
- Child Link
- Origin
- Robot Hierarchy
- Robot Kinematics
- Physical Robot Structure

---

# Reflection

Today's lesson marked the beginning of robot modeling. I learned that every robot is built from rigid bodies called Links connected by Joints, and that URDF provides the blueprint describing this structure before the robot can be visualized or simulated. Understanding this relationship between URDF and TF2 has strengthened my understanding of how ROS 2 represents both the physical structure and spatial relationships of a robot, laying the foundation for future work with RViz, Gazebo, and robot simulation.
