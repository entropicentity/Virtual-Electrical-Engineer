from pathlib import Path
from datetime import date
import csv

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import schemdraw
from schemdraw import elements as elm


BASE = Path("/workspace/circuits/toy_car_package")
SCHEMATIC_PNG = BASE / "toy_car_schematic.png"
SUMMARY_MD = BASE / "toy_car_package_summary.md"
BOM_CSV = BASE / "toy_car_bom.csv"
PDF_PATH = BASE / "toy_car_circuit_package.pdf"


PROJECT = {
    "title": "Programmable 4-Wheel Toy Car Control Circuit Package",
    "goal": "A beginner-friendly programmable car using two driven rear wheels, two free-rolling front wheels, an ESP32 controller, and a TB6612FNG dual motor driver.",
    "assumptions": [
        "Drive layout assumed: 2WD differential drive with one DC gear motor on the left side and one on the right side; front wheels are passive.",
        "Programming platform chosen: Arduino-compatible ESP32 dev board because it is easy to program and has enough PWM-capable GPIO for motor control.",
        "Battery assumed: 2-cell 18650 holder in series for about 7.4 V nominal, 8.4 V fully charged.",
        "Motor type assumed: common TT-style brushed DC gear motors rated for about 3-6 V operation.",
        "This is a concept/prototyping package, not a production automotive or toy safety certification package.",
        "Links are representative product pages from common vendors or manufacturers; live stock and exact price were not independently verified at delivery time.",
    ],
    "description": [
        "The battery pack feeds a master power switch. After the switch, the raw battery line powers the motor supply input of the TB6612FNG motor driver.",
        "The same switched battery line also feeds an LM2596 buck converter adjusted to 5 V. That regulated 5 V rail powers the ESP32 dev board through its 5V/VIN input and powers the TB6612FNG logic VCC pin.",
        "The ESP32 drives PWMA, AIN1, AIN2, PWMB, BIN1, BIN2, and STBY on the TB6612FNG. This allows independent speed and direction control of the left and right motors.",
        "Each motor output from the TB6612FNG connects to one TT motor. Grounds for battery, buck converter, motor driver, and ESP32 are all tied together.",
        "Bulk and decoupling capacitors are included near the motor supply and logic rail to reduce resets and noise from the brushed motors.",
    ],
    "pins": [
        ("GPIO25", "PWMA", "Left motor PWM"),
        ("GPIO26", "AIN1", "Left motor direction 1"),
        ("GPIO27", "AIN2", "Left motor direction 2"),
        ("GPIO14", "PWMB", "Right motor PWM"),
        ("GPIO12", "BIN1", "Right motor direction 1"),
        ("GPIO13", "BIN2", "Right motor direction 2"),
        ("GPIO33", "STBY", "Driver standby enable"),
    ],
}


