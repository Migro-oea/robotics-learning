import time

import rclpy
from rclpy.action import ActionServer
from rclpy.action import GoalResponse
from rclpy.node import Node

from migro_interfaces.action import CountUntil


class CountUntilActionServer(Node):

    def __init__(self):
        super().__init__("count_until_server")

        self._action_server = ActionServer(
            self,
            CountUntil,
            "count_until",
            self.execute_callback,
            goal_callback=self.goal_callback
        )

        self.get_logger().info("CountUntil Action Server started.")

    def goal_callback(self, goal_request):

        self.get_logger().info(
            f"Received goal request: Count until {goal_request.target_number}"
        )

        if goal_request.target_number < 0:

            self.get_logger().warn(
                "Rejecting goal because target number is negative."
            )

            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def execute_callback(self, goal_handle):

        self.get_logger().info(
            f"Executing goal: Count until {goal_handle.request.target_number}"
        )

        feedback = CountUntil.Feedback()

        for number in range(goal_handle.request.target_number + 1):

            feedback.current_number = number

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f"Current number: {number}"
            )

            time.sleep(1)

        goal_handle.succeed()

        result = CountUntil.Result()

        result.success = True
        result.message = (
            f"Successfully counted to {goal_handle.request.target_number}"
        )

        return result


def main(args=None):

    rclpy.init(args=args)

    node = CountUntilActionServer()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()