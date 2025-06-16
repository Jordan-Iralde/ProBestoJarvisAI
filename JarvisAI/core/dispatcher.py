from modules.clima import clima
from modules.sistema import sistema
from modules.hora import hora

def ejecutar_comando(texto: str) -> str:
    """Enruta el texto a la función correspondiente según el comando detectado."""

    if "clima" in texto:
        return clima.obtener_clima()

    elif "hora" in texto or "qué hora" in texto:
        return hora.decir_hora()

    elif "abrir" in texto:
        return sistema.abrir_aplicacion(texto)


    elif "salir" in texto:
        return "Cerrando Jarvis. Hasta luego."

    # Comandos adicionales pueden seguir acá...

    else:
        return None  # El engine responderá que no entendió
