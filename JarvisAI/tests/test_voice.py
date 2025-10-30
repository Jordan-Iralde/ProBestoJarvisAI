import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.voz_jarvis.virtual_voice import VozJarvis, virtual_voice


def main():
    print("=== Test TTS Main Thread ===")
    
    # Mensajes rápidos para probar la cola
    mensajes = [
        "Hola Jordan, probando voz número uno.",
        "Mensaje número dos en cola.",
        "Y este es el tercero, asegurando orden.",
        "Prueba de interrupción rápida."
    ]
    
    # Encolar todos los mensajes
    for m in mensajes:
        virtual_voice.hablar(m)
        time.sleep(0.05)  # simulamos llamadas rápidas desde threads distintos

    # Test de interrupción
    virtual_voice.hablar_interrupt("Interrupción: esto debe sonar inmediatamente.")

    # Procesamos mensajes en el main thread
    # Llamamos varias veces para simular loop del main
    for _ in range(20):
        virtual_voice.process_tts(block=False, max_messages=5)
        time.sleep(0.1)

    # Cierre seguropython -m tests.test

    virtual_voice.shutdown()

if __name__ == "__main__":
    main()
