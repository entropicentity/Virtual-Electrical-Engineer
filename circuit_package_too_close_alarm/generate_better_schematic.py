from pathlib import Path
import schemdraw
import schemdraw.elements as elm

out = Path(__file__).resolve().parent
svg_path = out / "schematic_improved.svg"

with schemdraw.Drawing(file=str(svg_path), show=False) as d:
    d.config(unit=2.0, fontsize=10, lw=2)

    d.add(elm.Label().label("Too-Close Scanning Alarm Schematic", fontsize=14).at((11.5, 10.8)))

    battery = d.add(elm.SourceV().at((0.8, 7.0)).up().label("BT1\n2S Li-ion pack\n7.4 V nom.", loc="left"))
    d.add(elm.Switch().right().at(battery.end).label("S1\nSPST", loc="top"))
    reg = d.add(
        elm.Ic(
            at=(3.0, 6.0),
            pins=[
                elm.IcPin(name="VIN", side="left"),
                elm.IcPin(name="GND", side="left"),
                elm.IcPin(name="VOUT", side="right"),
            ],
            label="REG1\nLM2596 module\n5.0 V out",
            size=(2.5, 2.0),
        )
    )
    d.add(elm.Line().at((2.0, 8.8)).right(1.0))
    d.add(elm.Line().at(reg.absanchors['VIN']).left(1.0))
    d.add(elm.Line().at(reg.absanchors['VOUT']).right(8.5))
    d.add(elm.Dot().at((13.5, reg.absanchors['VOUT'].y)).label("+5V rail", loc="top"))
    d.add(elm.Ground().at((reg.absanchors['GND'].x - 1.0, reg.absanchors['GND'].y)))

    d.add(elm.Capacitor().at((6.2, 6.9)).down(1.8).label("C1\n470 uF\nservo bulk", loc="right"))
    d.add(elm.Ground().at((6.2, 5.1)))
    d.add(elm.Line().at((6.2, 6.9)).up(0.7))
    d.add(elm.Line().at((6.2, 7.6)).right(7.3))

    d.add(elm.Capacitor().at((8.7, 6.9)).down(1.8).label("C2\n0.1 uF\nbypass", loc="right"))
    d.add(elm.Ground().at((8.7, 5.1)))
    d.add(elm.Line().at((8.7, 6.9)).up(0.7))
    d.add(elm.Line().at((8.7, 7.6)).right(4.8))

    nano = d.add(
        elm.Ic(
            at=(3.2, 1.8),
            pins=[
                elm.IcPin(name="5V", side="left"),
                elm.IcPin(name="GND", side="left"),
                elm.IcPin(name="D3", side="right"),
                elm.IcPin(name="D6", side="right"),
                elm.IcPin(name="D9", side="right"),
                elm.IcPin(name="D10", side="right"),
            ],
            label="U1\nArduino Nano",
            size=(2.7, 4.2),
        )
    )
    d.add(elm.Line().at(nano.absanchors['5V']).left(1.2))
    d.add(elm.Line().at((nano.absanchors['5V'].x - 1.2, nano.absanchors['5V'].y)).up(4.2))
    d.add(elm.Line().at((nano.absanchors['5V'].x - 1.2, nano.absanchors['5V'].y + 4.2)).right(7.8))
    d.add(elm.Dot().at((13.5, nano.absanchors['5V'].y + 4.2)).label("+5V rail", loc="top"))
    d.add(elm.Line().at(nano.absanchors['GND']).left(1.0))
    d.add(elm.Ground().at((nano.absanchors['GND'].x - 1.0, nano.absanchors['GND'].y)))

    servo = d.add(
        elm.Ic(
            at=(8.3, 3.7),
            pins=[
                elm.IcPin(name="SIG", side="left"),
                elm.IcPin(name="V+", side="left"),
                elm.IcPin(name="GND", side="left"),
            ],
            label="M1\nSG90 servo",
            size=(2.3, 2.1),
        )
    )
    d.add(elm.Line().at(nano.absanchors['D3']).right(1.0))
    d.add(elm.Line().at((nano.absanchors['D3'].x + 1.0, nano.absanchors['D3'].y)).up(1.5))
    d.add(elm.Line().at((nano.absanchors['D3'].x + 1.0, nano.absanchors['D3'].y + 1.5)).right(1.1))
    d.add(elm.Line().at(servo.absanchors['SIG']).left(1.2))
    d.add(elm.Label().label("D3 servo PWM", loc="bottom").at((7.3, servo.absanchors['SIG'].y + 0.2)))
    d.add(elm.Line().at(servo.absanchors['V+']).left(0.9))
    d.add(elm.Line().at((servo.absanchors['V+'].x - 0.9, servo.absanchors['V+'].y)).up(4.3))
    d.add(elm.Line().at((servo.absanchors['V+'].x - 0.9, servo.absanchors['V+'].y + 4.3)).right(4.3))
    d.add(elm.Line().at(servo.absanchors['GND']).left(0.9))
    d.add(elm.Ground().at((servo.absanchors['GND'].x - 0.9, servo.absanchors['GND'].y)))

    sensor = d.add(
        elm.Ic(
            at=(12.2, 2.9),
            pins=[
                elm.IcPin(name="TRIG", side="left"),
                elm.IcPin(name="ECHO", side="left"),
                elm.IcPin(name="VCC", side="left"),
                elm.IcPin(name="GND", side="left"),
            ],
            label="U2\nHC-SR04\nultrasonic",
            size=(2.6, 3.0),
        )
    )
    d.add(elm.Line().at(nano.absanchors['D9']).right(1.0))
    d.add(elm.Line().at((nano.absanchors['D9'].x + 1.0, nano.absanchors['D9'].y)).up(0.5))
    d.add(elm.Line().at((nano.absanchors['D9'].x + 1.0, nano.absanchors['D9'].y + 0.5)).right(3.7))
    d.add(elm.Line().at(sensor.absanchors['TRIG']).left(1.1))
    d.add(elm.Label().label("D9 TRIG", loc="bottom").at((10.4, sensor.absanchors['TRIG'].y + 0.2)))
    d.add(elm.Line().at(nano.absanchors['D10']).right(1.0))
    d.add(elm.Line().at((nano.absanchors['D10'].x + 1.0, nano.absanchors['D10'].y)).down(0.5))
    d.add(elm.Line().at((nano.absanchors['D10'].x + 1.0, nano.absanchors['D10'].y - 0.5)).right(3.7))
    d.add(elm.Line().at(sensor.absanchors['ECHO']).left(1.1))
    d.add(elm.Label().label("D10 ECHO", loc="top").at((10.6, sensor.absanchors['ECHO'].y - 0.1)))
    d.add(elm.Line().at(sensor.absanchors['VCC']).left(0.9))
    d.add(elm.Line().at((sensor.absanchors['VCC'].x - 0.9, sensor.absanchors['VCC'].y)).up(5.6))
    d.add(elm.Line().at((sensor.absanchors['VCC'].x - 0.9, sensor.absanchors['VCC'].y + 5.6)).right(2.2))
    d.add(elm.Line().at(sensor.absanchors['GND']).left(0.9))
    d.add(elm.Ground().at((sensor.absanchors['GND'].x - 0.9, sensor.absanchors['GND'].y)))

    buzzer = d.add(
        elm.Ic(
            at=(16.6, 2.8),
            pins=[
                elm.IcPin(name="IN", side="left"),
                elm.IcPin(name="V+", side="left"),
                elm.IcPin(name="GND", side="left"),
            ],
            label="BZ1\n5 V active\nbuzzer module",
            size=(2.6, 2.2),
        )
    )
    d.add(elm.Line().at(nano.absanchors['D6']).right(1.0))
    d.add(elm.Line().at((nano.absanchors['D6'].x + 1.0, nano.absanchors['D6'].y)).down(1.3))
    d.add(elm.Line().at((nano.absanchors['D6'].x + 1.0, nano.absanchors['D6'].y - 1.3)).right(8.4))
    d.add(elm.Line().at(buzzer.absanchors['IN']).left(1.1))
    d.add(elm.Label().label("D6 buzzer ctrl", loc="bottom").at((13.5, buzzer.absanchors['IN'].y + 0.15)))
    d.add(elm.Line().at(buzzer.absanchors['V+']).left(0.9))
    d.add(elm.Line().at((buzzer.absanchors['V+'].x - 0.9, buzzer.absanchors['V+'].y)).up(6.0))
    d.add(elm.Line().at((buzzer.absanchors['V+'].x - 0.9, buzzer.absanchors['V+'].y + 6.0)).right(0.6))
    d.add(elm.Line().at(buzzer.absanchors['GND']).left(0.9))
    d.add(elm.Ground().at((buzzer.absanchors['GND'].x - 0.9, buzzer.absanchors['GND'].y)))

    d.add(elm.Label().label("Sensor head mechanically mounted on servo horn", fontsize=9).at((12.7, 0.7)))
