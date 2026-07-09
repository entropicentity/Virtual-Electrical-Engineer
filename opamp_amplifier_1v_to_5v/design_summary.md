# Op-Amp Signal Amplifier (1 V sine to 5 V sine)
## Goal
Amplify a 1 V sine-wave input to a 5 V sine-wave output.
## Assumptions
- Input is a 1 V amplitude sine wave centered around ground.
- Target output is a 5 V amplitude sine wave, requiring a voltage gain of about 5.
- A dual-rail supply is assumed for clean ground-centered sine amplification.
- Chosen topology is a non-inverting op-amp with gain 1 + Rf/Rg = 5.
- Example supply rails are +12 V and -12 V.
- Circuit is intended as a conceptual low-frequency analog amplifier example.
## Basic circuit description
The circuit uses a non-inverting op-amp amplifier. The sine-wave input connects directly to the op-amp non-inverting input. The inverting input uses a resistive feedback network made of R2 from output to inverting input and R1 from inverting input to ground, producing gain = 1 + R2/R1 = 5. The op-amp is powered from positive and negative supply rails so the AC output can swing symmetrically around ground. C1 and C2 provide local bypass decoupling from each supply rail to ground near the op-amp.
## Main components
- Single op-amp device
- Two gain-setting resistors
- Two bypass capacitors
- Input/output connectors
## Firmware need
No firmware required; this is a purely analog circuit.
## BOM total
Estimated total: $17.00