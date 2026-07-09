# Programmable 4-Wheel Toy Car Control Circuit Package

## Goal
A beginner-friendly programmable car using two driven rear wheels, two free-rolling front wheels, an ESP32 controller, and a TB6612FNG dual motor driver.

## Assumptions
- Drive layout assumed: 2WD differential drive with one DC gear motor on the left side and one on the right side; front wheels are passive.
- Programming platform chosen: Arduino-compatible ESP32 dev board because it is easy to program and has enough PWM-capable GPIO for motor control.
- Battery assumed: 2-cell 18650 holder in series for about 7.4 V nominal, 8.4 V fully charged.
- Motor type assumed: common TT-style brushed DC gear motors rated for about 3-6 V operation.
- This is a concept/prototyping package, not a production automotive or toy safety certification package.
- Links are representative product pages from common vendors or manufacturers; live stock and exact price were not independently verified at delivery time.

## Basic circuit description
- The battery pack feeds a master power switch. After the switch, the raw battery line powers the motor supply input of the TB6612FNG motor driver.
- The same switched battery line also feeds an LM2596 buck converter adjusted to 5 V. That regulated 5 V rail powers the ESP32 dev board through its 5V/VIN input and powers the TB6612FNG logic VCC pin.
- The ESP32 drives PWMA, AIN1, AIN2, PWMB, BIN1, BIN2, and STBY on the TB6612FNG. This allows independent speed and direction control of the left and right motors.
- Each motor output from the TB6612FNG connects to one TT motor. Grounds for battery, buck converter, motor driver, and ESP32 are all tied together.
- Bulk and decoupling capacitors are included near the motor supply and logic rail to reduce resets and noise from the brushed motors.

## Suggested ESP32 to motor-driver pin map

| ESP32 | TB6612FNG | Purpose |
|---|---|---|
| GPIO25 | PWMA | Left motor PWM |
| GPIO26 | AIN1 | Left motor direction 1 |
| GPIO27 | AIN2 | Left motor direction 2 |
| GPIO14 | PWMB | Right motor PWM |
| GPIO12 | BIN1 | Right motor direction 1 |
| GPIO13 | BIN2 | Right motor direction 2 |
| GPIO33 | STBY | Driver standby enable |

## Output files
- Schematic: `toy_car_schematic.png`
- BOM CSV: `toy_car_bom.csv`
- PDF package: `toy_car_circuit_package.pdf`