#!/usr/bin/env bash
# ==============================================================================
# SolarClean Robotic Arm - Web Controller Dashboard Launcher
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=5000

clear
echo "================================================================================"
echo " 🌐 ROBOTIC ARM MOTOR WEB CONTROLLER DASHBOARD"
echo "================================================================================"
echo " Features:"
echo "   • Interactive Angle Sliders for all 6 joints (Base, Shoulder, Elbow, etc.)"
echo "   • Real-Time Motor Response & PCA9685 PWM Calibration"
echo "   • Quick Actions: Home Pose, Clean Sweep, Claw Toggle, Emergency Stop"
echo "================================================================================"
echo ""

# Free port if already occupied
fuser -k ${PORT}/tcp > /dev/null 2>&1
sleep 0.5

# Check if Arduino is connected for hardware control
ARDUINO_PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -n 1)
if [ -n "$ARDUINO_PORT" ]; then
    echo "[+] Arduino detected on $ARDUINO_PORT (Hardware Control Active)"
else
    echo "[i] Arduino not detected on USB. Running in Virtual Simulator Mode."
    echo "    (To control real motors, connect Arduino via USB to computer)"
fi

echo ""
echo "[*] Starting Web Server on http://localhost:${PORT}..."
xdg-open "http://localhost:${PORT}" > /dev/null 2>&1 || sensible-browser "http://localhost:${PORT}" > /dev/null 2>&1 &

python3 "$PROJECT_DIR/motor_web_app.py" --port ${PORT}
