import os
import psutil
import socket
import platform
from datetime import datetime
import requests
import subprocess

# Ruta donde se guardarán los datos
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "jarvis_data")
os.makedirs(data_folder, exist_ok=True)

# Archivo de datos
file_name = os.path.join(data_folder, f"system_data_{datetime.now().date()}.txt")

# Función para obtener la ubicación actual del usuario
def get_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = f"{data['region']}, {data['country']}"
        return location
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la ubicación: {e}")
        return "Ubicación no disponible"

# Función para obtener información del sistema (componentes y otros datos)
def get_system_info():
    system_info = {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "cpu_count": psutil.cpu_count(),
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().total,
        "memory_used": psutil.virtual_memory().used,
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').total,
        "disk_used": psutil.disk_usage('/').used,
        "disk_percent": psutil.disk_usage('/').percent,
        "uptime": psutil.boot_time(),
        "network": psutil.net_if_addrs(),
        "swap_memory": psutil.swap_memory(),
        "cpu_freq": psutil.cpu_freq()
    }
    return system_info

# Función para obtener detalles sobre procesos activos
def get_active_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'cpu_percent']):
        processes.append({
            "pid": proc.info['pid'],
            "name": proc.info['name'],
            "status": proc.info['status'],
            "memory": proc.info['memory_info'].rss,
            "cpu_percent": proc.info['cpu_percent']
        })
    return processes

# Función para obtener eventos importantes del registro de eventos de Windows
def get_event_logs():
    event_logs = []
    try:
        # Ejecutar comando para obtener los eventos del sistema (últimos 5 eventos)
        result = subprocess.check_output("wevtutil qe System /c:5 /f:text", shell=True, text=True)
        event_logs = result.splitlines()
    except subprocess.CalledProcessError as e:
        event_logs.append(f"Error al obtener eventos: {e}")
    return event_logs

# Función para guardar los datos en un archivo
def save_data(location, system_info, active_processes, event_logs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_name, 'w') as file:
        file.write(f"Fecha y Hora: {timestamp}\n")
        file.write(f"Ubicación: {location}\n")
        file.write("Información del Sistema:\n")
        for key, value in system_info.items():
            file.write(f"{key}: {value}\n")
        
        file.write("\nProcesos Activos:\n")
        for proc in active_processes:
            file.write(f"PID: {proc['pid']} | Name: {proc['name']} | Status: {proc['status']} | Memory: {proc['memory']} | CPU%: {proc['cpu_percent']}\n")
        
        file.write("\nRegistros de Eventos:\n")
        for log in event_logs:
            file.write(f"{log}\n")
    print(f"Datos guardados en: {file_name}")

def create_startup_file():
    """Crea un archivo .bat para asegurarse de que el script se ejecute al iniciar el sistema."""
    bat_content = f'''@echo off
                        where python >nul 2>nul
                        if %ERRORLEVEL% neq 0 (
                            echo Python no esta instalado. Instale Python.
                            exit /b
                        )

                        python -m pip install --upgrade pip
                        pip install psutil requests

                        set "PYTHON_SCRIPT={os.path.abspath(__file__)}"
                        powershell -windowstyle hidden -command "try {{ python '{os.path.abspath(__file__)}' }} catch {{ exit 1 }}"

                        :inicio
                        python %PYTHON_SCRIPT%
                        goto inicio
                    '''
    
    # Ruta de inicio correcto (Asegurándonos de la correcta localización en el sistema)
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    bat_file_path = os.path.join(startup_folder, 'run_system_data_collector.bat')
    
    # Verificamos si el archivo ya existe y, si no, lo creamos
    if not os.path.exists(bat_file_path):
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(bat_content)
        print(f'Archivo de inicio creado en: {bat_file_path}')
    else:
        print(f'El archivo de inicio ya existe en: {bat_file_path}')

# Función principal
def main():
    # Verifica si ya existe el archivo del día
    if not os.path.isfile(file_name):
        location = get_location()
        system_info = get_system_info()
        active_processes = get_active_processes()
        event_logs = get_event_logs()
        save_data(location, system_info, active_processes, event_logs)
    else:
        print(f"El archivo para el día de hoy ({datetime.now().date()}) ya existe.")

# Ejecutar el programa
if __name__ == "__main__":
    create_startup_file()  # Creamos el archivo de inicio al ejecutar el script
    main()
