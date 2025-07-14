# gui/app.py

import tkinter as tk
from .widgets import crear_labels
from .video_stream import iniciar_camara
from .controladores import iniciar_escucha

def iniciar_gui():
    ventana = tk.Tk()
    ventana.title("Jarvis AI")
    ventana.geometry("800x600")
    ventana.configure(bg="black")
    ventana.attributes('-topmost', True)

    lienzo_video = tk.Label(ventana)
    lienzo_video.pack()

    texto_voz, respuesta_jarvis = crear_labels(ventana)

    iniciar_escucha(texto_voz, respuesta_jarvis)
    cap = iniciar_camara(lienzo_video, ventana)

    ventana.mainloop()
    cap.release()
