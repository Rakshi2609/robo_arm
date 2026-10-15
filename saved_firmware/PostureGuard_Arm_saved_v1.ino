/*
  PostureGuard - Autonomous Standalone Cleaning & Random Positioning Firmware
  Hardware: Arduino Uno + PCA9685 16-Channel PWM Servo Driver (I2C 0x40)

  Operation:
    - Runs 100% standalone on wall adapter / power bank (no computer required).
    - Random state generator (0 to 5):
        0: Left Top      (Base: 138°, Shoulder: 44°, Elbow: 168°, Pitch: 141°, Claw: -25°)
        1: Left Bottom   (Base: 138°, Shoulder: 66°, Elbow: 156°, Pitch: 141°, Claw: -25°)
        2: Right Top     (Base: 96°,  Shoulder: 44°, Elbow: 168°, Pitch: 141°, Claw: -25°)
        3: Right Bottom  (Base: 96°,  Shoulder: 66°, Elbow: 156°, Pitch: 141°, Claw: -25°)
        4: Home Resting  (Base: 90°,  Shoulder: 135°, Elbow: 180°, Pitch: 90°,  Claw: -25°)
        5: Home Resting  (Base: 90°,  Shoulder: 135°, Elbow: 180°, Pitch: 90°,  Claw: -25°)
    - Wrist Roll (Channel 3 - SG90 360°):
        Cycles continuously: 3.0 seconds ON (spinning) -> 2.0 seconds OFF (pause).
    - Staged, smooth robotic interpolation to prevent current brownouts and arm jerking.
*/

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// Hardware Channels
const int CH_WAIST    = 0; // Base 360° Continuous Servo
const int CH_SHOULDER = 1; // MG995 High Torque (180° Positional)
const int CH_ELBOW    = 2; // MG995 High Torque (180° Positional)
const int CH_WRIST_3  = 3; // Wrist Roll (SG90 Continuous)
const int CH_WRIST_4  = 4; // Wrist Pitch (SG90 180° Positional)
const int CH_GRIPPER  = 5; // Gripper Claw (MG90S Positional)

// PWM & Calibration Constants
#define SERVOMIN   140
#define SERVOMAX   580
#define SERVO_FREQ 50
#define STOP_PULSE 0

// Continuous Rotation Pulses around Neutral (~307)
#define NEUTRAL_PULSE        307
#define BASE_CRUISE_OFFSET   95
#define BASE_CW_CRUISE       (NEUTRAL_PULSE + BASE_CRUISE_OFFSET)
#define BASE_CCW_CRUISE      (NEUTRAL_PULSE - BASE_CRUISE_OFFSET)
#define WRIST3_CRUISE_OFFSET 52
#define WRIST3_CW_CRUISE     (NEUTRAL_PULSE + WRIST3_CRUISE_OFFSET)
#define WRIST3_CCW_CRUISE    (NEUTRAL_PULSE - WRIST3_CRUISE_OFFSET)

#define MS_PER_DEG_BASE      20

// Timing Configuration
const unsigned long WRIST_ROLL_ON_MS   = 3000; // 3 seconds spinning
const unsigned long WRIST_ROLL_OFF_MS  = 2000; // 2 seconds stopped
const unsigned long POSE_HOLD_TIME_MS  = 4500; // Hold each position for 4.5 seconds

// State Tracking
int curAngleCh0 = 90;
int curAngleCh1 = 135;
int curAngleCh2 = 180;
int curAngleCh4 = 90;
int curAngleCh5 = -25;

unsigned long lastWristRollToggle = 0;
bool isWristRolling = false;
int wristRollDir = 1; // 1 = CW, -1 = CCW

unsigned long lastPoseChangeTime = 0;
int currentPosState = -1;

// Pulse Mapping Helper
int angleToPulse(int ang, int ch = -1) {
  ang = constrain(ang, -45, 180);
  if (ch == 1 || ch == 2) {
    // Dampened travel for MG995 high-torque shoulder and elbow
    return map(ang, 0, 180, 150, 500);
  }
  return map(ang, 0, 180, SERVOMIN, SERVOMAX);
}

