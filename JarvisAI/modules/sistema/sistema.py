import os

def abrir_aplicacion(texto):
    if "chrome" in texto:
        os.system("start chrome")
        return "Abriendo Chrome."
    elif "calculadora" in texto:
        os.system("calc")
        return "Abriendo calculadora."
    else:
        return "No sé cómo abrir esa aplicación."
