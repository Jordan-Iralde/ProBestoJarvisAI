import os
import sys
import subprocess
import requests
from tqdm import tqdm
import zipfile
import shutil
import logging
from datetime import datetime
import winshell
from win32com.client import Dispatch

# Configurar logging
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"installer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def mostrar_banner():
    banner = """
╔══════════════════════════════════════╗
║        Instalador de Jarvis          ║
║            Versión 1.0               ║
╚══════════════════════════════════════╝
"""
    print(banner)
    logging.info("Mostrando banner del instalador")

def verificar_conexion(timeout=3):
    urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.cloudflare.com"
    ]
    for url in urls:
        try:
            requests.get(url, timeout=timeout)
            logging.info(f"Conexión exitosa a {url}")
            return True
        except:
            logging.warning(f"Fallo al conectar con {url}")
            continue
    logging.error("No hay conexión a internet")
    return False

def verificar_espacio_disco(ruta, espacio_requerido_mb=100):
    try:
        espacio_libre = shutil.disk_usage(ruta).free / (1024 * 1024)  # Convertir a MB
        logging.info(f"Espacio libre en disco: {espacio_libre} MB")
        return espacio_libre >= espacio_requerido_mb
    except Exception as e:
        logging.error(f"Error al verificar espacio en disco: {e}")
        return False

def descargar_archivo(url, nombre_archivo):
    try:
        for intento in range(3):  # 3 intentos
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                total = int(response.headers.get('content-length', 0))
                
                with open(nombre_archivo, 'wb') as f, tqdm(
                    total=total,
                    unit='iB',
                    unit_scale=True,
                    desc=f"Descargando repositorio (Intento {intento + 1}/3)"
                ) as barra:
                    for datos in response.iter_content(8192):
                        tam = f.write(datos)
                        barra.update(tam)
                logging.info(f"Descarga completada: {nombre_archivo}")
                return True
            except requests.RequestException as e:
                logging.warning(f"Intento {intento + 1} fallido: {e}")
                if intento < 2:
                    print(f"\nReintentando descarga en 3 segundos...")
                    time.sleep(3)
                continue
        logging.error(f"Error en la descarga después de 3 intentos: {url}")
        return False
    except Exception as e:
        logging.error(f"Error en la descarga: {e}")
        print(f"\n❌ Error en la descarga: {e}")
        return False

def crear_launcher():
    contenido = """
import os
import sys
import ctypes
import zipfile
import logging
from datetime import datetime

# Configurar logging
log_dir = os.path.join(os.getenv('APPDATA'), 'JarvisAI', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"jarvis_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def solicitar_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not solicitar_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def mostrar_progreso(mensaje, progreso, total):
    barra = "█" * int(30 * (progreso / total)) + "░" * int(30 * (1 - progreso / total))
    print(f"\\r{mensaje}: |{barra}| {int(100 * progreso / total)}%", end="")

def instalar():
    try:
        ruta_base = "C:\\Program Files\\JarvisAI"
        os.makedirs(ruta_base, exist_ok=True)
        logging.info(f"Creado directorio de instalación: {ruta_base}")
        
        print("Extrayendo archivos...")
        with zipfile.ZipFile("repo_files.zip", 'r') as zip_ref:
            archivos = zip_ref.namelist()
            total = len(archivos)
            for i, archivo in enumerate(archivos, 1):
                zip_ref.extract(archivo, ruta_base)
                mostrar_progreso("Extrayendo", i, total)
        
        print("\\n\\n✓ Instalación completada!")
        print(f"Ubicación: {ruta_base}")
        print("\\nNOTA: Para completar la instalación, necesitas descargar Jarvis manualmente.")
        logging.info("Instalación completada exitosamente")
        
    except Exception as e:
        logging.error(f"Error durante la instalación: {e}")
        print(f"\\n❌ Error: {e}")
    
    input("\\nPresione Enter para salir...")

if __name__ == "__main__":
    print("=== Instalador de Jarvis ===\\n")
    instalar()
"""
    with open("launcher.py", "w", encoding='utf-8') as f:
        f.write(contenido)

