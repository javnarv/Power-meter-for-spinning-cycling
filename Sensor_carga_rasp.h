#include <SoftwareSerial.h>
#include "HX711.h"

const int DOUT_PIN = 3;
const int SCK_PIN = 2;
const int BLE_RX = 10;
const int BLE_TX = 11;

HX711 balanza;
SoftwareSerial ble(BLE_RX, BLE_TX);

float factor_calibracion = -7050;

void setup() {
  Serial.begin(9600);
  ble.begin(9600);
  
  balanza.begin(DOUT_PIN, SCK_PIN);
  balanza.set_scale(factor_calibracion);
  balanza.tare();
  
  Serial.println("Balanza BLE lista - Esperando comandos...");
}

void loop() {
  // Leer peso y enviar
  float peso = balanza.get_units(5);
  String data = "Peso: " + String(peso, 1) + " g";
  ble.println(data);
  Serial.println("Enviado: " + data);
  
  // Leer comandos desde BLE
  if (ble.available()) {
    String command = ble.readString();
    command.trim();
    
    Serial.print("Comando recibido: '");
    Serial.print(command);
    Serial.println("'");
    
    if (command == "T" || command == "t") {
      balanza.tare();
      ble.println("✅ Tara realizada - Peso: 0.0 g");
      Serial.println("Tara ejecutada");
    }
    else if (command == "STATUS") {
      ble.println("🔧 Estado: OK - Balanza operativa");
    }
    else {
      ble.println("❌ Comando no reconocido: " + command);
    }
  }
  
  delay(2000);
}