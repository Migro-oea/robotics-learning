import rclpy
from rclpy.node import Node


class DynamicParameterNode(Node):

    def __init__(self):
        super().__init__("dynamic_parameter_node")

        self.declare_parameter("robot_name", "MIGRO")

        self.timer = self.create_timer(
            2.0,
            self.timer_callback
        )

    def timer_callback(self):

        robot_name = self.get_parameter(
            "robot_name"
        ).value

        self.get_logger().info(
            f"Robot Name: {robot_name}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = DynamicParameterNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