BOM = [
    {
        "item": 1,
        "refs": "U1",
        "qty": 1,
        "description": "ESP32 DevKit V1 development board",
        "specs": "ESP32-WROOM-32, Arduino-compatible, 30-pin dev board, Wi-Fi/BLE, 5 V input via VIN/5V, 3.3 V logic",
        "mpn": "ESP32 DevKit V1 (generic CP2102 type)",
        "package": "Through-hole dev module",
        "supplier": "Adafruit / generic distributors",
        "url": "https://www.adafruit.com/product/3269",
        "notes": "Any widely used ESP32 DevKit with exposed GPIO and VIN/5V pin is acceptable; confirm actual pin labels before wiring.",
    },
    {
        "item": 2,
        "refs": "U2",
        "qty": 1,
        "description": "Dual DC motor driver breakout",
        "specs": "TB6612FNG, 4.5-13.5 V motor supply, 2.7-5.5 V logic, about 1 A continuous/channel",
        "mpn": "Pololu 713 TB6612FNG carrier",
        "package": "Breakout module",
        "supplier": "Pololu",
        "url": "https://www.pololu.com/product/713",
        "notes": "Chosen over L298N because it is more efficient and better suited to battery-powered toy cars.",
    },
    {
        "item": 3,
        "refs": "M1,M2",
        "qty": 2,
        "description": "TT style brushed DC gear motor",
        "specs": "3-6 V rated, about 160-200 RPM at 6 V, brushed motor for small robot car",
        "mpn": "Adafruit 3777 or equivalent",
        "package": "Wired motor",
        "supplier": "Adafruit",
        "url": "https://www.adafruit.com/product/3777",
        "notes": "If your selected motors have much higher stall current, upgrade the driver and power wiring.",
    },
    {
        "item": 4,
        "refs": "U3",
        "qty": 1,
        "description": "Buck converter module",
        "specs": "LM2596 adjustable step-down module, input >5 V, output set to 5.0 V, up to about 2 A practical without extra cooling",
        "mpn": "LM2596 module",
        "package": "Module",
        "supplier": "SunFounder / generic distributors",
        "url": "https://www.sunfounder.com/products/step-down-converter",
        "notes": "Adjust output to 5.0 V with a multimeter before connecting the ESP32.",
    },
    {
        "item": 5,
        "refs": "BT1",
        "qty": 1,
        "description": "2x18650 battery holder with switch",
        "specs": "Series holder, nominal 7.4 V output, wire leads, integrated on/off switch",
        "mpn": "2-cell 18650 holder with switch",
        "package": "Battery holder",
        "supplier": "Seeed Studio",
        "url": "https://www.seeedstudio.com/18650-Battery-Holder-Case-2-Slot-with-Switch-p-4160.html",
        "notes": "If your holder already includes a switch, the separate SW1 item can be omitted.",
    },
    {
        "item": 6,
        "refs": "B1,B2",
        "qty": 2,
        "description": "Protected 18650 Li-ion cells",
        "specs": "3.6-3.7 V nominal, around 3200-3400 mAh, protected preferred for beginner use",
        "mpn": "Panasonic NCR18650B protected",
        "package": "Cell",
        "supplier": "BatteryTekUSA",
        "url": "https://www.batterytekusa.com/product/panasonic-18650b-3400mah-protected-li-ion-battery/",
        "notes": "Use a proper Li-ion charger. Do not charge cells while wired into an improvised circuit unless a correct charging/protection design is added.",
    },
    {
        "item": 7,
        "refs": "SW1",
        "qty": 1,
        "description": "Master power switch",
        "specs": "SPST on/off, low-voltage DC switching, panel-mount or inline",
        "mpn": "C&K DA series SPST rocker or equivalent",
        "package": "Panel switch",
        "supplier": "C&K",
        "url": "http://www.ckswitches.com/products/switches/product-details/Rocker/DA/",
        "notes": "Optional if battery holder already includes adequate switch and current handling.",
    },
    {
        "item": 8,
        "refs": "C1",
        "qty": 1,
        "description": "Bulk electrolytic capacitor",
        "specs": "470 uF, 16 V minimum, radial, low-ESR preferred",
        "mpn": "Panasonic EEUFR1C471",
        "package": "Radial through-hole",
        "supplier": "RS",
        "url": "https://uk.rs-online.com/web/p/aluminium-capacitors/7083620",
        "notes": "Place across VM and GND near the motor driver.",
    },
    {
        "item": 9,
        "refs": "C2,C3,C4",
        "qty": 3,
        "description": "Ceramic decoupling capacitor",
        "specs": "0.1 uF, 50 V, radial or leaded ceramic",
        "mpn": "Jameco 15270 or equivalent",
        "package": "Radial through-hole",
        "supplier": "Jameco",
        "url": "https://www.jameco.com/z/DC-1-50-7-Capacitor-Ceramic-Disc-0-1-micro-F-50V-plusmn-20-_15270.html",
        "notes": "Use near ESP32 supply and motor driver logic supply.",
    },
    {
        "item": 10,
        "refs": "J1,J2",
        "qty": 2,
        "description": "2-pin screw terminal block",
        "specs": "5.08 mm pitch, >=10 A preferred for battery/motor wiring",
        "mpn": "Weidmuller 1760490000 or equivalent",
        "package": "Through-hole terminal block",
        "supplier": "RS",
        "url": "https://au.rs-online.com/web/p/pcb-terminal-blocks/4087871",
        "notes": "Optional when modules already provide terminals or prewired leads.",
    },
    {
        "item": 11,
        "refs": "HW1",
        "qty": 1,
        "description": "4-wheel robot chassis kit",
        "specs": "Chassis with 4 wheels and mounting hardware, compatible with TT motors",
        "mpn": "Generic 4-wheel robot chassis",
        "package": "Mechanical kit",
        "supplier": "Generic robotics supplier",
        "url": "https://www.dfrobot.com/product-100.html",
        "notes": "Mechanical item included for completeness; exact chassis can vary.",
    },
]


