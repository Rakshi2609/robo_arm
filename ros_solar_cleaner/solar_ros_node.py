#!/usr/bin/env python3
"""
Solar Cleaning Robotic Arm - ROS 2 CLI & Node Ecosystem
Simulates real ROS 2 nodes, topics, and standard ROS CLI commands (ros2 node list, ros2 topic list, ros2 topic echo, etc.)
Includes:
  - 4 Solar Panel Zones (Zone 0: Top-Left, Zone 1: Bottom-Left, Zone 2: Top-Right, Zone 3: Bottom-Right)
  - 4 Independent Current Sensors (Current drops when dust accumulates in that zone!)
  - Global Ambient Sensors: Temperature, Humidity, Irradiance, Weather Condition
  - 6-DOF Robotic Arm Joint States & Cleaning Executive
"""

import sys
import time
import math
import random
import threading
import json
import urllib.request
import os

# 4 Solar Cleaning Zones corresponding to the 4 Arm Positions
ZONES = {
    0: {"name": "Zone_0_Top_Left",     "base": 138, "shoulder": 44, "elbow": 168, "pitch": 141},
    1: {"name": "Zone_1_Bottom_Left",  "base": 138, "shoulder": 66, "elbow": 156, "pitch": 141},
    2: {"name": "Zone_2_Top_Right",    "base": 96,  "shoulder": 44, "elbow": 168, "pitch": 141},
    3: {"name": "Zone_3_Bottom_Right", "base": 96,  "shoulder": 66, "elbow": 156, "pitch": 141},
}

SHARED_DATA_FILE = "/tmp/solar_ros_state.json"

class SolarCleanerROSSystem:
    def __init__(self):
        # 4 Independent Current & Dust Sensors (per zone)
        self.zone_data = {
            z: {
                "current_a": round(random.uniform(4.8, 5.2), 2),  # Nominal ~5.0 A per clean panel
                "voltage_v": round(random.uniform(21.0, 21.8), 2),
                "dust_pct": round(random.uniform(5.0, 15.0), 1),
                "status": "CLEAN"
            }
            for z in range(4)
        }
        # Global Ambient / Weather Telemetry
        self.weather = {
            "temperature_c": 32.4,
            "humidity_pct": 46.0,
            "solar_irradiance_wm2": 860.0,
            "condition": "SUNNY / CLEAR"
        }
        # Arm State
        self.arm_state = {
            "current_zone": 4, # 4 = Home
            "active_state_name": "HOME_REST",
            "wrist_roll_active": False,
            "joint_angles": [90, 135, 180, 90, 90, -25] # Ch 0..5
        }
        self.lock = threading.Lock()
        self.save_state()

    def save_state(self):
        with self.lock:
            data = {
                "timestamp": time.time(),
                "zones": self.zone_data,
                "weather": self.weather,
                "arm": self.arm_state
            }
            try:
                with open(SHARED_DATA_FILE, "w") as f:
                    json.dump(data, f)
            except Exception:
                pass

    def run_simulation_loop(self):
        """Background thread updating dust accumulation, current drops, and weather fluctuations."""
        while True:
            time.sleep(1.0)
            with self.lock:
                # Slowly fluctuate temperature & irradiance
                self.weather["temperature_c"] = round(32.0 + math.sin(time.time() / 60.0) * 2.5 + random.uniform(-0.1, 0.1), 1)
                self.weather["humidity_pct"] = round(45.0 + math.cos(time.time() / 60.0) * 3.0 + random.uniform(-0.2, 0.2), 1)
                self.weather["solar_irradiance_wm2"] = round(850.0 + random.uniform(-15.0, 15.0), 1)

                # Simulate dust accumulation on a random zone if not currently being cleaned
                dirty_candidate = random.randint(0, 3)
                if self.arm_state["current_zone"] != dirty_candidate:
                    self.zone_data[dirty_candidate]["dust_pct"] = min(85.0, round(self.zone_data[dirty_candidate]["dust_pct"] + random.uniform(0.5, 1.8), 1))
                    # Current drops proportionally as dust blocks sunlight!
                    # Clean ~5.1A, 50% dust ~2.5A, 80% dust ~1.0A
                    efficiency = max(0.15, (100.0 - self.zone_data[dirty_candidate]["dust_pct"]) / 100.0)
                    self.zone_data[dirty_candidate]["current_a"] = round(5.1 * efficiency, 2)
                    if self.zone_data[dirty_candidate]["dust_pct"] > 40.0:
                        self.zone_data[dirty_candidate]["status"] = "DIRTY_REQUIRES_CLEANING"
                    else:
                        self.zone_data[dirty_candidate]["status"] = "NOMINAL"

                # If arm is actively in a zone, clean it up!
                active_zone = self.arm_state["current_zone"]
                if active_zone in self.zone_data:
                    self.zone_data[active_zone]["dust_pct"] = max(2.0, round(self.zone_data[active_zone]["dust_pct"] - 4.5, 1))
                    efficiency = (100.0 - self.zone_data[active_zone]["dust_pct"]) / 100.0
                    self.zone_data[active_zone]["current_a"] = round(5.1 * efficiency, 2)
                    self.zone_data[active_zone]["status"] = "ACTIVE_CLEANING"

            self.save_state()

