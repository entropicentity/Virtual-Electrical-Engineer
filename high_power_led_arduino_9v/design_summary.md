# Arduino-Controlled High-Power LED from 9 V Battery
## Goal
Use an Arduino to switch a high-power LED from a 9 V battery source.
## Assumptions
- Battery source is a 9 V DC battery or equivalent 9 V supply.
- High-power LED assumed to be a 1 W class white LED around 3.2 V forward voltage at about 350 mA.
- Arduino is assumed to be an Arduino Uno/Nano class 5 V board.
- Because a high-power LED should not be driven directly from an Arduino pin, the LED is switched with a logic-level N-channel MOSFET.
- LED current is limited with a dedicated series resistor for a simple buildable design; a constant-current driver would be a better production choice.
- Arduino is powered from the same 9 V source through VIN/barrel input for conceptual simplicity.
## Basic circuit description
A 9 V battery feeds both the Arduino input supply and the high-power LED power path. The LED positive terminal connects to +9V through a high-power series resistor R1. The LED negative terminal connects to the drain of logic-level N-MOSFET Q1. The MOSFET source goes to ground. Arduino digital pin D9 drives the MOSFET gate through R2, while R3 pulls the gate to ground so the LED stays off at boot. Battery negative, Arduino ground, and MOSFET source share common ground. C1 provides bulk supply decoupling on the 9 V rail and C2 provides local bypass support.
## Pin map
- D9 -> R2 -> Q1 gate
- GND -> Q1 source / R3 / battery negative common ground
- VIN (or barrel input) <- +9V battery
## BOM total
Estimated total: $17.35