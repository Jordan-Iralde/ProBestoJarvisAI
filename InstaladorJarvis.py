import os
import sys
import shutil
import subprocess
import platform
import urllib.request
import zipfile
import tempfile

class Instalador:
    def __init__(self):
        self.sistema = platform.system()
        self.ruta_instalacion = self.obtener_ruta_predeterminada()
        print("=== Instalador de Jarvis ===")
        
    def obtener_ruta_predeterminada(self):
        if self.sistema == "Windows":
            return "C:\\Program Files\\Jarvis"
        elif self.sistema == "Linux":
            return "/opt/jarvis"
        else:  # macOS
            return "/Applications/Jarvis"

    def descargar_archivos(self):
        print("Descargando archivos necesarios...")
        # Aquí deberías especificar la URL donde estén los archivos de Jarvis
        url = "https://github.com/Jordan-Iralde/ProBestoJarvisAI"
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "jarvis.zip")
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.ruta_instalacion)
            print("✓ Archivos descargados correctamente")
        except Exception as e:
            print(f"✗ Error descargando archivos: {e}")
            sys.exit(1)

    def instalar_python(self):
        print("\nInstalando Python...")
        try:
            if self.sistema == "Windows":
                # Descargar e instalar Python para Windows
                python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
                installer_path = os.path.join(tempfile.gettempdir(), "python_installer.exe")
                urllib.request.urlretrieve(python_url, installer_path)
                subprocess.call([installer_path, "/quiet", "PrependPath=1"])
            elif self.sistema == "Linux":
                # Instalar Python en Linux según la distribución
                if os.path.exists("/etc/debian_version"):
                    subprocess.call(["sudo", "apt-get", "update"])
                    subprocess.call(["sudo", "apt-get", "install", "-y", "python3", "python3-pip"])
                elif os.path.exists("/etc/fedora-release"):
                    subprocess.call(["sudo", "dnf", "install", "-y", "python3", "python3-pip"])
                elif os.path.exists("/etc/arch-release"):
                    subprocess.call(["sudo", "pacman", "-Sy", "python", "python-pip"])
            print("✓ Python instalado correctamente")
        except Exception as e:
            print(f"✗ Error instalando Python: {e}")
            sys.exit(1)

    def instalar_dependencias(self):
        print("\nInstalando dependencias...")
        dependencias = [
            "requests", "numpy", "pandas", "scikit-learn",
            "tensorflow", "pytorch", "transformers", "openai",
            "python-dotenv", "flask", "pygame", "pillow"
        ]
        
        for dep in dependencias:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ {dep} instalado")
            except:
                print(f"✗ Error instalando {dep}")

    def crear_accesos_directos(self):
        print("\nCreando accesos directos...")
        try:
            if self.sistema == "Windows":
                # Crear acceso directo en Windows
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                with open(os.path.join(desktop, "Jarvis.bat"), "w") as f:
                    f.write(f'@echo off\ncd "{self.ruta_instalacion}"\npython jarvis.py')
            elif self.sistema == "Linux":
                # Crear .desktop file en Linux
                desktop_entry = f"""[Desktop Entry]
                Name=Jarvis
                Exec=python3 {self.ruta_instalacion}/jarvis.py
                Type=Application
                Terminal=false"""
                
                desktop_path = os.path.expanduser("~/Desktop/jarvis.desktop")
                with open(desktop_path, "w") as f:
                    f.write(desktop_entry)
                os.chmod(desktop_path, 0o755)
            print("✓ Accesos directos creados")
        except Exception as e:
            print(f"✗ Error creando accesos directos: {e}")

    def instalar(self):
        print(f"\nInstalando Jarvis en: {self.ruta_instalacion}")
        
        # Crear directorio de instalación
        os.makedirs(self.ruta_instalacion, exist_ok=True)
        
        # Instalar Python si no está presente
        if not self.verificar_python():
            self.instalar_python()
        
        # Descargar archivos necesarios
        self.descargar_archivos()
        
        # Instalar dependencias
        self.instalar_dependencias()
        
        # Crear accesos directos
        self.crear_accesos_directos()
        
        print("\n✓ Instalación completada exitosamente!")
        print(f"Jarvis ha sido instalado en: {self.ruta_instalacion}")

    def verificar_python(self):
        try:
            subprocess.check_call([sys.executable, "--version"])
            return True
        except:
            return False

if __name__ == "__main__":
    instalador = Instalador()
    instalador.instalar()