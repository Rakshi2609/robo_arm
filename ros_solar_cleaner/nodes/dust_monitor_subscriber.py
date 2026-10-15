#!/usr/bin/env python3
"""
ROS 2 Node: DustMonitorSubscriber
Package: ros_solar_cleaner

Role:
  Subscribes to all 4 solar panel current sensor topics:
    • /solar/zone_0/current_sensor [std_msgs/Float32]
    • /solar/zone_1/current_sensor [std_msgs/Float32]
    • /solar/zone_2/current_sensor [std_msgs/Float32]
    • /solar/zone_3/current_sensor [std_msgs/Float32]

  Analysis:
    Compares real-time current against nominal baseline (~5.0 A).
    When localized current drop is detected (< 3.5 A), calculates dust soiling percentage
    and publishes an alert to `/cleaning/alert_dirty_panels` to dispatch the robotic cleaning arm!
"""

import sys
import os
import time
import json

# Add parent directory to path for ros_bridge_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Float32, String
    USING_REAL_RCLPY = True
except ImportError:
    import ros_bridge_core as rclpy
    from ros_bridge_core import Node, Float32, String
    USING_REAL_RCLPY = False

NOMINAL_CURRENT_AMPS = 5.10
CURRENT_DROP_THRESHOLD_AMPS = 3.50

class DustMonitorSubscriber(Node):
    def __init__(self):
        super().__init__('dust_monitor_subscriber')
        self.get_logger().info("Initializing Solar Dust Monitor Subscriber Node...")

        # 1. Register Subscriptions to the 4 Zone Current Sensor Topics
        self.sub_zone0 = self.create_subscription(
            Float32, '/solar/zone_0/current_sensor', self.zone0_callback, 10
        )
        self.sub_zone1 = self.create_subscription(
            Float32, '/solar/zone_1/current_sensor', self.zone1_callback, 10
        )
        self.sub_zone2 = self.create_subscription(
            Float32, '/solar/zone_2/current_sensor', self.zone2_callback, 10
        )
        self.sub_zone3 = self.create_subscription(
            Float32, '/solar/zone_3/current_sensor', self.zone3_callback, 10
        )

        # 2. Register Publisher for Dirty Panel Cleaning Alerts
        self.pub_alert = self.create_publisher(String, '/cleaning/alert_dirty_panels', 10)

        self.get_logger().info("Subscribed to 4 zone current topics. Ready to detect dust build-up.")

    def process_zone_current(self, zone_id, current_val):
        # Calculate soiling loss percentage
        loss_pct = max(0.0, min(100.0, (1.0 - (current_val / NOMINAL_CURRENT_AMPS)) * 100.0))
        
        if current_val < CURRENT_DROP_THRESHOLD_AMPS:
            self.get_logger().warn(
                f"[ALERT] Dust Detected on Zone {zone_id}! Current: {current_val:.2f}A (Normal ~5.10A) -> Soiling: {loss_pct:.1f}%"
            )
            # Publish alert message for the robotic cleaning arm executive
            alert_msg = {
                "timestamp": time.time(),
                "priority_zone": zone_id,
                "zone_name": f"Zone_{zone_id}",
                "current_amperes": current_val,
                "dust_percentage": round(loss_pct, 1),
                "action_required": "DISPATCH_ARM_CLEANING"
            }
            self.pub_alert.publish(String(data=json.dumps(alert_msg)))
        else:
            self.get_logger().info(
                f"[OK] Zone {zone_id} Current: {current_val:.2f}A (Nominal). Dust: {loss_pct:.1f}%"
            )

    # Individual Topic Callback Handlers
    def zone0_callback(self, msg):
        self.process_zone_current(0, msg.data)

    def zone1_callback(self, msg):
        self.process_zone_current(1, msg.data)

    def zone2_callback(self, msg):
        self.process_zone_current(2, msg.data)

    def zone3_callback(self, msg):
        self.process_zone_current(3, msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = DustMonitorSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("DustMonitorSubscriber stopped by user.")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
