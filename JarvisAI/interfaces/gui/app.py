# gui/gui.py

import tkinter as tk
from threading import Thread
import cv2
from PIL import Image, ImageTk

# Módulos propios
from core.engine import procesar_comando
from modules.vision_computadora.deteccion_objetos import detectar_objetos
from modules.reconocimiento_voz.voz_a_texto import capturar_voz, escribir_texto

def iniciar_gui():
    # Inicializar ventana
    ventana = tk.Tk()
    ventana.title("Jarvis AI")
    ventana.geometry("800x600")
    ventana.attributes('-topmost', True)  # Siempre arriba
    ventana.configure(bg="black")

    # Variables de texto
    texto_voz = tk.StringVar(value="🗣️ Esperando entrada de voz...")
    respuesta_jarvis = tk.StringVar(value="🤖 Esperando comando...")

    # Widgets de cámara
    lienzo_video = tk.Label(ventana)
    lienzo_video.pack()

    # Widgets de texto
    label_voz = tk.Label(ventana, textvariable=texto_voz, font=("Arial", 14), fg="white", bg="black")
    label_voz.pack(pady=5)

    label_respuesta = tk.Label(ventana, textvariable=respuesta_jarvis, font=("Arial", 14), fg="cyan", bg="black")
    label_respuesta.pack(pady=5)

    # Iniciar cámara
    cap = cv2.VideoCapture(0)

    def actualizar_video():
        ret, frame = cap.read()
        if ret:
            frame = detectar_objetos(frame)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            lienzo_video.imgtk = imgtk
            lienzo_video.configure(image=imgtk)
        ventana.after(30, actualizar_video)

    def escuchar_voz():
        while True:
            texto = capturar_voz()
            if texto:
                texto_voz.set(f"🗣️ Vos: {texto}")
                respuesta = procesar_comando(texto)
                respuesta_jarvis.set(f"🤖 Jarvis: {respuesta}")


    # Lanzar funciones
    Thread(target=escuchar_voz, daemon=True).start()
    actualizar_video()
    ventana.mainloop()
    cap.release()