// Low-level smooth Base Pan
void rotateBaseSmooth(int dir, int totalMs) {
  if (totalMs <= 0) return;
  int pulse = (dir > 0) ? BASE_CW_CRUISE : BASE_CCW_CRUISE;
  pwm.setPWM(CH_WAIST, 0, pulse);
  delay(totalMs);
  pwm.setPWM(CH_WAIST, 0, STOP_PULSE);
}

void moveBaseTo(int targetAngle) {
  targetAngle = constrain(targetAngle, 0, 360);
  int delta = targetAngle - curAngleCh0;
  if (delta == 0) return;
  int durationMs = abs(delta) * MS_PER_DEG_BASE;
  if (durationMs < 30) durationMs = 30;
  rotateBaseSmooth(delta > 0 ? 1 : -1, durationMs);
  curAngleCh0 = targetAngle;
}

// Low-level Positional Joint Movement with Ease Step
void moveJointSmooth(int ch, int fromAngle, int toAngle, int stepDelay = 12) {
  toAngle = constrain(toAngle, 0, 180);
  int step = (toAngle >= fromAngle) ? 1 : -1;
  for (int a = fromAngle; a != toAngle; a += step) {
    pwm.setPWM(ch, 0, angleToPulse(a, ch));
    delay(stepDelay);
  }
  pwm.setPWM(ch, 0, angleToPulse(toAngle, ch));
  delay(50);
}

void setPositional(int ch, int targetAngle) {
  targetAngle = constrain(targetAngle, 0, 180);
  int from = 90;
  if (ch == 1) { from = curAngleCh1; curAngleCh1 = targetAngle; }
  else if (ch == 2) { from = curAngleCh2; curAngleCh2 = targetAngle; }
  else if (ch == 4) { from = curAngleCh4; curAngleCh4 = targetAngle; }

  moveJointSmooth(ch, from, targetAngle, 12);
}

void setGripper(int targetAngle) {
  targetAngle = constrain(targetAngle, -45, 180);
  pwm.setPWM(CH_GRIPPER, 0, angleToPulse(targetAngle));
  curAngleCh5 = targetAngle;
  delay(200);
}

// Updates Wrist Roll in Background (Non-blocking: 3s ON / 2s OFF)
void updateWristRollBackground() {
  unsigned long now = millis();
  if (isWristRolling) {
    if (now - lastWristRollToggle >= WRIST_ROLL_ON_MS) {
      // 3s ON elapsed -> Turn OFF
      pwm.setPWM(CH_WRIST_3, 0, STOP_PULSE);
      isWristRolling = false;
      lastWristRollToggle = now;
      // Alternate direction between cycles for balanced cable tension
      wristRollDir = -wristRollDir;
    }
  } else {
    if (now - lastWristRollToggle >= WRIST_ROLL_OFF_MS) {
      // 2s OFF elapsed -> Turn ON
      int pulse = (wristRollDir > 0) ? WRIST3_CW_CRUISE : WRIST3_CCW_CRUISE;
      pwm.setPWM(CH_WRIST_3, 0, pulse);
      isWristRolling = true;
      lastWristRollToggle = now;
    }
  }
}

