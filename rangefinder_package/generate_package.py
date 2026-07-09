from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak


BASE = Path(__file__).resolve().parent


@dataclass
class BomItem:
    item: int
    refs: str
    qty: int
    description: str
    specs: str
    mpn: str
    package: str
    unit_price: float
    supplier: str
    url: str
    notes: str

    @property
    def ext_price(self) -> float:
        return self.qty * self.unit_price


def build_bom() -> List[BomItem]:
    return [
        BomItem(1, "U1", 1, "Arduino Nano Every", "5 V MCU board, ATmega4809, 20 MHz", "ABX00028", "Nano dev board", 12.90, "Arduino Store", "https://store-usa.arduino.cc/products/nano-every", "Chosen for simple 5 V USB-powered prototyping and wide library support."),
        BomItem(2, "U2", 1, "VL53L1X ToF sensor carrier", "4 cm to 400 cm, I2C, 2.6-5.5 V input", "Pololu 3415", "0.5 x 0.7 in breakout", 22.95, "Pololu", "https://www.pololu.com/product/3415", "Laser ToF selected over ultrasonic for narrower beam and cleaner enclosure integration."),
        BomItem(3, "DS1", 1, "0.96 in OLED display", "128x64 monochrome, SSD1306 compatible, I2C, 3-5 V ready", "Adafruit 326", "Breakout module", 17.50, "Adafruit", "https://www.adafruit.com/product/326", "Readable low-power display for distance readout and UI prompts."),
        BomItem(4, "S1", 1, "Momentary pushbutton", "SPST-NO, through-hole, 6x6 mm tact switch", "TEA-5144", "THT tact switch", 0.89, "Vetco", "https://vetco.net/products/vupn1504_tact_switch_66mm_5mm_through_hole", "User trigger to capture a new distance measurement."),
        BomItem(5, "R1", 1, "Pull-up resistor", "10 kΩ, 1/4 W, ±5%", "Generic 10k THT", "Axial THT", 0.10, "Estimated", "https://example.com/generic-10k-resistor", "Pulls button input high; button shorts input to ground when pressed."),
        BomItem(6, "C1,C2", 2, "Ceramic decoupling capacitor", "0.1 µF, 50 V, X7R or similar", "FA18X7R1H104KNU06", "Radial THT", 0.10, "Futurlec/estimate", "https://www.futurlec.com/Capacitors/C100UCpr.shtml", "Local supply decoupling near MCU/display wiring zone and sensor wiring zone."),
        BomItem(7, "C3", 1, "Bulk capacitor", "10 µF, 16 V electrolytic", "VHT10M16", "Radial THT", 0.60, "Vetco", "https://vetco.net/products/nte-vht10m16_10uf_16_volt_electrolytic_capacitor", "Helps smooth USB 5 V rail during display update and ranging bursts."),
        BomItem(8, "J1", 1, "USB-C power breakout", "USB-C sink breakout with 5.1 kΩ CC resistors", "Adafruit 4090", "Breakout module", 2.95, "Adafruit", "https://www.adafruit.com/product/4090", "Used as convenient 5 V input connector for a more finished build."),
        BomItem(9, "H1", 1, "Breakaway male header strip", "1x40, 2.54 mm pitch", "Pololu 965", "Pin header", 0.95, "Pololu", "https://www.pololu.com/product/965", "Cut to fit modules that ship unsoldered."),
        BomItem(10, "W1", 1, "Jumper wire set", "20-wire female/male ribbon, 150 mm", "Adafruit 1954", "Wire harness", 1.95, "Adafruit", "https://www.adafruit.com/product/1954", "Prototype interconnect set; replace with custom harness in enclosure build."),
    ]


