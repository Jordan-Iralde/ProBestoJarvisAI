from core.engine import procesar_comando
from tkinter import *

def enviar_comando():
    entrada = entrada_text.get()
    respuesta = procesar_comando(entrada)
    respuesta_label.config(text=respuesta)

# Acá sigue el código para la ventana
