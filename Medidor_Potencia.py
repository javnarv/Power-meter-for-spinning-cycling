import math
import time
import csv
import asyncio
import bleak
from collections import deque
from datetime import datetime
import RPi.GPIO as GPIO

# ================= CONFIGURACIÓN HARDWARE =================
# Sensor Hall
HALL_PIN = 17
PULSOS_POR_VUELTA = 1
FACTOR_BIELA = 4
DIAMETRO_RUEDA = 0.42  # metros
CIRCUNFERENCIA = math.pi * DIAMETRO_RUEDA  # metros por vuelta

# Célula de carga BLE
DEVICE_NAME = "BalanzaBLE"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_TX = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Parámetros mecánicos
LONGITUD_BIELA = 0.170  # 170 mm en metros
FLYWHEEL_RADIUS_M = 0.08  # radio del volante (ajustar según tu montaje)

# ================= VARIABLES GLOBALES =================
# Sensor Hall
contador_pulsos = 0
tiempo_ultimo_pulso = None
intervalos = deque(maxlen=3)
vueltas_totales = 0

# Célula de carga
peso_actual = 0.0  # en kg
celula_conectada = False

# Archivos
CSV_FILE = "sistema_completo_log.csv"
ULTIMO_REGISTRO = 0
INTERVALO_REGISTRO = 5  # segundos
HORA_INICIO = datetime.now()

# ================= CLASE CÉLULA DE CARGA BLE =================
class BalanzaBLE:
    def __init__(self):
        self.client = None
        self.device = None
        self.peso_kg = 0.0
        
    async def discover_device(self):
        """Buscar el dispositivo BLE"""
        print("Buscando BalanzaBLE...")
        devices = await bleak.BleakScanner.discover()
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                print(f"✓ Célula de carga encontrada: {device.name}")
                return device
        return None

    async def connect(self):
        """Conectar a la célula de carga"""
        self.device = await self.discover_device()
        
        if not self.device:
            print("❌ Célula de carga no encontrada")
            return False
            
        try:
            self.client = bleak.BleakClient(self.device.address)
            await self.client.connect()
            print("✓ Conectado a célula de carga!")
            
            # Suscribirse para recibir datos
            await self.client.start_notify(CHARACTERISTIC_UUID_TX, self.data_received)
            return True
            
        except Exception as e:
            print(f"Error conectando a célula: {e}")
            return False

    def data_received(self, sender, data):
        """Callback cuando llegan datos de peso"""
        global peso_actual
        try:
            mensaje = data.decode('utf-8').strip()
            if "Peso:" in mensaje:
                # Extraer valor numérico y convertir a kg
                peso_str = mensaje.replace("Peso:", "").replace("g", "").strip()
                peso_g = float(peso_str)
                peso_actual = peso_g / 1000.0  # Convertir a kg
                
        except Exception as e:
            print(f"Error procesando datos de peso: {e}")

    async def send_tara(self):
        """Enviar comando de tara"""
        try:
            if self.client and await self.client.is_connected():
                await self.client.write_gatt_char(CHARACTERISTIC_UUID_RX, b'T')
                print("✅ Tara enviada")
                return True
        except Exception as e:
            print(f"Error enviando tara: {e}")
        return False

    async def disconnect(self):
        """Desconectar célula"""
        if self.client and await self.client.is_connected():
            await self.client.disconnect()

# ================= FUNCIONES SENSOR HALL =================
def contar_pulso(channel=None):
    """Maneja la interrupción del sensor Hall"""
    global contador_pulsos, tiempo_ultimo_pulso, vueltas_totales
    tiempo_actual = time.time()
    contador_pulsos += 1

    if tiempo_ultimo_pulso is not None:
        intervalo = tiempo_actual - tiempo_ultimo_pulso
        intervalos.append(intervalo)
    
    tiempo_ultimo_pulso = tiempo_actual

def calcular_velocidad_y_distancia():
    """Calcula RPM, velocidad y distancia"""
    if len(intervalos) == 0 or tiempo_ultimo_pulso is None:
        return 0.0, 0.0, 0.0
    
    intervalo_medio = sum(intervalos) / len(intervalos)
    frecuencia_media = 1 / intervalo_medio if intervalo_medio > 0 else 0

    # RPM media (considerando factor biela)
    rpm_media = (frecuencia_media * 60) / (PULSOS_POR_VUELTA * FACTOR_BIELA)

    # Velocidad (km/h)
    velocidad_kmh = rpm_media * CIRCUNFERENCIA * 60 / 1000

    # Distancia total
    vueltas_totales = contador_pulsos / PULSOS_POR_VUELTA
    distancia_km = vueltas_totales * CIRCUNFERENCIA / 1000

    return rpm_media, velocidad_kmh, distancia_km

