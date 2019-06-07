#include <Wire.h>

int SLAVE_ADDRESS = 0x20; // arduino address
// Analog Pin
#define PIN_VOLT A1
// Charger flag
#define PIN_CHARGE 2
float InVolt;

void setup() {
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(analogReading);
  analogReference(INTERNAL);
  pinMode(PIN_CHARGE, INPUT);
}

void loop() {
}

void analogReading() {
  InVolt = 0;
  // read Analog pin
  InVolt = analogRead(PIN_VOLT);
  int16_t val;
  val = int(InVolt);
  boolean chg = digitalRead(PIN_CHARGE);
  byte Arr[3];
  Arr[0] = (val >> 8) & 0xFF;
  Arr[1] = val & 0xFF;
  Arr[2] = byte(chg);
  Wire.write(Arr, 3);
}
