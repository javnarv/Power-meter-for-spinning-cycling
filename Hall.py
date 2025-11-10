import RPi.GPIO as GPIO
import time
import math
import csv
from collections import deque
from datetime import datetime

HALL_PIN = 17

contador_pulsos = 0
tiempo_ultimo_pulso = None
PULSOS_POR_VUELTA = 1  # Pulsos por vuelta de la rueda
VENTANA_PROMEDIO = 3
FACTOR_BIELA=4
intervalos = deque(maxlen=VENTANA_PROMEDIO)

# Parámetros físicos
DIAMETRO_RUEDA = 0.42  # metros
CIRCUNFERENCIA = math.pi * DIAMETRO_RUEDA  # metros por vuelta

# Acumulador de distancia
vueltas_totales = 0

# Archivo CSV de registro
CSV_FILE = "hall_log.csv"

# Control del tiempo de guardado
ULTIMO_REGISTRO = 0
INTERVALO_REGISTRO = 5  # segundos

# Control del tiempo total de sesión
HORA_INICIO = datetime.now()

def inicializar_csv():
    """Crea el archivo CSV con encabezados si no existe."""
    try:
        with open(CSV_FILE, mode='x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["FechaHora", "RPM", "Velocidad_kmh", "Distancia_km"])
    except FileExistsError:
        pass  # Ya existe

def registrar_csv(rpm, velocidad, distancia):
    """Registra una línea de datos periódica."""
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"{rpm:.2f}",
            f"{velocidad:.2f}",
            f"{distancia:.4f}",
            f"{contador_pulsos:.0f}"
        ])

def registrar_resumen(distancia_total):
    """Registra una línea resumen al finalizar la sesión."""
    hora_fin = datetime.now()
    duracion = (hora_fin - HORA_INICIO).total_seconds() / 60  # minutos

    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([])
        writer.writerow(["--- RESUMEN SESIÓN ---"])
        writer.writerow(["Inicio", HORA_INICIO.strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Fin", hora_fin.strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Duración (min)", f"{duracion:.2f}"])
        writer.writerow(["Distancia total (km)", f"{distancia_total:.4f}"])
        writer.writerow(["Pulsos Totales", f"{contador_pulsos:.0f}"])
        writer.writerow([])

def contar_pulso(channel=None):
    """Maneja la interrupción del sensor Hall."""
    global contador_pulsos, tiempo_ultimo_pulso, vueltas_totales, ULTIMO_REGISTRO
    tiempo_actual = time.time()
    contador_pulsos += 1
    print(f"pulsos: ",{contador_pulsos})

    if tiempo_ultimo_pulso is not None:
        intervalo = tiempo_actual - tiempo_ultimo_pulso
        intervalos.append(intervalo)
        intervalo_medio = sum(intervalos) / len(intervalos)
        frecuencia_media = 1 / intervalo_medio if intervalo_medio > 0 else 0

        # RPM media
        rpm_media = (frecuencia_media * 60) / (PULSOS_POR_VUELTA*FACTOR_BIELA)

        # Velocidad (km/h)
        velocidad_kmh = rpm_media * CIRCUNFERENCIA * 60 / 1000

        # Calcular vueltas totales y distancia
        vueltas_totales = contador_pulsos / PULSOS_POR_VUELTA
        distancia_km = vueltas_totales * CIRCUNFERENCIA / 1000

        # Mostrar por consola
        print(f"Pulso {contador_pulsos}: {rpm_media:.2f} RPM | {velocidad_kmh:.2f} km/h | Distancia: {distancia_km:.4f} km")

        # Registrar datos cada INTERVALO_REGISTRO segundos
        if tiempo_actual - ULTIMO_REGISTRO >= INTERVALO_REGISTRO:
            registrar_csv(rpm_media, velocidad_kmh, distancia_km)
            ULTIMO_REGISTRO = tiempo_actual
    else:
        print("Primer pulso detectado")

    tiempo_ultimo_pulso = tiempo_actual

def peripheral_setup():
    """Configura el pin GPIO para el sensor Hall."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        GPIO.remove_event_detect(HALL_PIN)
    except Exception:
        pass

    GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=contar_pulso, bouncetime=100)

def main():
    """Bucle principal."""
    inicializar_csv()
    peripheral_setup()
    print(f"Esperando pulsos en pin {HALL_PIN}... (Ctrl+C para salir)")
    print(f"Inicio de sesión: {HORA_INICIO.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        distancia_total = (contador_pulsos / PULSOS_POR_VUELTA) * CIRCUNFERENCIA / 1000
        registrar_resumen(distancia_total)
        print("\nPrograma terminado correctamente.")
        print(f"Distancia total: {distancia_total:.4f} km")
        print("Resumen guardado en hall_log.csv")

if __name__ == '__main__':
    main()
