# main.py

import sys
import cv2
import speech_recognition as sr
from interfaces.cli.interface import iniciar_cli
from interfaces.gui.app import iniciar_gui
def hay_microfono():
    try:
        mic = sr.Microphone()
        print("Probando el micrófono...")
        return True
    except OSError:
        return False

def hay_camara():
    cap = cv2.VideoCapture(0)
    print("Probando la cámara...")
    if not cap.isOpened():
        return False
    cap.release()
    return True

if __name__ == "__main__":
    usar_cli = False

    # Si se pasa por argumento, respetar el modo
    if len(sys.argv) > 1:
        modo = sys.argv[1]
        usar_cli = (modo == "cli")
    else:
        # Auto detección
        tiene_microfono = hay_microfono()
        tiene_camara = hay_camara()
        usar_cli = not (tiene_microfono or tiene_camara)

    if usar_cli:
        print("Usando modo CLI (sin cámara ni micrófono)")
        iniciar_cli()
        
    else:
        print("Usando modo GUI (con cámara y micrófono)")
        iniciar_gui()
        
