# core/utils.py

import os
import logging
import cv2
import pyaudio
import platform
import shutil
import socket
from datetime import datetime
from config.settings import config
from core.config_manager import ConfigManager

# ----------------------------------------
# 🔐 Actualizar configuraciones
# ----------------------------------------
def update_local_config(updates: dict):
    """
    Carga la configuración local cifrada,
    actualiza con el diccionario 'updates',
    y guarda los cambios.

    Devuelve la config actualizada (dict).
    """
    cfg_mgr = ConfigManager()
    local_config = cfg_mgr.load_or_init()
    local_config.update(updates)
    cfg_mgr.save(local_config)
    return local_config

# ----------------------------------------
# 🔐 Logger por módulo
# ----------------------------------------
def get_logger(name: str):
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_DIR)

    log_path = os.path.join(config.LOG_DIR, f"{name}.log")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if config.debug else logging.INFO)

    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


# ----------------------------------------
# 📜 Cargar manifiesto ético
# ----------------------------------------
def get_ethics_manifest():
    ethics_path = "JarvisAI/docs/usage.md"
    try:
        with open(ethics_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al cargar manifiesto ético: {e}"


# ----------------------------------------
# 🎥 Detectar cámara disponible
# ----------------------------------------
def check_camera_available():
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return False
        cam.release()
        return True
    except:
        return False


# ----------------------------------------
# 🎙️ Detectar micrófono disponible
# ----------------------------------------
def check_microphone_available():
    try:
        audio = pyaudio.PyAudio()
        count = audio.get_device_count()
        for i in range(count):
            info = audio.get_device_info_by_index(i)
            if info.get('maxInputChannels') > 0:
                return True
        return False
    except:
        return False


# ----------------------------------------
# 🧠 Chequeo de compatibilidad general
# ----------------------------------------
def run_system_check():
    report = {
        "SO": platform.system(),
        "Version": platform.version(),
        "Python": platform.python_version(),
        "Cámara disponible": check_camera_available(),
        "Micrófono disponible": check_microphone_available(),
        "Espacio libre (GB)": shutil.disk_usage(".").free // (2**30)
    }
    return report


# ----------------------------------------
# 📌 Mostrar IP local
# ----------------------------------------
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "No detectada"


# ----------------------------------------
# 📅 Timestamp formateado
# ----------------------------------------
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------
# 🔁 Validar compatibilidad con módulos
# (A implementar en el futuro)
# ----------------------------------------
def check_module_compatibility(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


# ----------------------------------------
# 🔧 Comprobar dependencia instalada
# ----------------------------------------
def is_dependency_installed(package: str) -> bool:
    try:
        __import__(package)
        return True
    except ImportError:
        return False


# ----------------------------------------
# 🧬 Generador de ID único
# ----------------------------------------
def generate_unique_id(prefix="JVS"):
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ----------------------------------------
# 🧪 Ejecutar test de entorno
# ----------------------------------------
def full_environment_diagnostic():
    log = get_logger("diagnostic")
    results = run_system_check()
    log.info("DIAGNÓSTICO COMPLETO DEL SISTEMA:")
    for k, v in results.items():
        log.info(f"{k}: {v}")
    return results


# ----------------------------------------
# 🚨 Manejo de errores centralizado (futuro)
# ----------------------------------------
def handle_error(error: Exception, module_name: str):
    log = get_logger(module_name)
    log.error(f"Error en módulo [{module_name}]: {str(error)}")
    print(f"[!] Ocurrió un error en {module_name}: {error}")
