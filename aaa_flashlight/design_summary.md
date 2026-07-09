# Simple AAA Battery Flashlight
## Goal
Create a simple manual flashlight powered by AAA batteries.
## Assumptions
- Flashlight uses three AAA alkaline cells in series for a nominal 4.5 V source.
- The flashlight is a simple manual on/off design with no microcontroller.
- LED chosen as a standard white 5 mm LED around 20 mA nominal current.
- A single series resistor is used to set LED current conservatively for typical battery voltage.
- Mechanical enclosure and reflector details are out of scope; this package focuses on the electrical design.
## Basic circuit description
Three AAA batteries in series provide the flashlight supply. The positive battery terminal feeds an SPST switch. The switch output connects to resistor R1, which limits current into the white LED D1. The LED cathode returns to the battery negative terminal. This creates a minimal manual flashlight with one controlled light output path and no programmable electronics.
## Main components
- 3x AAA battery holder
- SPST switch
- White LED
- Series resistor
## Firmware need
No firmware required; behavior is fully defined by the passive/manual circuit.
## BOM total
Estimated total: $5.35