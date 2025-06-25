from modules.clima import clima
from modules.sistema import sistema
from modules.hora import hora
from modules.voz_jarvis import virtual_voice

def ejecutar_comando(texto: str) -> str:
    if "clima" in texto:
        return clima.obtener_clima()
    elif "hora" in texto or "qué hora" in texto:
        return hora.decir_hora()
    elif "abrir" in texto:
        return sistema.abrir_aplicacion(texto)
    elif "salir" in texto:
        return "Cerrando Jarvis. Hasta luego."
    else:
        return "No entendí el comando."

def main():
    while True:
        comando = ejecutar_comando()
        if comando:
            respuesta = ejecutar_comando(comando)
            if respuesta:
                virtual_voice.hablar(respuesta)
            if "salir" in comando:
                break
            
if __name__ == "__main__":
    main()
