from pathlib import Path
from textwrap import wrap
import csv

import cairosvg
import schemdraw
import schemdraw.elements as elm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUT = Path(__file__).resolve().parent
PDF_PATH = OUT / "temp_humidity_sd_logger_package.pdf"
MD_PATH = OUT / "design_summary.md"
CSV_PATH = OUT / "bom.csv"
INO_PATH = OUT / "temp_humidity_sd_logger.ino"
REVIEW_PATH = OUT / "schematic_review_log.csv"


ASSUMPTIONS = [
    "USB-powered 5 V design intended for indoor or sheltered use.",
    "Cost was prioritized over premium metrology performance while still targeting practical accuracy near 0.1 °C display resolution and about 1-2 %RH class sensor performance.",
    "Sensor chosen: Sensirion SHT31-D breakout/module because it is typically more accurate and more stable than DHT-class parts while remaining affordable.",
    "Microcontroller chosen: Arduino Nano compatible board for easy SD logging and broad library support.",
    "MicroSD module assumed to be a common SPI breakout with onboard 3.3 V regulator and level shifting for 5 V Arduino compatibility.",
    "This is a conceptual but buildable package, not a certified production release.",
]


BOM = [
    ["U1", "Arduino Nano compatible board (ATmega328P, 5 V)", 1, 6.50, "Amazon/Elegoo Nano compatible", "https://www.amazon.com/s?k=arduino+nano+compatible"],
    ["U2", "SHT31-D temperature/humidity breakout, I2C, 3.3-5 V tolerant module", 1, 7.50, "Adafruit/SparkFun-compatible module", "https://www.adafruit.com/product/2857"],
    ["U3", "MicroSD card module, SPI, 5 V interface", 1, 2.50, "Catalex-style microSD module", "https://www.amazon.com/s?k=micro+sd+card+module+arduino"],
    ["J1", "USB Mini/Micro cable or Nano USB cable", 1, 2.00, "Generic", "https://www.amazon.com/s?k=usb+cable+for+arduino+nano"],
    ["C1", "100 uF electrolytic capacitor, >=10 V", 1, 0.20, "Generic", "https://www.digikey.com/en/products/filter/aluminum-electrolytic-capacitors/58"],
    ["C2", "0.1 uF ceramic capacitor", 1, 0.05, "Generic", "https://www.digikey.com/en/products/filter/ceramic-capacitors/60"],
    ["SD1", "MicroSD card, 8-32 GB", 1, 4.00, "SanDisk or equivalent", "https://www.amazon.com/s?k=micro+sd+card+16gb"],
    ["HW1", "Breadboard or perfboard + jumper wires/header pins", 1, 3.00, "Generic", "https://www.amazon.com/s?k=breadboard+jumper+wires"],
]


FIRMWARE = r'''#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>

// Temperature/Humidity SD Logger
// Hardware mapping:
// U1 Arduino Nano compatible
// U2 SHT31-D breakout on I2C: SDA=A4, SCL=A5
// U3 microSD module on SPI: CS=D10, MOSI=D11, MISO=D12, SCK=D13

static const uint8_t SD_CHIP_SELECT = 10;
static const unsigned long LOG_INTERVAL_MS = 60000UL;  // 1 minute

Adafruit_SHT31 sht31 = Adafruit_SHT31();
File logFile;
unsigned long lastLogMs = 0;
char filename[] = "THLOG.CSV";

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }

  Wire.begin();

  if (!sht31.begin(0x44)) {
    Serial.println("SHT31 not detected. Check wiring.");
    while (1) { delay(1000); }
  }

  if (!SD.begin(SD_CHIP_SELECT)) {
    Serial.println("SD init failed. Check module/card wiring.");
    while (1) { delay(1000); }
  }

  bool needHeader = !SD.exists(filename);
  logFile = SD.open(filename, FILE_WRITE);
  if (!logFile) {
    Serial.println("Unable to open log file.");
    while (1) { delay(1000); }
  }

  if (needHeader) {
    logFile.println("millis,temperature_C,humidity_percent");
    logFile.flush();
  }

  Serial.println("Logger ready.");
}

void loop() {
  unsigned long now = millis();
  if (now - lastLogMs >= LOG_INTERVAL_MS) {
    lastLogMs = now;
    logMeasurement(now);
  }
}

void logMeasurement(unsigned long timestampMs) {
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println("Sensor read failed.");
    return;
  }

  String row = String(timestampMs);
  row += ",";
  row += String(t, 1);   // 0.1 C resolution in log file
  row += ",";
  row += String(h, 1);   // 0.1 %RH resolution in log file

  logFile.println(row);
  logFile.flush();
  Serial.println(row);
}
'''


