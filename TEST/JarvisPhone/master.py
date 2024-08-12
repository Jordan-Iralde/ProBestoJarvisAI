import subprocess
import logging
import threading
import os
import shutil
from tqdm import tqdm
import tkinter as tk
from tkinter import font
import time

# Asegúrate de que el directorio 'logs' exista
os.makedirs('logs', exist_ok=True)

# Configura el logging
logging.basicConfig(filename='logs/master_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def update_time():
    current_time = time.strftime('%H:%M:%S')
    time_label.config(text=current_time)  # Accede a 'time_label' correctamente
    window.after(1000, update_time)

def execute_script(script_path, description, pbar):
    if not os.path.exists(script_path):
        logging.error(f"{description} script not found: {script_path}")
        pbar.update(1)
        return

    try:
        logging.info(f"Executing {description}...")
        result = subprocess.run(['python', script_path], capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error executing {description}: {result.stderr}")
        else:
            logging.info(result.stdout)
    except Exception as e:
        logging.error(f"An error occurred while executing {description}: {e}")
    finally:
        pbar.update(1)

def main():
    global window, time_label  # Asegúrate de que las variables estén en el ámbito global

    window = tk.Tk()
    window.title("JarvisPhone")
    window.geometry("400x200")
    window.resizable(False, False)

    large_font = font.Font(family="Helvetica", size=48, weight="bold")

    time_label = tk.Label(window, font=large_font)
    time_label.pack(expand=True)

    update_time()

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

    window.mainloop()

if __name__ == "__main__":
    main()
