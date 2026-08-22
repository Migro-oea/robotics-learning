#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry


class HeadingController(Node):

    def __init__(self):

        super().__init__('heading_controller')

        # =====================================================
        # Parameters
        # =====================================================

        self.declare_parameter('target_yaw', 90.0)
        self.declare_parameter('kp_angular', 1.0)
        self.declare_parameter('max_angular_speed', 0.5)
        self.declare_parameter('heading_tolerance', 2.0)

        self.target_yaw = (
            self.get_parameter('target_yaw').value
        )

        self.kp_angular = (
            self.get_parameter('kp_angular').value
        )

        self.max_angular_speed = (
            self.get_parameter('max_angular_speed').value
        )

        self.heading_tolerance = (
            self.get_parameter('heading_tolerance').value
        )

        # Convert target from degrees to radians.
        self.target_yaw = math.radians(self.target_yaw)

        # =====================================================
        # State
        # =====================================================

        self.finished = False

        # =====================================================
        # Publisher
        # =====================================================

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        # =====================================================
        # Odometry subscriber
        # =====================================================

        self.odom_sub = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            10
        )

        self.get_logger().info(
            f'Heading controller started. '
            f'Target: {math.degrees(self.target_yaw):.1f} deg'
        )

    # =========================================================
    # Normalize angle
    # =========================================================

    def normalize_angle(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    # =========================================================
    # Odometry callback
    # =========================================================

    def odom_callback(self, msg):

        # -----------------------------------------------------
        # Extract quaternion
        # -----------------------------------------------------

        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        # -----------------------------------------------------
        # Convert quaternion to yaw
        # -----------------------------------------------------

        yaw = math.atan2(
            2.0 * qw * qz,
            1.0 - 2.0 * qz * qz
        )

        # -----------------------------------------------------
        # Calculate heading error
        # -----------------------------------------------------

        error = self.normalize_angle(
            self.target_yaw - yaw
        )

        error_degrees = math.degrees(error)
        yaw_degrees = math.degrees(yaw)

        # -----------------------------------------------------
        # Check whether target heading is reached
        # -----------------------------------------------------

        if abs(error_degrees) <= self.heading_tolerance:

            self.stop_robot()

            if not self.finished:

                self.finished = True

                self.get_logger().info(
                    f'Target heading reached! '
                    f'Yaw: {yaw_degrees:.1f} deg | '
                    f'Error: {error_degrees:.1f} deg'
                )

            return

        # -----------------------------------------------------
        # Proportional angular control
        # -----------------------------------------------------

        angular_speed = (
            self.kp_angular * error
        )

        # Clamp angular speed.
        angular_speed = max(
            -self.max_angular_speed,
            min(
                angular_speed,
                self.max_angular_speed
            )
        )

        # -----------------------------------------------------
        # Publish command
        # -----------------------------------------------------

        if not self.finished:

            msg_cmd = TwistStamped()

            msg_cmd.header.stamp = (
                self.get_clock().now().to_msg()
            )

            # Rotate only.
            msg_cmd.twist.linear.x = 0.0
            msg_cmd.twist.angular.z = angular_speed

            self.cmd_pub.publish(msg_cmd)

            self.get_logger().info(
                f'Rotating... '
                f'Yaw: {yaw_degrees:.1f} deg | '
                f'Target: '
                f'{math.degrees(self.target_yaw):.1f} deg | '
                f'Error: {error_degrees:.1f} deg | '
                f'Angular speed: '
                f'{angular_speed:.2f} rad/s'
            )

    # =========================================================
    # Stop robot
    # =========================================================

    def stop_robot(self):

        msg = TwistStamped()

        msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0

        self.cmd_pub.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = HeadingController()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.stop_robot()

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()