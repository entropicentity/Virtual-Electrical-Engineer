#include <Wire.h>
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
