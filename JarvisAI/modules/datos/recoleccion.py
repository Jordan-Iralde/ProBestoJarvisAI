import platform
import socket
import psutil
import getpass
from datetime import datetime
from core.utils import get_logger

log = get_logger("recoleccion_datos")

def recolectar_datos_usuario():
    return {
        "usuario": getpass.getuser(),
        "hostname": socket.gethostname(),
        "ip_local": socket.gethostbyname(socket.gethostname()),
        "sistema_operativo": platform.system(),
        "version_os": platform.version(),
        "arquitectura": platform.machine(),
        "cpu": platform.processor(),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "fecha": datetime.now().isoformat(),
    }

def iniciar_recoleccion_datos():
    datos = recolectar_datos_usuario()
    log.info("Datos recolectados: %s", datos)
    return datos
