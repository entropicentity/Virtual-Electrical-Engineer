from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
import schemdraw
schemdraw.use('matplotlib')
import schemdraw.elements as elm

OUTDIR = Path(__file__).resolve().parent

summary_text = """Goal
Design a conceptual 12 V motorized safe latch controller that locks or unlocks by reversing a geared DC motor. The user asked for a keypad-based design, with automatic end-of-travel stopping for safety.

Assumptions
- This is a conceptual electronics package for a hobby/prototype safe latch, not a certified physical security product.
- A low-speed 12 V DC geared motor rotates a cam or lead-screw that moves the latch between LOCKED and UNLOCKED positions.
- Two limit switches are mechanically positioned so they close at the ends of travel and inform the controller when the latch is fully locked or fully unlocked.
- A 4x4 matrix keypad provides the unlock/lock command input through firmware.
- The motor current is kept within the TB6612FNG driver capability; if the real actuator stalls above about 1 A average, a higher-current H-bridge is needed.
- The 12 V input comes from an external DC adapter or internal 12 V system and is stepped down to 5 V for logic.

Basic circuit description
The circuit is divided into five blocks: input power, logic power conversion, keypad/controller, motor driver, and end-of-travel sensing. A 12 V input rail feeds the geared latch motor directly through the motor driver and also feeds a 5 V buck converter for logic power. The ATtiny1616 microcontroller scans a 4x4 keypad, validates a PIN in firmware, and commands the H-bridge motor driver to run forward for unlock or reverse for lock. Two normally-open limit switches are wired to microcontroller inputs with pull-ups so that each end position is sensed independently. Firmware stops the motor immediately when the relevant limit switch becomes active, and can also impose a timeout as a backup fault response. The TB6612FNG driver receives two direction lines plus a PWM/enable line and drives the motor bidirectionally. Protection and support parts include local decoupling capacitors on the MCU and motor driver, bulk capacitance on the 12 V rail near the driver, a fuse on the 12 V input, and a shared ground reference between logic and motor power.

Main components
- U1: ATtiny1616 8-bit microcontroller for keypad scanning and state logic
- U2: TB6612FNG dual H-bridge used as one DC motor channel
- U3: LM2596 buck converter module adjusted to 5 V
- K1: 4x4 matrix keypad
- M1: 12 V geared DC motor coupled to latch mechanism
- S1: Locked-position limit switch
- S2: Unlocked-position limit switch
- F1: 2 A input fuse
- C1/C2/C3/C4: bulk and local decoupling capacitors

Firmware need
Yes. Firmware is required to scan the keypad matrix, compare entered PIN codes, command lock/unlock motor direction, monitor both limit switches, enforce a motor timeout, optionally debounce keys and switches, and optionally drive a status LED or buzzer.

Important unknowns / verification needed
- Real motor running and stall current
- Mechanical torque needed to move the latch
- Exact keypad model and connector style
- Whether fail-secure or fail-safe behavior is wanted on power loss
- Whether tamper sensors, battery backup, or door-position sensing are required
- Whether a higher-security product should use a certified safe lock assembly instead of a custom mechanism
"""

