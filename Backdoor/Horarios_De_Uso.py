import tkinter as tk

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Mensaje")
ventana.geometry("300x150")  # Tamaño de la ventana

# Configurar el texto en el recuadro
mensaje = tk.Label(ventana, text="Me estoy ejecutando2", font=("Arial", 16), pady=20)
mensaje.pack(expand=True)

# Mostrar la ventana
ventana.mainloop()
