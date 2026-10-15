#!/usr/bin/env python3
"""
PostureGuard Robotic Arm - Automated Arduino Firmware Uploader ("PUSH")
Compiles and flashes firmware/PostureGuard_Arm to the connected Arduino Uno.
"""

import os
import sys
import time
import subprocess
import serial.tools.list_ports

import glob

FIRMWARE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firmware", "PostureGuard_Arm")

def find_arduino_port():
    candidates = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
    if candidates:
        return candidates[-1]
    return None

def main():
    print("=" * 65)
    print(" ⚡ POSTUREGUARD ARDUINO FIRMWARE PUSHER (PORT 5000 DASHBOARD)")
    print("=" * 65)

    if not os.path.exists(FIRMWARE_DIR):
        print(f"[!] Error: Firmware directory not found at {FIRMWARE_DIR}")
        sys.exit(1)

    # 1. Detect Arduino Port
    port = find_arduino_port()
    if not port:
        print("[!] No Arduino board detected on USB.")
        print("    👉 Please plug your Arduino Uno into your computer USB port.")
        sys.exit(1)

    print(f"[+] Detected Arduino Uno on port: {port}")

    # 2. Compile Sketch
    print("[*] Compiling firmware/PostureGuard_Arm with arduino-cli...")
    compile_cmd = ["arduino-cli", "compile", "-b", "arduino:avr:uno", FIRMWARE_DIR]
    res = subprocess.run(compile_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Compilation failed:\n{res.stderr or res.stdout}")
        sys.exit(1)
    print("[+] Compilation successful!")

    # 3. Kill any process holding the serial port
    print(f"[*] Ensuring {port} is completely free for upload...")
    subprocess.run(["fuser", "-k", port], capture_output=True)
    time.sleep(1.0)

    # 4. Upload to Arduino
    print(f"[*] Uploading sketch to {port}...")
    upload_cmd = ["arduino-cli", "upload", "-p", port, "-b", "arduino:avr:uno", FIRMWARE_DIR]
    res = subprocess.run(upload_cmd, capture_output=True, text=True)

    if res.returncode == 0:
        print("=" * 65)
        print(f"🎉 SUCCESS: PostureGuard Firmware pushed to {port}!")
        print("    Motors are now calibrated and ready for the port 5000 dashboard.")
        print("=" * 65)
        sys.exit(0)
    else:
        err = res.stderr or res.stdout
        print(f"[!] Standard upload encountered sync error:\n{err}\n")
        print("💡 NOTE: If you see 'not in sync', press the small physical RESET button")
        print("   on the Arduino Uno once right when the upload command starts.")
        sys.exit(1)

if __name__ == "__main__":
    main()
