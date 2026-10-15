#!/usr/bin/env python3
"""
High-definition video generator for Solar Cleaning Robotic Arm & ROS 2 Demo.
Generates an animated 1920x1080 MP4 video showcasing:
1. System Architecture & 4-Zone Solar Array
2. ROS 2 Node & Topic Ecosystem CLI
3. Real-time Current Drop Dust Detection
4. Interactive demo.sh & Web Dashboard
"""

import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION_SEC = 32
TOTAL_FRAMES = FPS * DURATION_SEC

FONT_MONO_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SANS_PATH = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

font_title = get_font(FONT_SANS_PATH, 44)
font_subtitle = get_font(FONT_SANS_PATH, 24)
font_heading = get_font(FONT_SANS_PATH, 30)
font_body = get_font(FONT_SANS_PATH, 20)
font_mono = get_font(FONT_MONO_PATH, 19)
font_mono_bold = get_font(FONT_MONO_PATH, 21)
font_mono_small = get_font(FONT_MONO_PATH, 16)

def draw_header(draw, title_text, subtitle_text):
    # Top banner bar
    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(15, 23, 42))
    draw.line([(0, 90), (WIDTH, 90)], fill=(34, 197, 94), width=3)
    
    # Title & tags
    draw.text((40, 15), title_text, fill=(248, 250, 252), font=font_heading)
    draw.text((40, 55), subtitle_text, fill=(148, 163, 184), font=font_subtitle)
    
    # Live ROS status indicator
    draw.rounded_rectangle([(WIDTH - 260, 24), (WIDTH - 40, 66)], radius=8, fill=(22, 101, 52))
    draw.ellipse([(WIDTH - 245, 39), (WIDTH - 231, 53)], fill=(74, 222, 128))
    draw.text((WIDTH - 220, 34), "ROS 2 ACTIVE", fill=(240, 253, 244), font=get_font(FONT_SANS_PATH, 18))

def draw_terminal_window(draw, x, y, w, h, title="bash — terminal"):
    # Window chrome
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=12, fill=(11, 15, 25), outline=(30, 41, 59), width=2)
    draw.rounded_rectangle([(x, y), (x + w, y + 40)], radius=12, fill=(20, 27, 45))
    draw.rectangle([(x, y + 25), (x + w, y + 40)], fill=(20, 27, 45)) # straighten bottom corners
    
    # Traffic light buttons
    draw.ellipse([(x + 16, y + 14), (x + 28, y + 26)], fill=(239, 68, 68))
    draw.ellipse([(x + 36, y + 14), (x + 48, y + 26)], fill=(234, 179, 8))
    draw.ellipse([(x + 56, y + 14), (x + 68, y + 26)], fill=(34, 197, 94))
    
    # Title
    draw.text((x + 85, y + 11), title, fill=(148, 163, 184), font=font_mono_small)

