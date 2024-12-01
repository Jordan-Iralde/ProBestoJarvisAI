import requests
import os
import json
import datetime

# URL del repositorio en GitHub
repo_url = "https://api.github.com/repos/Jordan-Iralde/ProBestoJarvisAI/contents"
local_repo_path = "/ruta/a/tu/repositorio_local"  # Cambia esto por la ruta de tu repositorio local

# Función para obtener los archivos del repositorio
def obtener_archivos_github():
    response = requests.get(repo_url)
    
    if response.status_code == 200:
        try:
            # Respuesta esperada: un JSON con información sobre archivos y carpetas
            archivos = response.json()
            return archivos
        except json.JSONDecodeError:
            print("Error al parsear la respuesta JSON.")
            return None
    else:
        print(f"Error al acceder al repositorio: {response.status_code}")
        return None

# Función para actualizar archivos locales basados en los archivos de GitHub
def actualizar_archivos(archivos_github):
    for archivo in archivos_github:
        nombre = archivo["name"]
        tipo = archivo["type"]
        if tipo == "file":
            # Obtiene la URL de descarga del archivo
            url_descarga = archivo["download_url"]
            if url_descarga:
                response = requests.get(url_descarga)
                if response.status_code == 200:
                    # Guarda el archivo localmente
                    archivo_local_path = os.path.join(local_repo_path, nombre)
                    with open(archivo_local_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Archivo actualizado: {nombre}")
                else:
                    print(f"No se pudo descargar el archivo {nombre}")
            else:
                print(f"Archivo sin URL de descarga: {nombre}")
        elif tipo == "dir":
            # Si es un directorio, podemos recorrerlo recursivamente
            print(f"Directorio encontrado: {nombre}")
            subcarpeta = obtener_archivos_subcarpeta(archivo["url"])
            if subcarpeta:
                actualizar_archivos(subcarpeta)

# Función para obtener archivos dentro de un subdirectorio (recursión)
def obtener_archivos_subcarpeta(url_subcarpeta):
    response = requests.get(url_subcarpeta)
    
    if response.status_code == 200:
        try:
            archivos_subcarpeta = response.json()
            return archivos_subcarpeta
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