bom = [
    [1, 'U1', 1, 'Microcontroller', 'ATtiny1616-SFR', '8-bit AVR MCU, 16 KB Flash, SOIC-20, 2.7-5.5 V', 'SOIC-20', '$0.95', '$0.95', 'Microchip / DigiKey listing', 'https://www.microchip.com/en-us/product/ATtiny1616'],
    [2, 'U2', 1, 'Motor driver', 'TB6612FNG', 'Dual H-bridge, 4.5-13.5 V motor supply, 1.2 A avg/ch', 'SSOP-24 or module', '$2.50', '$2.50', 'Toshiba / breakout module sources', 'https://toshiba.semicon-storage.com/us/semiconductor/product/motor-driver-ics/brushed-dc-motor-driver-ics/detail.TB6612FNG.html'],
    [3, 'U3', 1, 'Buck converter module', 'LM2596 module', '12 V in to regulated 5 V out, >=0.5 A logic budget', 'Module', '$1.50', '$1.50', 'Generic module', 'https://www.ti.com/lit/ds/symlink/lm2596.pdf'],
    [4, 'K1', 1, 'User input keypad', '4x4 matrix keypad', 'Momentary matrix keypad, 8-wire interface', 'Panel/membrane', '$3.00', '$3.00', 'Generic', 'https://www.kiwi-electronics.com/en/3x4-phone-style-matrix-keypad-2907'],
    [5, 'M1', 1, 'Actuator motor', '12 V geared DC motor', 'Low-speed gearmotor sized to latch torque, <=1 A avg recommended', 'Wired motor', '$12.00', '$12.00', 'Generic', 'https://www.pololu.com/category/60/micro-metal-gearmotors'],
    [6, 'S1,S2', 2, 'End-of-travel switches', 'KW12-3A-style microswitch', 'SPDT or SPST lever microswitch, use NO contact', 'Panel/mech', '$0.50', '$1.00', 'Generic', 'https://www.kel-switch.com/product/28mm-lever-micro-switch-with-3-terminals-kw12-3a-12f/'],
    [7, 'F1', 1, 'Input protection fuse', '2 A blade or inline fuse', 'Protect 12 V input wiring against shorts/stall faults', 'Inline holder', '$1.00', '$1.00', 'Generic', 'https://www.littelfuse.com/products/fuses.aspx'],
    [8, 'C1', 1, 'Bulk input capacitor', '470 uF 25 V electrolytic', '12 V rail bulk decoupling near H-bridge', 'Radial', '$0.40', '$0.40', 'Generic', 'https://www.digikey.com/en/products/filter/aluminum-electrolytic-capacitors/58'],
    [9, 'C2', 1, 'Logic bulk capacitor', '47 uF 10 V electrolytic', '5 V rail bulk decoupling near MCU', 'Radial', '$0.20', '$0.20', 'Generic', 'https://www.digikey.com/en/products/filter/aluminum-electrolytic-capacitors/58'],
    [10, 'C3,C4', 2, 'Decoupling capacitors', '0.1 uF ceramic', 'One each at U1 and U2 supply pins', '0805/THT', '$0.05', '$0.10', 'Generic', 'https://www.digikey.com/en/products/filter/ceramic-capacitors/60'],
    [11, 'R1,R2', 2, 'Pull-up resistors', '10 kohm', 'Optional external pull-ups for limit switches if firmware pull-ups not used', 'Axial/0805', '$0.02', '$0.04', 'Generic', 'https://www.digikey.com/en/products/filter/chip-resistor-surface-mount/52'],
    [12, 'J1-J4', 4, 'Connectors/terminals', 'Screw terminals / headers', '12 V input, motor, switches, keypad/UPDI access', 'THT', '$2.00', '$2.00', 'Generic', 'https://www.digikey.com/en/products/filter/terminal-blocks-wire-to-board/370'],
]

