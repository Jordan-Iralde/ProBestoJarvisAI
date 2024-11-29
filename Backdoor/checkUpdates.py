import os
import shutil
import requests
import time
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import subprocess
from tkinter import Tk, Label

# Ruta de almacenamiento y log
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "jarvis_data")
os.makedirs(data_folder, exist_ok=True)
LOG_FILE = os.path.join(data_folder, "sync_log.json")

# Definición de URLs (sin autenticación con token)
repo_url = "https://api.github.com/repos/usuario/repositorio/contents"  # Cambiar según el repositorio

# Función para comprobar la conexión a Internet
def check_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

# Función para hacer la solicitud de GitHub
def safe_request(url, retries=3):
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print("Límite de API alcanzado. Esperando...")
                time.sleep(60)
            else:
                print(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error al conectarse: {e}")
    raise Exception("No se pudo completar la solicitud después de varios intentos.")

# Función para descargar un archivo
def download_file(file_url, destination_path):
    try:
        print(f"Descargando {file_url}...")
        response = safe_request(file_url)
        with open(destination_path, 'wb') as file:
            file.write(response.content)
        print(f"Descarga completada: {file_url}")
    except Exception as e:
        print(f"Error al descargar el archivo {file_url}: {e}")

# Función para respaldar el archivo antes de actualizarlo
def backup_file(file_path):
    backup_dir = os.path.join(os.path.dirname(file_path), ".backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copy2(file_path, backup_path)
    print(f"Archivo respaldado en: {backup_path}")

# Función para sincronizar el repositorio
def sync_repo():
    print("Iniciando sincronización del repositorio...")
    
    if not check_connection():
        print("Sin conexión a Internet. Intentando de nuevo en 30 segundos...")
        time.sleep(30)
        sync_repo()

    try:
        # Obtener los archivos desde el repositorio de GitHub
        response = safe_request(repo_url)
        files = response.json()

        # Descargar solo los archivos nuevos o actualizados
        with ThreadPoolExecutor(max_workers=5) as executor:
            for file in files:
                if file["type"] == "file":
                    local_path = os.path.join(data_folder, file["name"])
                    if os.path.exists(local_path):
                        backup_file(local_path)
                    executor.submit(download_file, file["download_url"], local_path)

        # Mostrar recuadro animado con la versión del repositorio
        show_version_window("Actualización completa", "Version del repositorio: 1.0.0")

    except Exception as e:
        print(f"Error al sincronizar: {e}")

# Función para mostrar el recuadro animado de notificación
def show_version_window(title, version):
    window = Tk()
    window.title(title)
    window.geometry("300x100")
    window.configure(bg="lightblue")
    label = Label(window, text=f"{version}\nDescarga completada", font=("Arial", 14), bg="lightblue")
    label.pack(padx=20, pady=20)

    # Animación
    def move_window():
        for i in range(0, 200):
            window.geometry(f"300x100+{i}+100")
            time.sleep(0.01)
            window.update()

    threading.Thread(target=move_window, daemon=True).start()

    window.mainloop()

# Función para registrar log de actividad
def log_activity(updates, errors):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "updated_files": updates,
        "errors": errors,
    }
    with open(LOG_FILE, "a") as log:
        json.dump(log_entry, log, indent=4)
        log.write("\n")

# Ejecutar sincronización diariamente (Ejemplo con 24 horas de intervalo)
if __name__ == "__main__":
    sync_repo()
