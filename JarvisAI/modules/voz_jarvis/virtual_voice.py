# modules/voz_jarvis/virtual_voice.py

import pyttsx3

class VozJarvis:
    def __init__(self, velocidad=150, idioma='spanish'):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', velocidad)
        self._seleccionar_voz(idioma)

    def _seleccionar_voz(self, idioma):
        for voice in self.engine.getProperty('voices'):
            if idioma.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def hablar(self, texto: str):
        self.engine.say(texto)
        self.engine.runAndWait()
