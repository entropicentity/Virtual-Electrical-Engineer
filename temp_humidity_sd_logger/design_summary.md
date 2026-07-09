# Temperature and Humidity Logger with SD Card
## Goal
USB-powered logger that measures ambient temperature and relative humidity and periodically stores readings to a microSD card.
## Assumptions
- USB-powered 5 V design intended for indoor or sheltered use.
- Cost was prioritized over premium metrology performance while still targeting practical accuracy near 0.1 °C display resolution and about 1-2 %RH class sensor performance.
- Sensor chosen: Sensirion SHT31-D breakout/module because it is typically more accurate and more stable than DHT-class parts while remaining affordable.
- Microcontroller chosen: Arduino Nano compatible board for easy SD logging and broad library support.
- MicroSD module assumed to be a common SPI breakout with onboard 3.3 V regulator and level shifting for 5 V Arduino compatibility.
- This is a conceptual but buildable package, not a certified production release.

## Basic circuit description
An Arduino Nano supplies system control. An SHT31-D breakout connects over I2C for digital temperature/humidity measurements. A microSD breakout connects over SPI for storage. USB provides 5 V input to the Nano and SD module; the SHT31 module is powered from the Nano 3.3 V rail to match the sensor breakout. Shared ground ties all blocks together. Local bulk and bypass capacitance stabilize the supply near the SD module.

## Pin map
- A4 -> SDA -> SHT31 SDA
- A5 -> SCL -> SHT31 SCL
- D10 -> SD CS
- D11 -> SD MOSI
- D12 -> SD MISO
- D13 -> SD SCK

## BOM total
Estimated total: $25.75
