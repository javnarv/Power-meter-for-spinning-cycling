#include <SoftwareSerial.h>
#include "HX711.h"

// Pines HX711
const int DOUT_PIN = 3;
const int SCK_PIN = 2;

// Pines BLE AT-09
const int BLE_RX = 10;
const int BLE_TX = 11;

HX711 balanza;
SoftwareSerial ble(BLE_RX, BLE_TX); // RX, TX

float factor_calibracion = -7050; // Ajusta con tu calibración
unsigned long lastSend = 0;
const long interval = 2000; // Enviar cada 2 segundos

void setup() {
  Serial.begin(9600);
  ble.begin(9600);
  
  Serial.println("Iniciando Balanza BLE para móvil...");
  
  // Inicializar balanza
  balanza.begin(DOUT_PIN, SCK_PIN);
  balanza.set_scale(factor_calibracion);
  balanza.tare();
  
  // Configurar BLE básico
  setupBLE();
  
  Serial.println("Listo! Busca 'BalanzaBLE' en tu móvil");
}

void setupBLE() {
  delay(1000);
  
  // Comandos AT básicos para el módulo
  sendATCommand("AT"); // Test de comunicación
  delay(200);
  sendATCommand("AT+NAMEBalanzaBLE"); // Nombre visible
  delay(200);
  sendATCommand("AT+RESET"); // Reiniciar
  delay(1000);
}

void sendATCommand(String command) {
  ble.println(command);
  delay(100);
  Serial.print("AT: ");
  Serial.println(command);
}

void loop() {
  // Leer peso
  float peso = balanza.get_units(5);
  
  // Enviar por BLE cada 2 segundos
  if (millis() - lastSend >= interval) {
    String data = "Peso: " + String(peso, 1) + " g";
    
    // Enviar por BLE
    ble.println(data);
    
    // Mostrar en monitor serial
    Serial.println("Enviado: " + data);
    
    lastSend = millis();
  }
  
  // Leer comandos desde BLE (para tarar desde móvil)
  if (ble.available()) {
    String command = ble.readString();
    command.trim(); // Eliminar espacios y saltos de línea
    
    Serial.print("Comando recibido: ");
    Serial.println(command);
    
    if (command == "T" || command == "t" || command == "TARA") {
      balanza.tare();
      ble.println("Tara realizada - Peso: 0.0 g");
      Serial.println("Tara ejecutada desde móvil");
    }
  }
  
  delay(100);
}