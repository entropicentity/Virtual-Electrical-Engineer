
# RFID Solenoid Access Controller - Revised Design

## Goal
Unlock a 12 V fail-secure cabinet solenoid for a short interval when an MFRC522 RFID reader detects a card whose UID matches one of the authorized UIDs stored in firmware.

## Revised design choices
- Produce a **real electrical schematic-style drawing** rather than a block diagram.
- Use an Arduino Nano for simple field programmability.
- Power the MFRC522 from a dedicated 3.3 V rail.
- Add resistor-divider level reduction on Nano outputs going into the MFRC522 inputs.
- Switch the solenoid with a low-side logic-level MOSFET and a flyback diode.
- Include LED indicators and optional buzzer.

## Electrical assumptions
- Supply: 12 V DC adapter.
- Solenoid: 12 V cabinet lock, intermittent duty, 0.4 A to 1.0 A typical.
- Nano VIN is fed from 12 V only for a prototype-grade design. A buck converter to 5 V would be better for continuous-duty production use.
- MFRC522 breakout is treated as a 3.3 V-only module.

## Pin map
- D10 -> RC522 SDA/SS (through divider)
- D13 -> RC522 SCK (through divider)
- D11 -> RC522 MOSI (through divider)
- D12 <- RC522 MISO (direct)
- D9  -> RC522 RST (through divider)
- D3  -> MOSFET gate
- D5  -> Green LED
- D6  -> Red LED
- D7  -> Active buzzer (optional)

## Notes
- UID-only authorization is easy to implement but weak against cloning; sector authentication or a more secure RFID/NFC platform is preferable for serious access control.
- A door sensor and egress logic are not included here.
