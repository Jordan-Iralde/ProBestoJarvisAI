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
from collections import OrderedDict
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
client = pymongo.MongoClient("mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/")
db = client["JarvisAI"]
collection = db["prueba"]

# Configuración
NUM_ITERATIONS = 12
SLEEP_INTERVAL = 5
WORDS_FILE = 'spanish_words.txt'  # Archivo con palabras en español
SEARCH_QUERIES = []  # Se llenará con oraciones generadas

def load_spanish_words(file_path):
    """Carga palabras en español desde un archivo."""
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()
    return words

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
        if item['type'] == 'directory':
            path.mkdir(parents=True, exist_ok=True)
            log.append(f"Directorio creado: {path.resolve()}")
        elif item['type'] == 'file':
            path.parent.mkdir(parents=True, exist_ok=True)
            content = item.get('content', f"# Contenido inicial para {path.name}")
            log.append(create_file(path, content))
        else:
            log.append(f"Error: Tipo desconocido para {path}")
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
        response = session.get(search_url, headers=headers, timeout=30)  # Reduce el timeout a 30 segundos
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
        self.train_button.pack(pady=20)

        # Canvas para gráficos
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(pady=20)

    def start_training(self):
        self.train_button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_training, daemon=True).start()

    def run_training(self):
        """Entrenamiento en segundo plano."""
        data_collected = []
        iteration_count = 0
        while iteration_count < NUM_ITERATIONS and self.search_queries:
            queries_to_process = random.sample(self.search_queries, min(len(self.search_queries), 10))
            self.search_queries = [q for q in self.search_queries if q not in self.completed_queries]
            if not queries_to_process:
                logging.info("No hay más consultas por realizar.")
                break
            contents = self.fetch_and_display_content(queries_to_process)
            if contents:
                data_collected.extend(contents)
                self.update_plot(data_collected)
            iteration_count += 1
            time.sleep(SLEEP_INTERVAL)
        if not self.search_queries:
            logging.info("No hay más consultas disponibles.")
        else:
            logging.info("Entrenamiento completado.")

    def update_plot(self, data_collected):
        """Actualiza el gráfico con los datos recopilados."""
        self.ax.clear()
        self.ax.set_title("Crecimiento de la IA", color="white")
        self.ax.set_xlabel("Iteraciones", color="white")
        self.ax.set_ylabel("Datos Recopilados", color="white")
        self.ax.plot(range(len(data_collected)), data_collected, 'c-', marker='o')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.canvas.draw()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JarvisPhone")
        self.geometry("1200x900")
        self.configure(bg="#1E1E1E")
        self.words = load_spanish_words(WORDS_FILE)
        self.search_queries = generate_search_queries(self.words)
        self.completed_queries = set()
        self.create_widgets()  # Llama al método local
        self.start_training()

    def create_widgets(self):
        """Crea y organiza los widgets en la ventana principal."""
        # Mejora el estilo visual
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('TLabel', background='#1E1E1E', foreground='white', font=('Helvetica', 12))

        self.header_frame = tk.Frame(self, bg="#1E1E1E")
        self.header_frame.pack(pady=10)

        self.progress_label = ttk.Label(self.header_frame, text="Progreso de Entrenamiento")
        self.progress_label.pack(side=tk.LEFT, padx=10)

        self.progress_bar = ttk.Progressbar(self.header_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, padx=10)

        self.content_frame = tk.Frame(self, bg="#1E1E1E")
        self.content_frame.pack(pady=10)

        self.content_label = ttk.Label(self.content_frame, text="Contenidos Recuperados")
        self.content_label.pack(pady=10)

        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, height=15, width=100)
        self.content_text.pack(padx=10)

        self.button_frame = tk.Frame(self, bg="#1E1E1E")
        self.button_frame.pack(pady=10)

        self.create_file_button = ttk.Button(self.button_frame, text="Crear Estructura de Archivos", command=self.open_file_creator)
        self.create_file_button.pack(side=tk.LEFT, padx=10)

        self.open_vscode_button = ttk.Button(self.button_frame, text="Abrir VS Code", command=lambda: open_vscode(Path(__file__).parent))
        self.open_vscode_button.pack(side=tk.LEFT, padx=10)

        self.open_explorer_button = ttk.Button(self.button_frame, text="Abrir Explorador de Archivos", command=lambda: open_file_explorer(Path(__file__).parent))
        self.open_explorer_button.pack(side=tk.LEFT, padx=10)

        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_facecolor('#1E1E1E')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Botón para hacer predicciones
        self.predict_button = ttk.Button(self.button_frame, text="Hacer Predicciones", command=self.on_predict_button_click)
        self.predict_button.pack(side=tk.LEFT, padx=10)

    def open_file_creator(self):
        """Abre un diálogo para seleccionar el archivo de configuración y crear la estructura de archivos."""
        try:
            file_path = filedialog.askopenfilename(title="Seleccionar archivo de configuración", filetypes=[("Archivos JSON", "*.json")])
            if file_path:
                items = load_config(Path(file_path))
                base_dir = Path(file_path).parent
                log = create_structure(base_dir, items)
                messagebox.showinfo("Estructura Creada", "\n".join(log))
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    def start_training(self):
        """Inicia el entrenamiento en un hilo separado."""
        self.training_thread = threading.Thread(target=self.run_training)
        self.training_thread.start()

    def run_training(self):
        """Entrenamiento en segundo plano."""
        data_collected = []
        for _ in range(NUM_ITERATIONS):
            if len(self.search_queries) == 0:
                logging.info("No hay más consultas para realizar.")
                break
            queries_to_process = random.sample(self.search_queries, min(len(self.search_queries), 10))
            self.search_queries = [q for q in self.search_queries if q not in self.completed_queries]
            if len(queries_to_process) == 0:
                logging.info("No hay más consultas por realizar.")
                break
            contents = self.fetch_and_display_content(queries_to_process)  # Llamar correctamente el método
            if contents:
                data_collected.extend(contents)
                self.update_plot(data_collected)
            time.sleep(SLEEP_INTERVAL)

    def fetch_and_display_content(self, queries):
        """Recupera y muestra el contenido web."""
        contents = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_web_content, query) for query in queries]
            for query, future in zip(queries, as_completed(futures)):
                content = future.result()
                if content:
                    contents.extend(content)
                    logging.info(f"Contenido para consulta '{query}' recuperado.")
                else:
                    logging.info(f"No se obtuvo contenido para la consulta '{query}'")
                time.sleep(1)  # Espacio entre consultas para evitar bloqueos
        self.save_data_to_mongo(contents)
        return contents

    def save_data_to_mongo(self, contents):
        """Guarda los datos en MongoDB con etiquetas."""
        for content in contents:
            collection.insert_one({"content": content, "type": "search_result"})
        logging.info(f"Datos guardados en MongoDB: {len(contents)} entradas.")

    def update_plot(self, data_collected):
        """Actualiza el gráfico con los datos recopilados."""
        self.ax.clear()
        self.ax.set_title("Crecimiento de la IA", color="white")
        self.ax.set_xlabel("Iteraciones", color="white")
        self.ax.set_ylabel("Datos Recopilados", color="white")
        self.ax.plot(range(len(data_collected)), data_collected, 'c-', marker='o')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.canvas.draw()

    def on_predict_button_click(self):
        """Método para manejar el clic en el botón de predicción."""
        # Aquí puedes implementar la lógica para hacer predicciones
        logging.info("Botón de predicción clicado.")
        # Implementar el código para hacer predicciones aquí

if __name__ == "__main__":
    app = App()
    app.mainloop()
