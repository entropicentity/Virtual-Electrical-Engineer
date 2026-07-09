
from pathlib import Path
import schemdraw
import schemdraw.elements as elm
import cairosvg

out = Path('/workspace/sun_tracking_camera/outputs')
out.mkdir(parents=True, exist_ok=True)

with schemdraw.Drawing(file=str(out/'sun_tracking_camera_schematic.svg')) as d:
    d.config(fontsize=11)
    d += elm.Dot(open=True).label('5V_IN', loc='left')
    d += elm.Line().right(1)
    d += elm.Dot().label('5V BUS', loc='top')
    pwr_node = d.here
    d.push()
    d += elm.Capacitor().down().label('C1\n470uF')
    d += elm.Ground()
    d.pop()
    d.push()
    d += elm.Line().right(1.3)
    d += elm.Capacitor().down().label('C2\n100nF')
    d += elm.Ground()
    d.pop()

    d += elm.Line().right(1.8)
    u1 = d.add(elm.Ic(pins=[
        elm.IcPin(name='5V', pin='5V', side='left'),
        elm.IcPin(name='GND', pin='GND', side='left'),
        elm.IcPin(name='GPIO14', pin='GPIO14', side='right'),
        elm.IcPin(name='GPIO15', pin='GPIO15', side='right'),
        elm.IcPin(name='ADC1', pin='ADC1', side='bottom'),
        elm.IcPin(name='ADC2', pin='ADC2', side='bottom'),
        elm.IcPin(name='ADC3', pin='ADC3', side='bottom'),
        elm.IcPin(name='ADC4', pin='ADC4', side='bottom')
    ], label='U1\nESP32-CAM\nAI-Thinker'))

    d.add(elm.Line().at(u1.absanchors['5V']).left(u1.absanchors['5V'].x - pwr_node.x))
    d.add(elm.Line().at(u1.absanchors['GND']).left(1.0))
    d.add(elm.Ground().at((u1.absanchors['GND'].x-1.0, u1.absanchors['GND'].y)))

    d.add(elm.Line().at(u1.absanchors['GPIO14']).right(1.4))
    d.add(elm.Tag().at((u1.absanchors['GPIO14'].x+1.6, u1.absanchors['GPIO14'].y)).label('J2 SIG -> M1 Pan Servo'))
    d.add(elm.Line().at(u1.absanchors['GPIO15']).right(1.4))
    d.add(elm.Tag().at((u1.absanchors['GPIO15'].x+1.6, u1.absanchors['GPIO15'].y)).label('J3 SIG -> M2 Tilt Servo'))

    adc_names = ['ADC1','ADC2','ADC3','ADC4']
    ldr_names = ['R1 LDR NW','R2 LDR NE','R3 LDR SW','R4 LDR SE']
    res_names = ['R5 10k','R6 10k','R7 10k','R8 10k']
    for adc, ldr, res in zip(adc_names, ldr_names, res_names):
        pin = u1.absanchors[adc]
        d.add(elm.Line().at(pin).down(0.6))
        node = (pin.x, pin.y-0.6)
        d.add(elm.Dot().at(node))
        d.add(elm.Resistor().at(node).up(1.3).label(ldr, loc='right'))
        d.add(elm.Tag().at((node[0], node[1]+1.55)).label('to 5V'))
        d.add(elm.Resistor().at(node).down(1.3).label(res, loc='right'))
        d.add(elm.Ground().at((node[0], node[1]-1.3)))

    d.add(elm.Tag().at((u1.absanchors['GPIO15'].x+2.0, u1.center.y-0.8)).label('M1/M2 power: 5V and GND shared with 5V bus'))

cairosvg.svg2png(url=str(out/'sun_tracking_camera_schematic.svg'), write_to=str(out/'sun_tracking_camera_schematic.png'), dpi=200)
