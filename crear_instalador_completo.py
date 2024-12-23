import os
import subprocess
import sys
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes

def run_as_admin():
    """Reinicia el script con privilegios de administrador si no los tiene."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

def download_python(progress_bar, status_label):
    """Descarga e instala Python."""
    python_url = "https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe"
    python_installer = "python_installer.exe"
    
    status_label.config(text="Descargando Python...")
    urllib.request.urlretrieve(python_url, python_installer)
    
    status_label.config(text="Instalando Python...")
    subprocess.run([python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
    os.remove(python_installer)

def clone_repository(repo_url, target_dir, progress_bar, status_label):
    """Clona el repositorio en la ruta indicada."""
    status_label.config(text="Clonando repositorio...")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)

def install_dependencies(requirements_path, progress_bar, status_label):
    """Instala las dependencias desde requirements.txt."""
    status_label.config(text="Instalando dependencias...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)

def start_installation(progress_bar, status_label):
    repo_url = "https://github.com/Jordan-Iralde/ProBestoJarvisAI"
    target_dir = "C:/ProBestoJarvisAI"
    requirements_path = os.path.join(target_dir, "requirements.txt")
    
    try:
        download_python(progress_bar, status_label)
        clone_repository(repo_url, target_dir, progress_bar, status_label)
        if os.path.exists(requirements_path):
            install_dependencies(requirements_path, progress_bar, status_label)
        else:
            status_label.config(text="No se encontró un archivo requirements.txt.")
        messagebox.showinfo("Éxito", "Instalación completada con éxito.")
    except Exception as e:
        messagebox.showerror("Error", f"Error durante la instalación: {e}")

def main():
    run_as_admin()

    root = tk.Tk()
    root.title("Instalador de ProBestoJarvisAI")
    root.geometry("400x200")
    
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