def draw_schematic(svg_path, png_path):
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.2)

    vin = d.add(elm.SourceV().up().label('12 V IN'))
    d.add(elm.Fuse().right().label('F1 2 A'))
    rail12 = d.add(elm.Line().right().length(1.4))
    d.add(elm.Dot().label('12V_BUS', loc='right'))

    d.push()
    d.add(elm.Line().down().length(1.6))
    d.add(elm.Capacitor().down().label('C1\n470 uF'))
    d.add(elm.Ground())
    d.pop()

    d.push()
    d.add(elm.Line().right().length(1.4))
    d.add(elm.Ic(label='U3\nLM2596\n5 V Buck', pins=[]))
    d.add(elm.Line().right().length(1.0))
    d.add(elm.Dot().label('5V_LOGIC', loc='right'))
    d.push()
    d.add(elm.Line().down().length(1.4))
    d.add(elm.Capacitor().down().label('C2\n47 uF'))
    d.add(elm.Ground())
    d.pop()
    d.pop()

    d.push()
    d.add(elm.Line().down().length(2.2))
    d.add(elm.Ic(label='U2\nTB6612FNG', pins=[]))
    d.add(elm.Line().right().length(1.4))
    d.add(elm.Motor().right().label('M1\n12 V Gearmotor'))
    d.add(elm.Line().down().length(1.2))
    d.add(elm.Ground())
    d.pop()

    d.push()
    d.add(elm.Line().right().length(6.0))
    d.add(elm.Line().down().length(2.4))
    d.add(elm.Ic(label='U1\nATtiny1616', pins=[]))
    d.add(elm.Line().left().length(1.5))
    d.add(elm.Ic(label='K1\n4x4 Keypad', pins=[]))
    d.pop()

    d.push()
    d.add(elm.Line().right().length(6.0))
    d.add(elm.Line().down().length(4.6))
    d.add(elm.Switch().right().label('S1 Locked limit'))
    d.add(elm.Line().down().length(0.8))
    d.add(elm.Ground())
    d.pop()

    d.push()
    d.add(elm.Line().right().length(6.0))
    d.add(elm.Line().down().length(5.8))
    d.add(elm.Switch().right().label('S2 Unlocked limit'))
    d.add(elm.Line().down().length(0.8))
    d.add(elm.Ground())
    d.pop()

    d.add(elm.Ground().at(vin.start))
    d.save(str(svg_path))
    d.save(str(png_path), dpi=200)


def build_files():
    svg = OUTDIR / 'safe_lock_schematic.svg'
    png = OUTDIR / 'safe_lock_schematic.png'
    draw_schematic(svg, png)

    (OUTDIR / 'circuit_summary.txt').write_text(summary_text)

    df = pd.DataFrame(bom, columns=['Item','Refs','Qty','Description','Part number','Required specs','Package','Unit price','Ext. price','Supplier','URL'])
    df.to_csv(OUTDIR / 'bom.csv', index=False)
    df.to_markdown(OUTDIR / 'bom.md', index=False)

    pdf_path = OUTDIR / 'safe_lock_circuit_package.pdf'
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8, leading=10))
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
    story = []
    story.append(Paragraph('Motorized Safe Latch Control Circuit Package', styles['Title']))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph('Concept package for a keypad-controlled 12 V geared motor that locks or unlocks a latch with automatic end-of-travel stopping.', styles['BodyText']))
    story.append(Spacer(1, 0.15*inch))
    for block in summary_text.strip().split('\n\n'):
        lines = block.split('\n')
        story.append(Paragraph(f'<b>{lines[0]}</b>', styles['Heading2']))
        for ln in lines[1:]:
            if ln.startswith('- '):
                story.append(Paragraph('&bull; ' + ln[2:], styles['BodyText']))
            elif ln.strip():
                story.append(Paragraph(ln, styles['BodyText']))
        story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph('Schematic', styles['Heading2']))
    story.append(Image(str(png), width=7.2*inch, height=4.8*inch))
    story.append(PageBreak())
    story.append(Paragraph('Bill of Materials', styles['Heading2']))
    table_data = [df.columns.tolist()] + df.values.tolist()
    tbl = Table(table_data, repeatRows=1, colWidths=[0.35*inch,0.55*inch,0.35*inch,1.0*inch,1.05*inch,1.65*inch,0.65*inch,0.55*inch,0.55*inch,0.9*inch,1.45*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.HexColor('#d9e2f3')),
        ('TEXTCOLOR',(0,0),(-1,0), colors.black),
        ('GRID',(0,0),(-1,-1), 0.25, colors.grey),
        ('FONTNAME',(0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1), 7),
        ('LEADING',(0,0),(-1,-1), 8),
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph('Estimated total BOM cost: about $24.69 excluding enclosure, PCB, wiring, shipping, taxes, and any higher-torque or higher-security mechanical hardware.', styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph('Limitations and disclaimer: this package is a conceptual design aid, not a certified secure-safe lock or production release. Real safe applications need mechanical force analysis, stall-current verification, EMI/ESD review, thermal checks, abuse testing, and threat modeling. Supplier pricing and stock were not comprehensively verified live; links are representative starting points.', styles['BodyText']))
    doc.build(story)

if __name__ == '__main__':
    build_files()
