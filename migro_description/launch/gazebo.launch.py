from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    # =========================================================
    # Package directories
    # =========================================================

    pkg_gazebo = get_package_share_directory("ros_gz_sim")
    pkg_migro = get_package_share_directory("migro_description")

    # =========================================================
    # MIGRO files
    # =========================================================

    robot_description = os.path.join(
        pkg_migro,
        "urdf",
        "migro.urdf.xacro"
    )

    world = os.path.join(
        pkg_migro,
        "worlds",
        "migro.world.sdf"
    )

    # =========================================================
    # Generate robot description from Xacro
    # =========================================================

    robot_description_content = os.popen(
        f"xacro {robot_description}"
    ).read()

    # =========================================================
    # Start Gazebo
    # =========================================================

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_gazebo,
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": f"-r {world}"
        }.items()
    )

    # =========================================================
    # Robot State Publisher
    # =========================================================

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description_content,
                "use_sim_time": True,
            }
        ],
        output="screen",
    )

    # =========================================================
    # Gazebo -> ROS 2 clock bridge
    # =========================================================

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/world/migro_world/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ],
        remappings=[
            (
                "/world/migro_world/clock",
                "/clock"
            )
        ],
        output="screen",
    )

    # =========================================================
    # Spawn MIGRO into Gazebo
    # =========================================================

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            "migro",
            "-topic",
            "robot_description",
            "-z",
            "0.5",
        ],
        output="screen",
    )

    # =========================================================
    # Joint State Broadcaster
    # =========================================================

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # =========================================================
    # Differential Drive Controller
    # =========================================================

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # =========================================================
    # Delay controller spawning
    #
    # Gazebo needs time to start gz_ros2_control and create
    # controller_manager before the spawners connect.
    # =========================================================

    controllers = TimerAction(
        period=5.0,
        actions=[
            joint_state_broadcaster_spawner,
            diff_drive_controller_spawner,
        ],
    )

    # =========================================================
    # Launch everything
    # =========================================================

    return LaunchDescription([
        gazebo,
        clock_bridge,
        robot_state_publisher,
        spawn_robot,
        controllers,
    ])