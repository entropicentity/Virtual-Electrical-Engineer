# Rangefinder with Screen and Trigger Button
## Goal
Create a compact USB-powered rangefinder that measures distance on demand when a front-panel pushbutton is pressed, then displays the result on a small OLED screen.
## Assumptions
- Laser time-of-flight sensing is preferred over ultrasonic for a tighter measurement cone and cleaner UI behavior.
- Power is from a 5 V USB-C source; battery operation is not included in this baseline design.
- The package targets a practical prototype / module-based build, not a production-certified PCB release.
- The VL53L1X carrier board handles its own 2.8 V regulation and I2C level shifting on SDA/SCL, but XSHUT and GPIO1 remain 2.8 V-domain pins and are therefore intentionally left unused in this design.

## Basic circuit description
The USB-C breakout feeds a 5 V rail shared by the Arduino Nano Every, the OLED display, and the VL53L1X carrier. A 10 µF bulk capacitor and two 0.1 µF decoupling capacitors stabilize the local rail. The OLED and VL53L1X share the I2C bus: Nano A4 -> SDA and Nano A5 -> SCL. A momentary pushbutton drives a digital input; the input is held high by a 10 kΩ pull-up resistor and goes low when the button is pressed. Firmware idles showing the last measurement and captures a new reading only when the button is pressed, reducing accidental continuous ranging and making the device feel like a handheld instrument.

## Connection table
| From | To | Notes |
|---|---|---|
| J1 VBUS | 5V rail | USB-C 5 V input |
| J1 GND | GND rail | Common return |
| U1 5V | 5V rail | Nano powered directly from regulated USB 5 V |
| U1 GND | GND rail | Common ground |
| U1 A4/SDA | U2 SDA and DS1 SDA | Shared I2C data |
| U1 A5/SCL | U2 SCL and DS1 SCL | Shared I2C clock |
| U2 VIN | 5V rail | VL53L1X carrier accepts 2.6-5.5 V |
| U2 GND | GND rail | Common ground |
| DS1 VIN | 5V rail | Display breakout is 5 V ready |
| DS1 GND | GND rail | Common ground |
| U1 D2 | S1 node | Button sense input, active low |
| R1 | Between 5V rail and S1/U1 D2 node | 10 kΩ pull-up |
| S1 | Between U1 D2 node and GND | Press to trigger measurement |

## Firmware behavior
- Initialize I2C, OLED, and VL53L1X.
- Display a startup splash and prompt.
- Debounce the button.
- On each valid button press, acquire one distance sample, convert to millimeters/centimeters, and update the display.
- If the sensor reports invalid data, show an error message instead of stale numbers.

## BOM
|Item|Refs|Qty|Description|MPN|Unit $|Ext $|Supplier|
|---|---|---:|---|---|---:|---:|---|
|1|U1|1|Arduino Nano Every|ABX00028|12.90|12.90|[Arduino Store](https://store-usa.arduino.cc/products/nano-every)|
|2|U2|1|VL53L1X ToF sensor carrier|Pololu 3415|22.95|22.95|[Pololu](https://www.pololu.com/product/3415)|
|3|DS1|1|0.96 in OLED display|Adafruit 326|17.50|17.50|[Adafruit](https://www.adafruit.com/product/326)|
|4|S1|1|Momentary pushbutton|TEA-5144|0.89|0.89|[Vetco](https://vetco.net/products/vupn1504_tact_switch_66mm_5mm_through_hole)|
|5|R1|1|Pull-up resistor|Generic 10k THT|0.10|0.10|[Estimated](https://example.com/generic-10k-resistor)|
|6|C1,C2|2|Ceramic decoupling capacitor|FA18X7R1H104KNU06|0.10|0.20|[Futurlec/estimate](https://www.futurlec.com/Capacitors/C100UCpr.shtml)|
|7|C3|1|Bulk capacitor|VHT10M16|0.60|0.60|[Vetco](https://vetco.net/products/nte-vht10m16_10uf_16_volt_electrolytic_capacitor)|
|8|J1|1|USB-C power breakout|Adafruit 4090|2.95|2.95|[Adafruit](https://www.adafruit.com/product/4090)|
|9|H1|1|Breakaway male header strip|Pololu 965|0.95|0.95|[Pololu](https://www.pololu.com/product/965)|
|10|W1|1|Jumper wire set|Adafruit 1954|1.95|1.95|[Adafruit](https://www.adafruit.com/product/1954)|

**Total estimated cost: $60.99**

## Electrical review summary
- No level shifter is required on SDA/SCL because the selected VL53L1X carrier includes level shifting and the OLED breakout is 5 V ready.
- Do not connect Nano 5 V GPIO directly to VL53L1X XSHUT or GPIO1 because those lines are not 5 V tolerant on the selected carrier. This design avoids that issue by leaving them unused.
- All modules share a common ground.
- This is a prototype/module package; enclosure thermal, EMC, ESD, and drop robustness are not validated.
