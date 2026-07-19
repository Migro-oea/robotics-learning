from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    target_number = LaunchConfiguration("target_number")

    declare_target_number = DeclareLaunchArgument(
        "target_number",
        default_value="10",
        description="Target number for the Action Client"
    )

    server = Node(
        package="migro_action_001",
        executable="count_until_action_server",
        name="count_until_server",
        output="screen",
    )

    client = Node(
        package="migro_action_001",
        executable="count_until_action_client",
        name="count_until_client",
        output="screen",
        parameters=[
            {"target_number": target_number}
        ],
    )

    return LaunchDescription([
        declare_target_number,
        server,
        client
    ])
