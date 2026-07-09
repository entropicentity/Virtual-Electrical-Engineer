from pathlib import Path

import schemdraw
import schemdraw.elements as elm


OUTDIR = Path('/workspace/circuits')
OUTDIR.mkdir(parents=True, exist_ok=True)


with schemdraw.Drawing(show=False, file=str(OUTDIR / 'arduino_led_toggle.svg')) as d:
    d.config(unit=2.5, fontsize=12)

    arduino = d.add(elm.Ic(pins=[
        elm.IcPin(name='D13', side='right', anchorname='d13'),
        elm.IcPin(name='GND', side='right', anchorname='gnd'),
    ],
        label='Arduino Uno\n(simplified)',
        size=(3, 2.5)))

    d.add(elm.Line().right().at(arduino.d13))
    d.add(elm.Resistor().right().label('R1\n330 Ω'))
    d.add(elm.LED().right().label('LED1'))
    d.add(elm.Line().down().length(1.5))
    d.add(elm.Ground())

    d.add(elm.Line().at(arduino.gnd).down().length(1.2))
    d.add(elm.Ground())

    d.save(str(OUTDIR / 'arduino_led_toggle.svg'))
