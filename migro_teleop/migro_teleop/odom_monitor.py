#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdomMonitor(Node):

    def __init__(self):

        super().__init__('odom_monitor')

        self.subscription = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            10
        )

        self.last_log_time = self.get_clock().now()

        self.get_logger().info(
            'MIGRO Odometry Monitor Started'
        )

    def odom_callback(self, msg):

        now = self.get_clock().now()

        # Only print once per second.
        if (now - self.last_log_time).nanoseconds < 1_000_000_000:
            return

        self.last_log_time = now

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        linear_velocity = msg.twist.twist.linear.x
        angular_velocity = msg.twist.twist.angular.z

        # Convert quaternion orientation to yaw.
        yaw = math.atan2(
            2.0 * qw * qz,
            1.0 - 2.0 * qz * qz
        )

        yaw_degrees = math.degrees(yaw)

        self.get_logger().info(
            f'Position: '
            f'x={x:.2f} m, '
            f'y={y:.2f} m | '
            f'Yaw={yaw_degrees:.1f} deg | '
            f'Linear={linear_velocity:.2f} m/s | '
            f'Angular={angular_velocity:.2f} rad/s'
        )


def main(args=None):

    rclpy.init(args=args)

    node = OdomMonitor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()