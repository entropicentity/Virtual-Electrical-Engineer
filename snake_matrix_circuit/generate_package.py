from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import schemdraw
from schemdraw import elements as elm


BASE = Path('/workspace/snake_matrix_circuit')


@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float
    kind: str
    name: str

    def overlaps(self, other: 'BBox', margin: float = 0.0) -> bool:
        return not (
            self.x2 + margin <= other.x1
            or other.x2 + margin <= self.x1
            or self.y2 + margin <= other.y1
            or other.y2 + margin <= self.y1
        )


def validate_layout(boxes: list[BBox]) -> None:
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if a.overlaps(b, margin=0.05):
                raise ValueError(f'Layout overlap detected between {a.name} and {b.name}')


def build_bom() -> pd.DataFrame:
    items = [
        {
            'Item': 1,
            'Refs': 'U1',
            'Qty': 1,
            'Description': 'Arduino Nano compatible board (ATmega328P/328PB, USB-C preferred)',
            'Specs': '5 V logic, Arduino IDE compatible, breadboard friendly',
            'MPN': 'GG-DIY-AB2',
            'Package': 'Nano dev board',
            'UnitPriceUSD': 2.86,
            'Supplier': 'Gringo Gadgets',
            'URL': 'https://www.gringogadgets.com/dev-board-nano-v3-0-for-arduino-ide-usb-c-ch340-atmega-328pb/',
            'Notes': 'Live web price seen for 328PB Nano-compatible board',
        },
        {
            'Item': 2,
            'Refs': 'U2',
            'Qty': 1,
            'Description': '8x8 LED dot matrix module with MAX7219 driver',
            'Specs': '5 V supply, SPI-like DIN/CLK/CS interface, red common-cathode matrix module',
            'MPN': 'FC-16 / MAX7219 module',
            'Package': 'Module',
            'UnitPriceUSD': 1.25,
            'Supplier': 'Electropeak',
            'URL': 'https://electropeak.com/max7219-dot-matrix-display-module',
            'Notes': 'As-low-as price used as estimate; exact vendor/region may vary',
        },
        {
            'Item': 3,
            'Refs': 'S1-S4',
            'Qty': 4,
            'Description': 'Momentary tactile pushbutton 6x6 mm, 4-pin',
            'Specs': 'SPST-NO, through-hole, human input buttons for U/D/L/R',
            'MPN': 'Generic 6x6mm tactile switch',
            'Package': 'THT switch',
            'UnitPriceUSD': 0.35,
            'Supplier': 'DIYMORE',
            'URL': 'https://www.diymore.cc/products/20pcs-6x6x6-mm-4pin-tactile-touch-push-button-switch-tact-switches',
            'Notes': 'Pack price divided to per-switch estimate',
        },
        {
            'Item': 4,
            'Refs': 'R1-R4',
            'Qty': 4,
            'Description': 'Resistor, through-hole',
            'Specs': '10 kΩ, 1/4 W, 5%, button pull-up/down or optional biasing',
            'MPN': 'Generic 10K resistor',
            'Package': 'Axial THT',
            'UnitPriceUSD': 0.02,
            'Supplier': 'Estimated',
            'URL': 'https://www.digikey.com/',
            'Notes': 'Estimated commodity pricing',
        },
        {
            'Item': 5,
            'Refs': 'C1-C2',
            'Qty': 2,
            'Description': 'Decoupling capacitor',
            'Specs': '100 nF ceramic, 16 V or higher',
            'MPN': 'Generic 100nF MLCC/THT',
            'Package': 'Radial or ceramic',
            'UnitPriceUSD': 0.03,
            'Supplier': 'Estimated',
            'URL': 'https://www.digikey.com/',
            'Notes': 'Recommended local decoupling at controller/display power',
        },
        {
            'Item': 6,
            'Refs': 'J1',
            'Qty': 1,
            'Description': 'USB-C breakout for 5 V power input (optional if Nano USB powers system directly)',
            'Specs': 'USB-C sink breakout with CC resistors, 5 V output',
            'MPN': 'Adafruit 4090',
            'Package': 'Breakout board',
            'UnitPriceUSD': 2.95,
            'Supplier': 'Adafruit',
            'URL': 'https://www.adafruit.com/product/4090',
            'Notes': 'Optional external power-entry module',
        },
        {
            'Item': 7,
            'Refs': 'H1-H3',
            'Qty': 1,
            'Description': 'Header pins / Dupont jumper set',
            'Specs': '2.54 mm pitch, for module and breadboard interconnect',
            'MPN': 'Generic header/jumper kit',
            'Package': 'Accessory',
            'UnitPriceUSD': 2.00,
            'Supplier': 'Estimated',
            'URL': 'https://www.adafruit.com/category/100',
            'Notes': 'Estimated accessory cost',
        },
    ]
    df = pd.DataFrame(items)
    df['ExtendedPriceUSD'] = df['Qty'] * df['UnitPriceUSD']
    return df


