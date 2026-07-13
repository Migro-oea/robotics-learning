from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package="migro_action_001",
            executable="count_until_action_server",
            name="count_until_server",
            output="screen"
        ),

        Node(
            package="migro_action_001",
            executable="count_until_action_client",
            name="count_until_client",
            output="screen"
        ),

    ])