# CLI Command Dispatcher (Allows running standard `ros2` style commands)
def load_state():
    if os.path.exists(SHARED_DATA_FILE):
        try:
            with open(SHARED_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def print_ros2_node_list():
    print("/solar_telemetry_broadcaster")
    print("/zone_current_monitor_node")
    print("/environmental_weather_station")
    print("/cleaning_mission_executive")
    print("/arm_hardware_controller")

def print_ros2_topic_list():
    print("/parameter_events")
    print("/rosout")
    print("/joint_states")
    print("/weather/ambient_telemetry")
    for z in range(4):
        print(f"/solar/zone_{z}/current_sensor")
        print(f"/solar/zone_{z}/voltage_sensor")
        print(f"/solar/zone_{z}/dust_level")
        print(f"/solar/zone_{z}/cleaning_status")
    print("/cleaning/active_zone")
    print("/cleaning/alert_dirty_panels")

def echo_topic(topic):
    state = load_state()
    if not state:
        print(f"[WARN] No active ROS telemetry found. Start the ROS daemon first: python3 ros_solar_cleaner/solar_ros_node.py")
        return

    print(f"--- Listening to topic [{topic}] (Press Ctrl+C to stop) ---")
    try:
        while True:
            state = load_state()
            ts = time.time()
            sec = int(ts)
            nsec = int((ts - sec) * 1e9)

            if topic == "/joint_states":
                arm = state["arm"]
                print(f"""header:
  stamp:
    sec: {sec}
    nanosec: {nsec}
  frame_id: 'base_link'
name: ['waist_pan_joint', 'shoulder_joint', 'elbow_joint', 'wrist_roll_joint', 'wrist_pitch_joint', 'gripper_claw_joint']
position: {[round(math.radians(a), 3) for a in arm['joint_angles']]}
velocity: []
effort: []
---""")

            elif topic == "/weather/ambient_telemetry":
                w = state["weather"]
                print(f"""header:
  stamp:
    sec: {sec}
    nanosec: {nsec}
  frame_id: 'weather_station_link'
temperature_celsius: {w['temperature_c']}
relative_humidity_pct: {w['humidity_pct']}
solar_irradiance_wm2: {w['solar_irradiance_wm2']}
weather_condition: '{w['condition']}'
---""")

            elif topic.startswith("/solar/zone_") and "/current_sensor" in topic:
                try:
                    z = int(topic.split("/")[2].split("_")[1])
                    curr = state["zones"][str(z)]["current_a"]
                    print(f"""header:
  stamp:
    sec: {sec}
    nanosec: {nsec}
  frame_id: 'panel_zone_{z}'
zone_id: {z}
current_amperes: {curr}
is_drop_detected: {curr < 3.5}
---""")
                except Exception as e:
                    print(f"Topic {topic} error: {e}")
                    break

            elif topic.startswith("/solar/zone_") and "/dust_level" in topic:
                try:
                    z = int(topic.split("/")[2].split("_")[1])
                    dust = state["zones"][str(z)]["dust_pct"]
                    status = state["zones"][str(z)]["status"]
                    print(f"""header:
  stamp:
    sec: {sec}
    nanosec: {nsec}
  frame_id: 'panel_zone_{z}'
zone_id: {z}
dust_soiling_percentage: {dust} %
status: '{status}'
---""")
                except Exception as e:
                    print(f"Topic {topic} error: {e}")
                    break

            elif topic == "/cleaning/alert_dirty_panels":
                dirty_zones = [z for z, data in state["zones"].items() if data["dust_pct"] > 40.0]
                print(f"""header:
  stamp:
    sec: {sec}
    nanosec: {nsec}
dirty_panel_count: {len(dirty_zones)}
zones_requiring_cleaning: {dirty_zones}
priority_zone: {dirty_zones[0] if dirty_zones else 'NONE (ALL CLEAN)'}
---""")

            else:
                print(f"[WARN] Topic '{topic}' not matched. Run 'ros2 topic list' to see available topics.")
                break

            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # Run background simulation server
        system = SolarCleanerROSSystem()
        print("=================================================================")
        print(" ☀️  ROS 2 SOLAR CLEANING TELEMETRY & HARDWARE BRIDGE NODE")
        print("=================================================================")
        print(" [+] Initialized 4-Zone Current & Dust Sensor Monitors")
        print(" [+] Initialized Ambient Environmental Weather Station")
        print(" [+] Initialized 6-DOF Arm Kinematics & Cleaning Executive")
        print(f" [+] Telemetry buffer active: {SHARED_DATA_FILE}")
        print(" [*] You can now open another terminal and run:")
        print("     ./ros2 node list")
        print("     ./ros2 topic list")
        print("     ./ros2 topic echo /solar/zone_0/current_sensor")
        print("     ./ros2 topic echo /joint_states")
        print("=================================================================")
        system.run_simulation_loop()

    # CLI Router: Emulates standard `ros2` tool commands
    if len(sys.argv) >= 3 and sys.argv[1] == "node" and sys.argv[2] == "list":
        print_ros2_node_list()
    elif len(sys.argv) >= 3 and sys.argv[1] == "topic" and sys.argv[2] == "list":
        print_ros2_topic_list()
    elif len(sys.argv) >= 4 and sys.argv[1] == "topic" and sys.argv[2] == "echo":
        echo_topic(sys.argv[3])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--help":
        print("Usage: ros2 [node list | topic list | topic echo <topic_name>]")
    else:
        # Default status check
        state = load_state()
        if state:
            print("=================================================================")
            print(" ☀️  SOLAR CLEANING 4-ZONE ROS 2 TELEMETRY OVERVIEW")
            print("=================================================================")
            print(f" Ambient Weather: {state['weather']['temperature_c']}°C | Humidity: {state['weather']['humidity_pct']}% | Irradiance: {state['weather']['solar_irradiance_wm2']} W/m²")
            print("-----------------------------------------------------------------")
            for z, data in state["zones"].items():
                alert = " ⚠️ DUST ALERT!" if data['dust_pct'] > 40.0 else " ✅ Clean"
                print(f" [Zone {z}] Current: {data['current_a']} A | Dust: {data['dust_pct']}% | Status: {data['status']}{alert}")
            print("=================================================================")
            print("Commands:")
            print("  ./ros2 node list")
            print("  ./ros2 topic list")
            print("  ./ros2 topic echo /solar/zone_0/current_sensor")
            print("  ./ros2 topic echo /weather/ambient_telemetry")
            print("  ./ros2 topic echo /joint_states")
        else:
            print("ROS Daemon not running. Launch it with: python3 ros_solar_cleaner/solar_ros_node.py --daemon")

if __name__ == "__main__":
    main()