def save_concept_and_bom(df: pd.DataFrame) -> None:
    total = df['ExtendedPriceUSD'].sum()
    concept = {
        'goal': 'USB-powered Snake game on a single 8x8 LED dot-matrix with 4 pushbuttons.',
        'assumptions': [
            'Single-player Snake uses one MAX7219-driven 8x8 module as the whole playfield.',
            'Arduino Nano-compatible board handles display refresh, game logic, scoring, and button debouncing.',
            'USB 5V is the system rail. The MAX7219 module and Nano both run from 5V logic.',
            'Buttons use the Nano internal pull-ups in firmware; external 10k resistors are included as optional support parts.',
            'This is a prototyping-friendly design, not a production EMI/safety-certified product.',
        ],
        'basic_circuit_description': [
            'U1 (Arduino Nano) is the controller. It reads S1-S4 direction buttons and updates the game state.',
            'U2 is a MAX7219 LED matrix module connected by DIN, CLK, and CS/LOAD to U1 digital pins.',
            'The 5V rail from USB powers U1 and U2 in parallel, with a common ground.',
            'Each pushbutton connects between a Nano GPIO pin and ground so a press reads active-low.',
            'Local 100nF decoupling capacitors are placed near the Nano 5V pin and near the matrix module VCC input.',
        ],
        'main_components': ['Arduino Nano compatible board', 'MAX7219 8x8 LED matrix module', '4 tactile buttons', '2 decoupling capacitors'],
        'firmware_needed': True,
        'important_unknowns': [
            'Whether you want sound, score display, or larger cascaded matrices later.',
            'Mechanical enclosure, PCB, or breadboard final build style.',
        ],
        'estimated_total_usd': round(float(total), 2),
    }
    (BASE / 'concept.json').write_text(json.dumps(concept, indent=2))
    df.to_csv(BASE / 'bom.csv', index=False)


