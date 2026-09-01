#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

from migro_interfaces.action import NavigateToWaypoint


class NavigateToWaypointServer(Node):

    def __init__(self):

        super().__init__('navigate_to_waypoint_server')

        # =====================================================
        # Parameters (same as goal_controller.py)
        # =====================================================

        self.declare_parameter('kp_angular', 1.0)
        self.declare_parameter('max_angular_speed', 0.5)
        self.declare_parameter('heading_tolerance', 2.0)

        self.declare_parameter('kp_linear', 0.8)
        self.declare_parameter('max_speed', 0.2)
        self.declare_parameter('min_speed', 0.03)

        self.kp_angular = self.get_parameter('kp_angular').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.heading_tolerance = self.get_parameter('heading_tolerance').value

        self.kp_linear = self.get_parameter('kp_linear').value
        self.max_speed = self.get_parameter('max_speed').value
        self.min_speed = self.get_parameter('min_speed').value

        # =====================================================
        # Latest pose, updated by odom_callback only.
        # execute_callback reads this — it never computes
        # control commands itself.
        # =====================================================

        self.current_pose = None

        # =====================================================
        # Publisher / Subscriber
        # =====================================================

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        # Reentrant group: lets odom_callback keep firing WHILE
        # execute_callback's loop is running, on a MultiThreadedExecutor.
        self.callback_group = ReentrantCallbackGroup()

        self.odom_sub = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            10,
            callback_group=self.callback_group
        )

        # =====================================================
        # Action Server
        # =====================================================

        self._action_server = ActionServer(
            self,
            NavigateToWaypoint,
            'navigate_to_waypoint',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('NavigateToWaypoint action server ready.')

    # =========================================================
    # Odometry callback — ONLY updates latest pose. No control logic.
    # =========================================================

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    # =========================================================
    # Angle normalization (unchanged from goal_controller.py)
    # =========================================================

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    # =========================================================
    # Goal acceptance — reject if we don't have odometry yet
    # =========================================================

    def goal_callback(self, goal_request):
        if self.current_pose is None:
            self.get_logger().warn('Rejecting goal: no odometry received yet.')
            return GoalResponse.REJECT
        self.get_logger().info(
            f'Received goal: x={goal_request.target_x:.2f}, '
            f'y={goal_request.target_y:.2f}'
        )
        return GoalResponse.ACCEPT

    # =========================================================
    # Cancel handling — always allow cancellation
    # =========================================================

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    # =========================================================
    # Stop robot
    # =========================================================

    def stop_robot(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0
        self.cmd_pub.publish(msg)

    # =========================================================
    # Execute callback — this replaces the old odom-driven
    # state machine. It's now a self-contained loop owned by
    # the action server, running in its own thread.
    # =========================================================

    def execute_callback(self, goal_handle):

        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y

        feedback_msg = NavigateToWaypoint.Feedback()
        result_msg = NavigateToWaypoint.Result()

        # ---- ROTATING phase setup ----
        pose = self.current_pose
        dx = target_x - pose.position.x
        dy = target_y - pose.position.y
        target_distance = math.sqrt(dx ** 2 + dy ** 2)
        target_yaw = math.atan2(dy, dx)

        state = 'ROTATING'
        start_x = None
        start_y = None

        loop_hz = 20.0
        loop_period = 1.0 / loop_hz

        while rclpy.ok():

            # ---- Cancel check ----
            if goal_handle.is_cancel_requested:
                self.stop_robot()
                goal_handle.canceled()
                result_msg.success = False
                result_msg.final_x = self.current_pose.position.x
                result_msg.final_y = self.current_pose.position.y
                self.get_logger().info('Goal canceled.')
                return result_msg

            pose = self.current_pose
            x = pose.position.x
            y = pose.position.y

            if state == 'ROTATING':

                qz = pose.orientation.z
                qw = pose.orientation.w
                yaw = math.atan2(2.0 * qw * qz, 1.0 - 2.0 * qz * qz)

                error = self.normalize_angle(target_yaw - yaw)
                error_degrees = math.degrees(error)

                if abs(error_degrees) <= self.heading_tolerance:
                    self.stop_robot()
                    self.get_logger().info(
                        f'Heading reached. Error: {error_degrees:.1f} deg. '
                        f'Switching to MOVING.'
                    )
                    state = 'MOVING'

                else:
                    angular_speed = self.kp_angular * error
                    angular_speed = max(
                        -self.max_angular_speed,
                        min(angular_speed, self.max_angular_speed)
                    )

                    cmd = TwistStamped()
                    cmd.header.stamp = self.get_clock().now().to_msg()
                    cmd.twist.angular.z = angular_speed
                    self.cmd_pub.publish(cmd)

                    feedback_msg.distance_remaining = target_distance
                    feedback_msg.current_state = 'ROTATING'
                    goal_handle.publish_feedback(feedback_msg)

            elif state == 'MOVING':

                if start_x is None:
                    start_x = x
                    start_y = y
                    self.get_logger().info(
                        f'Starting distance tracking from: x={x:.2f}, y={y:.2f}'
                    )

                dx = x - start_x
                dy = y - start_y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                error = target_distance - distance

                if distance >= target_distance:
                    self.stop_robot()
                    self.get_logger().info(f'Waypoint reached! Distance: {distance:.2f} m.')

                    goal_handle.succeed()
                    result_msg.success = True
                    result_msg.final_x = x
                    result_msg.final_y = y
                    return result_msg

                else:
                    speed = self.kp_linear * error
                    speed = min(speed, self.max_speed)
                    if speed < self.min_speed:
                        speed = self.min_speed

                    cmd = TwistStamped()
                    cmd.header.stamp = self.get_clock().now().to_msg()
                    cmd.twist.linear.x = speed
                    self.cmd_pub.publish(cmd)

                    feedback_msg.distance_remaining = target_distance - distance
                    feedback_msg.current_state = 'MOVING'
                    goal_handle.publish_feedback(feedback_msg)

            time.sleep(loop_period)

        # rclpy shut down mid-goal
        result_msg.success = False
        result_msg.final_x = self.current_pose.position.x
        result_msg.final_y = self.current_pose.position.y
        return result_msg


def main(args=None):
    rclpy.init(args=args)
    node = NavigateToWaypointServer()

    # MultiThreadedExecutor is required: odom_callback and
    # execute_callback must be able to run concurrently.
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()