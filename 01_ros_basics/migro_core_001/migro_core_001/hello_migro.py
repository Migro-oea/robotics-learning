#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class HelloMigro(Node):

    def __init__(self):
        super().__init__('hello_migro')
        self.get_logger().info("Hello from MIGRO! 🤖")


def main(args=None):
    rclpy.init(args=args)

    node = HelloMigro()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
