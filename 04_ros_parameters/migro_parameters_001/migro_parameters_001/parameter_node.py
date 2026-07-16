import rclpy
from rclpy.node import Node


class ParameterNode(Node):

    def __init__(self):
        super().__init__("parameter_node")

        # Declare a parameter with a default value
        self.declare_parameter("robot_name", "MIGRO")

        # Read the parameter
        robot_name = self.get_parameter(
            "robot_name"
        ).value

        self.get_logger().info(
            f"Hello, I am {robot_name}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = ParameterNode()

    rclpy.spin_once(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
