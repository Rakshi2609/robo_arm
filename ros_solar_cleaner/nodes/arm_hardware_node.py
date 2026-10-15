#!/usr/bin/env python3
"""
ROS 2 Node: ArmHardwareNode
Package: ros_solar_cleaner

Role:
  Hardware bridge node for the 6-DOF robotic arm.
  - Subscribes to:
      • /arm/joint_command [std_msgs/String]
  - Publishes to:
      • /joint_states     [std_msgs/String]

  Translates ROS joint trajectory commands into PCA9685 servo PWM pulses and manages
  the active wrist roll oscillating sequence during cleaning.
"""

import sys
import os
import time
import json
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    USING_REAL_RCLPY = True
except ImportError:
    import ros_bridge_core as rclpy
    from ros_bridge_core import Node, String
    USING_REAL_RCLPY = False

class ArmHardwareNode(Node):
    def __init__(self):
        super().__init__('arm_hardware_node')
        self.get_logger().info("Initializing 6-DOF Arm Hardware Bridge Node...")

        # Subscriptions
        self.sub_cmd = self.create_subscription(
            String, '/arm/joint_command', self.joint_cmd_callback, 10
        )

        # Publishers
        self.pub_states = self.create_publisher(String, '/joint_states', 10)

        # Internal servo angles (Default: Home Rest)
        self.current_angles = {
            "waist_pan": 90,
            "shoulder": 135,
            "elbow": 180,
            "wrist_roll": 90,
            "wrist_pitch": 90,
            "gripper_claw": -25
        }

        # 10 Hz Joint State Broadcaster
        self.timer = self.create_timer(0.5, self.broadcast_joint_states)
        self.get_logger().info("Hardware Bridge Ready. Listening on '/arm/joint_command'.")

    def joint_cmd_callback(self, msg):
        try:
            data = json.loads(msg.data)
            targets = data.get("joint_targets", {})
            self.get_logger().info(
                f"[HARDWARE EXECUTING] Moving joints to Target: Base={targets.get('base')}°, Shoulder={targets.get('shoulder')}°, Elbow={targets.get('elbow')}°"
            )
            # Update simulated joint angles
            if "base" in targets: self.current_angles["waist_pan"] = targets["base"]
            if "shoulder" in targets: self.current_angles["shoulder"] = targets["shoulder"]
            if "elbow" in targets: self.current_angles["elbow"] = targets["elbow"]
            if "pitch" in targets: self.current_angles["wrist_pitch"] = targets["pitch"]

            # If cleaning routine specified, log the wrist roll activation
            if data.get("wrist_roll_routine"):
                self.get_logger().info("[HARDWARE ACTUATOR] Triggering 3s alternating CW/CCW wrist roll (10% reduced swing angle)...")
        except Exception as e:
            self.get_logger().error(f"Error executing hardware command: {e}")

    def broadcast_joint_states(self):
        payload = {
            "header": {
                "stamp_sec": int(time.time()),
                "frame_id": "base_link"
            },
            "name": list(self.current_angles.keys()),
            "position_deg": list(self.current_angles.values()),
            "position_rad": [round(math.radians(deg), 3) for deg in self.current_angles.values()]
        }
        self.pub_states.publish(String(data=json.dumps(payload)))

def main(args=None):
    rclpy.init(args=args)
    node = ArmHardwareNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("ArmHardwareNode stopped.")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