def draw_schematic(path: Path) -> None:
    d = schemdraw.Drawing(file=str(path), show=False)
    d.config(unit=2.4)

    def anc(comp, name):
        return comp.absanchors[name]

    batt = d.add(elm.SourceV().up().label('BT1\n2x18650\n7.4V nom', loc='left'))
    d.add(elm.Line().right().length(1.2))
    d.add(elm.Switch().right().label('SW1\nMaster Power', loc='top'))
    d.add(elm.Dot(open=False))
    vm_node = d.here

    d.add(elm.Line().right().length(1.8))
    driver = d.add(elm.Ic(width=3.6, height=4.8, pins=[
        elm.IcPin(name='PWMA', side='left', slot='1/7'),
        elm.IcPin(name='AIN1', side='left', slot='2/7'),
        elm.IcPin(name='AIN2', side='left', slot='3/7'),
        elm.IcPin(name='PWMB', side='left', slot='4/7'),
        elm.IcPin(name='BIN1', side='left', slot='5/7'),
        elm.IcPin(name='BIN2', side='left', slot='6/7'),
        elm.IcPin(name='STBY', side='left', slot='7/7'),
        elm.IcPin(name='VM', side='top', slot='1/2'),
        elm.IcPin(name='VCC', side='top', slot='2/2'),
        elm.IcPin(name='GND', side='bottom', slot='1/1'),
        elm.IcPin(name='AO1/AO2', side='right', slot='1/2'),
        elm.IcPin(name='BO1/BO2', side='right', slot='2/2'),
    ]).label('U2\nTB6612FNG'))

    d.push()
    d.move_from(vm_node, dy=-0.1)
    d.add(elm.Line().down().length(2.2))
    d.add(elm.Capacitor().right().label('C1\n470uF', loc='bottom'))
    d.add(elm.Ground())
    d.pop()

    d.add(elm.Line().at(vm_node).to(anc(driver, 'VM')))

    d.push()
    d.move_from(vm_node)
    d.add(elm.Line().down().length(3.4))
    d.add(elm.Rect(w=2.8, h=1.4).label('U3\nLM2596\nBuck to 5V'))
    buck_out = d.add(elm.Line().right().length(1.6).label('5V', loc='top'))
    d.add(elm.Dot(open=False))
    five_node = d.here
    d.add(elm.Line().up().to(anc(driver, 'VCC')))
    d.pop()

    d.push()
    d.move_from(batt.start)
    d.add(elm.Line().down().length(5.8))
    d.add(elm.Ground().label('Common GND', loc='right'))
    d.pop()

    d.push()
    d.move_from(five_node, dy=-0.1)
    d.add(elm.Line().right().length(2.1))
    esp = d.add(elm.Ic(width=3.8, height=5.2, pins=[
        elm.IcPin(name='5V/VIN', side='left', slot='1/8'),
        elm.IcPin(name='GND', side='left', slot='2/8'),
        elm.IcPin(name='GPIO25', side='right', slot='1/7'),
        elm.IcPin(name='GPIO26', side='right', slot='2/7'),
        elm.IcPin(name='GPIO27', side='right', slot='3/7'),
        elm.IcPin(name='GPIO14', side='right', slot='4/7'),
        elm.IcPin(name='GPIO12', side='right', slot='5/7'),
        elm.IcPin(name='GPIO13', side='right', slot='6/7'),
        elm.IcPin(name='GPIO33', side='right', slot='7/7'),
    ]).label('U1\nESP32\nDevKit V1'))
    d.add(elm.Line().at(five_node).to(anc(esp, '5V/VIN')))
    d.add(elm.Line().at(anc(esp, 'GND')).down().length(1.1))
    d.add(elm.Ground())
    d.pop()

    for gpio, pin in [("GPIO25", "PWMA"), ("GPIO26", "AIN1"), ("GPIO27", "AIN2"), ("GPIO14", "PWMB"), ("GPIO12", "BIN1"), ("GPIO13", "BIN2"), ("GPIO33", "STBY")]:
        d.add(elm.Line().at(anc(esp, gpio)).to(anc(driver, pin)))

    d.add(elm.Line().at(anc(driver, 'AO1/AO2')).right().length(1.2))
    d.add(elm.Motor().right().label('M1\nLeft TT Motor', loc='top'))
    d.add(elm.Line().at(anc(driver, 'BO1/BO2')).right().length(1.2))
    d.add(elm.Motor().right().label('M2\nRight TT Motor', loc='top'))

    d.add(elm.Capacitor().at(five_node).down().label('C2 0.1uF', loc='right'))
    d.add(elm.Ground())
    d.add(elm.Capacitor().at(anc(driver, 'VCC')).up().label('C3 0.1uF', loc='right'))
    d.add(elm.Line().right().length(0.6))
    d.add(elm.Ground())

    d.save(str(path))


