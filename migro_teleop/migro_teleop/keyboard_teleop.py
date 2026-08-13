#!/usr/bin/env python3

import sys
import termios
import tty

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

        self.get_logger().info('MIGRO Keyboard Teleop Started')
        self.get_logger().info('↑ = forward | ↓ = backward')
        self.get_logger().info('← = left | → = right')
        self.get_logger().info('SPACE = stop | Q = quit')

    def publish_velocity(self, linear_x=0.0, angular_z=0.0):

        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.twist.linear.x = linear_x
        msg.twist.angular.z = angular_z

        self.publisher.publish(msg)


def get_key(settings):

    tty.setraw(sys.stdin.fileno())

    key = sys.stdin.read(1)

    if key == '\x1b':
        key += sys.stdin.read(2)

    termios.tcsetattr(
        sys.stdin,
        termios.TCSADRAIN,
        settings
    )

    return key


def main(args=None):

    rclpy.init(args=args)

    node = KeyboardTeleop()

    settings = termios.tcgetattr(sys.stdin)

    try:

        while rclpy.ok():

            key = get_key(settings)

            if key == '\x1b[A':
                node.publish_velocity(
                    linear_x=node.linear_speed,
                    angular_z=0.0
                )

            elif key == '\x1b[B':
                node.publish_velocity(
                    linear_x=-node.linear_speed,
                    angular_z=0.0
                )

            elif key == '\x1b[D':
                node.publish_velocity(
                    linear_x=0.0,
                    angular_z=node.angular_speed
                )

            elif key == '\x1b[C':
                node.publish_velocity(
                    linear_x=0.0,
                    angular_z=-node.angular_speed
                )

            elif key == ' ':
                node.publish_velocity()

            elif key.lower() == 'q':
                node.publish_velocity()
                break

            rclpy.spin_once(node, timeout_sec=0.0)

    except KeyboardInterrupt:
        pass

    finally:

        node.publish_velocity()

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            settings
        )

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()