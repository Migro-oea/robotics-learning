from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os
import xacro


def generate_launch_description():

    package_path = get_package_share_directory("migro_description")

    xacro_file = os.path.join(
        package_path,
        "urdf",
        "migro.urdf.xacro"
    )

    rviz_config = os.path.join(
        package_path,
        "rviz",
        "migro.rviz"
    )

    # Process the Xacro file
    robot_description_config = xacro.process_file(xacro_file)

    robot_description = {
        "robot_description": robot_description_config.toxml()
    }

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="screen"
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen"
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        output="screen"
    )

    return LaunchDescription([
        joint_state_publisher,
        robot_state_publisher,
        rviz
    ])