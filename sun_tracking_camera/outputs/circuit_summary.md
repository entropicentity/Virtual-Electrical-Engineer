# Sun-Tracking Camera Design Package

## Goal
Design a prototype sun-tracking camera using an ESP32-CAM module, a two-axis pan/tilt mechanism, and four light sensors so the camera can automatically steer toward the brightest direction while providing live image capture over Wi-Fi.

## Assumptions
- User selected a prototype dev-board style implementation.
- Power source is a regulated 5 V DC adapter.
- This is a conceptual/prototyping package, not a production-ready outdoor engineering release.
- Exact supplier stock and pricing were not verified live; links are representative product pages.
- Chosen controller is AI-Thinker ESP32-CAM, which commonly requires a strong 5 V supply because camera + Wi-Fi + servo transients can cause brownouts.
- Two SG90 micro servos are acceptable for lightweight indoor demonstration mechanics.

## Basic circuit description
The design has four main blocks:

1. **5 V power distribution**: A 5 V / >=2 A adapter feeds the ESP32-CAM 5 V pin and both SG90 servos in parallel. A 470 uF bulk capacitor and 100 nF bypass capacitor are placed across the 5 V rail near the servo/header area to suppress supply dips and high-frequency noise.

2. **Camera/control block**: An AI-Thinker ESP32-CAM module serves as the central processor and image sensor. It streams video over Wi-Fi and reads four analog voltages from light-dependent resistor divider networks. It also generates PWM outputs for the two servo control lines.

3. **Sun direction sensing block**: Four LDRs are arranged physically in a quadrant around a small vertical shade cross. Each LDR is paired with a 10 kOhm resistor to form a voltage divider. Differential comparison of left-vs-right and top-vs-bottom light levels estimates where the sun is relative to the current pointing direction.

4. **Actuation block**: Two SG90 servos move the pan and tilt axes. The ESP32-CAM drives one servo for azimuth and one for elevation. Control firmware moves only in small steps when light imbalance exceeds a threshold, reducing jitter.

### Recommended signal assignments
Because ESP32-CAM pin availability is constrained by the camera interface, use a build that exposes ADC-capable pins for the four LDR dividers and two PWM-capable GPIOs for servos. A practical prototype assumption is:
- Pan servo signal: GPIO14
- Tilt servo signal: GPIO15
- LDR dividers: ADC-capable available inputs on the chosen ESP32-CAM breakout/carrier implementation

If the specific carrier board does not expose enough ADC pins, add a small external ADC (for example ADS1115 over I2C) or use an ESP32 camera board variant with more broken-out pins.

## Main components
- U1: ESP32-CAM AI-Thinker module with OV2640 camera
- M1, M2: SG90 5 V micro servos
- R1-R4: LDR sensors in four-quadrant layout
- R5-R8: 10 kOhm divider resistors
- C1: 470 uF electrolytic bulk capacitor
- C2: 100 nF ceramic bypass capacitor
- J1: 5 V DC input connector
- J2, J3: servo headers
- J4: FTDI programming header
- MECH1: pan-tilt bracket

## Important unknowns / limitations
- A bare ESP32-CAM board has limited accessible ADC pins; the final wiring may depend on the exact carrier/backplane used.
- SG90 servos are acceptable for a lightweight camera head, but wind loading or outdoor use may require metal-geared servos and a separate servo supply rail.
- LDR-based solar pointing is simple but not high precision. For astronomy-grade solar tracking, use ephemeris/GPS/RTC or a calibrated sun sensor.
- Outdoor deployment would require enclosure, UV/weather protection, cable strain relief, thermal design, and likely different mechanics.

## Firmware concept
- Read four sensor voltages repeatedly.
- Compute horizontal error = (right pair average) - (left pair average).
- Compute vertical error = (top pair average) - (bottom pair average).
- If horizontal error exceeds threshold, increment/decrement pan servo.
- If vertical error exceeds threshold, increment/decrement tilt servo.
- Stream images over Wi-Fi for observation and tuning.
- Optionally add deadband and time averaging to prevent oscillation.
