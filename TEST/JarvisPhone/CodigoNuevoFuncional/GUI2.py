import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import pymongo
import json
import os
import subprocess
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
import random
from itertools import combinations

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar configuración desde .env
load_dotenv()
VS_CODE_PATH = os.getenv('VS_CODE_PATH', 'code')

# Conexión a MongoDB Atlas
def get_mongo_client():
    """Devuelve un cliente de conexión a MongoDB."""
    try:
        client = pymongo.MongoClient("mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/")
        logging.info("Conectado a MongoDB Atlas.")
        return client
    except pymongo.errors.ConnectionError as e:
        logging.error(f"Error de conexión a MongoDB: {e}")
        raise

mongo_client = get_mongo_client()
db = mongo_client["JarvisAI"]
collection = db["prueba"]

# Configuración
NUM_ITERATIONS = 12
SLEEP_INTERVAL = 5
WORDS_FILE = 'spanish_words.txt'
SEARCH_QUERIES = []

def load_spanish_words(file_path):
    """Carga palabras en español desde un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().splitlines()
        return words
    except FileNotFoundError:
        logging.error("El archivo de palabras en español no se encontró.")
        return []

def create_file(file_path: Path, content: str) -> str:
    """Crea un archivo con el contenido especificado."""
    try:
        file_path.write_text(content)
        logging.info(f"Archivo creado: {file_path.resolve()}")
        return f"Archivo creado: {file_path.resolve()}"
    except Exception as e:
        logging.error(f"Error al crear el archivo {file_path}: {e}")
        return f"Error al crear el archivo {file_path}: {e}"

def create_structure(base_dir: Path, items: list) -> list:
    """Crea la estructura de directorios y archivos según la configuración."""
    log = []
    for item in items:
        path = base_dir / item['path']
        try:
            if item['type'] == 'directory':
                path.mkdir(parents=True, exist_ok=True)
                log.append(f"Directorio creado: {path.resolve()}")
            elif item['type'] == 'file':
                path.parent.mkdir(parents=True, exist_ok=True)
                content = item.get('content', f"# Contenido inicial para {path.name}")
                log.append(create_file(path, content))
            else:
                raise ValueError(f"Tipo desconocido para {path}")
        except Exception as e:
            logging.error(f"Error al crear {path}: {e}")
            log.append(f"Error: {e}")
    return log

def load_config(file_path: Path) -> list:
    """Carga y valida la configuración del archivo JSON."""
    try:
        with open(file_path, 'r') as f:
            items = json.load(f)
            if not isinstance(items, list):
                raise ValueError("La configuración debe ser una lista en el archivo JSON.")
            for item in items:
                if not isinstance(item, dict) or 'type' not in item or 'path' not in item:
                    raise ValueError("Cada elemento debe ser un diccionario con 'type' y 'path'.")
                if item['type'] not in ['directory', 'file']:
                    raise ValueError("El valor de 'type' debe ser 'directory' o 'file'.")
            return items
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        logging.error(f"Error al leer el archivo de configuración: {e}")
        raise RuntimeError(f"Error al leer el archivo de configuración: {e}")

def open_vscode(directory: Path):
    """Abre Visual Studio Code en el directorio especificado."""
    vscode_command = [VS_CODE_PATH, str(directory)]
    if sys.platform == "win32":
        vscode_command = [r'C:\Program Files\Microsoft VS Code\Code.exe', str(directory)]

    if check_vscode_installed():
        try:
            subprocess.run(vscode_command, check=True)
            logging.info(f"Visual Studio Code abierto en {directory.resolve()}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al abrir Visual Studio Code: {e}")
            messagebox.showerror("Error", f"No se pudo abrir Visual Studio Code: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al abrir Visual Studio Code: {e}")
            messagebox.showerror("Error", f"Error inesperado: {e}")
    else:
        messagebox.showwarning("Advertencia", "Visual Studio Code no está instalado o el comando 'code' no está en el PATH. Por favor, instala Visual Studio Code y asegúrate de que el comando 'code' esté disponible en la línea de comandos.")

def open_file_explorer(directory: Path):
    """Abre el explorador de archivos en el directorio especificado."""
    try:
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            os.system(f"open {directory}")
        else:
            os.system(f"xdg-open {directory}")
        logging.info(f"Explorador de archivos abierto en {directory.resolve()}.")
    except Exception as e:
        logging.error(f"No se pudo abrir el explorador de archivos: {e}")
        messagebox.showerror("Error", f"No se pudo abrir el explorador de archivos: {e}")

def check_vscode_installed() -> bool:
    """Verifica si Visual Studio Code está instalado y accesible en la línea de comandos."""
    try:
        subprocess.run([VS_CODE_PATH, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def generate_search_queries(words, max_length=5):
    """Genera combinaciones de palabras para formar oraciones."""
    queries = []
    for length in range(1, max_length + 1):
        queries.extend([' '.join(comb) for comb in combinations(words, length)])
    return queries

def fetch_web_content(query):
    """Realiza una búsqueda en la web y devuelve el contenido."""
    session = requests.Session()
    try:
        search_url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(search_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [result.get_text() for result in soup.find_all('h3')]
        return results
    except requests.RequestException as e:
        logging.error(f"Error al buscar el contenido para '{query}': {e}")
        return []

class SearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Buscador de Datos')
        self.geometry('800x600')

        # Botón para iniciar el entrenamiento
        self.train_button = tk.Button(self, text='Iniciar Entrenamiento', command=self.start_training)
        self.train_button.pack(pady=10)

        # Botón para mostrar gráficos
        self.show_graph_button = tk.Button(self, text='Mostrar Gráfico', command=self.show_graph)
        self.show_graph_button.pack(pady=10)

        # Botón para abrir Visual Studio Code
        self.open_vscode_button = tk.Button(self, text='Abrir Visual Studio Code', command=lambda: open_vscode(Path(__file__).parent))
        self.open_vscode_button.pack(pady=10)

        # Botón para abrir el explorador de archivos
        self.open_explorer_button = tk.Button(self, text='Abrir Explorador de Archivos', command=lambda: open_file_explorer(Path(__file__).parent))
        self.open_explorer_button.pack(pady=10)

    def start_training(self):
        self.train_button.config(state='disabled')
        words = load_spanish_words(WORDS_FILE)
        if not words:
            messagebox.showerror("Error", "No se pudieron cargar las palabras en español.")
            self.train_button.config(state='normal')
            return

        SEARCH_QUERIES.extend(generate_search_queries(words))
        self.progress = ttk.Progressbar(self, orient='horizontal', length=200, mode='determinate')
        self.progress.pack(pady=20)

        # Uso de ThreadPoolExecutor para manejar solicitudes web en paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_web_content, query): query for query in SEARCH_QUERIES[:NUM_ITERATIONS]}

            for future in as_completed(futures):
                query = futures[future]
                try:
                    results = future.result()
                    if results:
                        # Insertar en MongoDB
                        collection.insert_one({'query': query, 'results': results})
                        logging.info(f"Resultados para '{query}' guardados en MongoDB.")
                    else:
                        logging.warning(f"No se encontraron resultados para '{query}'.")
                except Exception as exc:
                    logging.error(f"Generó una excepción: {exc}")

                self.progress['value'] += 100 / NUM_ITERATIONS
                self.update_idletasks()

        self.train_button.config(state='normal')

    def show_graph(self):
        """Muestra un gráfico con datos recopilados."""
        try:
            data = list(collection.find())
            queries = [item['query'] for item in data]
            results_count = [len(item['results']) for item in data]

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(queries, results_count, color='skyblue')
            ax.set_xlabel('Número de Resultados')
            ax.set_title('Resultados por Consulta')

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack()
        except Exception as e:
            logging.error(f"Error al mostrar el gráfico: {e}")
            messagebox.showerror("Error", f"Error al mostrar el gráfico: {e}")

if __name__ == '__main__':
    app = SearchApp()
    app.mainloop()