def write_bom_csv(path: Path) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["item", "refs", "qty", "description", "specs", "mpn", "package", "supplier", "url", "notes"],
        )
        writer.writeheader()
        writer.writerows(BOM)


def write_summary_md(path: Path) -> None:
    lines = [
        f"# {PROJECT['title']}",
        "",
        "## Goal",
        PROJECT["goal"],
        "",
        "## Assumptions",
    ]
    lines.extend([f"- {x}" for x in PROJECT["assumptions"]])
    lines.extend(["", "## Basic circuit description"])
    lines.extend([f"- {x}" for x in PROJECT["description"]])
    lines.extend(["", "## Suggested ESP32 to motor-driver pin map", "", "| ESP32 | TB6612FNG | Purpose |", "|---|---|---|"])
    lines.extend([f"| {a} | {b} | {c} |" for a, b, c in PROJECT["pins"]])
    lines.extend(["", "## Output files", f"- Schematic: `{SCHEMATIC_PNG.name}`", f"- BOM CSV: `{BOM_CSV.name}`", f"- PDF package: `{PDF_PATH.name}`"])
    path.write_text("\n".join(lines), encoding='utf-8')


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    canvas.drawString(20 * mm, 10 * mm, f"Generated {date.today().isoformat()} - conceptual prototyping package")
    canvas.drawRightString(190 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(path: Path) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SmallBody', parent=styles['BodyText'], fontSize=8.5, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Tiny', parent=styles['BodyText'], fontSize=7.5, leading=9))
    story = []

    story.append(Paragraph(PROJECT['title'], styles['Title']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(PROJECT['goal'], styles['BodyText']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Assumptions", styles['Heading2']))
    for item in PROJECT['assumptions']:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Basic circuit description", styles['Heading2']))
    for item in PROJECT['description']:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Schematic", styles['Heading2']))
    story.append(Image(str(SCHEMATIC_PNG), width=175*mm, height=110*mm))
    story.append(Spacer(1, 4*mm))

    pin_table = Table(
        [["ESP32 pin", "TB6612FNG pin", "Purpose"]] + [[a, b, c] for a, b, c in PROJECT['pins']],
        colWidths=[35*mm, 35*mm, 95*mm],
        repeatRows=1,
    )
    pin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9edf7')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ]))
    story.append(Paragraph("Suggested firmware pin map", styles['Heading2']))
    story.append(pin_table)
    story.append(PageBreak())

    story.append(Paragraph("Bill of materials", styles['Heading2']))
    bom_rows = [["Item", "Refs", "Qty", "Description", "MPN / supplier", "Purchase link"]]
    for row in BOM:
        bom_rows.append([
            str(row['item']),
            row['refs'],
            str(row['qty']),
            Paragraph(f"<b>{row['description']}</b><br/>{row['specs']}<br/>{row['notes']}", styles['Tiny']),
            Paragraph(f"{row['mpn']}<br/>{row['supplier']}", styles['Tiny']),
            Paragraph(f"<link href='{row['url']}' color='blue'>product page</link>", styles['Tiny']),
        ])
    bom_table = Table(bom_rows, colWidths=[10*mm, 18*mm, 10*mm, 80*mm, 40*mm, 28*mm], repeatRows=1)
    bom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dff0d8')),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bom_table)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Limitations and next steps", styles['Heading2']))
    for note in [
        "Add wheel encoders, an ultrasonic sensor, or line sensors if you want autonomous navigation rather than timed open-loop driving.",
        "Before connecting the ESP32, verify the buck converter output with a meter and confirm battery polarity.",
        "Brushed motor noise can reset microcontrollers; keep power wiring short and consider additional suppression capacitors directly on the motors if needed.",
        "If you expect motor stall currents above about 1 A continuous per channel, select a higher-current driver and heavier-gauge wiring.",
    ]:
        story.append(Paragraph(f"• {note}", styles['BodyText']))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    draw_schematic(SCHEMATIC_PNG)
    write_bom_csv(BOM_CSV)
    write_summary_md(SUMMARY_MD)
    build_pdf(PDF_PATH)


if __name__ == '__main__':
    main()
