#!/usr/bin/env python3
"""
SolarClean Robotic Arm - Standalone Wall-Charger Firmware Pusher
Compiles and flashes firmware/PostureGuard_Arm to the connected Arduino Uno.
Configured specifically for autonomous wall-charger / power-bank operation.
"""

import os
import sys
import time
import subprocess
import glob

FIRMWARE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firmware", "PostureGuard_Arm")

def find_arduino_port():
    candidates = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
    if candidates:
        return candidates[-1]
    return None

def main():
    print("=" * 75)
    print(" 🔌 ARDUINO UNO STANDALONE WALL-CHARGER FIRMWARE PUSHER")
    print("=" * 75)
    print(" Configured for:")
    print("   • 100% Standalone (Unplug from PC & connect to wall charger)")
    print("   • 4 Random Solar Cleaning Zones: Left-Top, Left-Btm, Right-Top, Right-Btm")
    print("   • Alternating CW / CCW Wrist Roll (10% reduced swing angle)")
    print("   • Home Rest State (Quiet rest pose, wrist roll inhibited)")
    print("=" * 75)

    if not os.path.exists(FIRMWARE_DIR):
        print(f"[!] Error: Firmware directory not found at {FIRMWARE_DIR}")
        sys.exit(1)

    # 1. Detect Arduino Port
    port = find_arduino_port()
    if not port:
        print("\n[!] Arduino Uno not detected yet.")
        print("    👉 Please plug your Arduino Uno USB cable into this computer.")
        print("    Waiting for board connection (Press Ctrl+C to abort)...")
        while not port:
            time.sleep(1.0)
            port = find_arduino_port()

    print(f"\n[+] Detected Arduino Uno on port: {port}")

    # 2. Compile Sketch
    print("[*] Compiling firmware/PostureGuard_Arm with arduino-cli...")
    compile_cmd = ["arduino-cli", "compile", "-b", "arduino:avr:uno", FIRMWARE_DIR]
    res = subprocess.run(compile_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Compilation failed:\n{res.stderr or res.stdout}")
        sys.exit(1)
    print("[+] Compilation successful!")

    # 3. Free serial port
    print(f"[*] Ensuring {port} is completely free for upload...")
    subprocess.run(["fuser", "-k", port], capture_output=True)
    time.sleep(1.0)

    # 4. Upload to Arduino
    print(f"[*] Uploading sketch to {port}...")
    upload_cmd = ["arduino-cli", "upload", "-p", port, "-b", "arduino:avr:uno", FIRMWARE_DIR]
    res = subprocess.run(upload_cmd, capture_output=True, text=True)

    if res.returncode == 0:
        print("\n" + "=" * 75)
        print(" 🎉 SUCCESS: AUTONOMOUS FIRMWARE PUSHED TO ARDUINO!")
        print("=" * 75)
        print(" 👉 NEXT STEPS FOR WALL CHARGER OPERATION:")
        print("   1. Unplug the USB cable from your computer.")
        print("   2. Plug your Arduino Uno into your wall charger or 5V power adapter.")
        print("   3. Turn ON your external 5V/5A power supply for the PCA9685 servos.")
        print("   4. The robot arm will automatically run its 4-zone cleaning routine:")
        print("      • Moves to a random zone (Left-Top, Left-Btm, Right-Top, Right-Btm)")
        print("      • Runs 3s alternating CW/CCW wrist roll (10% reduced angle)")
        print("      • Pauses for 2s")
        print("      • Returns to Home rest state")
        print("=" * 75)
        sys.exit(0)
    else:
        err = res.stderr or res.stdout
        print(f"\n[!] Standard upload encountered error:\n{err}\n")
        print("💡 NOTE: If you see 'not in sync', press the small physical RESET button")
        print("   on the Arduino Uno once right when the upload command starts.")
        sys.exit(1)

if __name__ == "__main__":
    main()
