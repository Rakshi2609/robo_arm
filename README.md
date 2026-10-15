# ☀️ SolarClean 6-DOF Robotic Arm & ROS 2 Architecture

An autonomous 6-Degree-of-Freedom (6-DOF) robotic arm system engineered for automated solar panel cleaning, localized dust detection, environmental monitoring, and ROS 2 telemetry integration.

---

## 🎯 System Architecture Overview

1. **Autonomous 4-Zone Panel Cleaning**:
   - The arm autonomously positions its cleaning tool over 4 distinct solar array zones:
     - **Zone 0**: Top-Left
     - **Zone 1**: Bottom-Left
     - **Zone 2**: Top-Right
     - **Zone 3**: Bottom-Right
     - **Home**: Rest/Standby pose
   - **Position-Triggered Wrist Roll**: When reaching any of the 4 cleaning zones, the wrist roller activates for **3 seconds** (alternating clockwise and counter-clockwise with a 10% reduced swing angle) followed by **2 seconds** rest. The wrist roller is inhibited when in Home position.

2. **Solar Telemetry & Localized Dust Detection**:
   - **4 Independent Current Sensors**: One for each solar panel zone. A localized current drop below threshold triggers an automatic `DIRTY_REQUIRES_CLEANING` alert indicating dust soiling on that specific panel.
   - **Ambient Weather Station**: Continuously tracks ambient temperature (°C), relative humidity (%), and solar irradiance (W/m²).

3. **ROS 2 Node & Topic Ecosystem**:
   - Full standard ROS 2 package architecture (`package.xml`, `setup.py`, and Python node scripts).
   - Real Publisher & Subscriber implementations matching `rclpy.node.Node` standards.
   - Interactive CLI runner: `./run_ros_nodes.sh` to run individual publishers and subscribers.

### 🧩 ROS 2 Node Architecture & Topic Mapping
| Node Name | Source File | Topics Published | Topics Subscribed |
|---|---|---|---|
| `/solar_telemetry_publisher` | `ros_solar_cleaner/nodes/solar_telemetry_publisher.py` | `/solar/zone_0/current_sensor`<br>`/solar/zone_1/current_sensor`<br>`/solar/zone_2/current_sensor`<br>`/solar/zone_3/current_sensor`<br>`/weather/ambient_telemetry`<br>`/joint_states` | *(None - Data Source)* |
| `/dust_monitor_subscriber` | `ros_solar_cleaner/nodes/dust_monitor_subscriber.py` | `/cleaning/alert_dirty_panels` | `/solar/zone_0/current_sensor`<br>`/solar/zone_1/current_sensor`<br>`/solar/zone_2/current_sensor`<br>`/solar/zone_3/current_sensor` |
| `/cleaning_executive_node` | `ros_solar_cleaner/nodes/cleaning_executive_node.py` | `/arm/joint_command`<br>`/cleaning/active_status` | `/cleaning/alert_dirty_panels` |
| `/arm_hardware_node` | `ros_solar_cleaner/nodes/arm_hardware_node.py` | `/joint_states` | `/arm/joint_command` |

---

## 📐 4-Zone Joint Calibration Matrix

| Joint | Channel | Home | Zone 0 (Top-L) | Zone 1 (Btm-L) | Zone 2 (Top-R) | Zone 3 (Btm-R) |
|---|---|---|---|---|---|---|
| **Base / Waist** | Ch 0 | `90°` | `138°` | `138°` | `96°` | `96°` |
| **Shoulder** | Ch 1 | `135°` | `44°` | `66°` | `44°` | `66°` |
| **Elbow** | Ch 2 | `180°` | `168°` | `156°` | `168°` | `156°` |
| **Wrist Pitch** | Ch 3 | `90°` | `141°` | `141°` | `141°` | `141°` |
| **Wrist Roll** | Ch 4 | `90°` (Off) | Auto ±36° (CW/CCW) | Auto ±36° (CW/CCW) | Auto ±36° (CW/CCW) | Auto ±36° (CW/CCW) |
| **Gripper / Tool** | Ch 5 | `-25°` | Clamped | Clamped | Clamped | Clamped |

---

## 🚀 Quick Demonstration Guide

### 1. Interactive Demo Suite
Run the interactive demonstration menu:
```bash
./demo.sh
```
This presents an interactive menu to view active ROS 2 nodes, stream live topic telemetry, check dust sensor alerts, or start the web dashboard.

---

### 2. Standard ROS 2 CLI Commands
You can run standard ROS 2 commands directly in your terminal:

* **List active ROS nodes**:
  ```bash
  ./ros2 node list
  ```
  *Output:*
  ```
  /solar_telemetry_broadcaster
  /zone_current_monitor_node
  /environmental_weather_station
  /cleaning_mission_executive
  /arm_hardware_controller
  ```

* **List available ROS topics**:
  ```bash
  ./ros2 topic list
  ```

* **Inspect live current sensor on Zone 0**:
  ```bash
  ./ros2 topic echo /solar/zone_0/current_sensor
  ```

* **Inspect ambient weather telemetry**:
  ```bash
  ./ros2 topic echo /weather/ambient_telemetry
  ```

* **Inspect 6-DOF arm joint angles**:
  ```bash
  ./ros2 topic echo /joint_states
  ```

* **Check dirty panel detection alerts**:
  ```bash
  ./ros2 topic echo /cleaning/alert_dirty_panels
  ```

* **Display full 4-Zone telemetry overview**:
  ```bash
  ./ros2
  ```

---

### 3. Web Motor Control & Calibration Dashboard
To launch the real-time web slider dashboard:
```bash
python3 motor_web_app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to manually position motors, calibrate zero-offsets, test individual joints, or trigger automated sweeps.

---

### 4. Arduino Firmware Flashing
The firmware is located at:
[`firmware/PostureGuard_Arm/PostureGuard_Arm.ino`](file:///home/appu/Downloads/robo_arm/firmware/PostureGuard_Arm/PostureGuard_Arm.ino)

To compile and upload via `arduino-cli`:
```bash
arduino-cli compile -b arduino:avr:uno firmware/PostureGuard_Arm
arduino-cli upload -p /dev/ttyUSB0 -b arduino:avr:uno firmware/PostureGuard_Arm
```
Once flashed, the Arduino runs the autonomous cleaning routine independently when powered via USB or wall adapter.

---

## ⚡ Hardware Wiring & Power

* **Arduino Uno Logic**:
  * `5V` → PCA9685 `VCC`
  * `GND` → PCA9685 `GND`
  * `A4` → PCA9685 `SDA`
  * `A5` → PCA9685 `SCL`
* **External Servo Power**:
  * 5V / 4A–5A regulated DC power supply connected directly to the PCA9685 high-current screw terminal (`V+` and `GND`).
  * Never draw high servo current directly through the Arduino board regulator.
