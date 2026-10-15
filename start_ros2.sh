#!/usr/bin/env bash
# ==============================================================================
# SolarClean Robotic Arm - ROS 2 Connect & Telemetry Bridge
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

clear
echo "================================================================================"
echo " 📡 CONNECTING TO SOLAR CLEANING ROS 2 ECOSYSTEM"
echo "================================================================================"

# Check / Start ROS 2 daemon
if ! pgrep -f "solar_ros_node.py --daemon" > /dev/null; then
    echo "[*] Launching ROS 2 Telemetry & Node Daemon in background..."
    python3 "$PROJECT_DIR/ros_solar_cleaner/solar_ros_node.py" --daemon > /dev/null 2>&1 &
    sleep 1.2
fi

echo "[+] Connected to ROS 2 Nodes successfully!"
echo ""

# Print Live Telemetry Summary
"$PROJECT_DIR/ros2"
echo ""

echo "--------------------------------------------------------------------------------"
echo " Active ROS 2 Nodes:"
echo "--------------------------------------------------------------------------------"
"$PROJECT_DIR/ros2" node list
echo ""

echo "--------------------------------------------------------------------------------"
echo " Standard ROS 2 Commands You Can Run:"
echo "--------------------------------------------------------------------------------"
echo "  • List all topics:            ./ros2 topic list"
echo "  • Stream Zone 0 Current:      ./ros2 topic echo /solar/zone_0/current_sensor"
echo "  • Stream Zone 1 Current:      ./ros2 topic echo /solar/zone_1/current_sensor"
echo "  • Stream Weather Station:     ./ros2 topic echo /weather/ambient_telemetry"
echo "  • Stream 6-DOF Joint Angles:  ./ros2 topic echo /joint_states"
echo "  • Full Interactive Demo:      ./demo.sh"
echo "================================================================================"
echo ""

# Interactive echo prompt
read -p "Enter topic name to stream now (or press Enter to exit): " topic_input
if [ -n "$topic_input" ]; then
    echo ">> Streaming $topic_input (Press Ctrl+C to stop)..."
    "$PROJECT_DIR/ros2" topic echo "$topic_input"
fi
