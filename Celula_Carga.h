#include "HX711.h"

// Pines de conexión
const int DOUT_PIN = 3;
const int SCK_PIN = 2;

HX711 balanza;

void setup() {
  Serial.begin(9600);
  Serial.println("Iniciando balanza...");
  
  balanza.begin(DOUT_PIN, SCK_PIN);
  Serial.print("Lectura sin tara: ");
  Serial.println(balanza.read());
  
  Serial.println("No ponga ningún peso sobre la balanza");
  Serial.println("Destarando...");
  balanza.tare(); // Establece el cero
  Serial.println("Listo para pesar");
}

void loop() {
  Serial.print("Peso: ");
  Serial.print(balanza.get_units(10), 1); // Promedia 10 lecturas
  Serial.println(" g");
  
  delay(1000);
}