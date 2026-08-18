#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry


class DistanceController(Node):

    def __init__(self):

        super().__init__('distance_controller')

        # =====================================================
        # Parameters
        # =====================================================

        self.declare_parameter('target_distance', 1.0)
        self.declare_parameter('kp', 0.8)
        self.declare_parameter('max_speed', 0.2)
        self.declare_parameter('min_speed', 0.03)

        self.target_distance = (
            self.get_parameter('target_distance')
            .value
        )

        self.kp = (
            self.get_parameter('kp')
            .value
        )

        self.max_speed = (
            self.get_parameter('max_speed')
            .value
        )

        self.min_speed = (
            self.get_parameter('min_speed')
            .value
        )

        # =====================================================
        # State
        # =====================================================

        self.start_x = None
        self.start_y = None
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
            f'Distance controller started. '
            f'Target: {self.target_distance:.2f} m'
        )

    # =========================================================
    # Odometry callback
    # =========================================================

    def odom_callback(self, msg):

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # -----------------------------------------------------
        # Save starting position
        # -----------------------------------------------------

        if self.start_x is None:

            self.start_x = x
            self.start_y = y

            self.get_logger().info(
                f'Start position: '
                f'x={x:.2f}, y={y:.2f}'
            )

        # -----------------------------------------------------
        # Calculate displacement
        # -----------------------------------------------------

        dx = x - self.start_x
        dy = y - self.start_y

        distance = math.sqrt(
            dx ** 2 + dy ** 2
        )

        error = self.target_distance - distance 

        # -----------------------------------------------------
        # Check target
        # -----------------------------------------------------

        if distance >= self.target_distance:

            self.stop_robot()

            if not self.finished:

                self.finished = True

                self.get_logger().info(
                    f'Target reached! '
                    f'Distance: {distance:.2f} m'
                )

            return

        # -----------------------------------------------------
        # Continue moving forward
        # -----------------------------------------------------

        if not self.finished:

            self.move_forward(distance, error)

    # =========================================================
    # Move robot
    # =========================================================

    def move_forward(self, distance, error):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()

        speed = self.kp * error

        speed = min(speed, self.max_speed)

        if speed < self.min_speed:
            speed = self.min_speed

        msg.twist.linear.x = speed
        msg.twist.angular.z = 0.0

        self.cmd_pub.publish(msg)

        self.get_logger().info(
            f'Moving... '
            f'{distance:.2f} / '
            f'{self.target_distance:.2f} m | '
            f'Error: {error:.2f} m | '
            f'Speed: {speed:.2f} m/s'
        )

    # =========================================================
    # Stop robot
    # =========================================================

    def stop_robot(self):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0

        self.cmd_pub.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = DistanceController()

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