// Master Function: Transition smoothly to any of the 6 States
void moveToState(int state) {
  Serial.print(F("[STATE CHANGE] Target State: "));
  Serial.print(state);

  int targetBase     = 90;
  int targetShoulder = 135;
  int targetElbow    = 180;
  int targetPitch    = 90;
  int targetClaw     = -25;

  switch (state) {
    case 0:
      // State 0: Left Top
      Serial.println(F(" -> LEFT TOP (Base 138, Sh 44, El 168, Pi 141)"));
      targetBase     = 138;
      targetShoulder = 44;
      targetElbow    = 168;
      targetPitch    = 141;
      targetClaw     = -25;
      break;

    case 1:
      // State 1: Left Bottom
      Serial.println(F(" -> LEFT BOTTOM (Base 138, Sh 66, El 156, Pi 141)"));
      targetBase     = 138;
      targetShoulder = 66;
      targetElbow    = 156;
      targetPitch    = 141;
      targetClaw     = -25;
      break;

    case 2:
      // State 2: Right Top
      Serial.println(F(" -> RIGHT TOP (Base 96, Sh 44, El 168, Pi 141)"));
      targetBase     = 96;
      targetShoulder = 44;
      targetElbow    = 168;
      targetPitch    = 141;
      targetClaw     = -25;
      break;

    case 3:
      // State 3: Right Bottom
      Serial.println(F(" -> RIGHT BOTTOM (Base 96, Sh 66, El 156, Pi 141)"));
      targetBase     = 96;
      targetShoulder = 66;
      targetElbow    = 156;
      targetPitch    = 141;
      targetClaw     = -25;
      break;

    case 4:
    case 5:
    default:
      // State 4 & 5: Home / Rest Dock
      Serial.println(F(" -> HOME RESTING DOCK (Base 90, Sh 135, El 180, Pi 90)"));
      targetBase     = 90;
      targetShoulder = 135;
      targetElbow    = 180;
      targetPitch    = 90;
      targetClaw     = -25;
      break;
  }

  // Staged Motion Sequence for mechanical safety:
  // Step 1: Claw firm clamp
  setGripper(targetClaw);
  updateWristRollBackground();

  // Step 2: Wrist Pitch
  setPositional(CH_WRIST_4, targetPitch);
  updateWristRollBackground();

  // Step 3: Base Pan to target azimuth
  moveBaseTo(targetBase);
  updateWristRollBackground();

  // Step 4: Elbow flexion / extension
  setPositional(CH_ELBOW, targetElbow);
  updateWristRollBackground();

  // Step 5: Shoulder elevation / reach
  setPositional(CH_SHOULDER, targetShoulder);
  updateWristRollBackground();

  currentPosState = state;
}

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(A0) ^ analogRead(A1));

  Wire.begin();
  delay(100);

  pwm.begin();
  pwm.setOscillatorFrequency(25000000);
  pwm.setPWMFreq(SERVO_FREQ);

  // Safety initial cutoff
  for (int i = 0; i < 16; i++) {
    pwm.setPWM(i, 0, STOP_PULSE);
  }

  Serial.println(F("=================================================="));
  Serial.println(F(" 🦾 POSTUREGUARD AUTONOMOUS CLEANING FIRMWARE"));
  Serial.println(F(" Random States (0..5) + Auto Roll 3s ON / 2s OFF"));
  Serial.println(F(" Standalone Wall-Adapter Compatible"));
  Serial.println(F("=================================================="));

  delay(1200); // Power stabilization delay

  // Initialize Home
  moveToState(4);

  // Start Wrist Roll timer
  lastWristRollToggle = millis();
  isWristRolling = true;
  int pulse = (wristRollDir > 0) ? WRIST3_CW_CRUISE : WRIST3_CCW_CRUISE;
  pwm.setPWM(CH_WRIST_3, 0, pulse);

  lastPoseChangeTime = millis();
}

void loop() {
  // 1. Maintain background Wrist Roll (3s ON -> 2s OFF non-blocking)
  updateWristRollBackground();

  // 2. Autonomous Periodic Position Switch
  unsigned long now = millis();
  if (now - lastPoseChangeTime >= POSE_HOLD_TIME_MS) {
    // Pick next random state (0, 1, 2, 3, 4, 5) ensuring it picks a new position
    int nextState;
    do {
      nextState = random(0, 6);
    } while (nextState == currentPosState);

    moveToState(nextState);
    lastPoseChangeTime = millis();
  }

  // 3. Optional Serial Command overrides if connected to PC
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();
    if (cmd == "HOME") {
      moveToState(4);
      lastPoseChangeTime = millis();
    } else if (cmd == "0" || cmd == "LEFT TOP") {
      moveToState(0);
      lastPoseChangeTime = millis();
    } else if (cmd == "1" || cmd == "LEFT BOTTOM") {
      moveToState(1);
      lastPoseChangeTime = millis();
    } else if (cmd == "2" || cmd == "RIGHT TOP") {
      moveToState(2);
      lastPoseChangeTime = millis();
    } else if (cmd == "3" || cmd == "RIGHT BOTTOM") {
      moveToState(3);
      lastPoseChangeTime = millis();
    } else if (cmd == "STOP") {
      pwm.setPWM(CH_WRIST_3, 0, STOP_PULSE);
      for (int i = 0; i < 16; i++) pwm.setPWM(i, 0, STOP_PULSE);
    }
  }

  delay(20);
}
