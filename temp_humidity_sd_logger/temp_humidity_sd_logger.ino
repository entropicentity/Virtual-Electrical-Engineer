#include <SPI.h>
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