def render_frame(frame_idx):
    t = frame_idx / FPS
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(10, 14, 23))
    draw = ImageDraw.Draw(img)
    
    # SCENE 0: Title Splash (0s - 4.5s)
    if t < 4.5:
        # Subtle glowing background grid lines
        for gx in range(0, WIDTH, 120):
            draw.line([(gx, 0), (gx, HEIGHT)], fill=(16, 24, 40), width=1)
        for gy in range(0, HEIGHT, 120):
            draw.line([(0, gy), (WIDTH, gy)], fill=(16, 24, 40), width=1)

        # Center card
        card_w, card_h = 1300, 680
        cx, cy = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=20, fill=(15, 23, 42), outline=(37, 99, 235), width=3)
        
        # Badge
        draw.rounded_rectangle([(cx + 50, cy + 60), (cx + 340, cy + 105)], radius=10, fill=(30, 58, 138))
        draw.text((cx + 70, cy + 70), "PROJECT SHOWCASE & DEMO", fill=(147, 197, 253), font=font_subtitle)
        
        # Big Titles
        draw.text((cx + 50, cy + 130), "☀️ Autonomous Solar Cleaning Arm", fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 52))
        draw.text((cx + 50, cy + 210), "6-DOF Kinematics • 4-Zone Array • ROS 2 Architecture", fill=(56, 189, 248), font=font_heading)

        # 3 Pillar feature boxes
        pillars = [
            ("🤖 6-DOF Robotic Arm", "Autonomous 4-zone cleaning routine with alternating CW/CCW wrist roll actuator and home rest state."),
            ("⚡ Localized Dust Detection", "4 independent current sensors detect panel soiling in real time via localized current drops."),
            ("📡 Standard ROS 2 Ecosystem", "Full ROS 2 CLI emulation: nodes, topics, services, and live sensor telemetry echo.")
        ]
        pw = 370
        for i, (p_title, p_desc) in enumerate(pillars):
            px = cx + 50 + i * (pw + 30)
            py = cy + 300
            draw.rounded_rectangle([(px, py), (px + pw, py + 260)], radius=14, fill=(24, 34, 58), outline=(51, 65, 85), width=2)
            draw.text((px + 20, py + 25), p_title, fill=(248, 250, 252), font=get_font(FONT_SANS_PATH, 22))
            
            # Word-wrapped description
            words = p_desc.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) < 30:
                    cur += (" " if cur else "") + w
                else:
                    lines.append(cur)
                    cur = w
            if cur: lines.append(cur)
            for li, line in enumerate(lines):
                draw.text((px + 20, py + 80 + li * 28), line, fill=(203, 213, 225), font=get_font(FONT_SANS_PATH, 17))
        
        # Progress indicator bar
        bar_w = int((t / 4.5) * card_w)
        draw.line([(cx, cy + card_h - 4), (cx + bar_w, cy + card_h - 4)], fill=(34, 197, 94), width=6)

    # SCENE 1: System Topology & 4 Solar Zones (4.5s - 10.5s)
    elif t < 10.5:
        draw_header(draw, "SYSTEM ARCHITECTURE & 4-ZONE ARRAY TOPOLOGY", "Hardware Kinematics, 4 Current Sensors, and Environmental Monitoring")
        
        # Left Panel: 4 Solar Zones Display
        grid_x, grid_y = 60, 130
        grid_w, grid_h = 950, 890
        draw.rounded_rectangle([(grid_x, grid_y), (grid_x + grid_w, grid_y + grid_h)], radius=16, fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((grid_x + 30, grid_y + 25), "SOLAR PANEL CLEANING ZONES (4-ZONE ARRAY)", fill=(248, 250, 252), font=font_heading)
        
        zones = [
            ("Zone 0 — Top Left", 138, 44, 168, 141, 5.1, 8.5, "CLEAN", (34, 197, 94)),
            ("Zone 2 — Top Right", 96, 44, 168, 141, 4.95, 12.0, "CLEAN", (34, 197, 94)),
            ("Zone 1 — Bottom Left", 138, 66, 156, 141, 1.82, 64.0, "DIRTY (CURRENT DROP!)", (239, 68, 68)),
            ("Zone 3 — Bottom Right", 96, 66, 156, 141, 4.88, 14.5, "CLEAN", (34, 197, 94)),
        ]
        
        zw, zh = 420, 360
        coords = [
            (grid_x + 35, grid_y + 90),
            (grid_x + 490, grid_y + 90),
            (grid_x + 35, grid_y + 490),
            (grid_x + 490, grid_y + 490),
        ]
        
        for idx, ((name, base, sh, elb, pitch, cur, dust, status, col), (zx, zy)) in enumerate(zip(zones, coords)):
            is_dirty = "DIRTY" in status
            bg_col = (45, 20, 25) if is_dirty else (20, 30, 48)
            border_col = col
            draw.rounded_rectangle([(zx, zy), (zx + zw, zy + zh)], radius=12, fill=bg_col, outline=border_col, width=3 if is_dirty else 1)
            
            draw.text((zx + 20, zy + 20), name, fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 24))
            draw.rounded_rectangle([(zx + zw - 160, zy + 18), (zx + zw - 20, zy + 50)], radius=6, fill=col)
            draw.text((zx + zw - 150, zy + 24), "ALERT" if is_dirty else "NORMAL", fill=(0, 0, 0) if not is_dirty else (255, 255, 255), font=get_font(FONT_SANS_PATH, 16))
            
            draw.text((zx + 20, zy + 80), f"Current Output: {cur:.2f} A", fill=(248, 250, 252), font=font_mono_bold)
            draw.text((zx + 20, zy + 120), f"Dust Soiling:   {dust:.1f} %", fill=(248, 250, 252), font=font_mono)
            draw.text((zx + 20, zy + 160), f"Zone Status:    {status}", fill=col, font=font_mono_bold)
            
            # Divider
            draw.line([(zx + 20, zy + 210), (zx + zw - 20, zy + 210)], fill=(51, 65, 85), width=1)
            draw.text((zx + 20, zy + 225), "Target Joint Angles:", fill=(148, 163, 184), font=font_mono_small)
            draw.text((zx + 20, zy + 255), f"Base: {base}°  | Shoulder: {sh}°", fill=(203, 213, 225), font=font_mono_small)
            draw.text((zx + 20, zy + 285), f"Elbow: {elb}° | Pitch: {pitch}°", fill=(203, 213, 225), font=font_mono_small)
            draw.text((zx + 20, zy + 315), "Wrist Roll: Auto-Alternating CW/CCW", fill=(56, 189, 248), font=font_mono_small)

        # Right Panel: Arm Specifications & Ambient Weather
        right_x, right_y = 1050, 130
        right_w, right_h = 810, 890
        draw.rounded_rectangle([(right_x, right_y), (right_x + right_w, right_y + 420)], radius=16, fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((right_x + 30, right_y + 25), "AMBIENT WEATHER TELEMETRY", fill=(248, 250, 252), font=font_heading)
        
        weather_items = [
            ("Ambient Temperature", "32.8 °C", "Nominal operational range (-10°C to 65°C)"),
            ("Relative Humidity", "46.2 %", "Optimal solar exposure conditions"),
            ("Solar Irradiance", "856.4 W/m²", "Peak solar production window"),
            ("Weather Condition", "CLEAR / SUNNY", "Active automated cleaning permitted")
        ]
        for wi, (w_label, w_val, w_sub) in enumerate(weather_items):
            wy = right_y + 90 + wi * 75
            draw.text((right_x + 30, wy), w_label, fill=(148, 163, 184), font=get_font(FONT_SANS_PATH, 19))
            draw.text((right_x + 340, wy), w_val, fill=(34, 197, 94) if "W/m²" in w_val or "°C" in w_val else (56, 189, 248), font=font_mono_bold)
            draw.text((right_x + 30, wy + 26), w_sub, fill=(100, 116, 139), font=get_font(FONT_SANS_PATH, 14))

        # Bottom Right: 6-DOF Hardware specs
        arm_box_y = right_y + 460
        draw.rounded_rectangle([(right_x, arm_box_y), (right_x + right_w, right_y + right_h)], radius=16, fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((right_x + 30, arm_box_y + 25), "6-DOF ROBOTIC ARM HARDWARE", fill=(248, 250, 252), font=font_heading)
        
        arm_specs = [
            ("Controller", "Arduino Uno (ATmega328P) via /dev/ttyUSB0"),
            ("PWM Driver", "PCA9685 16-Channel 12-Bit I2C Bus @ 50 Hz"),
            ("Shoulder & Elbow", "MG995 High-Torque Metal Gear Servos"),
            ("Wrist Actuators", "SG90 Micro Servos (Roll & Pitch)"),
            ("Cleaning Motion", "3s Active Roll (CW/CCW 10% reduced), 2s Rest"),
            ("Power Rail", "Regulated 5V/5A High-Current External Supply")
        ]
        for ai, (s_label, s_val) in enumerate(arm_specs):
            ay = arm_box_y + 85 + ai * 52
            draw.text((right_x + 30, ay), s_label, fill=(148, 163, 184), font=get_font(FONT_SANS_PATH, 18))
            draw.text((right_x + 240, ay), s_val, fill=(241, 245, 249), font=font_mono_small)

    # SCENE 2: Activating ROS 2 & Node Listing (10.5s - 17.5s)
    elif t < 17.5:
        draw_header(draw, "LIVE ROS 2 TELEMETRY & NODE MANAGEMENT", "Standard ROS 2 CLI commands executing in real time")
        
        # Big terminal on the left
        term_x, term_y = 60, 120
        term_w, term_h = 1150, 910
        draw_terminal_window(draw, term_x, term_y, term_w, term_h, "appu@workstation: ~/Downloads/robo_arm")
        
        ty = term_y + 60
        tx = term_x + 30
        
        # Step 1: ros2 status
        draw.text((tx, ty), "appu@workstation:~/Downloads/robo_arm$ ./ros2", fill=(74, 222, 128), font=font_mono)
        ty += 35
        
        ros_summary = [
            "=================================================================",
            " ☀️  SOLAR CLEANING 4-ZONE ROS 2 TELEMETRY OVERVIEW",
            "=================================================================",
            " Ambient Weather: 33.4°C | Humidity: 47.5% | Irradiance: 853.6 W/m²",
            "-----------------------------------------------------------------",
            " [Zone 0] Current: 5.12 A | Dust:  8.2% | Status: NOMINAL ✅ Clean",
            " [Zone 1] Current: 1.85 A | Dust: 63.8% | Status: DIRTY ⚠️ DUST ALERT!",
            " [Zone 2] Current: 4.98 A | Dust: 11.4% | Status: NOMINAL ✅ Clean",
            " [Zone 3] Current: 5.04 A | Dust:  9.1% | Status: NOMINAL ✅ Clean",
            "================================================================="
        ]
        for line in ros_summary:
            col = (239, 68, 68) if "DUST ALERT" in line else (56, 189, 248) if "Ambient" in line or "SOLAR" in line else (203, 213, 225)
            draw.text((tx, ty), line, fill=col, font=font_mono)
            ty += 26
        
        ty += 20
        # Step 2: ros2 node list
        draw.text((tx, ty), "appu@workstation:~/Downloads/robo_arm$ ./ros2 node list", fill=(74, 222, 128), font=font_mono)
        ty += 35
        
        nodes = [
            "/solar_telemetry_broadcaster",
            "/zone_current_monitor_node",
            "/environmental_weather_station",
            "/cleaning_mission_executive",
            "/arm_hardware_controller"
        ]
        for node in nodes:
            draw.text((tx + 20, ty), node, fill=(248, 250, 252), font=font_mono_bold)
            ty += 28
            
        ty += 20
        # Step 3: Prompt ready
        draw.text((tx, ty), "appu@workstation:~/Downloads/robo_arm$ █", fill=(74, 222, 128), font=font_mono)

        # Right Explanation Card
        rx, ry = 1250, 120
        rw, rh = 610, 910
        draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=16, fill=(15, 23, 42), outline=(37, 99, 235), width=2)
        draw.text((rx + 30, ry + 35), "ROS 2 NODE ROLES", fill=(255, 255, 255), font=font_heading)
        
        node_explanations = [
            ("/solar_telemetry_broadcaster", "Broadcasts global power generated, efficiency calculations, and system health status."),
            ("/zone_current_monitor_node", "Monitors 4 separate current sensors. Detects dust build-up when current dips below threshold."),
            ("/environmental_weather_station", "Publishes temperature, humidity, and solar irradiance from weather telemetry sensors."),
            ("/cleaning_mission_executive", "Autonomous state machine coordinating which panel zone requires robotic arm cleaning."),
            ("/arm_hardware_controller", "Bridge sending joint angles (Ch 0-5) to PCA9685 servo driver and executing wrist oscillation.")
        ]
        ey = ry + 100
        for n_name, n_desc in node_explanations:
            draw.rounded_rectangle([(rx + 25, ey), (rx + rw - 25, ey + 130)], radius=10, fill=(24, 34, 58), outline=(51, 65, 85), width=1)
            draw.text((rx + 40, ey + 18), n_name, fill=(56, 189, 248), font=font_mono_bold)
            
            words = n_desc.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) < 38:
                    cur += (" " if cur else "") + w
                else:
                    lines.append(cur)
                    cur = w
            if cur: lines.append(cur)
            for li, line in enumerate(lines):
                draw.text((rx + 40, ey + 55 + li * 24), line, fill=(203, 213, 225), font=get_font(FONT_SANS_PATH, 16))
            ey += 150

    # SCENE 3: Live Topic Echo & Sensor Streaming (17.5s - 24.5s)
    elif t < 24.5:
        draw_header(draw, "REAL-TIME TOPIC STREAMING & SENSOR TELEMETRY", "Streaming sensor_msgs and custom solar telemetry across ROS topics")
        
        # Terminal 1: Current Sensor Echo
        t1_x, t1_y = 60, 120
        t1_w, t1_h = 880, 910
        draw_terminal_window(draw, t1_x, t1_y, t1_w, t1_h, "Topic Echo: /solar/zone_1/current_sensor")
        
        y1 = t1_y + 55
        x1 = t1_x + 25
        draw.text((x1, y1), "appu@workstation:~$ ./ros2 topic echo /solar/zone_1/current_sensor", fill=(74, 222, 128), font=font_mono_small)
        y1 += 35
        draw.text((x1, y1), "--- Listening to topic [/solar/zone_1/current_sensor] ---", fill=(148, 163, 184), font=font_mono_small)
        y1 += 30
        
        sample_yaml_1 = [
            "header:",
            "  stamp:",
            f"    sec: {1791983000 + int(t)}",
            "    nanosec: 421098231",
            "  frame_id: 'panel_zone_1'",
            "zone_id: 1",
            "current_amperes: 1.82",
            "voltage_volts: 21.2",
            "is_drop_detected: True",
            "---",
            "header:",
            "  stamp:",
            f"    sec: {1791983001 + int(t)}",
            "    nanosec: 890123512",
            "  frame_id: 'panel_zone_1'",
            "zone_id: 1",
            "current_amperes: 1.79",
            "voltage_volts: 21.1",
            "is_drop_detected: True",
            "---"
        ]
        for yl in sample_yaml_1:
            col = (239, 68, 68) if "True" in yl or "1.82" in yl or "1.79" in yl else (248, 250, 252) if ":" in yl and not yl.startswith(" ") else (203, 213, 225)
            draw.text((x1, y1), yl, fill=col, font=font_mono)
            y1 += 26

        # Terminal 2: Weather & Joint States
        t2_x, t2_y = 980, 120
        t2_w, t2_h = 880, 440
        draw_terminal_window(draw, t2_x, t2_y, t2_w, t2_h, "Topic Echo: /weather/ambient_telemetry")
        
        y2 = t2_y + 55
        x2 = t2_x + 25
        draw.text((x2, y2), "appu@workstation:~$ ./ros2 topic echo /weather/ambient_telemetry", fill=(74, 222, 128), font=font_mono_small)
        y2 += 35
        
        sample_yaml_2 = [
            "header:",
            "  frame_id: 'weather_station_link'",
            "temperature_celsius: 33.1",
            "relative_humidity_pct: 46.8",
            "solar_irradiance_wm2: 852.4",
            "weather_condition: 'SUNNY / CLEAR'",
            "---"
        ]
        for yl in sample_yaml_2:
            col = (56, 189, 248) if "33.1" in yl or "852.4" in yl else (203, 213, 225)
            draw.text((x2, y2), yl, fill=col, font=font_mono)
            y2 += 26

        # Terminal 3: Joint States
        t3_y = 590
        draw_terminal_window(draw, t2_x, t3_y, t2_w, 440, "Topic Echo: /joint_states")
        y3 = t3_y + 55
        draw.text((x2, y3), "appu@workstation:~$ ./ros2 topic echo /joint_states", fill=(74, 222, 128), font=font_mono_small)
        y3 += 35
        
        sample_yaml_3 = [
            "header:",
            "  frame_id: 'base_link'",
            "name: ['waist_pan', 'shoulder', 'elbow', 'wrist_roll', 'wrist_pitch', 'tool']",
            "position: [2.408, 0.768, 2.932, 1.571, 2.461, -0.436]",
            "velocity: [0.0, 0.0, 0.0, 1.25, 0.0, 0.0]",
            "---"
        ]
        for yl in sample_yaml_3:
            draw.text((x2, y3), yl, fill=(203, 213, 225), font=font_mono)
            y3 += 26

    # SCENE 4: Interactive Demo Suite (./demo.sh) & Web Dashboard (24.5s - 29.5s)
    elif t < 29.5:
        draw_header(draw, "INTERACTIVE DEMO SUITE & WEB MOTOR DASHBOARD", "Quick-launch script and real-time PCA9685 slider interface")
        
        # Left: demo.sh terminal
        d_x, d_y = 60, 120
        d_w, d_h = 920, 910
        draw_terminal_window(draw, d_x, d_y, d_w, d_h, "Interactive Showcase Menu: ./demo.sh")
        
        dy = d_y + 55
        dx = d_x + 25
        draw.text((dx, dy), "appu@workstation:~/Downloads/robo_arm$ ./demo.sh", fill=(74, 222, 128), font=font_mono)
        dy += 35
        
        menu_lines = [
            "================================================================================",
            " ☀️  AUTONOMOUS SOLAR CLEANING ROBOTIC ARM — ROS 2 DEMO SUITE",
            "================================================================================",
            " Architecture Overview:",
            "   • 4 Solar Zones: Top-Left (0), Bottom-Left (1), Top-Right (2), Bottom-Right (3)",
            "   • 4 Current Sensors (Detects localized dust accumulation via current drop)",
            "   • Ambient Weather Station (Temperature, Humidity, Solar Irradiance)",
            "   • 6-DOF Robotic Arm with Autonomous Position Routine & Wrist Roll Actuator",
            "================================================================================",
            "",
            " Choose a demonstration action:",
            " [1] List Active ROS 2 Nodes        (./ros2 node list)",
            " [2] List Active ROS 2 Topics       (./ros2 topic list)",
            " [3] Stream Zone 0 Current Sensor   (./ros2 topic echo /solar/zone_0/current_sensor)",
            " [4] Stream Weather Telemetry       (./ros2 topic echo /weather/ambient_telemetry)",
            " [5] Stream Arm Joint States        (./ros2 topic echo /joint_states)",
            " [6] Stream Panel Dust Alerts       (./ros2 topic echo /cleaning/alert_dirty_panels)",
            " [7] Launch Motor Web Dashboard     (http://localhost:8000)",
            " [q] Quit",
            "--------------------------------------------------------------------------------",
            "Select option [1-7, q]: 1 █"
        ]
        for ml in menu_lines:
            col = (74, 222, 128) if "Select option" in ml else (255, 255, 255) if "Choose" in ml or "SOLAR" in ml else (203, 213, 225)
            draw.text((dx, dy), ml, fill=col, font=font_mono_small)
            dy += 27

        # Right: Web dashboard visual card
        wx, wy = 1020, 120
        ww, wh = 840, 910
        draw.rounded_rectangle([(wx, wy), (wx + ww, wy + wh)], radius=16, fill=(15, 23, 42), outline=(37, 99, 235), width=2)
        
        # Web Header
        draw.rounded_rectangle([(wx + 30, wy + 30), (wx + ww - 30, wy + 110)], radius=12, fill=(24, 34, 58))
        draw.text((wx + 50, wy + 45), "🌐 Web Controller Dashboard (Port 8000)", fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 24))
        draw.text((wx + 50, wy + 75), "http://localhost:8000 — Live PCA9685 Servo Slider Cockpit", fill=(148, 163, 184), font=get_font(FONT_SANS_PATH, 16))
        
        # Sliders representation
        sliders = [
            ("Waist Pan (Ch 0)", 138, 0, 360, "138°"),
            ("Shoulder (Ch 1)", 66, 0, 180, "66°"),
            ("Elbow (Ch 2)", 156, 0, 180, "156°"),
            ("Wrist Pitch (Ch 3)", 141, 0, 180, "141°"),
            ("Wrist Roll (Ch 4)", 90, 0, 180, "90° (Oscillating)"),
            ("Gripper Claw (Ch 5)", -25, -25, 110, "-25° (Clamped)"),
        ]
        sy = wy + 140
        for s_label, s_val, s_min, s_max, s_text in sliders:
            draw.text((wx + 50, sy), s_label, fill=(248, 250, 252), font=get_font(FONT_SANS_PATH, 18))
            draw.text((wx + ww - 230, sy), s_text, fill=(56, 189, 248), font=font_mono_bold)
            
            # Slider track
            track_w = ww - 100
            draw.rounded_rectangle([(wx + 50, sy + 32), (wx + 50 + track_w, sy + 44)], radius=6, fill=(30, 41, 59))
            
            # Slider fill
            pct = (s_val - s_min) / max(1, (s_max - s_min))
            fill_w = int(track_w * max(0.05, min(1.0, pct)))
            draw.rounded_rectangle([(wx + 50, sy + 32), (wx + 50 + fill_w, sy + 44)], radius=6, fill=(37, 99, 235))
            
            # Knob
            kx = wx + 50 + fill_w
            draw.ellipse([(kx - 8, sy + 28), (kx + 8, sy + 48)], fill=(255, 255, 255), outline=(37, 99, 235), width=2)
            
            sy += 90
            
        # Preset buttons preview
        draw.rounded_rectangle([(wx + 50, wy + wh - 120), (wx + 260, wy + wh - 50)], radius=10, fill=(22, 101, 52))
        draw.text((wx + 75, wy + wh - 95), "RUN AUTO CLEAN", fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 18))
        
        draw.rounded_rectangle([(wx + 290, wy + wh - 120), (wx + 500, wy + wh - 50)], radius=10, fill=(30, 58, 138))
        draw.text((wx + 340, wy + wh - 95), "HOME POSE", fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 18))
        
        draw.rounded_rectangle([(wx + 530, wy + wh - 120), (wx + ww - 50, wy + wh - 50)], radius=10, fill=(153, 27, 27))
        draw.text((wx + 580, wy + wh - 95), "EMERGENCY STOP", fill=(255, 255, 255), font=get_font(FONT_SANS_PATH, 18))

    # SCENE 5: Summary & Presentation Cheat Sheet (29.5s - 32.0s)
    else:
        draw_header(draw, "DEMONSTRATION COMPLETE — READY FOR PRESENTATION", "Summary of commands and GitHub project repository")
        
        cx, cy = 160, 160
        cw, ch = 1600, 800
        draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=20, fill=(15, 23, 42), outline=(34, 197, 94), width=3)
        
        draw.text((cx + 60, cy + 50), "✅ All Systems Operational & Pushed to GitHub", fill=(248, 250, 252), font=get_font(FONT_SANS_PATH, 40))
        draw.text((cx + 60, cy + 115), "GitHub Repository: https://github.com/Rakshi2609/robo_arm", fill=(56, 189, 248), font=get_font(FONT_SANS_PATH, 24))
        
        draw.line([(cx + 60, cy + 170), (cx + cw - 60, cy + 170)], fill=(51, 65, 85), width=2)
        
        cheatsheet = [
            ("1. Start Interactive Demo", "./demo.sh", "Presents single-key menu to demonstrate all ROS nodes, topics, and sensors"),
            ("2. Check Overall System Status", "./ros2", "Prints 4-zone current, dust percentage, alerts, and weather summary"),
            ("3. List ROS 2 Nodes", "./ros2 node list", "Displays all 5 active nodes (Broadcaster, Current Monitor, Executive, etc.)"),
            ("4. Stream Current Sensor", "./ros2 topic echo /solar/zone_0/current_sensor", "Shows real-time YAML messages with current drops on dirty panels"),
            ("5. Launch Web Controller", "python3 motor_web_app.py", "Opens real-time motor calibration dashboard at http://localhost:8000"),
            ("6. Arduino Firmware", "firmware/PostureGuard_Arm/PostureGuard_Arm.ino", "Autonomous 4-zone cleaning routine with alternating wrist roll")
        ]
        
        cy_item = cy + 200
        for title_step, cmd_str, desc_str in cheatsheet:
            draw.text((cx + 60, cy_item), title_step, fill=(241, 245, 249), font=get_font(FONT_SANS_PATH, 22))
            draw.text((cx + 520, cy_item), cmd_str, fill=(74, 222, 128), font=font_mono_bold)
            draw.text((cx + 1040, cy_item), desc_str, fill=(148, 163, 184), font=get_font(FONT_SANS_PATH, 16))
            cy_item += 85

    return img