def crear_acceso_directo():
    try:
        desktop = winshell.desktop()
        ruta_carpeta = "C:\\Program Files\\JarvisAI"
        acceso_directo = os.path.join(desktop, "JarvisAI.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(acceso_directo)
        shortcut.Targetpath = ruta_carpeta
        shortcut.WorkingDirectory = ruta_carpeta
        shortcut.IconLocation = os.path.join(ruta_carpeta, "icon.ico") if os.path.exists(os.path.join(ruta_carpeta, "icon.ico")) else None
        shortcut.save()
        logging.info("Acceso directo creado en el escritorio")
    except Exception as e:
        logging.error(f"Error al crear acceso directo: {e}")
        print(f"❌ Error al crear acceso directo: {e}")

def crear_instalador():
    mostrar_banner()
    logging.info("Iniciando proceso de creación del instalador")
    
    # Verificaciones iniciales
    if not verificar_conexion():
        print("❌ Error: No hay conexión a internet")
        return False
        
    if not verificar_espacio_disco("."):
        print("❌ Error: Espacio insuficiente en disco")
        return False
        
    try:
        # Instalar dependencias
        print("Instalando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyinstaller", "requests", "tqdm", "pywin32", "winshell"])
        logging.info("Dependencias instaladas correctamente")
        
        # Descargar repositorio
        url_repo = "https://github.com/Jordan-Iralde/ProBestoJarvisAI/archive/refs/heads/main.zip"
        if not descargar_archivo(url_repo, "repo_files.zip"):
            return False
            
        # Verificar archivo ZIP
        print("\nVerificando archivo...")
        try:
            with zipfile.ZipFile("repo_files.zip", 'r') as zip_ref:
                zip_ref.testzip()
            logging.info("Archivo ZIP verificado correctamente")
        except Exception as e:
            logging.error(f"Error en archivo ZIP: {e}")
            print(f"\n❌ Error: Archivo ZIP dañado - {e}")
            return False
            
        # Crear launcher
        crear_launcher()
        logging.info("Launcher creado correctamente")
        
        # Crear ejecutable
        print("\nCreando ejecutable...")
        icono = "icon.ico" if os.path.exists("icon.ico") else None
        comando_pyinstaller = [
            "pyinstaller",
            "--onefile",
            "--name=JarvisAI_Setup",
            "--add-data=repo_files.zip;.",
            "--uac-admin",
            "--console",
            "launcher.py"
        ]
        if icono:
            comando_pyinstaller.extend(["--icon", icono])
        
        resultado = subprocess.run(comando_pyinstaller, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            logging.error(f"Error al crear ejecutable: {resultado.stderr}")
            print(f"\n❌ Error al crear ejecutable: {resultado.stderr}")
            return False
            
        # Verificar ejecutable
        exe_path = os.path.join("dist", "JarvisAI_Setup.exe")
        if not os.path.exists(exe_path):
            logging.error("No se encontró el ejecutable")
            print("\n❌ Error: No se encontró el ejecutable")
            return False
            
        print(f"\n✓ Instalador creado exitosamente en: {exe_path}")
        logging.info(f"Instalador creado exitosamente en: {exe_path}")
        
        # Crear acceso directo
        crear_acceso_directo()
        
        return True
        
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        print(f"\n❌ Error inesperado: {e}")
        return False
    finally:
        # Limpiar archivos temporales
        print("\nLimpiando archivos temporales...")
        for archivo in ["repo_files.zip", "launcher.py"]:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    logging.info(f"Eliminado archivo temporal: {archivo}")
            except Exception as e:
                logging.warning(f"No se pudo eliminar {archivo}: {e}")

if __name__ == "__main__":
    exito = crear_instalador()
    if not exito:
        print("\n❌ El proceso no se completó correctamente")
        print(f"Consulte el archivo de log para más detalles: {log_file}")
    input("\nPresione Enter para salir...")