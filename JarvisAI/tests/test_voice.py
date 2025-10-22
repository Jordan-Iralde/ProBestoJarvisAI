import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.voz_jarvis.virtual_voice import virtual_voice
import time

print("== Test TTS Queue ==")

virtual_voice.hablar("Hola .")
virtual_voice.hablar("Mensaje  .")
virtual_voice.hablar("Y este es .")

time.sleep(8)  # espera que hable todo
virtual_voice.shutdown()

print("== Test Finalizado ==")
