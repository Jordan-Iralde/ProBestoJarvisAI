import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
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
from sklearn.feature_extraction.text import TfidfVectorizer
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

def generate_search_queries(words, max_length=5):
    """Genera combinaciones de palabras para formar oraciones."""
    queries = []
    for length in range(1, max_length + 1):
        queries.extend([' '.join(comb) for comb in combinations(words, length)])
    return queries

def extract_keywords(content):
    """Extrae palabras clave utilizando TF-IDF y convierte el resultado a una lista para evitar problemas de codificación."""
    vectorizer = TfidfVectorizer(max_df=0.8)
    tfidf_matrix = vectorizer.fit_transform(content)
    features = vectorizer.get_feature_names_out()

    # Convertimos a lista antes de devolver
    return features[:10].tolist()  # Devuelve las 10 principales palabras clave como lista



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

def create_file(file_path: Path, content: str) -> str:
    """Crea un archivo con el contenido especificado."""
    try:
        file_path.write_text(content)
        logging.info(f"Archivo creado: {file_path.resolve()}")
        return f"Archivo creado: {file_path.resolve()}"
    except Exception as e:
        logging.error(f"Error al crear el archivo {file_path}: {e}")
        return f"Error al crear el archivo {file_path}: {e}"

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
    else:
        messagebox.showwarning("Advertencia", "Visual Studio Code no está instalado.")

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
                        # Inserta resultados en MongoDB con palabras clave extraídas
                        keywords = extract_keywords(results)
                        collection.insert_one({'query': query, 'results': results, 'keywords': keywords})
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

            fig, ax = plt.subplots()
            ax.bar(queries, results_count)
            ax.set_xlabel('Consultas')
            ax.set_ylabel('Número de Resultados')
            ax.set_title('Resultados de Búsqueda por Consulta')
            plt.xticks(rotation=90)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack()
        except Exception as e:
            logging.error(f"Error al mostrar el gráfico: {e}")
            messagebox.showerror("Error", f"No se pudo mostrar el gráfico: {e}")

if __name__ == '__main__':
    app = SearchApp()
    app.mainloop()
