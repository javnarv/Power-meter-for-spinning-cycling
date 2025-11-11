#include <SoftwareSerial.h>

const int BLE_RX = 10;
const int BLE_TX = 11;
SoftwareSerial ble(BLE_RX, BLE_TX);

void setup() {
  Serial.begin(9600);
  ble.begin(9600);
  
  Serial.println("Configurando AT-09 para ser visible...");
  delay(1000);
  
  setupBLE();
}

void setupBLE() {
  // Comandos esenciales para visibilidad
  sendATCommand("AT");                    // Test
  delay(200);
  sendATCommand("AT+RESET");              // Resetear primero
  delay(1000);
  sendATCommand("AT");                    // Verificar después del reset
  delay(200);
  sendATCommand("AT+ROLE0");              // Modo periférico (esclavo)
  delay(200);
  sendATCommand("AT+IMME0");              // Modo automático - ¡IMPORTANTE!
  delay(200);
  sendATCommand("AT+ADVI3");              // Intervalo de advertising
  delay(200);
  sendATCommand("AT+NAMEBalanzaBLE");     // Nombre
  delay(200);
  sendATCommand("AT+UUID0xFFE0");         // UUID servicio
  delay(200);
  sendATCommand("AT+CHAR0xFFE1");         // UUID característica
  delay(200);
  
  Serial.println("Configuración completada - Debería ser visible ahora");
}

void sendATCommand(String command) {
  ble.println(command);
  delay(500);  // Más tiempo para respuesta
  Serial.print("Enviado: ");
  Serial.println(command);
  
  // Leer y mostrar respuesta
  unsigned long startTime = millis();
  while (millis() - startTime < 1000) {
    if (ble.available()) {
      String response = ble.readString();
      Serial.print("Respuesta: ");
      Serial.println(response);
    }
  }
}

void loop() {
  // El módulo ahora debería ser visible
  delay(1000);
}