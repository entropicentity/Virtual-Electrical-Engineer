#include <Servo.h>

// Pin map matches the package schematic.
static const int SERVO_PIN = 3;
static const int BUZZER_PIN = 6;
static const int TRIG_PIN = 9;
static const int ECHO_PIN = 10;

static const int MIN_ANGLE = 30;
static const int MAX_ANGLE = 150;
static const int STEP_ANGLE = 5;
static const long THRESHOLD_CM = 100;   // 1 meter
static const unsigned long SETTLE_MS = 180;

Servo scanner;

long readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(3);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return 999;
  long distance = duration / 58;
  return distance;
}

void beepAlert(bool on) {
  digitalWrite(BUZZER_PIN, on ? HIGH : LOW);
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  beepAlert(false);
  scanner.attach(SERVO_PIN);
  scanner.write((MIN_ANGLE + MAX_ANGLE) / 2);
  delay(500);
}

void loop() {
  bool tooClose = false;

  for (int angle = MIN_ANGLE; angle <= MAX_ANGLE; angle += STEP_ANGLE) {
    scanner.write(angle);
    delay(SETTLE_MS);
    long d = readDistanceCm();
    if (d < THRESHOLD_CM) {
      tooClose = true;
      break;
    }
  }

  for (int angle = MAX_ANGLE; angle >= MIN_ANGLE; angle -= STEP_ANGLE) {
    scanner.write(angle);
    delay(SETTLE_MS);
    long d = readDistanceCm();
    if (d < THRESHOLD_CM) {
      tooClose = true;
      break;
    }
  }

  if (tooClose) {
    for (int i = 0; i < 4; ++i) {
      beepAlert(true);
      delay(120);
      beepAlert(false);
      delay(100);
    }
  } else {
    beepAlert(false);
  }
}
