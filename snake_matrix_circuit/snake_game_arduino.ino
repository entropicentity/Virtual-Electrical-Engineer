#include <LedControl.h>

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
