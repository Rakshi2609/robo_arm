#!/usr/bin/env python3
"""
Script to reset an Arduino Uno via USB Serial (DTR toggle).
On an Arduino Uno, toggling the DTR (Data Terminal Ready) line pulls the 
ATmega328P RESET pin LOW via an onboard capacitor, triggering a hardware reboot.
"""

import sys
import time
import glob
try:
    import serial
except ImportError:
    print("Error: 'pyserial' is not installed.")
    print("Install it using: pip install pyserial")
    sys.exit(1)


def find_arduino_port():
    """Auto-detect common Arduino serial ports on Linux/macOS/Windows."""
    candidates = (
        glob.glob("/dev/ttyACM*") +
        glob.glob("/dev/ttyUSB*") +
        glob.glob("/dev/cu.usbmodem*") +
        glob.glob("/dev/cu.usbserial*")
    )
    if candidates:
        return candidates[0]
    return None


def reset_arduino(port=None, baudrate=9600):
    if not port:
        port = find_arduino_port()
        if not port:
            print("No Arduino detected automatically.")
            print("Usage: python3 reset_arduino.py <port>")
            print("Example: python3 reset_arduino.py /dev/ttyACM0")
            sys.exit(1)

    print(f"Connecting to Arduino on {port}...")
    try:
        # Open serial connection
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(0.1)
            print("Toggling DTR line to trigger reset...")
            
            # Pull DTR LOW then HIGH to initiate reset pulse
            ser.setDTR(False)
            time.sleep(0.2)
            ser.setDTR(True)
            time.sleep(0.5)

            print("Arduino Uno reset command sent successfully!")
    except serial.SerialException as err:
        print(f"Failed to access serial port {port}: {err}")
        print("Tip: Ensure you have read/write permissions (e.g., sudo usermod -a -G dialout $USER).")
        sys.exit(1)


if __name__ == "__main__":
    target_port = sys.argv[1] if len(sys.argv) > 1 else None
    reset_arduino(target_port)
