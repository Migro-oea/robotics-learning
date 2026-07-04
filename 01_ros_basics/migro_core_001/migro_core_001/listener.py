#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class Listener(Node):

    def __init__(self):
        super().__init__('listener')

        self.subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.listener_callback,
            10
        )

        self.get_logger().info("Listener node started!")

    def listener_callback(self, msg):
        self.get_logger().info(
            f"I received: linear.x = {msg.linear.x}, angular.z = {msg.angular.z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = Listener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
