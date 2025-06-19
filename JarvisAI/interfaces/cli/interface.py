# cli.py

from core.engine import procesar_comando

def iniciar_cli():
    print("🧠 Jarvis (CLI) iniciado. Decí algo o escribilo:")

    while True:
        texto = input("🗣️ Vos: ")
        if texto:
            respuesta = procesar_comando(texto)
            print(f"🤖 Jarvis: {respuesta}")

