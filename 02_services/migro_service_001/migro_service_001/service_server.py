#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_srvs.srv import SetBool


class ServiceServer(Node):

    def __init__(self):
        super().__init__('service_server')

        self.srv = self.create_service(
            SetBool,
            'toggle_robot',
            self.callback
        )

        self.get_logger().info("Service Server is ready!")

    def callback(self, request, response):

        if request.data:
            response.success = True
            response.message = "Robot enabled."
        else:
            response.success = True
            response.message = "Robot disabled."

        return response


def main(args=None):
    rclpy.init(args=args)

    node = ServiceServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()