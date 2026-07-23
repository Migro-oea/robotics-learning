#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class TFBroadcaster(Node):

    def __init__(self):
        super().__init__("tf_broadcaster")

        # Create the TF Broadcaster
        self.broadcaster = TransformBroadcaster(self)

        # Publish at 10 Hz
        self.timer = self.create_timer(
            0.1,
            self.broadcast_transform
        )

        self.get_logger().info("TF Broadcaster Started.")

    def broadcast_transform(self):

        self.get_logger().info("Timer is running...")

        transform = TransformStamped()

        # Current time
        transform.header.stamp = self.get_clock().now().to_msg()

        # Parent Frame
        transform.header.frame_id = "base_link"

        # Child Frame
        transform.child_frame_id = "camera_link"

        # Translation
        transform.transform.translation.x = 0.0
        transform.transform.translation.y = 0.0
        transform.transform.translation.z = 0.5

        # No Rotation (Identity Quaternion)
        transform.transform.rotation.x = 0.0
        transform.transform.rotation.y = 0.0
        transform.transform.rotation.z = 0.0
        transform.transform.rotation.w = 1.0

        # Publish Transform
        self.broadcaster.sendTransform(transform)


def main(args=None):

    rclpy.init(args=args)

    node = TFBroadcaster()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
