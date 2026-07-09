# Too-Close Scanning Alarm Circuit Package

## Goal
Build a battery-powered device that scans its surroundings, detects when a person or object is closer than about 1 meter, and sounds an audible alarm.

## Assumptions
- The device should actively "look around," so the distance sensor is mounted on a small servo that sweeps left/right.
- Battery-powered operation is desired; this package uses a 2-cell lithium battery feeding a 5 V buck regulator.
- Prototype / hobby build using widely available modules.
- Target detection threshold: approximately 1.0 m.
- This is a concept-level package suitable for breadboard or perfboard build, not a production safety device.

## Basic circuit description
The circuit is organized into five blocks:
1. Power: a 2-cell battery pack and switch feed a 5 V buck regulator.
2. Controller: an Arduino Nano reads the sensor and controls outputs.
3. Scanning sensor head: an HC-SR04 ultrasonic module mounted on an SG90 micro servo.
4. Alarm output: a 5 V active buzzer driven from an Arduino digital pin.
5. Stability parts: a 470 uF bulk capacitor near the servo supply and a 0.1 uF ceramic bypass capacitor on the 5 V rail.

During operation, the Arduino sweeps the servo through a viewing arc of roughly 30° to 150°. At each angle it triggers the HC-SR04 and reads the echo pulse to estimate distance. If any valid reading is below the threshold, the Arduino drives the buzzer with an intermittent warning pattern. Otherwise it continues scanning silently.

## Pin map
- D3: servo signal
- D6: active buzzer control
- D9: HC-SR04 TRIG
- D10: HC-SR04 ECHO
- 5V: powers Arduino, servo, HC-SR04, and buzzer
- GND: common return for all blocks

## Limitations
- HC-SR04 performance can degrade on soft or angled targets.
- A small SG90 servo introduces power noise; the bulk capacitor is important.
- Battery runtime depends strongly on servo duty cycle and buzzer activity.
