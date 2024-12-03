import requests
import os
import datetime
import time
import hashlib
import json

# URL base del repositorio raw y API
REPO_OWNER = "Jordan-Iralde"
REPO_NAME = "ProBestoJarvisAI"
BRANCH = "main"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"

def encontrar_repo_local():
    """Encuentra la ruta del repositorio local buscando la carpeta .git"""
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(ruta_actual, '.git')):
            return ruta_actual
        padre = os.path.dirname(ruta_actual)
        if padre == ruta_actual:
            return None
        ruta_actual = padre

def obtener_estructura_github():
    """Obtiene la estructura actual del repositorio desde GitHub"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    estructura = {"": []}  # Archivos en la raíz
    
    def explorar_directorio(path=""):
        url = f"{API_URL}/{path}" if path else API_URL
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            contenido = response.json()
            for item in contenido:
                if item['type'] == 'file':
                    carpeta = os.path.dirname(item['path'])
                    nombre = os.path.basename(item['path'])
                    if carpeta not in estructura:
                        estructura[carpeta] = []
                    estructura[carpeta].append(nombre)
                elif item['type'] == 'dir':
                    explorar_directorio(item['path'])
    
    try:
        explorar_directorio()
        return estructura
    except Exception as e:
        print(f"Error al obtener la estructura del repositorio: {str(e)}")
        return None

def obtener_hash_archivo(ruta):
    """Calcula el hash MD5 de un archivo"""
    if not os.path.exists(ruta):
        return None
    try:
        with open(ruta, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def necesita_actualizacion(ruta_local, contenido_nuevo):
    """Comprueba si el archivo necesita actualización"""
    if not os.path.exists(ruta_local):
        return True
    try:
        hash_local = obtener_hash_archivo(ruta_local)
        hash_nuevo = hashlib.md5(contenido_nuevo).hexdigest()
        return hash_local != hash_nuevo
    except Exception:
        return True

def descargar_archivo(ruta_relativa, ruta_local):
    """Descarga un archivo desde GitHub si es necesario"""
    url = f"{BASE_RAW_URL}/{ruta_relativa}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if necesita_actualizacion(ruta_local, response.content):
                os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
                with open(ruta_local, 'wb') as f:
                    f.write(response.content)
                print(f"Archivo actualizado: {ruta_relativa}")
                return 'actualizado'
            else:
                print(f"Archivo sin cambios: {ruta_relativa}")
                return 'sin_cambios'
        else:
            print(f"No se pudo acceder a {ruta_relativa} (Status: {response.status_code})")
            return 'error'
    except Exception as e:
        print(f"Error al procesar {ruta_relativa}: {str(e)}")
        return 'error'

def sincronizar():
    REPO_LOCAL = encontrar_repo_local()
    if not REPO_LOCAL:
        print("Error: No se pudo encontrar el repositorio local.")
        return
    
    print(f"Repositorio local encontrado en: {REPO_LOCAL}")
    print("Obteniendo estructura actual del repositorio...")
    
    estructura = obtener_estructura_github()
    if not estructura:
        print("Error: No se pudo obtener la estructura del repositorio.")
        return
    
    print("\nIniciando sincronización...")
    actualizados = 0
    sin_cambios = 0
    errores = 0
    
    for carpeta, archivos in estructura.items():
        for archivo in archivos:
            ruta_relativa = os.path.join(carpeta, archivo).replace("\\", "/")
            ruta_local = os.path.join(REPO_LOCAL, ruta_relativa)
            
            # Pequeña pausa para evitar demasiadas solicitudes rápidas
            time.sleep(0.5)
            
            resultado = descargar_archivo(ruta_relativa, ruta_local)
            if resultado == 'actualizado':
                actualizados += 1
            elif resultado == 'sin_cambios':
                sin_cambios += 1
            else:
                errores += 1
    
    print("\nResumen de la sincronización:")
    print(f"Archivos actualizados: {actualizados}")
    print(f"Archivos sin cambios: {sin_cambios}")
    print(f"Errores: {errores}")
    
    version = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nLos cambios fueron actualizados a la versión de {version}")

if __name__ == "__main__":
    sincronizar()
