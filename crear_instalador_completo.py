import os
import subprocess
import sys
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import shutil

# URLs para descargar las versiones más recientes de Python y Git
PYTHON_URL = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
GIT_URL = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.40.1-64-bit.exe"

def run_as_admin():
    """Reinicia el script con privilegios de administrador si no los tiene."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

def download_file(url, filename, progress_bar, status_label):
    """Descarga un archivo desde una URL y muestra el progreso."""
    def download_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        progress_bar["value"] = min(100, downloaded * 100 // total_size)
        progress_bar.update()
    
    try:
        status_label.config(text=f"Descargando {filename}...")
        urllib.request.urlretrieve(url, filename, download_progress)
    except Exception as e:
        status_label.config(text="Error al descargar archivo.")
        messagebox.showerror("Error de descarga", f"Error al intentar descargar {filename}:\n{e}")
        raise

def install_python(progress_bar, status_label):
    """Descarga e instala Python si no está instalado."""
    if shutil.which("python") is None:
        python_installer = "python_installer.exe"
        try:
            download_file(PYTHON_URL, python_installer, progress_bar, status_label)
            status_label.config(text="Instalando Python...")
            subprocess.run([python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
            os.remove(python_installer)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo instalar Python: {e}")

def install_git(progress_bar, status_label):
    """Descarga e instala Git si no está instalado."""
    if shutil.which("git") is None:
        git_installer = "git_installer.exe"
        try:
            download_file(GIT_URL, git_installer, progress_bar, status_label)
            status_label.config(text="Instalando Git...")
            subprocess.run([git_installer, "/SILENT"], check=True)
            os.remove(git_installer)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo instalar Git: {e}")

def clone_repository(repo_url, target_dir, progress_bar, status_label):
    """Clona el repositorio en la ruta indicada."""
    if shutil.which("git") is None:
        raise EnvironmentError("Git no está instalado o no está en el PATH.")
    
    status_label.config(text="Clonando repositorio...")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def install_dependencies(requirements_path, progress_bar, status_label):
    """Instala las dependencias desde requirements.txt."""
    if not os.path.exists(requirements_path):
        raise FileNotFoundError(f"No se encontró el archivo requirements.txt: {requirements_path}")
    
    status_label.config(text="Instalando dependencias...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)

def start_installation(progress_bar, status_label):
    repo_url = "https://github.com/Jordan-Iralde/ProBestoJarvisAI"
    target_dir = "C:/ProBestoJarvisAI"
    requirements_path = os.path.join(target_dir, "requirements.txt")
    
    try:
        progress_bar["value"] = 0
        
        # Instalar Python y Git si no están presentes
        install_python(progress_bar, status_label)
        install_git(progress_bar, status_label)
        
        # Clonar el repositorio y gestionar dependencias
        clone_repository(repo_url, target_dir, progress_bar, status_label)
        install_dependencies(requirements_path, progress_bar, status_label)
        
        progress_bar["value"] = 100
        status_label.config(text="Instalación completada.")
        messagebox.showinfo("Éxito", "Instalación completada con éxito.")
    except Exception as e:
        messagebox.showerror("Error", f"Error durante la instalación: {e}")

def main():
    run_as_admin()

    root = tk.Tk()
    root.title("Instalador de ProBestoJarvisAI")
    root.geometry("400x250")
    
    tk.Label(root, text="Instalador de ProBestoJarvisAI", font=("Arial", 14)).pack(pady=10)
    
    status_label = tk.Label(root, text="Estado: Esperando", font=("Arial", 10))
    status_label.pack(pady=5)
    
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    
    install_button = tk.Button(root, text="Iniciar instalación", command=lambda: start_installation(progress_bar, status_label))
    install_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
