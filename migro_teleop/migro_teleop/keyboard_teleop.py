#!/usr/bin/env python3

import sys
import termios
import tty
import select
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class KeyboardTeleop(Node):

    def __init__(self):
        super().__init__('keyboard_teleop')

        self.publisher = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        self.linear_speed = 0.2
        self.angular_speed = 0.8

        self.linear_x = 0.0
        self.angular_z = 0.0

        self.last_key_time = time.monotonic()
        self.key_timeout = 0.3

        self.timer = self.create_timer(
            0.05,
            self.publish_velocity
        )

        self.get_logger().info('MIGRO Keyboard Teleop Started')
        self.get_logger().info('Use W/S/A/D for movement')
        self.get_logger().info('SPACE = stop | Q = quit')

    def publish_velocity(self):

        if time.monotonic() - self.last_key_time > self.key_timeout:
            linear_x = 0.0
            angular_z = 0.0
        else:
            linear_x = self.linear_x
            angular_z = self.angular_z

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.twist.linear.x = linear_x
        msg.twist.angular.z = angular_z

        self.publisher.publish(msg)

    def set_velocity(self, linear_x, angular_z):

        self.linear_x = linear_x
        self.angular_z = angular_z
        self.last_key_time = time.monotonic()

    def stop(self):

        self.linear_x = 0.0
        self.angular_z = 0.0
        self.last_key_time = time.monotonic()


def main(args=None):

    rclpy.init(args=args)

    node = KeyboardTeleop()

    old_settings = termios.tcgetattr(sys.stdin)

    try:

        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():

            # Check keyboard without blocking ROS.
            ready, _, _ = select.select(
                [sys.stdin],
                [],
                [],
                0.05
            )

            if ready:

                key = sys.stdin.read(1).lower()

                if key == 'w':

                    node.set_velocity(
                        node.linear_speed,
                        0.0
                    )

                elif key == 's':

                    node.set_velocity(
                        -node.linear_speed,
                        0.0
                    )

                elif key == 'a':

                    node.set_velocity(
                        0.0,
                        node.angular_speed
                    )

                elif key == 'd':

                    node.set_velocity(
                        0.0,
                        -node.angular_speed
                    )

                elif key == ' ':

                    node.stop()

                elif key == 'q':

                    node.stop()
                    break

            rclpy.spin_once(
                node,
                timeout_sec=0.0
            )

    except KeyboardInterrupt:
        pass

    finally:

        node.stop()

        # Publish stop commands before shutting down.
        for _ in range(3):
            node.publish_velocity()

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            old_settings
        )

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
    