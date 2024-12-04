import os
import sys
import shutil
import ctypes
import platform
from tkinter import *
from tkinter import filedialog, messagebox

class InstaladorJarvis:
    def __init__(self):
        self.root = Tk()
        self.root.title("Instalador de Jarvis")
        self.root.geometry("500x300")
        
        # Ruta de instalación predeterminada según el SO
        self.ruta_instalacion = self.obtener_ruta_predeterminada()
        
    def obtener_ruta_predeterminada(self):
        sistema = platform.system()
        if sistema == "Windows":
            return "C:\\Program Files\\Jarvis"
        elif sistema == "Linux":
            return "/opt/jarvis"
        elif sistema == "Darwin":  # macOS
            return "/Applications/Jarvis"
            
    def verificar_privilegios(self):
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
            
    def solicitar_privilegios(self):
        if platform.system() == "Windows":
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            messagebox.showerror("Error", "Por favor, ejecute el instalador con sudo")
            sys.exit(1)

    def instalar(self):
        ruta = self.ruta_entry.get()
        
        if not self.verificar_privilegios():
            self.solicitar_privilegios()
            return
            
        try:
            # Crear directorio de instalación
            os.makedirs(ruta, exist_ok=True)
            
            # Aquí copiaríamos los archivos del proyecto
            # shutil.copytree("./proyecto_jarvis", ruta)
            
            # Crear accesos directos según el SO
            self.crear_accesos_directos(ruta)
            
            messagebox.showinfo("Éxito", "Jarvis se ha instalado correctamente en:\n" + ruta)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la instalación:\n{str(e)}")

    def crear_accesos_directos(self, ruta):
        sistema = platform.system()
        if sistema == "Windows":
            # Crear acceso directo en el escritorio
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            # Aquí iría el código para crear el acceso directo .lnk
        elif sistema == "Linux":
            # Crear archivo .desktop
            desktop_entry = """[Desktop Entry]
            Name=Jarvis
            Exec={}/jarvis
            Type=Application
            Terminal=false
            """.format(ruta)
            with open("/usr/share/applications/jarvis.desktop", "w") as f:
                f.write(desktop_entry)

    def crear_interfaz(self):
        Label(self.root, text="Instalador de Jarvis", font=("Arial", 16)).pack(pady=20)
        
        frame = Frame(self.root)
        frame.pack(pady=20)
        
        Label(frame, text="Ruta de instalación:").pack()
        
        self.ruta_entry = Entry(frame, width=50)
        self.ruta_entry.insert(0, self.ruta_instalacion)
        self.ruta_entry.pack(pady=5)
        
        Button(frame, text="Examinar", command=self.examinar).pack()
        
        Button(self.root, text="Instalar", command=self.instalar).pack(pady=20)

    def examinar(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_entry.delete(0, END)
            self.ruta_entry.insert(0, ruta)

    def iniciar(self):
        self.crear_interfaz()
        self.root.mainloop()

if __name__ == "__main__":
    instalador = InstaladorJarvis()
    instalador.iniciar() 