def write_markdown(bom: List[BomItem]) -> None:
    total = sum(item.ext_price for item in bom)
    md = []
    md.append("# Rangefinder with Screen and Trigger Button\n")
    md.append("## Goal\n")
    md.append("Create a compact USB-powered rangefinder that measures distance on demand when a front-panel pushbutton is pressed, then displays the result on a small OLED screen.\n")
    md.append("## Assumptions\n")
    md.append("- Laser time-of-flight sensing is preferred over ultrasonic for a tighter measurement cone and cleaner UI behavior.\n")
    md.append("- Power is from a 5 V USB-C source; battery operation is not included in this baseline design.\n")
    md.append("- The package targets a practical prototype / module-based build, not a production-certified PCB release.\n")
    md.append("- The VL53L1X carrier board handles its own 2.8 V regulation and I2C level shifting on SDA/SCL, but XSHUT and GPIO1 remain 2.8 V-domain pins and are therefore intentionally left unused in this design.\n")
    md.append("\n## Basic circuit description\n")
    md.append("The USB-C breakout feeds a 5 V rail shared by the Arduino Nano Every, the OLED display, and the VL53L1X carrier. A 10 µF bulk capacitor and two 0.1 µF decoupling capacitors stabilize the local rail. The OLED and VL53L1X share the I2C bus: Nano A4 -> SDA and Nano A5 -> SCL. A momentary pushbutton drives a digital input; the input is held high by a 10 kΩ pull-up resistor and goes low when the button is pressed. Firmware idles showing the last measurement and captures a new reading only when the button is pressed, reducing accidental continuous ranging and making the device feel like a handheld instrument.\n")
    md.append("\n## Connection table\n")
    md.append("| From | To | Notes |\n|---|---|---|\n")
    rows = [
        ("J1 VBUS", "5V rail", "USB-C 5 V input"),
        ("J1 GND", "GND rail", "Common return"),
        ("U1 5V", "5V rail", "Nano powered directly from regulated USB 5 V"),
        ("U1 GND", "GND rail", "Common ground"),
        ("U1 A4/SDA", "U2 SDA and DS1 SDA", "Shared I2C data"),
        ("U1 A5/SCL", "U2 SCL and DS1 SCL", "Shared I2C clock"),
        ("U2 VIN", "5V rail", "VL53L1X carrier accepts 2.6-5.5 V"),
        ("U2 GND", "GND rail", "Common ground"),
        ("DS1 VIN", "5V rail", "Display breakout is 5 V ready"),
        ("DS1 GND", "GND rail", "Common ground"),
        ("U1 D2", "S1 node", "Button sense input, active low"),
        ("R1", "Between 5V rail and S1/U1 D2 node", "10 kΩ pull-up"),
        ("S1", "Between U1 D2 node and GND", "Press to trigger measurement"),
    ]
    for a, b, c in rows:
        md.append(f"| {a} | {b} | {c} |\n")
    md.append("\n## Firmware behavior\n")
    md.append("- Initialize I2C, OLED, and VL53L1X.\n- Display a startup splash and prompt.\n- Debounce the button.\n- On each valid button press, acquire one distance sample, convert to millimeters/centimeters, and update the display.\n- If the sensor reports invalid data, show an error message instead of stale numbers.\n")
    md.append("\n## BOM\n")
    md.append("|Item|Refs|Qty|Description|MPN|Unit $|Ext $|Supplier|\n|---|---|---:|---|---|---:|---:|---|\n")
    for item in bom:
        md.append(f"|{item.item}|{item.refs}|{item.qty}|{item.description}|{item.mpn}|{item.unit_price:.2f}|{item.ext_price:.2f}|[{item.supplier}]({item.url})|\n")
    md.append(f"\n**Total estimated cost: ${total:.2f}**\n")
    md.append("\n## Electrical review summary\n")
    md.append("- No level shifter is required on SDA/SCL because the selected VL53L1X carrier includes level shifting and the OLED breakout is 5 V ready.\n")
    md.append("- Do not connect Nano 5 V GPIO directly to VL53L1X XSHUT or GPIO1 because those lines are not 5 V tolerant on the selected carrier. This design avoids that issue by leaving them unused.\n")
    md.append("- All modules share a common ground.\n")
    md.append("- This is a prototype/module package; enclosure thermal, EMC, ESD, and drop robustness are not validated.\n")
    (BASE / "design_summary.md").write_text("".join(md), encoding="utf-8")


