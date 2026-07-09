
# RFID-Controlled Solenoid Access Circuit Package

## Goal
Design a circuit that energizes a 12 V cabinet-lock solenoid for a configurable time after a valid RFID card is scanned. Access should be granted only to cards whose UIDs are programmed into the controller.

## Assumptions
- Solenoid is a 12 V DC cabinet lock / pull-type lock.
- Control platform is an Arduino Nano compatible board.
- RFID reader is an MFRC522 module using SPI at 3.3 V logic.
- Main supply is a 12 V DC adapter.
- The Arduino Nano is powered from the 12 V input through its VIN pin for simplicity in a prototype-oriented build.
- A 3.3 V regulator is included for the MFRC522 because the reader module should not be powered from 5 V.
- The solenoid current is switched by a logic-level N-channel MOSFET with flyback diode protection.
- Solenoid energize interval default: 3 seconds, adjustable in firmware.
- This is a practical prototype / low-volume project package, not a certified production access-control design.

## Basic circuit description
The circuit has four functional blocks:

1. **Power input block**
   - A 12 V DC barrel jack feeds the system.
   - The 12 V rail powers the solenoid directly.
   - The Arduino Nano receives 12 V on VIN.
   - A 3.3 V regulator generates power for the MFRC522 RFID reader.
   - Bulk and local decoupling capacitors stabilize the rails.

2. **Controller and RFID block**
   - An Arduino Nano reads the MFRC522 through SPI.
   - SPI signals used: SDA/SS, SCK, MOSI, MISO, and RST.
   - The firmware compares the scanned card UID against an allowlist stored in code.

3. **Solenoid driver block**
   - Arduino digital output D3 drives the gate of a logic-level MOSFET through a series resistor.
   - The MOSFET low-side switches the solenoid current.
   - A flyback diode is connected across the solenoid coil to clamp inductive kick.
   - A gate pull-down resistor keeps the MOSFET off during reset.

4. **Status / user feedback block**
   - A green LED indicates access granted.
   - A red LED indicates access denied.
   - A piezo buzzer can optionally beep on accept/reject events.

## Pin mapping
- MFRC522 SDA/SS -> Arduino D10
- MFRC522 SCK -> Arduino D13
- MFRC522 MOSI -> Arduino D11
- MFRC522 MISO -> Arduino D12
- MFRC522 RST -> Arduino D9
- Solenoid MOSFET gate -> Arduino D3
- Green LED -> Arduino D5 through resistor
- Red LED -> Arduino D6 through resistor
- Buzzer -> Arduino D7 (optional)

## Main components
- Arduino Nano
- MFRC522 RFID module
- 12 V cabinet lock solenoid
- IRLZ44N logic-level N-channel MOSFET
- 1N5408 flyback diode
- LM1117-3.3 or AMS1117-3.3 regulator module / TO-220 style board option
- LEDs, resistors, screw terminals, DC jack, capacitors

## Firmware need
Yes. Firmware is required to:
- initialize the RFID reader
- read card UIDs
- compare against authorized UID list
- energize solenoid for a timed interval
- drive status indicators
- optionally print debug events over serial

## Important unknowns / checks
- Exact solenoid hold current should be verified before final hardware procurement.
- If the solenoid current exceeds roughly 2-3 A, a lower-Rds(on) MOSFET and heavier wiring may be preferred.
- Many MFRC522 breakout boards are not 5 V tolerant on logic inputs; level-shifting is advisable for robust production use. For a simple prototype package, resistor-divider level reduction on Nano->reader lines is included.
- For production door access systems, use a dedicated lock supply, surge suppression, tamper monitoring, and secure credential storage.