def line_total(item):
    return item[2] * item[3]


def version_paths(version: int):
    stem = f"temp_humidity_sd_logger_schematic_{version}"
    return OUT / f"{stem}.svg", OUT / f"{stem}.png"


def rect(x0, y0, x1, y1, margin=0.0):
    xmin, xmax = sorted((x0, x1))
    ymin, ymax = sorted((y0, y1))
    return (xmin - margin, ymin - margin, xmax + margin, ymax + margin)


def intersects(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def segment_rect_intersection(seg, r):
    kind, a, b, fixed = seg
    xmin, ymin, xmax, ymax = r
    if kind == 'h':
        x0, x1 = sorted((a, b))
        return ymin < fixed < ymax and not (x1 <= xmin or x0 >= xmax)
    y0, y1 = sorted((a, b))
    return xmin < fixed < xmax and not (y1 <= ymin or y0 >= ymax)


def point_in_rect(x, y, r):
    return r[0] < x < r[2] and r[1] < y < r[3]


def add_label(labels, name, x, y, w=0.9, h=0.28):
    labels.append((name, rect(x - w/2, y - h/2, x + w/2, y + h/2)))


def validate_layout(components, labels, wires):
    errors = []
    comp_items = list(components.items())
    for i, (name_a, rect_a) in enumerate(comp_items):
        for name_b, rect_b in comp_items[i+1:]:
            if intersects(rect_a, rect_b):
                errors.append(f"component overlap: {name_a} with {name_b}")
    label_items = labels
    for i, (name_a, rect_a) in enumerate(label_items):
        for name_b, rect_b in label_items[i+1:]:
            if intersects(rect_a, rect_b):
                errors.append(f"label overlap: {name_a} with {name_b}")
    for lname, lrect in label_items:
        for cname, crect in comp_items:
            if intersects(lrect, crect):
                errors.append(f"label/component overlap: {lname} with {cname}")
    for wname, seg, allow_components in wires:
        for cname, crect in comp_items:
            if cname in allow_components:
                continue
            if segment_rect_intersection(seg, crect):
                errors.append(f"wire/component overlap: {wname} with {cname}")
        for lname, lrect in label_items:
            if segment_rect_intersection(seg, lrect):
                errors.append(f"wire/label overlap: {wname} with {lname}")
    return errors


def append_review(version, status, notes):
    rows = []
    if REVIEW_PATH.exists():
        rows = REVIEW_PATH.read_text(encoding='utf-8').splitlines()
    with REVIEW_PATH.open('a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if not rows:
            writer.writerow(['version', 'status', 'notes'])
        writer.writerow([version, status, ' | '.join(notes) if notes else 'passed'])


def write_text_outputs():
    total = sum(line_total(item) for item in BOM)
    lines = [
        "# Temperature and Humidity Logger with SD Card\n",
        "## Goal\n",
        "USB-powered logger that measures ambient temperature and relative humidity and periodically stores readings to a microSD card.\n",
        "## Assumptions\n",
    ]
    lines.extend([f"- {a}\n" for a in ASSUMPTIONS])
    lines.extend([
        "\n## Basic circuit description\n",
        "An Arduino Nano supplies system control. An SHT31-D breakout connects over I2C for digital temperature/humidity measurements. A microSD breakout connects over SPI for storage. USB provides 5 V input to the Nano and SD module; the SHT31 module is powered from the Nano 3.3 V rail to match the sensor breakout. Shared ground ties all blocks together. Local bulk and bypass capacitance stabilize the supply near the SD module.\n",
        "\n## Pin map\n",
        "- A4 -> SDA -> SHT31 SDA\n",
        "- A5 -> SCL -> SHT31 SCL\n",
        "- D10 -> SD CS\n",
        "- D11 -> SD MOSI\n",
        "- D12 -> SD MISO\n",
        "- D13 -> SD SCK\n",
        "\n## BOM total\n",
        f"Estimated total: ${total:.2f}\n",
    ])
    MD_PATH.write_text("".join(lines), encoding="utf-8")

    csv_lines = ["RefDes,Description,Qty,UnitPriceUSD,ExtendedPriceUSD,Supplier,Link\n"]
    for item in BOM:
        csv_lines.append(
            f'{item[0]},"{item[1]}",{item[2]},{item[3]:.2f},{line_total(item):.2f},"{item[4]}","{item[5]}"\n'
        )
    csv_lines.append(f'TOTAL,,,,{total:.2f},,\n')
    CSV_PATH.write_text("".join(csv_lines), encoding="utf-8")
    INO_PATH.write_text(FIRMWARE, encoding="utf-8")


def render_schematic(version: int):
    svg_path, png_path = version_paths(version)

    components = {
        'J1': rect(0.4, 11.0, 2.2, 12.0, margin=0.15),
        'C1': rect(2.8, 8.7, 3.4, 11.1, margin=0.15),
        'C2': rect(4.3, 8.7, 4.9, 11.1, margin=0.15),
        'U1': rect(5.6, 4.8, 9.4, 10.8, margin=0.25),
        'U2': rect(13.4, 7.8, 16.8, 11.4, margin=0.25),
        'U3': rect(13.4, 0.8, 17.2, 7.2, margin=0.25),
        'SD1': rect(18.2, 2.4, 20.8, 5.8, margin=0.25),
    }
    labels = []
    wires = []

    add_label(labels, 'title', 10.5, 13.1, 5.0, 0.35)
    add_label(labels, 'rail_5v', 3.0, 12.2, 0.9, 0.28)
    add_label(labels, 'rail_3v3', 10.8, 9.35, 0.9, 0.28)
    add_label(labels, 'sda_label', 11.3, 9.55, 1.0, 0.28)
    add_label(labels, 'scl_label', 11.3, 8.75, 1.0, 0.28)
    add_label(labels, 'cs_label', 11.0, 5.05, 0.9, 0.28)
    add_label(labels, 'mosi_label', 11.0, 4.15, 1.0, 0.28)
    add_label(labels, 'miso_label', 11.0, 3.25, 1.0, 0.28)
    add_label(labels, 'sck_label', 11.0, 2.35, 0.9, 0.28)
    add_label(labels, 'sd_card_label', 19.5, 6.15, 1.6, 0.28)
    add_label(labels, 'all_gnd', 3.0, 0.55, 1.4, 0.28)

    for pin_name, y in [('5V', 10.1), ('3V3', 9.3), ('GND', 8.5)]:
        add_label(labels, f'U1_{pin_name}', 5.05, y, 0.7, 0.22)
    for pin_name, y in [('A4/SDA', 9.9), ('A5/SCL', 9.1), ('D10/CS', 6.1), ('D11/MOSI', 5.3), ('D12/MISO', 4.5), ('D13/SCK', 3.7)]:
        add_label(labels, f'U1_{pin_name}', 9.95, y, 0.95, 0.22)
    for pin_name, y in [('VIN', 10.7), ('GND', 9.9), ('SDA', 9.1), ('SCL', 8.3)]:
        add_label(labels, f'U2_{pin_name}', 12.85, y, 0.7, 0.22)
    for pin_name, y in [('VCC', 6.1), ('GND', 5.3), ('CS', 4.5), ('MOSI', 3.7), ('MISO', 2.9), ('SCK', 2.1)]:
        add_label(labels, f'U3_{pin_name}', 12.75, y, 0.8, 0.22)

    wires.extend([
        ('usb_to_5v_1', ('h', 2.2, 5.4, 11.5), {'J1'}),
        ('usb_to_5v_2', ('h', 5.4, 5.6, 10.1), {'U1'}),
        ('sensor_vin_1', ('h', 9.4, 10.8, 9.3), {'U1'}),
        ('sensor_vin_2', ('h', 10.8, 13.4, 9.3), {'U2'}),
        ('sd_vcc_1', ('v', 10.2, 6.1, 11.5), set()),
        ('sd_vcc_2', ('h', 10.2, 13.4, 6.1), {'U3'}),
        ('sda_1', ('h', 9.4, 10.2, 9.9), {'U1'}),
        ('sda_2', ('v', 10.2, 9.1, 9.9), set()),
        ('sda_3', ('h', 10.2, 13.4, 9.1), {'U2'}),
        ('scl_1', ('h', 9.4, 10.2, 9.1), {'U1'}),
        ('scl_2', ('v', 10.2, 8.3, 9.1), set()),
        ('scl_3', ('h', 10.2, 13.4, 8.3), {'U2'}),
        ('cs_1', ('h', 9.4, 9.9, 6.1), {'U1'}),
        ('cs_2', ('v', 9.9, 4.5, 6.1), set()),
        ('cs_3', ('h', 9.9, 13.4, 4.5), {'U3'}),
        ('mosi_1', ('h', 9.4, 10.1, 5.3), {'U1'}),
        ('mosi_2', ('v', 10.1, 3.7, 5.3), set()),
        ('mosi_3', ('h', 10.1, 13.4, 3.7), {'U3'}),
        ('miso_1', ('h', 9.4, 10.3, 4.5), {'U1'}),
        ('miso_2', ('v', 10.3, 2.9, 4.5), set()),
        ('miso_3', ('h', 10.3, 13.4, 2.9), {'U3'}),
        ('sck_1', ('h', 9.4, 10.5, 3.7), {'U1'}),
        ('sck_2', ('v', 10.5, 2.1, 3.7), set()),
        ('sck_3', ('h', 10.5, 13.4, 2.1), {'U3'}),
        ('sd_slot_1', ('h', 17.2, 18.2, 4.1), {'U3', 'SD1'}),
        ('gnd_u1', ('h', 4.6, 5.6, 8.5), {'U1'}),
        ('gnd_u2', ('h', 12.4, 13.4, 9.9), {'U2'}),
        ('gnd_u3', ('h', 12.4, 13.4, 5.3), {'U3'}),
    ])

    errors = validate_layout(components, labels, wires)
    if errors:
        append_review(version, 'validation_failed', errors)
        raise ValueError('Layout validation failed: ' + '; '.join(errors))

    with schemdraw.Drawing(file=str(svg_path), show=False) as d:
        d.config(unit=2.0, fontsize=10, lw=2)
        d.add(elm.Label().label("Temperature / Humidity SD Logger", fontsize=14).at((10.5, 13.1)))

        j1 = d.add(elm.Ic(at=(0.4, 11.0), pins=[elm.IcPin(name='VBUS', side='right', anchorname='vbus')], label='J1\nUSB 5V In', size=(1.8, 1.0)))
        d.add(elm.Line().at(j1.vbus).right(3.2))
        d.add(elm.Label().label('+5V', loc='top').at((3.0, 12.2)))

        d.add(elm.CapacitorPolarized().at((3.1, 10.9)).down(1.8).label('C1\n100 uF', loc='right'))
        d.add(elm.Ground().at((3.1, 9.1)))

        d.add(elm.Capacitor().at((4.6, 10.9)).down(1.8).label('C2\n0.1 uF', loc='right'))
        d.add(elm.Ground().at((4.6, 9.1)))

        nano = d.add(
            elm.Ic(
                at=(5.6, 4.8),
                pins=[
                    elm.IcPin(name="5V", side="left"),
                    elm.IcPin(name="3V3", side="left"),
                    elm.IcPin(name="GND", side="left"),
                    elm.IcPin(name="A4/SDA", side="right"),
                    elm.IcPin(name="A5/SCL", side="right"),
                    elm.IcPin(name="D10/CS", side="right"),
                    elm.IcPin(name="D11/MOSI", side="right"),
                    elm.IcPin(name="D12/MISO", side="right"),
                    elm.IcPin(name="D13/SCK", side="right"),
                ],
                label="U1\nArduino Nano",
                size=(3.8, 6.0),
            )
        )

        d.add(elm.Line().at(j1.vbus).right(3.4))
        d.add(elm.Line().at((5.6, 11.5)).down(1.4))
        d.add(elm.Line().at((5.6, 10.1)).right(0.0))

        d.add(elm.Line().at(nano.absanchors['GND']).left(1.0))
        d.add(elm.Ground().at((4.6, 8.5)))

        sensor = d.add(
            elm.Ic(
                at=(13.4, 7.8),
                pins=[
                    elm.IcPin(name="VIN", side="left"),
                    elm.IcPin(name="GND", side="left"),
                    elm.IcPin(name="SDA", side="left"),
                    elm.IcPin(name="SCL", side="left"),
                ],
                label="U2\nSHT31-D\nI2C Sensor Module",
                size=(3.4, 3.6),
            )
        )

        d.add(elm.Line().at(nano.absanchors['3V3']).right(1.4))
        d.add(elm.Line().at((10.8, 9.3)).right(2.6))
        d.add(elm.Label().label("3.3V", loc="top").at((10.8, 9.35)))

        d.add(elm.Line().at(sensor.absanchors['GND']).left(1.0))
        d.add(elm.Ground().at((12.4, 9.9)))

        d.add(elm.Line().at(nano.absanchors['A4/SDA']).right(0.8))
        d.add(elm.Line().at((10.2, 9.9)).down(0.8))
        d.add(elm.Line().at((10.2, 9.1)).right(3.2))
        d.add(elm.Label().label("I2C SDA", loc="top").at((11.3, 9.55)))

        d.add(elm.Line().at(nano.absanchors['A5/SCL']).right(0.8))
        d.add(elm.Line().at((10.2, 9.1)).down(0.8))
        d.add(elm.Line().at((10.2, 8.3)).right(3.2))
        d.add(elm.Label().label("I2C SCL", loc="bottom").at((11.3, 8.75)))

        sdmod = d.add(
            elm.Ic(
                at=(13.4, 0.8),
                pins=[
                    elm.IcPin(name="VCC", side="left"),
                    elm.IcPin(name="GND", side="left"),
                    elm.IcPin(name="CS", side="left"),
                    elm.IcPin(name="MOSI", side="left"),
                    elm.IcPin(name="MISO", side="left"),
                    elm.IcPin(name="SCK", side="left"),
                ],
                label="U3\nMicroSD SPI Module",
                size=(3.8, 6.4),
            )
        )

        sdcard = d.add(elm.Ic(at=(18.2, 2.4), pins=[elm.IcPin(name='DAT/BUS', side='left')], label='SD1\nMicroSD Card', size=(2.6, 3.4)))
        d.add(elm.Line().at((17.2, 4.1)).right(1.0))
        d.add(elm.Label().label('Card socket', loc='top').at((19.5, 6.15)))

        d.add(elm.Line().at((10.2, 11.5)).down(5.4))
        d.add(elm.Line().at((10.2, 6.1)).right(3.2))

        d.add(elm.Line().at(sdmod.absanchors['GND']).left(1.0))
        d.add(elm.Ground().at((12.4, 5.3)))

        spi_routes = [
            ("CS", "D10/CS", 4.5, "SD CS", 5.05),
            ("MOSI", "D11/MOSI", 3.7, "SPI MOSI", 4.15),
            ("MISO", "D12/MISO", 2.9, "SPI MISO", 3.25),
            ("SCK", "D13/SCK", 2.1, "SPI SCK", 2.35),
        ]
        for sd_pin, nano_pin, y_bus, text, y_label in spi_routes:
            d.add(elm.Line().at(nano.absanchors[nano_pin]).right(0.5))
            d.add(elm.Line().at((9.9, nano.absanchors[nano_pin].y)).down(nano.absanchors[nano_pin].y - y_bus))
            d.add(elm.Line().at((9.9, y_bus)).right(3.5))
            d.add(elm.Label().label(text, loc='top').at((11.0, y_label)))

        d.add(elm.Label().label("All grounds common", fontsize=9).at((3.0, 0.5)))

    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), dpi=220)
    append_review(version, 'rendered', ['validation_passed'])
    return svg_path, png_path


