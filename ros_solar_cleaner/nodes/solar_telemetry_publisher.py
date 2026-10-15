#!/usr/bin/env python3
"""
ROS 2 Node: SolarTelemetryPublisher
Package: ros_solar_cleaner

Role:
  Publishes real-time telemetry from the 4 solar panel current sensors and ambient weather station:
  - Topics Published:
      • /solar/zone_0/current_sensor [std_msgs/Float32]
      • /solar/zone_1/current_sensor [std_msgs/Float32]
      • /solar/zone_2/current_sensor [std_msgs/Float32]
      • /solar/zone_3/current_sensor [std_msgs/Float32]
      • /weather/ambient_telemetry   [std_msgs/String]
      • /joint_states                [sensor_msgs/JointState or std_msgs/String]

Compatible with standard rclpy (if ROS 2 is installed) or standalone Python execution.
"""

import sys
import os
import time
import random
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

class SolarTelemetryPublisher(Node):
    def __init__(self):
        super().__init__('solar_telemetry_publisher')
        
        self.get_logger().info("Initializing Solar Telemetry Broadcaster Node...")
        
        # 1. Register Publishers for 4 Individual Zone Current Sensors
        self.pub_zone0 = self.create_publisher(Float32, '/solar/zone_0/current_sensor', 10)
        self.pub_zone1 = self.create_publisher(Float32, '/solar/zone_1/current_sensor', 10)
        self.pub_zone2 = self.create_publisher(Float32, '/solar/zone_2/current_sensor', 10)
        self.pub_zone3 = self.create_publisher(Float32, '/solar/zone_3/current_sensor', 10)
        
        # 2. Register Weather & Arm Telemetry Publishers
        self.pub_weather = self.create_publisher(String, '/weather/ambient_telemetry', 10)
        self.pub_joint_states = self.create_publisher(String, '/joint_states', 10)
        
        # 3. Create Periodic Publishing Timer (1.0 Hz)
        self.timer_period = 1.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.publish_telemetry_callback)
        
        # Internal state simulation
        self.step_count = 0
        self.get_logger().info("All publishers successfully registered. Publishing at 1.0 Hz.")

    def publish_telemetry_callback(self):
        self.step_count += 1
        
        # Simulate normal solar output (~5.0 A), with Zone 1 experiencing a current drop due to dust build-up
        c0 = round(random.uniform(4.9, 5.2), 2)
        # Zone 1 simulates dust accumulation causing current drop to ~1.85 A
        c1 = round(1.80 + random.uniform(-0.05, 0.05), 2)
        c2 = round(random.uniform(4.8, 5.1), 2)
        c3 = round(random.uniform(4.9, 5.2), 2)
        
        # Create ROS Messages
        msg0 = Float32(data=c0)
        msg1 = Float32(data=c1)
        msg2 = Float32(data=c2)
        msg3 = Float32(data=c3)
        
        # Publish Zone Current Sensor Topics
        self.pub_zone0.publish(msg0)
        self.pub_zone1.publish(msg1)
        self.pub_zone2.publish(msg2)
        self.pub_zone3.publish(msg3)
        
        # Weather data
        weather_payload = {
            "temperature_celsius": round(32.5 + random.uniform(-0.2, 0.2), 1),
            "humidity_pct": round(46.0 + random.uniform(-0.3, 0.3), 1),
            "solar_irradiance_wm2": round(855.0 + random.uniform(-5.0, 5.0), 1),
            "condition": "CLEAR / SUNNY"
        }
        self.pub_weather.publish(String(data=json.dumps(weather_payload)))
        
        # Joint states
        joints_payload = {
            "joints": ["waist_pan", "shoulder", "elbow", "wrist_roll", "wrist_pitch", "claw"],
            "angles_deg": [138, 44, 168, 90, 141, -25]
        }
        self.pub_joint_states.publish(String(data=json.dumps(joints_payload)))
        
        # Standard ROS 2 Logger output
        self.get_logger().info(
            f"[PUBLISH] Currents -> Z0: {c0}A | Z1: {c1}A (DROP!) | Z2: {c2}A | Z3: {c3}A"
        )

def main(args=None):
    rclpy.init(args=args)
    node = SolarTelemetryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("SolarTelemetryPublisher stopped by user.")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
