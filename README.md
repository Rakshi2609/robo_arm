# 🦾 Cyber-Arm 6-DOF // PCA9685 Robotic Cockpit

An advanced, gamified web application and Arduino firmware system to control a 6-Degree-of-Freedom (6-DOF) robotic arm using an **Arduino Uno** and **PCA9685 16-Channel 12-Bit PWM Driver**.

Features a **3D WebGL Digital Twin**, **Live Angle Gauges & Glowing Sliders**, **Procedural Web Audio API Sound Effects**, **Gamepad / Flight Stick Support**, a **Pick & Place Gamified Mission Arena**, and an industrial **Teach Pendant Sequencer**.

---

## ⚡ Hardware Connections & Wiring Specifications

### 1. Arduino Uno → PCA9685 (Logic & I2C)
| Arduino Uno Pin | PCA9685 Pin | Typical Wire Color | Function |
|---|---|---|---|
| **5V** | **VCC** | Red | +5V Logic Power (powers PCA9685 chip) |
| **GND** | **GND** | Black | Common Logic Ground |
| **A4** (or dedicated SDA) | **SDA** | Blue / Green | I2C Data Line |
| **A5** (or dedicated SCL) | **SCL** | Yellow | I2C Clock Line |

---

### 2. External Power Supply (5V / 4A–5A) → PCA9685 (Servo Power)
> [!CAUTION]
> **NEVER power servos directly from the Arduino 5V pin!** High inrush currents will cause brown-out resets on the Arduino and can damage the regulator. Connect an external 5V power supply to the PCA9685 screw terminal.

| External PSU Terminal | PCA9685 Terminal | Description |
|---|---|---|
| **+5V (V+)** | **V+** (Screw Terminal) | High-current power rail dedicated to servos |
| **GND (0V)** | **GND** (Screw Terminal) | High-current power return |
| **Arduino GND** | **PCA9685 GND** | Common Ground Tie (prevents floating voltages and servo jitter) |
| **1000 µF Capacitor (+)** | **V+** | Filter capacitor across screw terminal to absorb motor spikes |
| **1000 µF Capacitor (-)** | **GND** | Filter capacitor ground |

---

### 3. PCA9685 Servo Channels (3-Pin Headers: Signal, V+, GND)
Standard 3-pin servo plug orientation:
- **Yellow / Orange wire** → **PWM Signal pin** (top row)
- **Red wire** → **V+** (middle row)
- **Brown / Black wire** → **GND** (bottom row)

| Channel | Arm Joint | Motor Model | Operating Range | Function |
|---|---|---|---|---|
| **Channel 0** | Base / Waist Pan | 360° Continuous Servo | **0° – 360°** | Full azimuth rotational sweep |
| **Channel 1** | Shoulder Joint | MG995 High-Torque Metal Gear | **0° – 180°** | Main arm boom elevation |
| **Channel 2** | Elbow Joint | MG995 High-Torque Metal Gear | **0° – 180°** | Forearm flexion & extension |
| **Channel 3** | Wrist Roll | SG90 Micro Servo | **0° – 180°** | End-effector axial rotation |
| **Channel 4** | Wrist Pitch | SG90 Micro Servo | **0° – 180°** | End-effector vertical angle |
| **Channel 5** | Gripper Claw | MG90S Metal-Gear Micro | **-25° – 110°** | Claw jaw opening & closing |

---

### 4. Host PC → Arduino Uno
- **Connection**: USB Type-A to Type-B cable (e.g. `/dev/ttyACM0` or `/dev/ttyACM1` on Linux)
- **Baud Rate**: **115200 baud** (8-N-1)

---

## 🚀 Quick Start

### 1. Start the Web App
From the project directory:
```bash
./start.sh
```
*(Or manually: `python3 server.py`)*

Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

### 2. Upload / Flash Firmware to Arduino Uno
You can upload the firmware directly from the **Web UI** by clicking the **"⚡ Upload Firmware"** button in the top bar, or via terminal using `arduino-cli`:
```bash
arduino-cli compile -b arduino:avr:uno firmware/robotic_arm_firmware
arduino-cli upload -p /dev/ttyACM1 -b arduino:avr:uno firmware/robotic_arm_firmware
```

