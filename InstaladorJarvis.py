import os
import sys
import shutil
import ctypes
import platform
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox

class InstaladorJarvis:
    def __init__(self):
        try:
            import tkinter
        except ImportError:
            print("Tkinter no está instalado. Intentando instalar dependencias del sistema...")
            self.verificar_dependencias_sistema()
            
        if not self.verificar_python():
            print("Error: Python no está instalado o la versión es incompatible.")
            sys.exit(1)
        
        self.root = Tk()
        self.root.title("Instalador de Jarvis")
        self.root.geometry("500x300")
        
        # Ruta de instalación predeterminada según el SO
        self.ruta_instalacion = self.obtener_ruta_predeterminada()
        
        self.instalar_dependencias()

    def verificar_dependencias_sistema(self):
        sistema = platform.system()
        if sistema == "Linux":
            distro = ""
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            distro = line.split("=")[1].strip().strip('"')
                            break
            except:
                pass

            try:
                if distro == "arch":
                    # Para Arch Linux
                    print("Instalando dependencias del sistema en Arch Linux...")
                    subprocess.check_call(["sudo", "pacman", "-S", "--noconfirm", "tk"])
                elif distro in ["ubuntu", "debian"]:
                    # Para Ubuntu/Debian
                    subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-tk"])
                elif distro in ["fedora"]:
                    # Para Fedora
                    subprocess.check_call(["sudo", "dnf", "install", "-y", "python3-tkinter"])
                else:
                    messagebox.showwarning("Advertencia", 
                        "No se pudo detectar la distribución Linux.\n"
                        "Por favor, instale manualmente el paquete tk/tkinter para Python.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", 
                    f"Error instalando dependencias del sistema:\n{str(e)}\n"
                    "Por favor, instale manualmente tk/tkinter.")
                sys.exit(1)
        elif sistema == "Darwin":  # macOS
            try:
                subprocess.check_call(["brew", "install", "python-tk"])
            except:
                messagebox.showwarning("Advertencia",
                    "Por favor instale tkinter usando:\n"
                    "brew install python-tk\n"
                    "O descargue Python desde python.org que incluye tkinter")
        
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

    def verificar_python(self):
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 6):
                return False
            return True
        except Exception as e:
            print(f"Error verificando Python: {e}")
            return False

    def instalar_dependencias(self):
        dependencies = [
            "tk", "matplotlib", "requests", "beautifulsoup4", "pymongo",
            "python-dotenv", "apscheduler", "numpy", "pandas", "joblib",
            "scikit-learn", "schedule", "psutil", "pillow", "pyttsx3",
            "SpeechRecognition", "pyaudio", "openai", "python-vlc",
            "pynput", "pyautogui", "keyboard", "mouse"
        ]

        print("Instalando dependencias de Python...")
        for dep in dependencies:
            try:
                print(f"Instalando {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            except subprocess.CalledProcessError as e:
                print(f"Error instalando {dep}: {e}")

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
            try:
                import winshell
                from win32com.client import Dispatch
                desktop = winshell.desktop()
                path = os.path.join(desktop, "Jarvis.lnk")
                target = os.path.join(ruta, "jarvis.exe")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = ruta
                shortcut.save()
            except Exception as e:
                print(f"Error creando acceso directo en Windows: {e}")
                
        elif sistema == "Linux":
            try:
                desktop_entry = """[Desktop Entry]
                Name=Jarvis
                Exec={}/jarvis
                Type=Application
                Terminal=false
                Categories=Utility;
                """.format(ruta)
                
                # Crear acceso directo en el menú de aplicaciones
                with open("/usr/share/applications/jarvis.desktop", "w") as f:
                    f.write(desktop_entry)
                
                # Crear acceso directo en el escritorio
                desktop_path = os.path.expanduser("~/Desktop")
                with open(os.path.join(desktop_path, "jarvis.desktop"), "w") as f:
                    f.write(desktop_entry)
                
                # Dar permisos de ejecución
                os.chmod(os.path.join(desktop_path, "jarvis.desktop"), 0o755)
            except Exception as e:
                print(f"Error creando acceso directo en Linux: {e}")
                
        elif sistema == "Darwin":  # macOS
            try:
                # Crear alias en Applications
                app_path = os.path.join(ruta, "Jarvis.app")
                os.system(f"ln -s {ruta}/jarvis {app_path}")
                
                # Crear alias en el Dock
                os.system(f"defaults write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>{app_path}</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'")
                os.system("killall Dock")
            except Exception as e:
                print(f"Error creando acceso directo en macOS: {e}")

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