def build_pdf():
    total = sum(line_total(item) for item in BOM)
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.spaceAfter = 6
    small = ParagraphStyle("Small", parent=body, fontSize=9, leading=11)
    title_style = styles["Title"]

    story = []
    story.append(Paragraph("Temperature and Humidity Logger with microSD Storage", title_style))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("USB-powered Arduino Nano logger using an SHT31-D digital sensor and SPI microSD module.", body))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Assumptions", styles["Heading2"]))
    for a in ASSUMPTIONS:
        story.append(Paragraph(f"- {a}", body))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Schematic", styles["Heading2"]))
    story.append(Image(str(PNG_PATH), width=7.2 * inch, height=5.2 * inch))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Firmware files", styles["Heading2"]))
    story.append(Paragraph(f"Arduino sketch: {INO_PATH.name}", body))
    story.append(Paragraph("The sketch logs elapsed milliseconds, temperature in °C, and humidity in %RH once per minute with 0.1-unit formatted output.", body))
    story.append(PageBreak())

    story.append(Paragraph("Bill of Materials", styles["Heading1"]))
    data = [["RefDes", "Description", "Qty", "Unit $", "Ext. $", "Supplier / Link"]]
    for ref, desc, qty, unit, supplier, link in BOM:
        data.append([
            ref,
            Paragraph("<br/>".join(wrap(desc, 38)), small),
            str(qty),
            f"{unit:.2f}",
            f"{line_total([ref, desc, qty, unit, supplier, link]):.2f}",
            Paragraph(f"{supplier}<br/>{link}", small),
        ])
    data.append(["", Paragraph("<b>Total estimated cost</b>", body), "", "", f"<b>{total:.2f}</b>", ""])

    table = Table(data, colWidths=[0.6*inch, 2.5*inch, 0.45*inch, 0.7*inch, 0.7*inch, 2.25*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e8fb")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef5e8")),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph("Limitations / notes", styles["Heading2"]))
    story.append(Paragraph("Live supplier pricing and stock were not verified; listed prices are reasonable estimates for single-quantity hobbyist purchases.", body))
    story.append(Paragraph("Absolute sensor accuracy depends on the exact module vendor, airflow, placement, and calibration. The firmware writes values with 0.1-unit resolution, which is not the same as guaranteed absolute accuracy.", body))
    story.append(Paragraph("For long-term deployments, add a real-time clock and enclosure design review.", body))

    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=0.45*inch, rightMargin=0.45*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    doc.build(story)


def main():
    write_text_outputs()
    raise SystemExit('Current temp_humidity generator still fails validation and needs redesign before reliable versioned rendering.')


if __name__ == "__main__":
    main()
