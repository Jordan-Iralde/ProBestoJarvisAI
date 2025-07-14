# core/terms.py

import os
import getpass
import sys
from datetime import datetime
from core.utils import get_ethics_manifest

TERMS_FILE = os.path.expanduser("~/.jarvis/terms_accepted")

CATEGORIAS_RECOLECCION = {
    "📊 Uso de comandos": "Historial de comandos y acciones ejecutadas (sin contenido textual sensible).",
    "🖥️ Estado del sistema": "CPU, RAM, espacio libre, conectividad, info básica del hardware.",
    "🧠 Comportamiento de uso": "Frecuencia de uso, tipo de tareas, reintentos o errores frecuentes.",
    "🎯 Preferencias y contexto": "Tema elegido, idioma, voz, historial de preferencias.",
    "🔍 Navegación y búsquedas": "Palabras clave que usás para buscar código o info.",
    "💡 Aprendizaje automático": "Resultados de pruebas internas, código generado y ajustado por IA.",
}

class TermsManager:
    def __init__(self):
        self.terms_path = TERMS_FILE
        os.makedirs(os.path.dirname(self.terms_path), exist_ok=True)

    def has_accepted(self):
        return os.path.isfile(self.terms_path)

    def prompt_acceptance(self):
        print("\n🧠 MANIFIESTO ÉTICO DE JARVIS\n" + "-" * 40)
        print(get_ethics_manifest())
        print("\n🔐 Jarvis recolectará algunos datos de uso **localmente**, para aprender y ayudarte mejor.")
        print("\n📦 Categorías de datos recolectados:\n")

        for k, v in CATEGORIAS_RECOLECCION.items():
            print(f"  {k}: {v}")

        print("\n📌 Estos datos **no se envían** a servidores externos salvo que vos lo actives explícitamente.")

        respuesta = input("\n¿Aceptás los términos y política de datos? [sí/no]: ").strip().lower()
        if respuesta in ("sí", "si", "s", "yes", "y"):
            with open(self.terms_path, "w") as f:
                f.write(f"{getpass.getuser()}|{datetime.now()}\n")
            print("✅ Términos aceptados. ¡Bienvenido a Jarvis!")
        else:
            print("🚫 No aceptaste los términos. Jarvis se cerrará.")
            sys.exit(0)
