
#include <SPI.h>
#include <MFRC522.h>

// RFID-controlled solenoid access controller
// Target: Arduino Nano (ATmega328P)
// Power assumptions:
// - Nano logic: 5 V
// - MFRC522: 3.3 V supply and 3.3 V logic
// - Solenoid: 12 V switched on low side by MOSFET
//
// Pin cross-check with schematic:
// D10 -> MFRC522 SDA/SS
// D13 -> MFRC522 SCK
// D11 -> MFRC522 MOSI
// D12 -> MFRC522 MISO
// D9  -> MFRC522 RST
// D3  -> MOSFET gate / solenoid driver
// D5  -> green LED
// D6  -> red LED
// D7  -> optional buzzer

constexpr uint8_t SS_PIN = 10;
constexpr uint8_t RST_PIN = 9;
constexpr uint8_t SOLENOID_PIN = 3;
constexpr uint8_t GREEN_LED_PIN = 5;
constexpr uint8_t RED_LED_PIN = 6;
constexpr uint8_t BUZZER_PIN = 7;

constexpr unsigned long UNLOCK_MS = 3000;
constexpr unsigned long CARD_HOLDOFF_MS = 1500;

MFRC522 rfid(SS_PIN, RST_PIN);

struct CardUID {
  byte length;
  byte uid[7];
};

const CardUID authorizedCards[] = {
  {4, {0xDE, 0xAD, 0xBE, 0xEF, 0, 0, 0}},
  {4, {0x12, 0x34, 0x56, 0x78, 0, 0, 0}},
};

unsigned long lastScanMs = 0;

void setLockedState() {
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
}

void beep(unsigned int durationMs, unsigned int frequency = 2400) {
  tone(BUZZER_PIN, frequency, durationMs);
}

bool uidMatches(const MFRC522::Uid &uid, const CardUID &allowed) {
  if (uid.size != allowed.length) return false;
  for (byte i = 0; i < uid.size; ++i) {
    if (uid.uidByte[i] != allowed.uid[i]) return false;
  }
  return true;
}

bool isAuthorized(const MFRC522::Uid &uid) {
  for (const auto &card : authorizedCards) {
    if (uidMatches(uid, card)) return true;
  }
  return false;
}

void printUid(const MFRC522::Uid &uid) {
  Serial.print(F("UID:"));
  for (byte i = 0; i < uid.size; ++i) {
    if (uid.uidByte[i] < 0x10) Serial.print('0');
    Serial.print(uid.uidByte[i], HEX);
    if (i + 1 < uid.size) Serial.print(':');
  }
  Serial.println();
}

void grantAccess() {
  Serial.println(F("Access granted"));
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, HIGH);
  beep(80, 2800);
  digitalWrite(SOLENOID_PIN, HIGH);
  delay(UNLOCK_MS);
  setLockedState();
}

void denyAccess() {
  Serial.println(F("Access denied"));
  digitalWrite(GREEN_LED_PIN, LOW);
  for (int i = 0; i < 2; ++i) {
    digitalWrite(RED_LED_PIN, HIGH);
    beep(80, 1800);
    delay(120);
    digitalWrite(RED_LED_PIN, LOW);
    delay(120);
  }
}

void setup() {
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setLockedState();
  digitalWrite(RED_LED_PIN, LOW);
  noTone(BUZZER_PIN);

  Serial.begin(115200);
  while (!Serial) {}

  SPI.begin();
  rfid.PCD_Init();
  Serial.println(F("RFID solenoid access controller ready"));
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  const unsigned long now = millis();
  if (now - lastScanMs < CARD_HOLDOFF_MS) {
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    return;
  }

  printUid(rfid.uid);

  if (isAuthorized(rfid.uid)) {
    grantAccess();
  } else {
    denyAccess();
  }

  lastScanMs = millis();
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