def draw_schematic() -> Path:
    boxes = [
        BBox(0.2, 4.2, 3.3, 7.9, 'component', 'U1_ArduinoNano'),
        BBox(6.3, 4.6, 9.7, 7.6, 'component', 'U2_MAX7219Matrix'),
        BBox(0.3, 0.6, 1.7, 1.8, 'component', 'S1_UP'),
        BBox(2.0, 0.6, 3.4, 1.8, 'component', 'S2_DOWN'),
        BBox(3.7, 0.6, 5.1, 1.8, 'component', 'S3_LEFT'),
        BBox(5.4, 0.6, 6.8, 1.8, 'component', 'S4_RIGHT'),
        BBox(0.2, 8.4, 2.5, 9.2, 'component', 'J1_USB5V'),
        BBox(4.0, 8.35, 5.3, 9.0, 'component', 'C1'),
        BBox(8.2, 8.35, 9.5, 9.0, 'component', 'C2'),
    ]
    validate_layout(boxes)

    out = BASE / 'snake_matrix_schematic.svg'
    with schemdraw.Drawing(file=str(out), show=False) as d:
        d.config(unit=1.0, fontsize=10)

        d += elm.Dot(open=True).label('J1 USB 5V input / or Nano USB power', loc='right')
        d += elm.Line().up(0.8)
        d += elm.Label().label('5V rail', loc='right')
        d.push()
        d += elm.Line().right(8.4)
        d += elm.Dot()
        d.pop()
        d += elm.Line().down(0.8)

        nano = d.add(elm.Ic(pins=[
            elm.IcPin(name='D2', side='left', slot='1/7'),
            elm.IcPin(name='D3', side='left', slot='2/7'),
            elm.IcPin(name='D4', side='left', slot='3/7'),
            elm.IcPin(name='D5', side='left', slot='4/7'),
            elm.IcPin(name='5V', side='left', slot='5/7'),
            elm.IcPin(name='GND', side='left', slot='6/7'),
            elm.IcPin(name='RST', side='left', slot='7/7'),
            elm.IcPin(name='D10/CS', side='right', slot='1/7'),
            elm.IcPin(name='D11/DIN', side='right', slot='2/7'),
            elm.IcPin(name='D13/CLK', side='right', slot='3/7'),
            elm.IcPin(name='3V3', side='right', slot='4/7'),
            elm.IcPin(name='A0', side='right', slot='5/7'),
            elm.IcPin(name='VIN', side='right', slot='6/7'),
            elm.IcPin(name='GND', side='right', slot='7/7'),
        ], label='U1\nArduino Nano\nATmega328P/328PB').at((2.0, 5.8)))

        matrix = d.add(elm.Ic(pins=[
            elm.IcPin(name='VCC', side='left', slot='1/5'),
            elm.IcPin(name='GND', side='left', slot='2/5'),
            elm.IcPin(name='DIN', side='left', slot='3/5'),
            elm.IcPin(name='CS', side='left', slot='4/5'),
            elm.IcPin(name='CLK', side='left', slot='5/5'),
            elm.IcPin(name='DOUT', side='right', slot='3/5'),
        ], label='U2\nMAX7219\n8x8 Matrix Module').at((8.0, 5.8)))

        # power rails
        nano_5v = nano.absanchors['5V']
        nano_gnd_left = nano.absanchors['GND']
        nano_d2 = nano.absanchors['D2']
        nano_d3 = nano.absanchors['D3']
        nano_d4 = nano.absanchors['D4']
        nano_d5 = nano.absanchors['D5']
        nano_cs = nano.absanchors['D10/CS']
        nano_din = nano.absanchors['D11/DIN']
        nano_clk = nano.absanchors['D13/CLK']

        matrix_vcc = matrix.absanchors['VCC']
        matrix_gnd = matrix.absanchors['GND']
        matrix_din = matrix.absanchors['DIN']
        matrix_cs = matrix.absanchors['CS']
        matrix_clk = matrix.absanchors['CLK']

        d += elm.Line().at(nano_5v).up(3.0)
        d += elm.Dot()
        d += elm.Line().left(1.8)
        d += elm.Label().label('5V', loc='left')
        d += elm.Line().at(matrix_vcc).up(3.0)
        d += elm.Dot()
        d += elm.Line().left(0.8)

        d += elm.Ground().at(nano_gnd_left).down()
        d += elm.Ground().at(matrix_gnd).down()

        # SPI-like lines
        d += elm.Line().at(nano_cs).right(1.3)
        d += elm.Line().up(0.2)
        d += elm.Line().right(2.0)
        d += elm.Line().down(0.2)
        d += elm.Line().to(matrix_cs)

        d += elm.Line().at(nano_din).right(1.0)
        d += elm.Line().right(2.5)
        d += elm.Line().to(matrix_din)

        d += elm.Line().at(nano_clk).right(1.2)
        d += elm.Line().down(0.2)
        d += elm.Line().right(2.1)
        d += elm.Line().up(0.2)
        d += elm.Line().to(matrix_clk)

        # buttons
        button_positions = [(0.8, 1.3, 'S1 UP', 'D2'), (2.5, 1.3, 'S2 DOWN', 'D3'), (4.2, 1.3, 'S3 LEFT', 'D4'), (5.9, 1.3, 'S4 RIGHT', 'D5')]
        pin_lookup = {'D2': nano_d2, 'D3': nano_d3, 'D4': nano_d4, 'D5': nano_d5}
        for (x, y, label, pin) in button_positions:
            sw = d.add(elm.Switch().at((x, y)).right().label(label, loc='top'))
            d += elm.Ground().at(sw.end).down()
            start = pin_lookup[pin]
            d += elm.Line().at(start).left(0.9)
            d += elm.Line().down(abs(start.y - y))
            d += elm.Line().to(sw.start)

        # decoupling capacitors
        c1 = d.add(elm.Capacitor().at((4.5, 8.2)).down().label('C1 100nF', loc='right'))
        d += elm.Line().at(c1.start).left(0.7)
        d += elm.Label().label('5V', loc='left')
        d += elm.Ground().at(c1.end).down()
        c2 = d.add(elm.Capacitor().at((8.8, 8.2)).down().label('C2 100nF', loc='right'))
        d += elm.Line().at(c2.start).left(0.7)
        d += elm.Label().label('5V', loc='left')
        d += elm.Ground().at(c2.end).down()

        d.save(str(out))
    return out


