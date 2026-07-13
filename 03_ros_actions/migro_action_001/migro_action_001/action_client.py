import threading
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from migro_interfaces.action import CountUntil


class CountUntilActionClient(Node):

    def __init__(self):
        super().__init__("count_until_client")

        self._client = ActionClient(
            self,
            CountUntil,
            "count_until"
        )

        self.goal_handle = None

    def send_goal(self):

        goal = CountUntil.Goal()

        target = int(input("Count Until: "))

        goal.target_number = target

        self._client.wait_for_server()

        self.get_logger().info("Sending Goal...")

        self._send_goal_future = self._client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):

        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().info("Goal Rejected")
            return

        self.get_logger().info("Goal Accepted")

        threading.Thread(
            target=self.cancel_after_delay,
            daemon=True
        ).start()

        self._result_future = self.goal_handle.get_result_async()

        self._result_future.add_done_callback(
            self.result_callback
        )

    def cancel_after_delay(self):

        time.sleep(3)

        self.get_logger().info("Cancelling Goal...")

        cancel_future = self.goal_handle.cancel_goal_async()

        cancel_future.add_done_callback(
            self.cancel_done_callback
        )

    def cancel_done_callback(self, future):

        cancel_response = future.result()

        if len(cancel_response.goals_canceling) > 0:

            self.get_logger().info(
                "Goal successfully cancelled."
            )

        else:

            self.get_logger().info(
                "Goal failed to cancel."
            )

    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback

        self.get_logger().info(
            f"Current Number: {feedback.current_number}"
        )

    def result_callback(self, future):

        result = future.result().result

        self.get_logger().info(
            f"Success: {result.success}"
        )

        self.get_logger().info(
            f"Message: {result.message}"
        )

        rclpy.shutdown()


def main(args=None):

    rclpy.init(args=args)

    node = CountUntilActionClient()

    node.send_goal()

    rclpy.spin(node)


if __name__ == "__main__":
    main()