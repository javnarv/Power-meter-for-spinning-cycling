# test_tft.py
from TFT_ILI9341 import create_tft
import time

def main():
    # Crear instancia de TFT (configuración por defecto)
    tft = create_tft()
    
    try:
        # Demostración de funciones
        tft.clear(tft.get_color('BLUE'))
        time.sleep(1)
        
        # Texto
        tft.draw_text(50, 50, "LIBRERIA TFT", tft.get_color('WHITE'), tft.get_color('BLUE'))
        tft.draw_text(50, 70, "ILI9341", tft.get_color('YELLOW'), tft.get_color('BLUE'))
        tft.draw_text(50, 90, "Raspberry Pi", tft.get_color('GREEN'), tft.get_color('BLUE'))
        
        time.sleep(3)
        
        # Figuras geométricas
        tft.clear(tft.get_color('BLACK'))
        tft.draw_rect(50, 50, 100, 80, tft.get_color('RED'))
        tft.fill_rect(60, 60, 80, 60, tft.get_color('GREEN'))
        tft.draw_line(10, 10, 200, 150, tft.get_color('YELLOW'))
        
        time.sleep(3)
        
        # Más texto
        tft.clear(tft.get_color('MAGENTA'))
        tft.draw_text(30, 100, "¡Funciona!", tft.get_color('WHITE'), tft.get_color('MAGENTA'))
        
        print("Demo completada")
        
    finally:
        tft.cleanup()

if __name__ == "__main__":
    main()