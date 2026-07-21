from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    target_number = LaunchConfiguration("target_number")
    server_name = LaunchConfiguration("server_name")
    client_name = LaunchConfiguration("client_name")

    return LaunchDescription([

        DeclareLaunchArgument(
            "target_number",
            default_value="10",
            description="Target number for the Action Client"
        ),

        DeclareLaunchArgument(
            "server_name",
            default_value="count_until_server",
            description="Action Server node name"
        ),

        DeclareLaunchArgument(
            "client_name",
            default_value="count_until_client",
            description="Action Client node name"
        ),

        Node(
            package="migro_action_001",
            executable="count_until_action_server",
            name=server_name,
            output="screen",
        ),

        Node(
            package="migro_action_001",
            executable="count_until_action_client",
            name=client_name,
            output="screen",
            parameters=[
                {"target_number": target_number}
            ],
        )

    ])
