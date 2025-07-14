# gui/video_stream.py

import cv2
from PIL import Image, ImageTk
from modules.vision_computadora.deteccion_objetos import detectar_objetos

def iniciar_camara(lienzo, ventana):
    cap = cv2.VideoCapture(0)

    def actualizar():
        ret, frame = cap.read()
        if ret:
            frame = detectar_objetos(frame)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            lienzo.imgtk = imgtk
            lienzo.configure(image=imgtk)
        ventana.after(30, actualizar)

    actualizar()
    return cap
