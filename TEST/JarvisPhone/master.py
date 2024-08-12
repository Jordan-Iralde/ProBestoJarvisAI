import subprocess
import logging
import threading
import os
import shutil
from tqdm import tqdm
from pymongo import MongoClient
import tkinter as tk
from tkinter import font, ttk
import time

# Asegúrate de que el directorio 'logs' exista
os.makedirs('logs', exist_ok=True)

# Configura el logging
logging.basicConfig(filename='logs/master_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Configura MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['jarvis_db']
collection = db['script_logs']

def execute_script(script_path, description, pbar):
    if not os.path.exists(script_path):
        logging.error(f"{description} script not found: {script_path}")
        pbar.update(1)
        return

    try:
        logging.info(f"Executing {description}...")
        result = subprocess.run(['python', script_path], capture_output=True, text=True)

        data = {
            'script': script_path,
            'description': description,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        collection.insert_one(data)

        if result.returncode != 0:
            logging.error(f"Error executing {description}: {result.stderr}")
        else:
            logging.info(result.stdout)
    except Exception as e:
        logging.error(f"An error occurred while executing {description}: {e}")
    finally:
        pbar.update(1)

def update_time():
    current_time = time.strftime('%H:%M:%S')
    time_label.config(text=current_time)
    window.after(1000, update_time)

def save_data():
    data = {
        'time': time.strftime('%H:%M:%S'),
        'info': 'Some data related to the operation'
    }
    collection.insert_one(data)
    status_label.config(text="Datos guardados correctamente.")

def main():
    # Configura la GUI
    window = tk.Tk()
    window.title("Panel de Control de Jarvis")
    window.geometry("600x400")
    window.resizable(False, False)

    large_font = font.Font(family="Helvetica", size=48, weight="bold")
    time_label = tk.Label(window, font=large_font)
    time_label.pack(expand=True)
    save_button = ttk.Button(window, text="Guardar Datos", command=save_data)
    save_button.pack(pady=10)
    status_label = tk.Label(window, text="")
    status_label.pack(pady=10)
    update_time()

    # Ejecuta los scripts en paralelo
    scripts_to_execute = [
        (r'TEST\JarvisPhone\training\train.py', 'Training the Model'),
        (r'TEST\JarvisPhone\predictions.py', 'Making Predictions'),
        (r'TEST\JarvisPhone\web_content\continuous_learning.py', 'Continuous Learning')
    ]

    threads = []
    with tqdm(total=len(scripts_to_execute), desc="Overall Progress", ncols=100) as pbar:
        for script, description in scripts_to_execute:
            thread = threading.Thread(target=execute_script, args=(script, description, pbar))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    logging.info("All tasks completed successfully!")

    # Inicia el bucle principal de la ventana
    window.mainloop()

if __name__ == "__main__":
    main()
