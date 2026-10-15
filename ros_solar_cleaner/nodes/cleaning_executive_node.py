#!/usr/bin/env python3
"""
ROS 2 Node: CleaningExecutiveNode
Package: ros_solar_cleaner

Role:
  Mission coordinator for the solar cleaning robotic arm.
  - Subscribes to:
      • /cleaning/alert_dirty_panels [std_msgs/String]
  - Publishes to:
      • /arm/joint_command          [std_msgs/String]
      • /cleaning/active_status     [std_msgs/String]

  Translates detected dirty panel zones into exact 6-DOF joint trajectory target coordinates
  and triggers the position-specific alternating CW/CCW wrist roll cycle.
"""

import sys
import os
import time
import json

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

# Calibrated 4-Zone Joint Presets
ZONE_COORDINATES = {
    0: {"name": "Top-Left",     "base": 138, "shoulder": 44, "elbow": 168, "pitch": 141, "claw": -25},
    1: {"name": "Bottom-Left",  "base": 138, "shoulder": 66, "elbow": 156, "pitch": 141, "claw": -25},
    2: {"name": "Top-Right",    "base": 96,  "shoulder": 44, "elbow": 168, "pitch": 141, "claw": -25},
    3: {"name": "Bottom-Right", "base": 96,  "shoulder": 66, "elbow": 156, "pitch": 141, "claw": -25},
    4: {"name": "Home-Rest",    "base": 90,  "shoulder": 135, "elbow": 180, "pitch": 90,  "claw": -25}
}

class CleaningExecutiveNode(Node):
    def __init__(self):
        super().__init__('cleaning_executive_node')
        self.get_logger().info("Initializing Cleaning Mission Executive Node...")

        # Subscriptions
        self.sub_alerts = self.create_subscription(
            String, '/cleaning/alert_dirty_panels', self.alert_callback, 10
        )

        # Publishers
        self.pub_arm_cmd = self.create_publisher(String, '/arm/joint_command', 10)
        self.pub_status = self.create_publisher(String, '/cleaning/active_status', 10)

        self.is_cleaning = False
        self.current_zone = 4 # Home
        self.get_logger().info("Executive standby. Monitoring dirty panel alerts...")

    def alert_callback(self, msg):
        try:
            alert = json.loads(msg.data)
            target_zone = alert.get("priority_zone", 0)
            dust_pct = alert.get("dust_percentage", 0)
            
            if self.is_cleaning and self.current_zone == target_zone:
                return # Already cleaning this zone

            self.get_logger().info(
                f"[DISPATCH] Received Alert! Target: Zone {target_zone} ({ZONE_COORDINATES[target_zone]['name']}) | Dust: {dust_pct}%"
            )
            self.execute_cleaning_cycle(target_zone)
        except Exception as e:
            self.get_logger().error(f"Error parsing alert payload: {e}")

    def execute_cleaning_cycle(self, zone_id):
        self.is_cleaning = True
        self.current_zone = zone_id
        coords = ZONE_COORDINATES[zone_id]

        cmd = {
            "action": "MOVE_AND_CLEAN",
            "zone_id": zone_id,
            "zone_name": coords["name"],
            "joint_targets": coords,
            "wrist_roll_routine": "ALTERNATING_CW_CCW_REDUCED_10PCT",
            "roll_duration_sec": 3.0,
            "rest_duration_sec": 2.0
        }
        
        self.get_logger().info(
            f"[ARM COMMAND] Deploying 6-DOF Arm to {coords['name']}: Base={coords['base']}°, Shoulder={coords['shoulder']}°, Elbow={coords['elbow']}°, Pitch={coords['pitch']}°"
        )
        self.pub_arm_cmd.publish(String(data=json.dumps(cmd)))
        self.pub_status.publish(String(data=f"CLEANING_IN_PROGRESS_ZONE_{zone_id}"))

def main(args=None):
    rclpy.init(args=args)
    node = CleaningExecutiveNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("CleaningExecutiveNode stopped.")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