---

## 🎮 Features & Control Matrix

### 🎛️ 1. Gamified Joint Controls
- **Live Angle Feedback**: Big numerical readout showing current interpolated angle (e.g. `142.5°`) alongside target angle.
- **Dynamic Dial Gauges**: Circular SVG arcs that fill and deplete smoothly in real time.
- **Cyberpunk Glowing Sliders**: Tactile sliders with customizable neon track fills.
- **Fine-Tune Steppers**: `[-5°]`, `[-1°]`, `[+1°]`, `[+5°]` buttons for precision positioning.
- **Snap Buttons**: `MIN`, `MID`, `MAX` one-click presets for each joint.
- **Quick Grip Toggle**: Big instant action button for the Gripper Claw (or press **Spacebar**).
- **Diagnostics Ticker**: Real-time pulse microseconds (`µs`) and PCA9685 tick value (`ticks / 4096`).

### 🦾 2. 3D Digital Twin Viewport (Three.js)
- Fully articulated 6-DOF mechanical robot arm model matching actual link kinematics.
- Real-time Forward Kinematics solver displaying End-Effector Cartesian coordinates (**X, Y, Z mm**, Reach, and Claw aperture %).
- Camera Orbit Controls: Orbit, zoom, pan, and view presets (`Perspective`, `Top`, `Side`).

### 🎯 3. "Robo-Ops" Gamified Pick & Place Mission Arena
- Interactive physics mini-game:
  1. Virtual **Energon Cubes** spawn on the work surface.
  2. Navigate the arm and clamp the claw onto the target cube.
  3. Carry the cube and release it inside the **Green Drop Bin**.
  4. Build score combos and streaks (`1x`, `2x`, `3x...`) with celebratory chime chords!

### 🔊 4. Procedural Web Audio API Sound Effects
- Synthesized **servo motor hum** whose pitch and volume scale dynamically with arm speed.
- Metallic **claw clamp snaps**, UI clicks, success chimes, and **E-STOP alarm siren**.
- One-click mute/unmute toggle in header.

### 🕹️ 5. Console Gamepad & Keyboard Support
- **Gamepad API**: Connect any USB or Bluetooth Xbox, PlayStation, or generic gamepad.
  - **Left Stick**: Base Pan (X) & Shoulder (Y)
  - **Right Stick**: Elbow (Y) & Wrist Roll (X)
  - **D-Pad Up/Down**: Wrist Pitch
  - **Triggers / Bumpers**: Gripper Claw Open / Close
  - **B Button**: Emergency Stop
- **Keyboard Hotkeys**:
  - `A` / `D`: Base Pan Left / Right
  - `W` / `S`: Shoulder Up / Down
  - `Q` / `E`: Elbow Up / Down
  - `R` / `F`: Wrist Pitch Up / Down
  - `Z` / `C`: Wrist Roll Left / Right
  - `Spacebar`: Toggle Gripper Claw
  - `Escape`: Emergency Stop (E-STOP)

### 🤖 6. Teach Pendant & Choreography Sequencer
- **Record Keyframes**: Pose the arm and click **"➕ Record Keyframe"**.
- **Choreography Library**: Built-in routines for **"Wave Greeting"**, **"Pick & Place Cycle"**, and **"Cyber Dance"**.
- **Pose Presets**: Quick launch for *Home Standby*, *Rest/Folded*, *Ready/Reach*, *Pick Table*, *Lift High*, *Bin Drop*, *Salute*, and *Look Around*.

### 🛑 7. Big Red Emergency Stop (E-STOP)
- Instant halt for all servos and trajectory interpolation.
- Visual pulsing red hazard state and sound alert.

### 🔌 8. Hardware vs. Virtual Simulation Mode
- If an Arduino Uno is connected on `/dev/ttyACM1` or `/dev/ttyACM0`, commands are sent directly to the PCA9685 chip.
- If disconnected or tested without hardware, the system seamlessly runs in **Virtual Simulation Mode** using the kinematic physics engine, so the entire interface and 3D simulation work anytime.
