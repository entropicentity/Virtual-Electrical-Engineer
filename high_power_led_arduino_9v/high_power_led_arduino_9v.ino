// Arduino-controlled high-power LED example
// Pin map:
// D9 -> 220R gate resistor -> Q1 gate
// Q1 source -> GND
// Q1 drain -> LED cathode
// LED anode -> R1 -> +9V
// R3 10k pulls gate to GND for safe boot-off behavior

const int PIN_LED_GATE = 9;

void setup() {
  pinMode(PIN_LED_GATE, OUTPUT);
  digitalWrite(PIN_LED_GATE, LOW);
}

void loop() {
  digitalWrite(PIN_LED_GATE, HIGH);
  delay(1000);
  digitalWrite(PIN_LED_GATE, LOW);
  delay(1000);
}
