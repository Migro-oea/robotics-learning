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

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info("Goal Rejected")
            return

        self.get_logger().info("Goal Accepted")

        self._result_future = goal_handle.get_result_async()

        self._result_future.add_done_callback(
            self.result_callback
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