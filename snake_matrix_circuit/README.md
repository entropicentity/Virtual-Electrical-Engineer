# Snake Game LED Matrix Circuit Package

## Goal
Build a USB-powered circuit that runs Snake on a single 8x8 LED dot matrix with four pushbuttons.

## Selected architecture
- U1: Arduino Nano compatible board
- U2: MAX7219 8x8 LED matrix module
- S1-S4: four directional tactile buttons
- 5V USB power shared by controller and display

## Pin map
- D2 -> S1 Up button
- D3 -> S2 Down button
- D4 -> S3 Left button
- D5 -> S4 Right button
- D10 -> U2 CS
- D11 -> U2 DIN
- D13 -> U2 CLK
- 5V/GND -> U2 VCC/GND and button return ground

## BOM total
Estimated total: $10.60 USD

## Output files
- Schematic: /workspace/snake_matrix_circuit/snake_matrix_schematic.svg
- Block diagram: /workspace/snake_matrix_circuit/snake_matrix_block_diagram.png
- Firmware: /workspace/snake_matrix_circuit/snake_game_arduino.ino
- BOM CSV: /workspace/snake_matrix_circuit/bom.csv
- Concept JSON: /workspace/snake_matrix_circuit/concept.json
- PDF package: /workspace/snake_matrix_circuit/snake_matrix_circuit_package.pdf

## Notes
- Buttons are intended to use Arduino internal pull-ups.
- Optional USB-C breakout is only needed if you want separate external 5V entry instead of powering through the Nano USB port.
- This is a prototype-friendly design package, not a production release.
