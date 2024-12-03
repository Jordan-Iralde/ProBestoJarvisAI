import requests
import os
import json
import datetime
from dateutil.parser import parse

# URL del repositorio en GitHub
repo_url = "https://api.github.com/repos/Jordan-Iralde/ProBestoJarvisAI/contents"
local_repo_path = "/ruta/a/tu/repositorio_local"  # Cambia esto por la ruta de tu repositorio local

# Función para obtener los archivos del repositorio
def obtener_archivos_github():
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Error al parsear la respuesta JSON.")
            return None
    else:
        print(f"Error al acceder al repositorio: {response.status_code}")
        return None

# Función para actualizar archivos locales basados en los archivos de GitHub
def actualizar_archivos(archivos_github, ruta_actual=local_repo_path):
    for archivo in archivos_github:
        nombre = archivo["name"]
        tipo = archivo["type"]
        ruta_archivo = os.path.join(ruta_actual, nombre)
        
        if tipo == "file":
            necesita_actualizacion = True
            
            # Verifica si el archivo existe localmente
            if os.path.exists(ruta_archivo):
                # Compara fechas de modificación
                fecha_github = parse(archivo["commit"]["commit"]["committer"]["date"])
                fecha_local = datetime.datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
                necesita_actualizacion = fecha_github > fecha_local
            
            if necesita_actualizacion:
                url_descarga = archivo["download_url"]
                if url_descarga:
                    response = requests.get(url_descarga)
                    if response.status_code == 200:
                        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
                        with open(ruta_archivo, 'wb') as f:
                            f.write(response.content)
                        print(f"Archivo actualizado: {nombre}")
                    else:
                        print(f"No se pudo descargar el archivo {nombre}")
        
        elif tipo == "dir":
            print(f"Procesando directorio: {nombre}")
            os.makedirs(ruta_archivo, exist_ok=True)
            subcarpeta = obtener_archivos_subcarpeta(archivo["url"])
            if subcarpeta:
                actualizar_archivos(subcarpeta, ruta_archivo)

# Función para obtener archivos dentro de un subdirectorio (recursión)
def obtener_archivos_subcarpeta(url_subcarpeta):
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url_subcarpeta, headers=headers)
    
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Error al parsear la respuesta JSON del subdirectorio.")
            return None
    else:
        print(f"Error al acceder al subdirectorio: {response.status_code}")
        return None

# Función para mostrar un mensaje con la versión más reciente
def mostrar_version():
    version = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Los cambios fueron actualizados a la versión de {version}")

# Función principal que integra todo
def sincronizar():
    print("Iniciando sincronización...")
    archivos_github = obtener_archivos_github()
    
    if archivos_github:
        actualizar_archivos(archivos_github)
        mostrar_version()
    else:
        print("No se pudieron obtener los archivos de GitHub.")

# Ejecutar la sincronización
if __name__ == "__main__":
    sincronizar()