def main():
    out_dir = "/tmp/solar_demo_frames"
    os.makedirs(out_dir, exist_ok=True)
    
    mp4_target = "/home/appu/Downloads/robo_arm/solar_cleaner_ros_demo.mp4"
    artifact_target = "/home/appu/.gemini/antigravity-cli/brain/e303c611-1793-452a-9856-35ea9afd0d69/solar_cleaner_ros_demo.mp4"
    
    print(f"[*] Generating {TOTAL_FRAMES} frames ({DURATION_SEC}s @ {FPS}fps)...")
    
    # We pipe frames directly to ffmpeg for maximum speed and memory efficiency
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        mp4_target
    ]
    
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    for f in range(TOTAL_FRAMES):
        frame_img = render_frame(f)
        process.stdin.write(frame_img.tobytes())
        if f % 150 == 0:
            print(f"  -> Processed {f}/{TOTAL_FRAMES} frames ({f/TOTAL_FRAMES*100:.1f}%)...")
            
    process.stdin.close()
    process.wait()
    print(f"[+] Video rendered successfully: {mp4_target}")
    
    # Copy to artifact directory for UI display
    subprocess.run(["cp", mp4_target, artifact_target], check=True)
    print(f"[+] Copied to artifact folder: {artifact_target}")

if __name__ == "__main__":
    main()
