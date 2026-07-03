#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class HelloMigro(Node):

    def __init__(self):
        # Initialize the ROS node
        super().__init__('hello_migro')

        # Create a publisher that sends Twist messages
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Create a timer that calls move_robot() every 0.1 seconds
        self.timer = self.create_timer(
            0.1,
            self.move_robot
        )

        self.get_logger().info("Hello from MIGRO! 🤖")

    def move_robot(self):
        # Create a Twist message
        msg = Twist()

        # Set forward speed
        msg.linear.x = 2.0

        # Publish the message
        self.publisher.publish(msg)


def main(args=None):
    # Start ROS
    rclpy.init(args=args)

    # Create the node
    node = HelloMigro()

    # Keep the node alive
    rclpy.spin(node)

    # Clean up when the program is stopped
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()