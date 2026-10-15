#!/usr/bin/env bash
# ==============================================================================
# SolarClean Robotic Arm - ROS 2 Python Nodes Runner
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODES_DIR="$PROJECT_DIR/ros_solar_cleaner/nodes"

clear
echo "================================================================================"
echo " 🤖 ROS 2 PYTHON NODES — PUBLISHER & SUBSCRIBER LAUNCHER"
echo "================================================================================"
echo " Complete ROS 2 Node Source Files (with create_publisher & create_subscription):"
echo "   1. solar_telemetry_publisher.py  (Publishes /solar/zone_*/current_sensor)"
echo "   2. dust_monitor_subscriber.py    (Subscribes to currents, detects dust drops)"
echo "   3. cleaning_executive_node.py    (Subscribes to alerts, dispatches arm)"
echo "   4. arm_hardware_node.py          (Subscribes to cmd, publishes /joint_states)"
echo "================================================================================"
echo ""
echo " Choose which ROS 2 Node you want to run:"
echo " [1] Run Publisher Node (solar_telemetry_publisher.py)"
echo " [2] Run Subscriber Node (dust_monitor_subscriber.py)"
echo " [3] Run Mission Executive Node (cleaning_executive_node.py)"
echo " [4] Run Hardware Bridge Node (arm_hardware_node.py)"
echo " [5] Run Both Publisher & Subscriber concurrently (Live Pub-Sub Showcase)"
echo " [q] Quit"
echo "--------------------------------------------------------------------------------"
read -p "Select option [1-5, q]: " choice
echo ""

case "$choice" in
    1)
        echo ">> Launching /solar_telemetry_publisher (Press Ctrl+C to stop)..."
        python3 -u "$NODES_DIR/solar_telemetry_publisher.py"
        ;;
    2)
        echo ">> Launching /dust_monitor_subscriber (Press Ctrl+C to stop)..."
        python3 -u "$NODES_DIR/dust_monitor_subscriber.py"
        ;;
    3)
        echo ">> Launching /cleaning_executive_node (Press Ctrl+C to stop)..."
        python3 -u "$NODES_DIR/cleaning_executive_node.py"
        ;;
    4)
        echo ">> Launching /arm_hardware_node (Press Ctrl+C to stop)..."
        python3 -u "$NODES_DIR/arm_hardware_node.py"
        ;;
    5)
        echo ">> Launching Live Publisher + Subscriber Demo (Press Ctrl+C to stop)..."
        python3 -u "$NODES_DIR/solar_telemetry_publisher.py" &
        PUB_PID=$!
        sleep 0.5
        python3 -u "$NODES_DIR/dust_monitor_subscriber.py" &
        SUB_PID=$!

        trap "kill $PUB_PID $SUB_PID 2>/dev/null; exit 0" SIGINT SIGTERM
        wait
        ;;
    q|Q)
        exit 0
        ;;
    *)
        echo "Invalid selection."
        ;;
esac
