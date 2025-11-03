# TFT_ILI9341.py
import time
import RPi.GPIO as GPIO
import spidev

class TFT_ILI9341:
    def __init__(self, rst_pin=24, dc_pin=25, cs_pin=8, spi_bus=0, spi_device=0):
        # Configuración de pines
        self.RST_PIN = rst_pin
        self.DC_PIN = dc_pin
        self.CS_PIN = cs_pin
        
        # Dimensiones (apaisado 90°)
        self.WIDTH = 320
        self.HEIGHT = 240
        
        # Configurar GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        
        # Configurar SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 40000000
        self.spi.mode = 0b00
        
        # Fuente 8x8
        self.font = self._create_font()
        
        # Colores predefinidos RGB565
        self.colors = {
            'BLACK': 0x0000,
            'WHITE': 0xFFFF,
            'RED': 0xF800,
            'GREEN': 0x07E0,
            'BLUE': 0x001F,
            'YELLOW': 0xFFE0,
            'MAGENTA': 0xF81F,
            'CYAN': 0x07FF,
            'ORANGE': 0xFC00,
            'GRAY': 0x8410
        }
        
        print("Librería TFT ILI9341 inicializada")

    def _create_font(self):
        """Crear diccionario de fuente 8x8"""
        return {
            # Letras mayúsculas (A-Z)
            'A': [0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x00],
            'B': [0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0x00],
            'C': [0x3C, 0x66, 0x60, 0x60, 0x60, 0x66, 0x3C, 0x00],
            'D': [0x78, 0x6C, 0x66, 0x66, 0x66, 0x6C, 0x78, 0x00],
            'E': [0x7E, 0x60, 0x60, 0x78, 0x60, 0x60, 0x7E, 0x00],
            'F': [0x7E, 0x60, 0x60, 0x78, 0x60, 0x60, 0x60, 0x00],
            'G': [0x3C, 0x66, 0x60, 0x6E, 0x66, 0x66, 0x3C, 0x00],
            'H': [0x66, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00],
            'I': [0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'J': [0x1E, 0x0C, 0x0C, 0x0C, 0x0C, 0x6C, 0x38, 0x00],
            'K': [0x66, 0x6C, 0x78, 0x70, 0x78, 0x6C, 0x66, 0x00],
            'L': [0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7E, 0x00],
            'M': [0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0x00],
            'N': [0x66, 0x76, 0x7E, 0x7E, 0x6E, 0x66, 0x66, 0x00],
            'O': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'P': [0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0x00],
            'Q': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x0E, 0x00],
            'R': [0x7C, 0x66, 0x66, 0x7C, 0x78, 0x6C, 0x66, 0x00],
            'S': [0x3C, 0x66, 0x60, 0x3C, 0x06, 0x66, 0x3C, 0x00],
            'T': [0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00],
            'U': [0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'V': [0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00],
            'W': [0x63, 0x63, 0x63, 0x6B, 0x7F, 0x77, 0x63, 0x00],
            'X': [0x66, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x66, 0x00],
            'Y': [0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0x00],
            'Z': [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x7E, 0x00],
            
            # Letras minúsculas (a-z)
            'a': [0x00, 0x00, 0x3C, 0x06, 0x3E, 0x66, 0x3E, 0x00],
            'b': [0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x7C, 0x00],
            'c': [0x00, 0x00, 0x3C, 0x66, 0x60, 0x66, 0x3C, 0x00],
            'd': [0x06, 0x06, 0x3E, 0x66, 0x66, 0x66, 0x3E, 0x00],
            'e': [0x00, 0x00, 0x3C, 0x66, 0x7E, 0x60, 0x3C, 0x00],
            'f': [0x1C, 0x36, 0x30, 0x78, 0x30, 0x30, 0x30, 0x00],
            'g': [0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x3C],
            'h': [0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00],
            'i': [0x18, 0x00, 0x38, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'j': [0x0C, 0x00, 0x1C, 0x0C, 0x0C, 0x0C, 0x6C, 0x38],
            'k': [0x60, 0x60, 0x66, 0x6C, 0x78, 0x6C, 0x66, 0x00],
            'l': [0x38, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'm': [0x00, 0x00, 0x66, 0x7F, 0x7F, 0x6B, 0x63, 0x00],
            'n': [0x00, 0x00, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00],
            'o': [0x00, 0x00, 0x3C, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'p': [0x00, 0x00, 0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60],
            'q': [0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x06],
            'r': [0x00, 0x00, 0x7C, 0x66, 0x60, 0x60, 0x60, 0x00],
            's': [0x00, 0x00, 0x3E, 0x60, 0x3C, 0x06, 0x7C, 0x00],
            't': [0x30, 0x30, 0x7C, 0x30, 0x30, 0x30, 0x1C, 0x00],
            'u': [0x00, 0x00, 0x66, 0x66, 0x66, 0x66, 0x3E, 0x00],
            'v': [0x00, 0x00, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00],
            'w': [0x00, 0x00, 0x63, 0x6B, 0x7F, 0x7F, 0x36, 0x00],
            'x': [0x00, 0x00, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x00],
            'y': [0x00, 0x00, 0x66, 0x66, 0x66, 0x3E, 0x06, 0x3C],
            'z': [0x00, 0x00, 0x7E, 0x0C, 0x18, 0x30, 0x7E, 0x00],
            
            # Números (0-9)
            '0': [0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0x00],
            '1': [0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x7E, 0x00],
            '2': [0x3C, 0x66, 0x06, 0x0C, 0x30, 0x60, 0x7E, 0x00],
            '3': [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00],
            '4': [0x06, 0x0E, 0x1E, 0x66, 0x7F, 0x06, 0x06, 0x00],
            '5': [0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00],
            '6': [0x3C, 0x66, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00],
            '7': [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x30, 0x30, 0x00],
            '8': [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00],
            '9': [0x3C, 0x66, 0x66, 0x3E, 0x06, 0x66, 0x3C, 0x00],
            
            # Símbolos comunes
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            '!': [0x18, 0x18, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00],
            '?': [0x3C, 0x66, 0x0C, 0x18, 0x18, 0x00, 0x18, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00],
            ',': [0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x30],
            ':': [0x00, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00, 0x00],
            '-': [0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00],
            '_': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7E, 0x00],
            '=': [0x00, 0x00, 0x7E, 0x00, 0x7E, 0x00, 0x00, 0x00],
            '+': [0x00, 0x18, 0x18, 0x7E, 0x18, 0x18, 0x00, 0x00],
            '*': [0x00, 0x66, 0x3C, 0xFF, 0x3C, 0x66, 0x00, 0x00],
            '/': [0x00, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x00, 0x00],
            '(': [0x0C, 0x18, 0x30, 0x30, 0x30, 0x18, 0x0C, 0x00],
            ')': [0x30, 0x18, 0x0C, 0x0C, 0x0C, 0x18, 0x30, 0x00],
        }

    def _write_command(self, cmd):
        """Escribir comando al display"""
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.xfer([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def _write_data(self, data):
        """Escribir datos al display"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.xfer([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def _write_data_multiple(self, data_list):
        """Escribir múltiples datos"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.xfer(data_list)
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def reset(self):
        """Reset del display"""
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.12)

    def init(self, rotation=1):
        """
        Inicializar display
        rotation: 0=0°, 1=90°, 2=180°, 3=270°
        """
        print("Inicializando display TFT ILI9341...")
        
        self.reset()
        
        # Comandos básicos
        self._write_command(0x01)  # Software Reset
        time.sleep(0.12)
        
        self._write_command(0x11)  # Sleep Out
        time.sleep(0.12)
        
        # Configurar rotación
        self.set_rotation(rotation)
        
        self._write_command(0x3A)  # Pixel Format
        self._write_data(0x55)     # 16 bits/pixel
        
        self._write_command(0x29)  # Display ON
        time.sleep(0.12)
        
        print("Display inicializado correctamente")

    def set_rotation(self, rotation):
    """Configurar rotación - VERSIÓN VALIDADA"""
    self._write_command(0x36)  # Memory Access Control
    
    if rotation == 0:    # 0° (portrait)
        self._write_data(0x48) 
        self.WIDTH = 240
        self.HEIGHT = 320
    elif rotation == 1:  # 90° (landscape) - ¡VALIDADO!
        self._write_data(0x28)  # Este funciona sin espejo
        self.WIDTH = 320
        self.HEIGHT = 240
    elif rotation == 2:  # 180° (portrait invertido)
        self._write_data(0x88) 
        self.WIDTH = 240
        self.HEIGHT = 320
    elif rotation == 3:  # 270° (landscape invertido)
        self._write_data(0xE8)
        self.WIDTH = 320
        self.HEIGHT = 240

    def clear(self, color=0x0000):
        """Limpiar pantalla con color"""
        self.fill_rect(0, 0, self.WIDTH, self.HEIGHT, color)

    def fill_rect(self, x, y, width, height, color):
        """Dibujar rectángulo relleno"""
        # Establecer área de escritura
        self._write_command(0x2A)  # Column address
        self._write_data(x >> 8)
        self._write_data(x & 0xFF)
        self._write_data((x + width - 1) >> 8)
        self._write_data((x + width - 1) & 0xFF)
        
        self._write_command(0x2B)  # Page address
        self._write_data(y >> 8)
        self._write_data(y & 0xFF)
        self._write_data((y + height - 1) >> 8)
        self._write_data((y + height - 1) & 0xFF)
        
        self._write_command(0x2C)  # Memory Write
        
        # Preparar datos de color
        high_byte = (color >> 8) & 0xFF
        low_byte = color & 0xFF
        
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        
        # Enviar datos para el área especificada
        for _ in range(width * height):
            self.spi.xfer([high_byte, low_byte])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def draw_pixel(self, x, y, color):
        """Dibujar un pixel"""
        self.fill_rect(x, y, 1, 1, color)

    def draw_char(self, x, y, char, color, bg_color):
        """Dibujar un carácter"""
        char_data = self.font.get(char, self.font.get(char.upper(), self.font[' ']))
        
        # Establecer área del carácter (8x8)
        self._write_command(0x2A)
        self._write_data(x >> 8)
        self._write_data(x & 0xFF)
        self._write_data((x + 7) >> 8)
        self._write_data((x + 7) & 0xFF)
        
        self._write_command(0x2B)
        self._write_data(y >> 8)
        self._write_data(y & 0xFF)
        self._write_data((y + 7) >> 8)
        self._write_data((y + 7) & 0xFF)
        
        self._write_command(0x2C)
        
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        
        # Dibujar carácter pixel por pixel
        for row in range(8):
            row_data = char_data[row]
            for col in range(8):
                if row_data & (0x80 >> col):
                    self.spi.xfer([(color >> 8) & 0xFF, color & 0xFF])
                else:
                    self.spi.xfer([(bg_color >> 8) & 0xFF, bg_color & 0xFF])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def draw_text(self, x, y, text, color, bg_color):
        """Dibujar texto"""
        for i, char in enumerate(text):
            self.draw_char(x + i * 8, y, char, color, bg_color)

    def draw_line(self, x0, y0, x1, y1, color):
        """Dibujar línea usando algoritmo Bresenham"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.draw_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_rect(self, x, y, width, height, color):
        """Dibujar rectángulo (solo bordes)"""
        # Líneas horizontales
        self.draw_line(x, y, x + width - 1, y, color)
        self.draw_line(x, y + height - 1, x + width - 1, y + height - 1, color)
        # Líneas verticales
        self.draw_line(x, y, x, y + height - 1, color)
        self.draw_line(x + width - 1, y, x + width - 1, y + height - 1, color)

    def get_color(self, color_name):
        """Obtener color por nombre"""
        return self.colors.get(color_name.upper(), 0x0000)

    def cleanup(self):
        """Limpiar recursos"""
        self.spi.close()
        GPIO.cleanup()
        print("Recursos liberados")

# Función de conveniencia para crear instancia
def create_tft(rst_pin=24, dc_pin=25, cs_pin=8, rotation=1):
    """Crear y configurar instancia de TFT"""
    tft = TFT_ILI9341(rst_pin, dc_pin, cs_pin)
    tft.init(rotation)
    return tft