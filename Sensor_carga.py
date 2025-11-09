import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Configuración
DT_PIN = 5
SCK_PIN = 6

class CelulaCarga:
    def __init__(self, dt_pin=DT_PIN, sck_pin=SCK_PIN):
        self.hx = HX711(dt_pin, sck_pin)
        self.configurar_sensor()
        
    def configurar_sensor(self):
        # Reset y configuración inicial
        self.hx.reset()
        
        # Configurar ganancia y canal (128 para canal A)
        self.hx.set_gain(128)
        
        # Tara - eliminar peso base
        print("Eliminando peso base... No coloques nada en la balanza")
        time.sleep(3)
        self.hx.tare()
        print("Tara completada")
        
        # Obtener valor de referencia para calibración
        print("Coloca un peso conocido para calibrar...")
        time.sleep(5)
        self.calibrar()
    
    def calibrar(self):
        # Leer valor con peso conocido
        valor = self.hx.get_value()
        print(f"Valor leído con peso conocido: {valor}")
        
        # Aquí debes calcular el factor de escala
        # factor_escala = valor / peso_conocido
        # self.hx.set_scale(factor_escala)
        
    def leer_peso(self, muestras=10):
        try:
            # Leer múltiples muestras y promediar
            valor = self.hx.get_value(muestras)
            peso = valor  # Aquí aplicarías la conversión con el factor de escala
            
            return {
                'valor_raw': valor,
                'peso_kg': peso / 1000.0,  # Ajustar según calibración
                'estado': 'ok'
            }
            
        except Exception as e:
            return {
                'valor_raw': 0,
                'peso_kg': 0,
                'estado': f'error: {str(e)}'
            }
    
    def limpiar(self):
        GPIO.cleanup()

# Uso principal
if __name__ == "__main__":
    try:
        sensor = CelulaCarga()
        
        print("Leyendo datos de la célula de carga...")
        print("Presiona Ctrl+C para detener")
        
        while True:
            datos = sensor.leer_peso()
            print(f"Valor: {datos['valor_raw']:8d} | Peso: {datos['peso_kg']:6.3f} kg | Estado: {datos['estado']}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nDeteniendo aplicación...")
    finally:
        sensor.limpiar()