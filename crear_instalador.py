import os
import sys
import subprocess

def limpiar_dependencias():
    paquetes_conflictivos = ['pathlib']
    
    print("Limpiando dependencias conflictivas...")
    for paquete in paquetes_conflictivos:
        try:
            subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '-y', paquete])
            print(f"✓ {paquete} eliminado correctamente")
        except Exception as e:
            print(f"! Error al eliminar {paquete}: {e}")

def instalar_dependencias_necesarias():
    dependencias = [
        'pyinstaller',
        'pywin32-ctypes;platform_system=="Windows"',
        'pefile;platform_system=="Windows"'
    ]
    
    print("\nInstalando dependencias necesarias...")
    for dep in dependencias:
        try:
            subprocess.call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} instalado correctamente")
        except Exception as e:
            print(f"! Error al instalar {dep}: {e}")

def crear_instalador():
    limpiar_dependencias()
    instalar_dependencias_necesarias()
    
    print("\nCreando instalador...")
    
    # Asegurarse de que existe la carpeta recursos
    if not os.path.exists('recursos'):
        os.makedirs('recursos')
    
    # Crear archivo ZIP con los archivos de Jarvis si no existe
    if not os.path.exists('recursos/archivos_jarvis.zip'):
        print("! Error: No se encuentra recursos/archivos_jarvis.zip")
        print("Por favor, coloca los archivos de Jarvis en un ZIP en la carpeta recursos")
        sys.exit(1)
    
    archivos = [
        '--name=InstaladorJarvis',
        '--onefile',
        '--noconsole',
        '--add-data=recursos/*;recursos',
        '--icon=recursos/jarvis.ico',
        '--clean',
        '--noupx',
        '--uac-admin',  # Solicitar privilegios de administrador
        'InstaladorJarvis.py'
    ]
    
    try:
        subprocess.call(['pyinstaller'] + archivos)
        print("\n✓ Instalador creado exitosamente!")
        print("El instalador se encuentra en la carpeta 'dist'")
    except Exception as e:
        print(f"\n! Error al crear el instalador: {e}")

if __name__ == "__main__":
    crear_instalador() 