def draw_block_png() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    blocks = [
        ((0.5, 4.7), 2.0, 0.8, 'USB 5V'),
        ((3.0, 3.2), 2.5, 1.6, 'Arduino Nano\nGame logic + buttons'),
        ((7.0, 3.4), 2.3, 1.4, 'MAX7219\n8x8 LED Matrix'),
        ((1.0, 0.9), 5.6, 1.0, 'S1-S4 pushbuttons\nUp / Down / Left / Right'),
    ]
    for (x, y), w, h, label in blocks:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, linewidth=2))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center', fontsize=12)
    ax.annotate('', xy=(3.0, 4.0), xytext=(2.5, 5.1), arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(7.0, 4.1), xytext=(5.5, 4.1), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(6.15, 4.3, 'DIN / CS / CLK', ha='center', fontsize=11)
    ax.annotate('', xy=(3.6, 2.2), xytext=(3.6, 1.9), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(4.0, 2.05, 'GPIO inputs', fontsize=11)
    ax.text(1.2, 5.65, '5V rail to Nano + Matrix', fontsize=11)
    path = BASE / 'snake_matrix_block_diagram.png'
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close(fig)
    return path


def write_firmware() -> Path:
    code = r'''#include <LedControl.h>

// Snake game firmware template for a single MAX7219 8x8 matrix.
// Hardware mapping must match the schematic package.

static const uint8_t PIN_BTN_UP    = 2;   // S1 -> U1 D2
static const uint8_t PIN_BTN_DOWN  = 3;   // S2 -> U1 D3
static const uint8_t PIN_BTN_LEFT  = 4;   // S3 -> U1 D4
static const uint8_t PIN_BTN_RIGHT = 5;   // S4 -> U1 D5

static const uint8_t PIN_MAX_CS   = 10;   // U2 CS  <- U1 D10
static const uint8_t PIN_MAX_DIN  = 11;   // U2 DIN <- U1 D11 (MOSI)
static const uint8_t PIN_MAX_CLK  = 13;   // U2 CLK <- U1 D13 (SCK)

LedControl matrix = LedControl(PIN_MAX_DIN, PIN_MAX_CLK, PIN_MAX_CS, 1);

struct Point { int8_t x; int8_t y; };

enum Direction { UP, DOWN, LEFT, RIGHT };

Point snake[64];
uint8_t snakeLength = 3;
Direction dir = RIGHT;
Point food = {5, 4};
unsigned long lastStepMs = 0;
const unsigned long stepIntervalMs = 350;
bool gameOver = false;

void resetGame() {
  snake[0] = {2, 4};
  snake[1] = {1, 4};
  snake[2] = {0, 4};
  snakeLength = 3;
  dir = RIGHT;
  food = {5, 4};
  gameOver = false;
}

void placeFood() {
  while (true) {
    Point candidate = { (int8_t)random(0, 8), (int8_t)random(0, 8) };
    bool clash = false;
    for (uint8_t i = 0; i < snakeLength; ++i) {
      if (snake[i].x == candidate.x && snake[i].y == candidate.y) {
        clash = true;
        break;
      }
    }
    if (!clash) {
      food = candidate;
      return;
    }
  }
}

void clearMatrix() {
  for (uint8_t row = 0; row < 8; ++row) matrix.setRow(0, row, 0);
}

void drawGame() {
  clearMatrix();
  matrix.setLed(0, food.y, food.x, true);
  for (uint8_t i = 0; i < snakeLength; ++i) {
    matrix.setLed(0, snake[i].y, snake[i].x, true);
  }
}

bool pressed(uint8_t pin) {
  return digitalRead(pin) == LOW;
}

void readControls() {
  // Active-low due to INPUT_PULLUP wiring.
  if (pressed(PIN_BTN_UP) && dir != DOWN) dir = UP;
  else if (pressed(PIN_BTN_DOWN) && dir != UP) dir = DOWN;
  else if (pressed(PIN_BTN_LEFT) && dir != RIGHT) dir = LEFT;
  else if (pressed(PIN_BTN_RIGHT) && dir != LEFT) dir = RIGHT;
}

void stepGame() {
  Point head = snake[0];
  if (dir == UP) head.y -= 1;
  if (dir == DOWN) head.y += 1;
  if (dir == LEFT) head.x -= 1;
  if (dir == RIGHT) head.x += 1;

  if (head.x < 0 || head.x > 7 || head.y < 0 || head.y > 7) {
    gameOver = true;
    return;
  }

  for (uint8_t i = 0; i < snakeLength; ++i) {
    if (snake[i].x == head.x && snake[i].y == head.y) {
      gameOver = true;
      return;
    }
  }

  for (int i = snakeLength; i > 0; --i) snake[i] = snake[i - 1];
  snake[0] = head;

  if (head.x == food.x && head.y == food.y) {
    if (snakeLength < 63) snakeLength++;
    placeFood();
  }
}

void showGameOver() {
  static bool blink = false;
  blink = !blink;
  for (uint8_t row = 0; row < 8; ++row) {
    matrix.setRow(0, row, blink ? B11111111 : 0);
  }
}

void setup() {
  randomSeed(analogRead(A0));
  pinMode(PIN_BTN_UP, INPUT_PULLUP);
  pinMode(PIN_BTN_DOWN, INPUT_PULLUP);
  pinMode(PIN_BTN_LEFT, INPUT_PULLUP);
  pinMode(PIN_BTN_RIGHT, INPUT_PULLUP);

  matrix.shutdown(0, false);
  matrix.setIntensity(0, 3);
  matrix.clearDisplay(0);

  resetGame();
  drawGame();
}

void loop() {
  if (gameOver) {
    showGameOver();
    delay(250);
    if (pressed(PIN_BTN_UP) || pressed(PIN_BTN_DOWN) || pressed(PIN_BTN_LEFT) || pressed(PIN_BTN_RIGHT)) {
      delay(150);
      resetGame();
    }
    return;
  }

  readControls();

  unsigned long now = millis();
  if (now - lastStepMs >= stepIntervalMs) {
    lastStepMs = now;
    stepGame();
    drawGame();
  }
}
'''
    path = BASE / 'snake_game_arduino.ino'
    path.write_text(code)
    return path


def make_pdf(df: pd.DataFrame, schematic_path: Path, block_path: Path, firmware_path: Path) -> Path:
    total = df['ExtendedPriceUSD'].sum()
    pdf_path = BASE / 'snake_matrix_circuit_package.pdf'
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Small', fontSize=8, leading=10))
    story = []
    story.append(Paragraph('Snake Game LED Dot Matrix Circuit Package', styles['Title']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('USB-powered Arduino Nano compatible design using one MAX7219 8x8 LED matrix and four pushbuttons for directional control.', styles['BodyText']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('<b>Assumptions:</b> single 8x8 playfield, 5V USB power, active-low buttons using internal pull-ups, prototype-level design.', styles['BodyText']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f'<b>Files:</b> schematic {schematic_path.name}, block diagram {block_path.name}, firmware {firmware_path.name}', styles['Small']))
    story.append(Spacer(1, 4*mm))
    story.append(RLImage(str(block_path), width=170*mm, height=102*mm))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('The detailed schematic is also included as an SVG file in the package directory. The block diagram above summarizes power, control, and display interconnects.', styles['Small']))
    story.append(Spacer(1, 5*mm))

    bom_table = [['Item', 'Refs', 'Qty', 'Description', 'Unit $', 'Ext $', 'Supplier']]
    for _, row in df.iterrows():
        bom_table.append([
            str(row['Item']), str(row['Refs']), str(row['Qty']),
            Paragraph(str(row['Description']), styles['Small']),
            f"{row['UnitPriceUSD']:.2f}", f"{row['ExtendedPriceUSD']:.2f}",
            Paragraph(f'<link href="{row["URL"]}">{row["Supplier"]}</link>', styles['Small'])
        ])
    bom_table.append(['', '', '', Paragraph('<b>Total estimated cost</b>', styles['Small']), '', f'{total:.2f}', 'USD'])
    table = Table(bom_table, colWidths=[10*mm, 18*mm, 10*mm, 78*mm, 16*mm, 16*mm, 28*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.whitesmoke),
    ]))
    story.append(table)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('Firmware summary: the Arduino sketch reads the four buttons, drives the MAX7219 with LedControl, updates snake position on a timed loop, and blinks the matrix on game-over.', styles['BodyText']))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph('Limitations: one 8x8 matrix makes the game very compact; prices were assembled from public web pages and some commodity parts use estimates rather than live cart-verified distributor quotes.', styles['BodyText']))
    doc.build(story)
    return pdf_path


def write_summary(df: pd.DataFrame, schematic: Path, block: Path, firmware: Path, pdf: Path) -> None:
    total = df['ExtendedPriceUSD'].sum()
    md = f'''# Snake Game LED Matrix Circuit Package

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
Estimated total: ${total:.2f} USD

## Output files
- Schematic: {schematic}
- Block diagram: {block}
- Firmware: {firmware}
- BOM CSV: {BASE / 'bom.csv'}
- Concept JSON: {BASE / 'concept.json'}
- PDF package: {pdf}

## Notes
- Buttons are intended to use Arduino internal pull-ups.
- Optional USB-C breakout is only needed if you want separate external 5V entry instead of powering through the Nano USB port.
- This is a prototype-friendly design package, not a production release.
'''
    (BASE / 'README.md').write_text(md)


def main() -> None:
    df = build_bom()
    save_concept_and_bom(df)
    schematic = draw_schematic()
    block = draw_block_png()
    firmware = write_firmware()
    pdf = make_pdf(df, schematic, block, firmware)
    write_summary(df, schematic, block, firmware, pdf)
    print('Generated package in', BASE)


if __name__ == '__main__':
    main()