def calcular_potencia(rpm, peso_kg):
    """Calcula la potencia mecánica en vatios"""
    if rpm <= 0 or peso_kg <= 0:
        return 0.0
    
    # Fuerza aplicada (N)
    fuerza_N = peso_kg * 9.80665
    
    # Torque (N·m) - fuerza × longitud de biela
    torque_Nm = fuerza_N * LONGITUD_BIELA
    
    # Velocidad angular (rad/s)
    omega_rad_s = 2.0 * math.pi * (rpm / 60.0)
    
    # Potencia (W) = torque × velocidad angular
    potencia_W = torque_Nm * omega_rad_s
    
    return potencia_W

# ================= FUNCIONES ARCHIVO CSV =================
def inicializar_csv():
    """Crea el archivo CSV con encabezados"""
    try:
        with open(CSV_FILE, mode='x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["FechaHora", "RPM", "Velocidad_kmh", "Distancia_km", 
                           "Peso_kg", "Fuerza_N", "Torque_Nm", "Potencia_W", "Pulsos_Totales"])
    except FileExistsError:
        pass

def registrar_csv(rpm, velocidad, distancia, peso, fuerza, torque, potencia):
    """Registra una línea de datos"""
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"{rpm:.2f}",
            f"{velocidad:.2f}",
            f"{distancia:.4f}",
            f"{peso:.3f}",
            f"{fuerza:.2f}",
            f"{torque:.3f}",
            f"{potencia:.2f}",
            f"{contador_pulsos:.0f}"
        ])

def registrar_resumen(distancia_total, tiempo_total_min):
    """Registra resumen al finalizar"""
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([])
        writer.writerow(["--- RESUMEN SESIÓN ---"])
        writer.writerow(["Inicio", HORA_INICIO.strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Fin", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Duracion (min)", f"{tiempo_total_min:.2f}"])
        writer.writerow(["Distancia total (km)", f"{distancia_total:.4f}"])
        writer.writerow(["Pulsos Totales", f"{contador_pulsos:.0f}"])
        writer.writerow(["Peso maximo (kg)", f"{max([peso_actual]):.3f}"])
        writer.writerow([])

# ================= CONFIGURACIÓN GPIO =================
def peripheral_setup():
    """Configura el pin GPIO para el sensor Hall"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        GPIO.remove_event_detect(HALL_PIN)
    except Exception:
        pass

    GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=contar_pulso, bouncetime=100)

# ================= PROGRAMA PRINCIPAL =================
async def main():
    global peso_actual, ULTIMO_REGISTRO, celula_conectada
    
    # Inicializar sistemas
    inicializar_csv()
    peripheral_setup()
    
    # Conectar a célula de carga
    balanza = BalanzaBLE()
    celula_conectada = await balanza.connect()
    
    if not celula_conectada:
        print("⚠️  Ejecutando sin célula de carga")
    
    print(f"\n🚴 Sistema iniciado - {HORA_INICIO.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Esperando datos... (Ctrl+C para salir)")
    
    try:
        while True:
            tiempo_actual = time.time()
            
            # Calcular métricas del sensor Hall
            rpm, velocidad, distancia = calcular_velocidad_y_distancia()
            
            # Calcular potencia
            fuerza_N = peso_actual * 9.80665
            torque_Nm = fuerza_N * LONGITUD_BIELA
            potencia_W = calcular_potencia(rpm, peso_actual)
            
            # Mostrar en pantalla
            print("\n" + "="*50)
            print(f"📊 MÉTRICAS EN TIEMPO REAL")
            print(f"🔄 RPM: {rpm:6.2f}")
            print(f"🚀 Velocidad: {velocidad:6.2f} km/h")
            print(f"📏 Distancia: {distancia:8.4f} km")
            print(f"⚖️  Peso: {peso_actual:6.3f} kg")
            print(f"💪 Fuerza: {fuerza_N:6.2f} N")
            print(f"🔧 Torque: {torque_Nm:6.3f} N·m")
            print(f"⚡ Potencia: {potencia_W:6.2f} W")
            print(f"🔴 Pulsos totales: {contador_pulsos}")
            print("="*50)
            
            # Registrar en CSV periódicamente
            if tiempo_actual - ULTIMO_REGISTRO >= INTERVALO_REGISTRO:
                registrar_csv(rpm, velocidad, distancia, peso_actual, 
                            fuerza_N, torque_Nm, potencia_W)
                ULTIMO_REGISTRO = tiempo_actual
            
            await asyncio.sleep(1)  # Espera asíncrona
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        
        # Calcular estadísticas finales
        tiempo_fin = datetime.now()
        duracion_min = (tiempo_fin - HORA_INICIO).total_seconds() / 60
        distancia_total = (contador_pulsos / PULSOS_POR_VUELTA) * CIRCUNFERENCIA / 1000
        
        # Guardar resumen
        registrar_resumen(distancia_total, duracion_min)
        
        # Limpiar recursos
        if celula_conectada:
            await balanza.disconnect()
        GPIO.cleanup()
        
        print(f"\n✅ Sistema detenido correctamente")
        print(f"📈 Distancia total: {distancia_total:.4f} km")
        print(f"⏱️  Duración: {duracion_min:.2f} min")
        print(f"💾 Datos guardados en: {CSV_FILE}")

if __name__ == '__main__':
    asyncio.run(main())