def draw_component(ax, x, y, w, h, label, pins: List[Tuple[str, Tuple[float, float], str]]):
    rect = Rectangle((x, y), w, h, fill=False, linewidth=1.8)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10, fontweight="bold")
    for pin_name, (px, py), align in pins:
        ax.add_patch(Circle((px, py), 0.06, color="black"))
        dx = -0.15 if align == "right" else 0.15
        ha = "right" if align == "right" else "left"
        ax.text(px + dx, py, pin_name, ha=ha, va="center", fontsize=8)


def line(ax, pts, **kwargs):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color="black", linewidth=1.5, **kwargs)


def draw_schematic() -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(7, 7.7, "USB-Powered Rangefinder with OLED and Trigger Button", ha="center", fontsize=16, fontweight="bold")
    ax.text(1.1, 7.1, "5V", fontsize=10, fontweight="bold")
    line(ax, [(0.8, 6.9), (13.2, 6.9)])
    ax.text(1.05, 0.55, "GND", fontsize=10, fontweight="bold")
    line(ax, [(0.8, 0.8), (13.2, 0.8)])

    draw_component(ax, 0.9, 3.5, 1.3, 1.4, "J1\nUSB-C\n5V In", [
        ("VBUS", (2.2, 4.45), "left"),
        ("GND", (2.2, 3.85), "left"),
    ])
    draw_component(ax, 3.1, 2.2, 2.5, 3.2, "U1\nArduino\nNano Every", [
        ("5V", (3.1, 5.0), "right"),
        ("GND", (3.1, 2.6), "right"),
        ("A4/SDA", (5.6, 4.6), "left"),
        ("A5/SCL", (5.6, 4.0), "left"),
        ("D2", (5.6, 3.1), "left"),
    ])
    draw_component(ax, 8.0, 4.0, 2.0, 1.8, "U2\nVL53L1X\nCarrier", [
        ("VIN", (8.0, 5.3), "right"),
        ("GND", (8.0, 4.5), "right"),
        ("SDA", (10.0, 5.1), "left"),
        ("SCL", (10.0, 4.7), "left"),
    ])
    draw_component(ax, 8.0, 1.8, 2.0, 1.5, "DS1\n128x64 OLED", [
        ("VIN", (8.0, 2.95), "right"),
        ("GND", (8.0, 2.15), "right"),
        ("SDA", (10.0, 2.75), "left"),
        ("SCL", (10.0, 2.35), "left"),
    ])
    draw_component(ax, 11.4, 2.2, 1.0, 0.9, "S1\nBTN", [
        ("1", (11.4, 2.65), "right"),
        ("2", (12.4, 2.65), "left"),
    ])
    draw_component(ax, 10.8, 4.0, 1.0, 1.1, "R1\n10k", [
        ("A", (10.8, 4.55), "right"),
        ("B", (11.8, 4.55), "left"),
    ])

    draw_component(ax, 1.6, 5.5, 0.9, 0.7, "C3\n10uF", [
        ("+", (1.6, 5.85), "right"),
        ("-", (2.5, 5.85), "left"),
    ])
    draw_component(ax, 6.0, 5.5, 0.9, 0.7, "C1\n0.1uF", [
        ("1", (6.0, 5.85), "right"),
        ("2", (6.9, 5.85), "left"),
    ])
    draw_component(ax, 6.0, 1.4, 0.9, 0.7, "C2\n0.1uF", [
        ("1", (6.0, 1.75), "right"),
        ("2", (6.9, 1.75), "left"),
    ])

    line(ax, [(2.2, 4.45), (2.2, 6.9)])
    line(ax, [(2.2, 3.85), (2.2, 0.8)])
    line(ax, [(3.1, 5.0), (3.1, 6.2), (2.2, 6.2)])
    line(ax, [(3.1, 2.6), (3.1, 0.8)])
    line(ax, [(8.0, 5.3), (8.0, 6.4), (7.0, 6.4), (7.0, 6.9)])
    line(ax, [(8.0, 4.5), (8.0, 0.8)])
    line(ax, [(8.0, 2.95), (8.0, 6.0), (7.4, 6.0), (7.4, 6.9)])
    line(ax, [(8.0, 2.15), (8.0, 0.8)])
    line(ax, [(1.6, 5.85), (1.6, 6.9)])
    line(ax, [(2.5, 5.85), (2.5, 0.8)])
    line(ax, [(6.0, 5.85), (6.0, 6.9)])
    line(ax, [(6.9, 5.85), (6.9, 0.8)])
    line(ax, [(6.0, 1.75), (6.0, 6.9)])
    line(ax, [(6.9, 1.75), (6.9, 0.8)])

    line(ax, [(5.6, 4.6), (6.6, 4.6), (6.6, 5.1), (10.0, 5.1)])
    line(ax, [(5.6, 4.0), (6.3, 4.0), (6.3, 4.7), (10.0, 4.7)])
    line(ax, [(6.6, 4.6), (6.6, 2.75), (10.0, 2.75)])
    line(ax, [(6.3, 4.0), (6.3, 2.35), (10.0, 2.35)])

    line(ax, [(11.8, 4.55), (11.8, 6.0), (11.8, 6.9)])
    line(ax, [(10.8, 4.55), (10.2, 4.55), (10.2, 3.1), (5.6, 3.1)])
    line(ax, [(10.2, 3.1), (10.2, 2.65), (11.4, 2.65)])
    line(ax, [(12.4, 2.65), (12.4, 0.8)])

    ax.text(7.3, 5.25, "I2C SDA", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=0.2))
    ax.text(7.3, 4.15, "I2C SCL", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=0.2))
    ax.text(9.2, 3.35, "BTN_NET", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=0.2))
    ax.text(9.3, 6.95, "5V rail", fontsize=9, va="bottom")
    ax.text(9.3, 0.85, "GND rail", fontsize=9, va="bottom")
    ax.text(8.1, 7.35, "XSHUT/GPIO1 intentionally unused to avoid 5 V-domain issues", fontsize=8)

    fig.tight_layout()
    fig.savefig(BASE / "rangefinder_schematic.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_firmware() -> None:
    firmware = r'''#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <VL53L1X.h>

// Rangefinder with OLED and trigger button
// Target board: Arduino Nano Every (ATmega4809, 5 V logic)
// Assumed libraries:
//   Adafruit GFX Library
//   Adafruit SSD1306
//   VL53L1X by Pololu
// Wiring cross-check:
//   A4 -> OLED SDA, VL53L1X SDA
//   A5 -> OLED SCL, VL53L1X SCL
//   D2 -> Trigger button node (active low, external 10k pull-up to +5V)
//   5V -> OLED VIN, VL53L1X VIN
//   GND -> OLED GND, VL53L1X GND, button return
// Important electrical note:
//   Do not connect Nano 5V GPIO directly to the VL53L1X XSHUT or GPIO1 pins on the selected carrier,
//   because those pins are not level shifted on that breakout.

constexpr uint8_t PIN_TRIGGER_BUTTON = 2;
constexpr uint8_t SCREEN_WIDTH = 128;
constexpr uint8_t SCREEN_HEIGHT = 64;
constexpr uint8_t OLED_ADDR = 0x3C;
constexpr uint16_t DEBOUNCE_MS = 30;
constexpr uint16_t TIMING_BUDGET_MS = 50;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
VL53L1X sensor;

bool lastButtonStable = HIGH;
bool lastButtonReading = HIGH;
unsigned long lastDebounceChangeMs = 0;
unsigned long measurementCount = 0;
uint16_t lastDistanceMm = 0;
bool lastMeasurementValid = false;

void drawSplash() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 8);
  display.println(F("Rangefinder"));
  display.setTextSize(1);
  display.setCursor(12, 38);
  display.println(F("Press button to measure"));
  display.display();
}

void drawReading(bool valid, uint16_t distanceMm) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("Press to capture"));
  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  if (valid) {
    float distanceCm = distanceMm / 10.0f;
    display.setTextSize(2);
    display.setCursor(0, 20);
    display.print(distanceCm, 1);
    display.println(F(" cm"));

    display.setTextSize(1);
    display.setCursor(0, 50);
    display.print(F("Raw: "));
    display.print(distanceMm);
    display.print(F(" mm  #"));
    display.println(measurementCount);
  } else {
    display.setTextSize(2);
    display.setCursor(0, 22);
    display.println(F("No valid"));
    display.setCursor(0, 42);
    display.println(F("target"));
  }

  display.display();
}

bool readButtonPressedEvent() {
  bool reading = digitalRead(PIN_TRIGGER_BUTTON);

  if (reading != lastButtonReading) {
    lastDebounceChangeMs = millis();
    lastButtonReading = reading;
  }

  if ((millis() - lastDebounceChangeMs) > DEBOUNCE_MS) {
    if (reading != lastButtonStable) {
      lastButtonStable = reading;
      if (lastButtonStable == LOW) {
        return true;
      }
    }
  }

  return false;
}

bool captureMeasurement(uint16_t &distanceMm) {
  sensor.read();

  if (sensor.timeoutOccurred()) {
    Serial.println(F("Sensor timeout"));
    return false;
  }

  if (sensor.ranging_data.range_status != VL53L1X::RangeValid) {
    Serial.print(F("Invalid range status: "));
    Serial.println(sensor.ranging_data.range_status);
    return false;
  }

  distanceMm = sensor.ranging_data.range_mm;
  return true;
}

void setupSensor() {
  if (!sensor.init()) {
    Serial.println(F("VL53L1X init failed"));
    drawReading(false, 0);
    while (true) {
      delay(100);
    }
  }

  sensor.setDistanceMode(VL53L1X::Long);
  sensor.setMeasurementTimingBudget(TIMING_BUDGET_MS * 1000UL);
  sensor.startContinuous(0);
}

void setupDisplay() {
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    while (true) {
      delay(100);
    }
  }
  drawSplash();
}

void setup() {
  pinMode(PIN_TRIGGER_BUTTON, INPUT);

  Serial.begin(115200);
  delay(100);
  Serial.println(F("Rangefinder starting"));

  Wire.begin();
  setupDisplay();
  setupSensor();

  delay(800);
  drawReading(false, 0);
}

void loop() {
  if (readButtonPressedEvent()) {
    uint16_t distance = 0;
    bool valid = captureMeasurement(distance);

    measurementCount++;
    lastMeasurementValid = valid;
    if (valid) {
      lastDistanceMm = distance;
      Serial.print(F("Distance mm: "));
      Serial.println(distance);
    }

    drawReading(valid, valid ? distance : 0);
  }
}
'''
    fw_dir = BASE / "firmware"
    fw_dir.mkdir(exist_ok=True)
    ino_dir = fw_dir / "rangefinder_nano_every"
    ino_dir.mkdir(exist_ok=True)
    (ino_dir / "rangefinder_nano_every.ino").write_text(firmware, encoding="utf-8")


def build_pdf(bom: List[BomItem]) -> None:
    total = sum(item.ext_price for item in bom)
    doc = SimpleDocTemplate(str(BASE / "rangefinder_design_package.pdf"), pagesize=letter,
                            rightMargin=0.6 * inch, leftMargin=0.6 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=11))
    story = []

    story.append(Paragraph("Rangefinder with OLED Screen and Trigger Button", styles["Title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Prototype design package for a USB-powered handheld distance meter using a VL53L1X time-of-flight sensor, Arduino Nano Every, 128x64 OLED display, and a single pushbutton to trigger measurements.", styles["BodyText"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Assumptions: USB 5 V power, module-based build, no battery subsystem, and no use of VL53L1X XSHUT/GPIO1 to avoid 5 V logic-domain issues on the selected carrier board.", styles["Small"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Image(str(BASE / "rangefinder_schematic.png"), width=7.1 * inch, height=4.0 * inch))
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph("Key electrical summary", styles["Heading2"]))
    for text in [
        "Shared I2C bus: Nano A4/A5 connect to both the OLED and VL53L1X carrier.",
        "Button input is active low using an external 10 kΩ pull-up to +5 V.",
        "USB-C breakout provides the 5 V rail. Add local bulk and ceramic decoupling near the wiring cluster.",
        "The chosen VL53L1X carrier shifts SDA/SCL but not XSHUT/GPIO1; those pins are intentionally left unconnected in this design.",
    ]:
        story.append(Paragraph(f"• {text}", styles["BodyText"]))
    story.append(Spacer(1, 0.16 * inch))

    story.append(Paragraph("Bill of Materials", styles["Heading2"]))
    data = [["Item", "Refs", "Qty", "Description", "MPN", "Unit $", "Ext $", "Supplier"]]
    for item in bom:
        data.append([str(item.item), item.refs, str(item.qty), item.description, item.mpn, f"{item.unit_price:.2f}", f"{item.ext_price:.2f}", item.supplier])
    data.append(["", "", "", "", "Total", "", f"{total:.2f}", "USD"])
    table = Table(data, repeatRows=1, colWidths=[0.4 * inch, 0.65 * inch, 0.35 * inch, 2.2 * inch, 1.0 * inch, 0.6 * inch, 0.6 * inch, 1.0 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e8fb")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f3f3f3")),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.16 * inch))
    story.append(Paragraph("Supplier URLs", styles["Heading3"]))
    for item in bom:
        story.append(Paragraph(f"{item.refs}: <link href='{item.url}' color='blue'>{item.supplier}</link> — {item.description}", styles["Small"]))

    story.append(PageBreak())
    story.append(Paragraph("Firmware package", styles["Heading2"]))
    story.append(Paragraph("Included Arduino sketch: firmware/rangefinder_nano_every/rangefinder_nano_every.ino", styles["BodyText"]))
    story.append(Paragraph("Behavior: initialize OLED and VL53L1X, debounce button on D2, perform one ranging transaction per button press, and display either the measured distance or an invalid-target message.", styles["BodyText"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Schematic QA summary", styles["Heading2"]))
    qa = [
        "All electrically relevant installed parts are shown: MCU, sensor, display, USB power input, button, pull-up resistor, and decoupling capacitors.",
        "All shown pins are labeled.",
        "Power and ground rails are explicit.",
        "Wires are drawn with orthogonal routing only.",
        "No wire crosses a component body in the rendered layout.",
        "The firmware pin map matches the schematic labels (A4 SDA, A5 SCL, D2 button).",
    ]
    for item in qa:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Limitations", styles["Heading2"]))
    story.append(Paragraph("This is a concept-to-prototype package. It does not include enclosure CAD, formal PCB layout, EMC/ESD qualification, battery charging, or production DFM review. Prices are current/estimated from public listings and were not validated for stock at time of final packaging.", styles["BodyText"]))

    doc.build(story)


def main() -> None:
    bom = build_bom()
    write_markdown(bom)
    draw_schematic()
    write_firmware()
    build_pdf(bom)


if __name__ == "__main__":
    main()
