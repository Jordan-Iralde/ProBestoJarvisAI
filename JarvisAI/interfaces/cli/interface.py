from core.engine import procesar_comando

while True:
    entrada = input("👨‍💻 Vos: ")
    salida = procesar_comando(entrada)
    print(f"🤖 Jarvis: {salida}")
