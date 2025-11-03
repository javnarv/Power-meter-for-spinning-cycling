import time
import RPi.GPIO as GPIO

# ========================
# CONFIGURACION DE PINES
# ========================
DT_PIN = 5      # Pin DATA del HX711
SCK_PIN = 6     # Pin CLOCK del HX711

#DEFINICION DE ESCALA
ESCALA=41940
BIELA=0.17
G=9.806


# ========================
# CLASE HX711
# ========================
class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.PD_SCK = pd_sck_pin
        self.DOUT = dout_pin
        self.GAIN = gain
        self.OFFSET = 0
        self.SCALE = 1

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        # Esperar a que DOUT se ponga en bajo
        while GPIO.input(self.DOUT) == 1:
            time.sleep(0.0001)

        count = 0
        for i in range(24):
            GPIO.output(self.PD_SCK, True)
            count = count << 1
            GPIO.output(self.PD_SCK, False)
            if GPIO.input(self.DOUT):
                count += 1

        # Pulsos extra para el canal/gain
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        # Convertir a valor con signo
        if count & 0x800000:
            count |= ~0xffffff

        return count

    def read_average(self, times=10):
        total = 0
        for _ in range(times):
            total += self.read()
        return total / times

    def tare(self, times=15):
        """Calibrar en vacio (tara)."""
        sum = self.read_average(times)
        self.OFFSET = sum
        print(f"Tara completada. OFFSET = {self.OFFSET}")

    def get_value(self, times=5):
        value = self.read_average(times) - self.OFFSET
        return value

    def get_weight(self, times=5):
        value = self.get_value(times)
        weight = value / self.SCALE
        return weight

    def set_scale(self, scale):
        self.SCALE = scale

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

# ========================
# PROGRAMA PRINCIPAL
# ========================
def main():
    hx = HX711(dout_pin=DT_PIN, pd_sck_pin=SCK_PIN)
    hx.set_scale(ESCALA)   # Ajusta este factor segun tu calibracion
    #hx.tare()             # Calibrar sin peso

    print("Iniciando lectura continua. Ctrl+C para salir.\n")

    try:
        while True:
            peso = hx.get_weight(5)
            fuerza= peso*G
            par=fuerza*BIELA
            print(f"Peso: {peso:.2f} Kg", f"Fuerza: {fuerza:.2f} N", f"Par: {par:.2f} Nm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLectura detenida.")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
