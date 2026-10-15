#!/usr/bin/env bash
# ==============================================================================
# SolarClean Robotic Arm - Standalone Wall-Charger Firmware Flasher
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKETCH_DIR="$PROJECT_DIR/firmware/PostureGuard_Arm"

clear
echo "================================================================================"
echo " 🔌 ARDUINO UNO STANDALONE WALL-CHARGER FIRMWARE PUSHER"
echo "================================================================================"
echo " Flashing firmware with:"
echo "   • 100% Autonomous (No PC/laptop connection needed after flashing)"
echo "   • 4 Random Solar Cleaning Zones: Left-Top, Left-Btm, Right-Top, Right-Btm"
echo "   • Alternating CW / CCW Wrist Roll (10% reduced swing angle)"
echo "   • Home Rest State (Quiet rest pose, wrist roll inhibited)"
echo "================================================================================"
echo ""

# Function to search for serial port
get_arduino_port() {
    for p in /dev/ttyUSB* /dev/ttyACM*; do
        if [ -e "$p" ]; then
            echo "$p"
            return 0
        fi
    done
    return 1
}

PORT=$(get_arduino_port)

if [ -z "$PORT" ]; then
    echo "[!] Arduino Uno not detected yet."
    echo "    👉 Please plug your Arduino Uno USB cable into this computer."
    echo "    Waiting for board connection (Press Ctrl+C to abort)..."
    
    while [ -z "$PORT" ]; do
        sleep 1
        PORT=$(get_arduino_port)
    done
fi

echo "[+] Detected Arduino Uno on port: $PORT"
echo ""

# Compile firmware
echo "[*] Compiling PostureGuard_Arm sketch..."
if ! arduino-cli compile -b arduino:avr:uno "$SKETCH_DIR"; then
    echo "[!] Compilation failed. Please check code errors above."
    exit 1
fi
echo "[+] Compilation successful!"
echo ""

# Free serial port
echo "[*] Ensuring port $PORT is free..."
sudo fuser -k "$PORT" > /dev/null 2>&1 || fuser -k "$PORT" > /dev/null 2>&1
sleep 1

# Upload firmware
echo "[*] Uploading sketch to Arduino ($PORT)..."
if arduino-cli upload -p "$PORT" -b arduino:avr:uno "$SKETCH_DIR"; then
    echo ""
    echo "================================================================================"
    echo " 🎉 SUCCESS: AUTONOMOUS FIRMWARE SUCCESSFULLY FLASHED TO ARDUINO!"
    echo "================================================================================"
    echo " 👉 NEXT STEPS FOR WALL CHARGER OPERATION:"
    echo "   1. You can now unplug the USB cable from your computer."
    echo "   2. Plug the Arduino into your wall charger or 5V power adapter."
    echo "   3. Ensure your PCA9685 external 5V power supply is switched ON."
    echo "   4. The robotic arm will immediately begin its autonomous cleaning routine:"
    echo "      • Moves to a random cleaning zone (Left Top / Bottom or Right Top / Bottom)"
    echo "      • Actuates 3s alternating CW & CCW wrist roll"
    echo "      • Pauses for 2s"
    echo "      • Moves to Home rest state"
    echo "================================================================================"
else
    echo ""
    echo "[!] Upload failed."
    echo "💡 TIP: If you see 'not in sync', press the small red RESET button on your"
    echo "   Arduino Uno board once right when the upload starts."
    exit 1
fi
