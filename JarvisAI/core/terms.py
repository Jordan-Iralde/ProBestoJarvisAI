# core/terms.py

import os
import getpass
from core.utils import get_ethics_manifest

TERMS_FILE = os.path.expanduser("~/.jarvis/terms_accepted")

class TermsManager:
    def __init__(self):
        self.terms_path = TERMS_FILE
        os.makedirs(os.path.dirname(self.terms_path), exist_ok=True)

    def has_accepted(self):
        return os.path.isfile(self.terms_path)

    def prompt_acceptance(self):
        print(get_ethics_manifest())
        print("\nPara acelerar tu Jarvis, recolectaremos algunos datos (ver lista).")
        respuesta = input("¿Aceptás términos y política de datos? [sí/no]: ").strip().lower()
        if respuesta in ("sí", "si", "s", "yes", "y"):
            with open(self.terms_path, "w") as f:
                f.write(f"{getpass.getuser()}|{__import__('datetime').datetime.now()}\n")
            print("¡Gracias! Continuamos con Jarvis.")
        else:
            print("Sin aceptación no podemos continuar. Chau.")
            sys.exit(0)
