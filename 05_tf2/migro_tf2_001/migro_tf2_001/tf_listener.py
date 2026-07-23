#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from tf2_ros import Buffer
from tf2_ros import TransformListener
from tf2_ros import TransformException


class TFListener(Node):

    def __init__(self):
        super().__init__("tf_listener")

        # Create a TF buffer
        self.tf_buffer = Buffer()

        # Create a Transform Listener
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        # Run every 1 second
        self.timer = self.create_timer(
            1.0,
            self.lookup_transform
        )

        self.get_logger().info("TF Listener Started.")

    def lookup_transform(self):

        try:

            transform = self.tf_buffer.lookup_transform(
                "base_link",
                "camera_link",
                rclpy.time.Time()
            )

            translation = transform.transform.translation

            self.get_logger().info(
                f"Camera Position -> "
                f"x={translation.x:.2f}, "
                f"y={translation.y:.2f}, "
                f"z={translation.z:.2f}"
            )

        except TransformException as ex:

            self.get_logger().warn(
                f"Transform unavailable: {ex}"
            )


def main(args=None):

    rclpy.init(args=args)

    node = TFListener()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()