from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    pkg_gazebo = get_package_share_directory("ros_gz_sim")
    pkg_migro = get_package_share_directory("migro_description")

    robot_description = os.path.join(
        pkg_migro,
        "urdf",
        "migro.urdf.xacro"
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_gazebo,
                "launch",
                "gz_sim.launch.py"
            )
        )
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description":
            os.popen(f"xacro {robot_description}").read()
        }]
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "migro",
            "-topic", "robot_description"
        ],
        output="screen"
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot
    ])
