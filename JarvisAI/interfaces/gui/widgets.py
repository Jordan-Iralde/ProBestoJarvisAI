# gui/widgets.py

import tkinter as tk

def crear_labels(ventana):
    texto_voz = tk.StringVar(value="🗣️ Esperando entrada de voz...")
    respuesta_jarvis = tk.StringVar(value="🤖 Esperando comando...")

    label_voz = tk.Label(ventana, textvariable=texto_voz, font=("Arial", 14), fg="white", bg="black")
    label_voz.pack(pady=5)

    label_respuesta = tk.Label(ventana, textvariable=respuesta_jarvis, font=("Arial", 14), fg="cyan", bg="black")
    label_respuesta.pack(pady=5)

    return texto_voz, respuesta_jarvis
