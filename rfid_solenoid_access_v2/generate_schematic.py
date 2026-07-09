
import schemdraw
import schemdraw.elements as elm

OUT = '/workspace/rfid_solenoid_access_v2/schematic_v2.svg'

with schemdraw.Drawing(file=OUT, show=False) as d:
    d.config(unit=2.1, fontsize=10)

    j1 = d.add(elm.SourceV().up().label('J1\n12V IN', loc='bottom'))
    d.add(elm.Line().right(1.0))
    top12 = d.add(elm.Dot(label='+12V', loc='right'))

    d.push()
    d.add(elm.Line().down(1.2))
    d.add(elm.Capacitor().down().label('C1\n100uF', loc='right'))
    d.add(elm.Ground())
    d.pop()

    d.add(elm.Line().right(2.0))
    d.add(elm.Dot())
    d.add(elm.Line().down(0.7))
    u1 = d.add(elm.Ic(pins=[
        elm.IcPin(name='VIN', side='left', slot='1/7'),
        elm.IcPin(name='GND', side='left', slot='2/7'),
        elm.IcPin(name='D13/SCK', side='left', slot='3/7'),
        elm.IcPin(name='D12/MISO', side='left', slot='4/7'),
        elm.IcPin(name='D11/MOSI', side='left', slot='5/7'),
        elm.IcPin(name='D10/SS', side='left', slot='6/7'),
        elm.IcPin(name='D9/RST', side='left', slot='7/7'),
        elm.IcPin(name='D7/BZ', side='right', slot='1/4'),
        elm.IcPin(name='D6/RED', side='right', slot='2/4'),
        elm.IcPin(name='D5/GRN', side='right', slot='3/4'),
        elm.IcPin(name='D3/SOL', side='right', slot='4/4'),
    ], label='U1\nArduino Nano', pinspacing=0.55, edgepadW=.5, edgepadH=.4))

    d.add(elm.Line().at(u1.GND).left(0.8))
    d.add(elm.Dot())
    d.add(elm.Line().down(2.7))
    d.add(elm.Ground())

    d.add(elm.Line().at(top12.center).right(6.0))
    d.add(elm.Dot())
    reg = d.add(elm.VoltageRegulator().down().label('REG1\nAMS1117-3.3', loc='right'))
    d.add(elm.Ground())
    d.add(elm.Line().at(reg.out).right(2.0))
    rail33 = d.add(elm.Dot(label='+3.3V', loc='right'))

    d.push()
    d.add(elm.Line().at(rail33.center).down(1.2))
    d.add(elm.Capacitor().down().label('C2\n10uF', loc='right'))
    d.add(elm.Ground())
    d.pop()

    d.add(elm.Line().at(rail33.center).down(1.7))
    u2 = d.add(elm.Ic(pins=[
        elm.IcPin(name='3V3', side='left', slot='1/7'),
        elm.IcPin(name='GND', side='left', slot='2/7'),
        elm.IcPin(name='SCK', side='left', slot='3/7'),
        elm.IcPin(name='MISO', side='left', slot='4/7'),
        elm.IcPin(name='MOSI', side='left', slot='5/7'),
        elm.IcPin(name='SDA', side='left', slot='6/7'),
        elm.IcPin(name='RST', side='left', slot='7/7'),
    ], label='U2\nMFRC522', pinspacing=0.55, edgepadW=.5, edgepadH=.4))

    d.add(elm.Line().at(u2.GND).left(0.8))
    d.add(elm.Dot())
    d.add(elm.Line().down(2.4))
    d.add(elm.Ground())

    def divider(src_anchor, dst_anchor, top_label, bottom_label, netlabel, ydrop=0.9):
        d.add(elm.Line().at(src_anchor).left(0.5))
        d.add(elm.Resistor().left().label(top_label, loc='top'))
        mid = d.add(elm.Dot(label=netlabel, loc='bottom'))
        d.push()
        d.add(elm.Resistor().down().label(bottom_label, loc='right'))
        d.add(elm.Ground())
        d.pop()
        d.add(elm.Line().at(mid.center).to(dst_anchor))

    divider(u1['D13/SCK'], u2['SCK'], 'R5 2.2k', 'R8 3.3k', 'SCK_3V3')
    divider(u1['D11/MOSI'], u2['MOSI'], 'R6 2.2k', 'R9 3.3k', 'MOSI_3V3')
    divider(u1['D10/SS'], u2['SDA'], 'R7 2.2k', 'R10 3.3k', 'SS_3V3')
    divider(u1['D9/RST'], u2['RST'], 'R11 2.2k', 'R12 3.3k', 'RST_3V3')

    d.add(elm.Line().at(u2['MISO']).left(0.4))
    mid_miso = d.add(elm.Dot(label='MISO', loc='bottom'))
    d.add(elm.Line().at(mid_miso.center).to(u1['D12/MISO']))

    d.add(elm.Line().at(u1['D3/SOL']).right(0.8))
    d.add(elm.Resistor().right().label('R1 220R', loc='top'))
    gate = d.add(elm.Dot())
    d.push()
    d.add(elm.Resistor().down().label('R2 100k', loc='right'))
    d.add(elm.Ground())
    d.pop()
    q1 = d.add(elm.NFet().right().label('Q1\nIRLZ44N', loc='right'))
    d.add(elm.Line().at(gate.center).to(q1.gate))
    d.add(elm.Line().at(q1.source).down(1.2))
    d.add(elm.Ground())
    d.add(elm.Line().at(q1.drain).right(1.2))
    lockneg = d.add(elm.Dot())
    d.add(elm.Inductor2().up().label('LOCK1\n12V Solenoid', loc='right'))
    locktop = d.add(elm.Dot())
    d.add(elm.Line().to(top12.center))
    d.add(elm.Diode().at(lockneg.center).toy(locktop.center).label('D1 1N5408', loc='right'))

    d.add(elm.Line().at(u1['D5/GRN']).right(0.8))
    d.add(elm.Resistor().right().label('R3 330R', loc='top'))
    d.add(elm.LED().right().label('LED1 GRN', loc='right'))
    d.add(elm.Ground())

    d.add(elm.Line().at(u1['D6/RED']).right(0.8))
    d.add(elm.Resistor().right().label('R4 330R', loc='top'))
    d.add(elm.LED().right().label('LED2 RED', loc='right'))
    d.add(elm.Ground())

    d.add(elm.Line().at(u1['D7/BZ']).right(0.8))
    d.add(elm.Speaker().right().label('BZ1 active buzzer', loc='right'))
    d.add(elm.Ground())
