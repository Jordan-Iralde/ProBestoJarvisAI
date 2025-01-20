import subprocess
import sys
import pkg_resources
import platform
import os
import concurrent.futures
import multiprocessing
import psutil
from tqdm import tqdm

# Lista completa de dependencias necesarias para el proyecto
dependencies = [
    # Interfaces gráficas y widgets
    "tkinter",
    "customtkinter",
    "pillow",  # Para manejo de imágenes
    
    # Procesamiento de datos y análisis
    "numpy",
    "pandas",
    "scikit-learn",
    "matplotlib",
    
    # Web scraping y APIs
    "requests",
    "beautifulsoup4",
    "selenium",
    "webdriver_manager",
    
    # Base de datos
    "pymongo",
    "python-dotenv",
    
    # Utilidades del sistema
    "psutil",
    "schedule",
    "apscheduler",
    
    # Machine Learning y procesamiento
    "joblib",
    "nltk",
    "tensorflow",
    "transformers",
    
    # Otras utilidades
    "python-dateutil",
    "tqdm",  # Para barras de progreso
]

def check_installed_packages():
    """Verifica qué paquetes ya están instalados"""
    installed = {pkg.key for pkg in pkg_resources.working_set}
    return installed

def get_platform_info():
    """Obtiene información del sistema operativo"""
    sistema = platform.system()
    arquitectura = platform.machine()
    return {"sistema": sistema, "arquitectura": arquitectura}

def get_optimal_workers():
    """Determina el número óptimo de workers basado en CPU y memoria"""
    cpu_count = multiprocessing.cpu_count()
    memory = psutil.virtual_memory()
    # Usa más workers si hay más memoria disponible
    if memory.available > (8 * 1024 * 1024 * 1024):  # Más de 8GB libre
        return max(cpu_count - 1, 1)
    return max(cpu_count // 2, 1)

def install_package(package_info):
    """Instala un paquete individual"""
    dep, plataforma, installed_packages = package_info
    try:
        if dep.lower() not in installed_packages:
            if dep == "pyaudio" and plataforma["sistema"] == "Windows":
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pipwin"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                subprocess.check_call([sys.executable, "-m", "pipwin", "install", "pyaudio"],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--upgrade"],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
            return (dep, True, None)
        return (dep, False, None)
    except Exception as e:
        return (dep, False, str(e))

def ensure_pip_and_setuptools():
    """Asegura que pip y setuptools estén instalados"""
    try:
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Error asegurando pip y setuptools: {e}")
        sys.exit(1)

def install_dependencies(deps):
    """Instala las dependencias en paralelo"""
    installed_packages = check_installed_packages()
    plataforma = get_platform_info()
    
    print("\nInformación del sistema:")
    for key, value in plataforma.items():
        print(f"{key}: {value}")
    
    print(f"\nInstalando dependencias usando {get_optimal_workers()} workers...")
    
    # Preparar argumentos para la instalación paralela
    install_args = [(dep, plataforma, installed_packages) for dep in deps]
    
    # Barra de progreso
    with tqdm(total=len(deps), desc="Instalando paquetes", ncols=100) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=get_optimal_workers()) as executor:
            # Iniciar instalaciones en paralelo
            future_to_pkg = {executor.submit(install_package, arg): arg[0] 
                           for arg in install_args}
            
            # Procesar resultados
            for future in concurrent.futures.as_completed(future_to_pkg):
                pkg = future_to_pkg[future]
                try:
                    dep, installed, error = future.result()
                    if error:
                        print(f"\n❌ Error instalando {dep}: {error}")
                    elif installed:
                        print(f"\n✓ {dep} instalado correctamente")
                    else:
                        print(f"\n✓ {dep} ya está instalado")
                except Exception as e:
                    print(f"\n❌ Error inesperado instalando {pkg}: {e}")
                pbar.update(1)

def setup_nltk_parallel():
    """Descarga recursos NLTK en paralelo"""
    nltk_resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    
    def download_nltk_resource(resource):
        try:
            import nltk
            nltk.download(resource, quiet=True)
            return (resource, True, None)
        except Exception as e:
            return (resource, False, str(e))
    
    print("\nDescargando recursos NLTK en paralelo...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(nltk_resources)) as executor:
        future_to_resource = {executor.submit(download_nltk_resource, resource): resource 
                            for resource in nltk_resources}
        
        for future in concurrent.futures.as_completed(future_to_resource):
            resource = future_to_resource[future]
            try:
                res, success, error = future.result()
                if success:
                    print(f"✓ Recurso NLTK '{res}' descargado correctamente")
                else:
                    print(f"❌ Error descargando recurso NLTK '{res}': {error}")
            except Exception as e:
                print(f"❌ Error inesperado con recurso NLTK '{resource}': {e}")

def main():
    print("=" * 60)
    print("Iniciando instalación paralela de dependencias para JarvisPhone")
    print("=" * 60)
    
    try:
        os.makedirs('logs', exist_ok=True)
        
        # Asegurar que pip y setuptools estén instalados
        print("\nAsegurando que pip y setuptools estén instalados...")
        ensure_pip_and_setuptools()
        
        # Instalación paralela de dependencias
        install_dependencies(dependencies)
        
        # Configuración paralela de NLTK
        setup_nltk_parallel()
        
        print("\n" + "=" * 60)
        print("✓ Instalación paralela completada exitosamente")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error durante la instalación: {e}")
        print("=" * 60)

if __name__ == "__main__":
    main()
