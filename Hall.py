import RPi.GPIO as GPIO
import time
from collections import deque  # para guardar los últimos intervalos

HALL_PIN = 17

contador_pulsos = 0
tiempo_ultimo_pulso = None

# --- CONFIGURACIÓN ---
PULSOS_POR_VUELTA = 2          # Ajusta según tu sensor/imán
VENTANA_PROMEDIO = 3          # Número de intervalos usados para promediar
intervalos = deque(maxlen=VENTANA_PROMEDIO)

def contar_pulso(channel=None):
    global contador_pulsos, tiempo_ultimo_pulso

    tiempo_actual = time.time()
    contador_pulsos += 1

    if tiempo_ultimo_pulso is not None:
        intervalo = tiempo_actual - tiempo_ultimo_pulso
        intervalos.append(intervalo)

        # Calcular promedio de intervalos
        intervalo_medio = sum(intervalos) / len(intervalos)
        frecuencia_media = 1 / intervalo_medio if intervalo_medio > 0 else 0
        rpm_media = (frecuencia_media * 60) / PULSOS_POR_VUELTA

        print(f"Pulso {contador_pulsos}: {rpm_media:.2f} RPM (promedio sobre {len(intervalos)} muestras)")
    else:
        print("Primer pulso detectado (sin intervalo previo)")

    tiempo_ultimo_pulso = tiempo_actual

def peripheral_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=contar_pulso, bouncetime=200)

def main():
    peripheral_setup()
    print("Esperando pulsos en pin 17... (Ctrl+C para salir)")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nPrograma terminado correctamente.")

if __name__ == '__main__':
    main()
