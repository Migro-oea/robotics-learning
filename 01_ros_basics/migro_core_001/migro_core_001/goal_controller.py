#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry


class GoalController(Node):

    def __init__(self):

        super().__init__('goal_controller')

        # =====================================================
        # Parameters
        # =====================================================

        self.declare_parameter('target_yaw', 90.0)
        self.declare_parameter('kp_angular', 1.0)
        self.declare_parameter('max_angular_speed', 0.5)
        self.declare_parameter('heading_tolerance', 2.0)

        self.declare_parameter('target_distance', 1.0)
        self.declare_parameter('kp_linear', 0.8)
        self.declare_parameter('max_speed', 0.2)
        self.declare_parameter('min_speed', 0.03)

        self.target_yaw = self.get_parameter('target_yaw').value
        self.kp_angular = self.get_parameter('kp_angular').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.heading_tolerance = self.get_parameter('heading_tolerance').value

        self.target_distance = self.get_parameter('target_distance').value
        self.kp_linear = self.get_parameter('kp_linear').value
        self.max_speed = self.get_parameter('max_speed').value
        self.min_speed = self.get_parameter('min_speed').value

        # Convert target heading from degrees to radians.
        self.target_yaw = math.radians(self.target_yaw)

        # =====================================================
        # State machine
        # =====================================================

        self.state = 'ROTATING'

        self.start_x = None
        self.start_y = None

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
            f'Goal controller started. '
            f'Target heading: {math.degrees(self.target_yaw):.1f} deg | '
            f'Target distance: {self.target_distance:.2f} m'
        )

    # =========================================================
    # Normalize angle into (-pi, pi]
    # =========================================================

    def normalize_angle(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    # =========================================================
    # Odometry callback — dispatches based on current state
    # =========================================================

    def odom_callback(self, msg):

        if self.state == 'ROTATING':
            self.do_rotating(msg)

        elif self.state == 'MOVING':
            self.do_moving(msg)

        elif self.state == 'DONE':
            # Nothing further to do. Robot already stopped.
            pass

    # =========================================================
    # ROTATING state
    # =========================================================

    def do_rotating(self, msg):

        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        yaw = math.atan2(
            2.0 * qw * qz,
            1.0 - 2.0 * qz * qz
        )

        error = self.normalize_angle(self.target_yaw - yaw)
        error_degrees = math.degrees(error)

        # -----------------------------------------------------
        # Transition check: heading reached
        # -----------------------------------------------------

        if abs(error_degrees) <= self.heading_tolerance:

            self.stop_robot()

            self.get_logger().info(
                f'Heading reached. Yaw: {math.degrees(yaw):.1f} deg | '
                f'Error: {error_degrees:.1f} deg. '
                f'Switching to MOVING.'
            )

            self.state = 'MOVING'
            return

        # -----------------------------------------------------
        # Proportional angular control
        # -----------------------------------------------------

        angular_speed = self.kp_angular * error

        angular_speed = max(
            -self.max_angular_speed,
            min(angular_speed, self.max_angular_speed)
        )

        msg_cmd = TwistStamped()
        msg_cmd.header.stamp = self.get_clock().now().to_msg()
        msg_cmd.twist.linear.x = 0.0
        msg_cmd.twist.angular.z = angular_speed

        self.cmd_pub.publish(msg_cmd)

        self.get_logger().info(
            f'Rotating... Yaw: {math.degrees(yaw):.1f} deg | '
            f'Error: {error_degrees:.1f} deg | '
            f'Angular speed: {angular_speed:.2f} rad/s'
        )

    # =========================================================
    # MOVING state
    # =========================================================

    def do_moving(self, msg):

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # -----------------------------------------------------
        # Capture starting position on entry into MOVING.
        # This must happen here (not in __init__ / node startup)
        # because we only want distance measured from the pose
        # the robot is in *after* rotation finished.
        # -----------------------------------------------------

        if self.start_x is None:
            self.start_x = x
            self.start_y = y

            self.get_logger().info(
                f'Starting distance tracking from: '
                f'x={x:.2f}, y={y:.2f}'
            )

        dx = x - self.start_x
        dy = y - self.start_y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        error = self.target_distance - distance

        # -----------------------------------------------------
        # Transition check: distance reached
        # -----------------------------------------------------

        if distance >= self.target_distance:

            self.stop_robot()

            self.get_logger().info(
                f'Distance reached! Distance: {distance:.2f} m. '
                f'Goal complete.'
            )

            self.state = 'DONE'
            return

        # -----------------------------------------------------
        # Proportional linear control
        # -----------------------------------------------------

        speed = self.kp_linear * error
        speed = min(speed, self.max_speed)

        if speed < self.min_speed:
            speed = self.min_speed

        msg_cmd = TwistStamped()
        msg_cmd.header.stamp = self.get_clock().now().to_msg()
        msg_cmd.twist.linear.x = speed
        msg_cmd.twist.angular.z = 0.0

        self.cmd_pub.publish(msg_cmd)

        self.get_logger().info(
            f'Moving... {distance:.2f} / {self.target_distance:.2f} m | '
            f'Error: {error:.2f} m | Speed: {speed:.2f} m/s'
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
    rclpy.init(args=args, signal_handler_options=rclpy.signals.SignalHandlerOptions.NO)
    node = GoalController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()

        # Stop processing odometry so the grace-period spin below
        # can't re-trigger the state machine and republish motion.
        node.destroy_subscription(node.odom_sub)

        # Give the executor a brief chance to actually flush the
        # zero-velocity command out over DDS before the node (and its
        # publisher) are torn down. publish() only queues the message —
        # it doesn't guarantee it has been sent.
        for _ in range(5):
            rclpy.spin_once(node, timeout_sec=0.05)

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
