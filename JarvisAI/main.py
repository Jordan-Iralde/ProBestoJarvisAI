import tkinter as tk
from threading import Thread
import cv2
from PIL import Image, ImageTk
from modules.vision_computadora.deteccion_objetos import detectar_objetos
from modules.reconocimiento_voz.voz_a_texto import capturar_voz

# Inicializar ventana
ventana = tk.Tk()
ventana.title("Jarvis AI")
ventana.attributes('-topmost', True)  # Siempre arriba
ventana.geometry("800x600")

# Mostrar video
lienzo_video = tk.Label(ventana)
lienzo_video.pack()

# Mostrar texto de voz
texto_voz = tk.StringVar()
label_voz = tk.Label(ventana, textvariable=texto_voz, font=("Arial", 14))
label_voz.pack()

# Captura de cámara y actualización en interfaz
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

# Captura de voz constante en hilo separado
def escuchar_voz():
    while True:
        texto = capturar_voz()
        if texto:
            texto_voz.set(f"🗣️ {texto}")

# Lanzar hilos
Thread(target=escuchar_voz, daemon=True).start()
actualizar_video()

ventana.mainloop()
cap.release()
