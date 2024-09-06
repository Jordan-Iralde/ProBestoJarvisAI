import subprocess

# Lista de dependencias
dependencies = [
    "tk", "ttk", "filedialog", "messagebox", "threading", "time", "matplotlib", 
    "concurrent.futures", "requests", "bs4", "pymongo", "collections", "json", 
    "os", "subprocess", "sys", "pathlib", "logging", "dotenv", "random", "itertools", 
    "platform", "apscheduler", "numpy", "pandas", "joblib", "sklearn", "python-dotenv"
]

# Función para instalar dependencias
def install_dependencies(deps):
    for dep in deps:
        try:
            print(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Error instalando {dep}: {e}")

if __name__ == "__main__":
    install_dependencies(dependencies)
#Ejecuta este script desde tu terminal para instalar automáticamente todas las dependencias.