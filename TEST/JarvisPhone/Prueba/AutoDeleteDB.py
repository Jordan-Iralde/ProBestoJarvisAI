import os
import platform
import subprocess
from pathlib import Path
import pymongo
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Configuración de MongoDB
MONGO_URI = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = pymongo.MongoClient(MONGO_URI)
db = client['tu_nombre_base_de_datos']  # Reemplaza con el nombre de tu base de datos
collection = db['tu_nombre_coleccion']  # Reemplaza con el nombre de tu colección

def clear_database():
    """Elimina todos los documentos de la colección especificada."""
    try:
        result = collection.delete_many({})
        print(f"Se eliminaron {result.deleted_count} documentos a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")
    except Exception as e:
        print(f"Error al eliminar los documentos: {e}")

def schedule_clear_database():
    """Programa la eliminación de la base de datos todos los días a las 17:00."""
    scheduler = BlockingScheduler()
    scheduler.add_job(clear_database, 'cron', hour=17, minute=0)
    print("Tarea programada para ejecutar a las 17:00 todos los días.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

def create_windows_startup():
    """Crea un archivo .bat para ejecutar el script al inicio en Windows."""
    bat_content = r'''
    @echo off
    cd /d "{script_dir}"
    python combined_script.py
    '''
    
    script_dir = Path(__file__).parent.resolve()
    bat_content = bat_content.format(script_dir=script_dir)
    
    # Ruta del archivo .bat en la carpeta de inicio de Windows
    startup_path = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    bat_file = startup_path / "run_clear_database.bat"

    with open(bat_file, 'w') as file:
        file.write(bat_content)
    print(f"Archivo de inicio creado en {bat_file}")

def create_linux_startup():
    """Crea un archivo .sh para ejecutar el script al inicio en Linux y lo añade al crontab."""
    sh_content = f'''#!/bin/bash
    cd {Path(__file__).parent.resolve()}
    /usr/bin/python3 combined_script.py
    '''

    script_dir = Path(__file__).parent.resolve()
    sh_file = script_dir / "run_clear_database.sh"
    
    # Crear el archivo .sh
    with open(sh_file, 'w') as file:
        file.write(sh_content)
    
    # Hacer ejecutable el archivo
    sh_file.chmod(0o755)
    
    # Añadir al crontab para que se ejecute al iniciar
    cron_command = f'@reboot {sh_file}\n'
    process = subprocess.Popen(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if b'no crontab for' in stderr:
        # Si no hay crontab, crear uno nuevo
        with open('/tmp/crontab.txt', 'w') as f:
            f.write(cron_command)
        subprocess.run(['crontab', '/tmp/crontab.txt'])
    else:
        # Añadir al crontab existente
        with open('/tmp/crontab.txt', 'w') as f:
            f.write(stdout.decode() + cron_command)
        subprocess.run(['crontab', '/tmp/crontab.txt'])
    
    print(f"Archivo de inicio creado en {sh_file} y agregado a crontab")

def setup_autorun():
    """Configura la ejecución automática del script según el sistema operativo."""
    os_type = platform.system()
    if os_type == 'Windows':
        create_windows_startup()
    elif os_type == 'Linux':
        create_linux_startup()
    else:
        print(f"Sistema operativo {os_type} no soportado.")

def main():
    # Configurar la ejecución automática al iniciar
    setup_autorun()
    # Programar la eliminación de la base de datos a las 17:00
    schedule_clear_database()

if __name__ == "__main__":
    main()
