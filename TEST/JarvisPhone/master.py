import subprocess
import logging
import threading
import os
import shutil
from tqdm import tqdm

# Configuración de logging
logging.basicConfig(filename='logs/master_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')


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


    scripts_to_execute = [
        ('JarvisPhone/training/train.py', 'Training the Model'),
        ('JarvisPhone/predictions.py', 'Making Predictions'),
        ('JarvisPhone/web_content/continuous_learning.py', 'Continuous Learning')
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

if __name__ == "__main__":
    main()
