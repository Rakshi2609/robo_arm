#!/usr/bin/env bash
# ==============================================================================
# Solar Cleaning Robotic Arm - Interactive ROS 2 & System Demo
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Ensure Python node daemon is running
if ! pgrep -f "solar_ros_node.py --daemon" > /dev/null; then
    echo "[*] Starting ROS 2 telemetry node in background..."
    python3 "$PROJECT_DIR/ros_solar_cleaner/solar_ros_node.py" --daemon > /dev/null 2>&1 &
    sleep 1.5
fi

clear
echo "================================================================================"
echo " ☀️  AUTONOMOUS SOLAR CLEANING ROBOTIC ARM — ROS 2 DEMO SUITE"
echo "================================================================================"
echo " Architecture Overview:"
echo "   • 4 Solar Zones: Top-Left (0), Bottom-Left (1), Top-Right (2), Bottom-Right (3)"
echo "   • 4 Independent Current Sensors (Current drops detect localized dust accumulation)"
echo "   • Ambient Weather Station (Temperature, Humidity, Solar Irradiance)"
echo "   • 6-DOF Robotic Arm with Autonomous Position Routine & Wrist Roll Actuator"
echo "================================================================================"
echo ""

# Quick Status Check
"$PROJECT_DIR/ros2"
echo ""

show_menu() {
    echo "--------------------------------------------------------------------------------"
    echo " Choose a demonstration action:"
    echo "--------------------------------------------------------------------------------"
    echo " [1] List Active ROS 2 Nodes        (./ros2 node list)"
    echo " [2] List Active ROS 2 Topics       (./ros2 topic list)"
    echo " [3] Stream Zone 0 Current Sensor   (./ros2 topic echo /solar/zone_0/current_sensor)"
    echo " [4] Stream Weather Telemetry       (./ros2 topic echo /weather/ambient_telemetry)"
    echo " [5] Stream Arm Joint States        (./ros2 topic echo /joint_states)"
    echo " [6] Stream Panel Dust Alerts       (./ros2 topic echo /cleaning/alert_dirty_panels)"
    echo " [7] Launch Motor Web Dashboard     (http://localhost:8000)"
    echo " [q] Quit"
    echo "--------------------------------------------------------------------------------"
    read -p "Select option [1-7, q]: " choice
    echo ""

    case "$choice" in
        1)
            echo ">> Running: ./ros2 node list"
            "$PROJECT_DIR/ros2" node list
            echo ""
            ;;
        2)
            echo ">> Running: ./ros2 topic list"
            "$PROJECT_DIR/ros2" topic list
            echo ""
            ;;
        3)
            echo ">> Streaming Zone 0 Current Sensor (Press Ctrl+C to return to menu)..."
            "$PROJECT_DIR/ros2" topic echo /solar/zone_0/current_sensor
            echo ""
            ;;
        4)
            echo ">> Streaming Ambient Weather Telemetry (Press Ctrl+C to return to menu)..."
            "$PROJECT_DIR/ros2" topic echo /weather/ambient_telemetry
            echo ""
            ;;
        5)
            echo ">> Streaming 6-DOF Joint Angles (Press Ctrl+C to return to menu)..."
            "$PROJECT_DIR/ros2" topic echo /joint_states
            echo ""
            ;;
        6)
            echo ">> Streaming Dirty Panel Alerts (Press Ctrl+C to return to menu)..."
            "$PROJECT_DIR/ros2" topic echo /cleaning/alert_dirty_panels
            echo ""
            ;;
        7)
            echo ">> Starting Motor Web Dashboard at http://localhost:8000..."
            xdg-open "http://localhost:8000" > /dev/null 2>&1 || sensible-browser "http://localhost:8000" > /dev/null 2>&1 &
            python3 "$PROJECT_DIR/motor_web_app.py"
            ;;
        q|Q)
            echo "Exiting demo. Telemetry remains active in background."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

while true; do
    show_menu
done
