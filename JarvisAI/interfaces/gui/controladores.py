# gui/controladores.py

from threading import Thread
from modules.reconocimiento_voz.voz_a_texto import capturar_voz
from core.engine import procesar_comando
from modules.voz_jarvis.virtual_voice import VozJarvis

voz_jarvis = VozJarvis()

def iniciar_escucha(texto_voz, respuesta_jarvis):
    def escuchar():
        while True:
            texto = capturar_voz()
            if texto:
                texto_voz.set(f"🗣️ Vos: {texto}")
                respuesta = procesar_comando(texto)
                respuesta_jarvis.set(f"🤖 Jarvis: {respuesta}")
                voz_jarvis.hablar(respuesta)
    Thread(target=escuchar, daemon=True).start()
