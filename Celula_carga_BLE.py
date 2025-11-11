import asyncio
import bleak
import time
import json
from datetime import datetime

DEVICE_NAME = "BalanzaBLE"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_TX = "0000ffe1-0000-1000-8000-00805f9b34fb"

class BalanzaBLE:
    def __init__(self):
        self.client = None
        self.device = None
        self.archivo_datos = datos_balanza.csv"
        self.archivo_log = "log_balanza.txt"
        
        # Crear archivo CSV con cabecera si no existe
        try:
            with open(self.archivo_datos, 'a') as f:
                f.seek(0, 2)  # Ir al final del archivo
                if f.tell() == 0:  # Si está vacío
                    f.write("fecha,hora,peso_g,comando\n")
        except Exception as e:
            print(f"Error creando archivo: {e}")

    async def discover_device(self):
        """Buscar el dispositivo BLE"""
        print("Buscando BalanzaBLE...")
        devices = await bleak.BleakScanner.discover()
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                print(f"✓ Encontrado: {device.name}")
                return device
        return None

    async def connect_and_control(self):
        """Conectar y permitir enviar comandos"""
        self.device = await self.discover_device()
        
        if not self.device:
            print("❌ Dispositivo no encontrado")
            return
            
        try:
            self.client = bleak.BleakClient(self.device.address)
            await self.client.connect()
            print("✓ Conectado!")
            
            # Suscribirse para recibir datos
            await self.client.start_notify(CHARACTERISTIC_UUID_TX, self.data_received)
            
            # Bucle principal para enviar comandos
            await self.control_loop()
            
        except Exception as e:
            print(f"Error: {e}")
            self.guardar_log(f"ERROR: {e}")
        finally:
            if self.client and await self.client.is_connected():
                await self.client.disconnect()

    def data_received(self, sender, data):
        """Callback cuando llegan datos"""
        try:
            mensaje = data.decode('utf-8').strip()
            print(f"📊 {mensaje}")
            
            # Guardar datos si es un peso
            if "Peso:" in mensaje:
                self.guardar_datos(mensaje)
                
        except Exception as e:
            print(f"Error recibiendo datos: {e}")

    def guardar_datos(self, mensaje_peso):
        """Guardar datos de peso en CSV"""
        try:
            ahora = datetime.now()
            fecha = ahora.strftime("%Y-%m-%d")
            hora = ahora.strftime("%H:%M:%S")
            
            # Extraer el valor numérico del peso
            peso_valor = mensaje_peso.replace("Peso:", "").replace("g", "").strip()
            
            with open(self.archivo_datos, 'a') as f:
                f.write(f'"{fecha}","{hora}","{peso_valor}","auto"\n')
                
            print(f"💾 Dato guardado: {peso_valor}g")
            
        except Exception as e:
            print(f"Error guardando datos: {e}")

    def guardar_log(self, mensaje):
        """Guardar eventos en log"""
        try:
            with open(self.archivo_log, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensaje}\n")
        except Exception as e:
            print(f"Error guardando log: {e}")

    async def send_command(self, command):
        """Enviar comando al Arduino"""
        try:
            if self.client and await self.client.is_connected():
                data_to_send = command.encode('utf-8')
                await self.client.write_gatt_char(CHARACTERISTIC_UUID_RX, data_to_send)
                print(f"✅ Comando enviado: '{command}'")
                
                # Guardar en log el comando enviado
                self.guardar_log(f"COMANDO_ENVIADO: {command}")
                return True
        except Exception as e:
            error_msg = f"Error enviando comando: {e}"
            print(f"❌ {error_msg}")
            self.guardar_log(error_msg)
        return False

    async def control_loop(self):
        """Bucle principal para enviar comandos"""
        print("\n💡 Comandos disponibles:")
        print("  'T' - Tara (poner a cero)")
        print("  'S' - Estado")
        print("  'R' - Ver últimos datos")
        print("  'quit' - Salir")
        
        while True:
            try:
                command = input("\nIngrese comando: ").strip().upper()
                
                if command == 'QUIT':
                    break
                elif command == 'T':
                    await self.send_command("T")
                    # Guardar tara manual en CSV
                    ahora = datetime.now()
                    with open(self.archivo_datos, 'a') as f:
                        f.write(f'"{ahora.strftime("%Y-%m-%d")}","{ahora.strftime("%H:%M:%S")}","0.0","tara_manual"\n')
                elif command == 'S':
                    await self.send_command("STATUS")
                elif command == 'R':
                    self.mostrar_ultimos_datos()
                elif command:
                    await self.send_command(command)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    def mostrar_ultimos_datos(self):
        """Mostrar los últimos datos guardados"""
        try:
            with open(self.archivo_datos, 'r') as f:
                lineas = f.readlines()
                print("\n📈 Últimos 5 registros:")
                for linea in lineas[-5:]:
                    print(f"  {linea.strip()}")
        except Exception as e:
            print(f"Error leyendo datos: {e}")

async def main():
    balanza = BalanzaBLE()
    await balanza.connect_and_control()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Programa terminado")