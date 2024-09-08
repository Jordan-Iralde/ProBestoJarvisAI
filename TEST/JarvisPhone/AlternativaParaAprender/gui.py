import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from tqdm import tqdm
import logging
from pymongo import MongoClient
import threading
import time
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://JarvisUser:2wssnlZhLTw5WuvF4@jorvisai.lrskk.mongodb.net/")
db = client['JarvisAI']
collection = db['b']

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SEARCH_QUERIES = ["Mejorar Codigo"]
NUM_ITERATIONS = 12
SLEEP_INTERVAL = 5  # Intervalo de espera simulado para pruebas

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
    for item in tqdm(items, desc="Creando estructura", unit="item"):
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

def gui_setup():
    """Configura y ejecuta la interfaz gráfica."""
    root = tk.Tk()
    root.title("Creador de Estructura de Proyecto")
    root.geometry("1200x800")
    root.configure(bg="#2b2b2b")  # Fondo oscuro para un look moderno

    def select_base_dir():
        directory = filedialog.askdirectory(title="Seleccionar Directorio Base")
        if directory:
            base_dir.set(directory)
    
    def select_config_file():
        file = filedialog.askopenfilename(title="Seleccionar Archivo de Configuración", filetypes=[("Archivos JSON", "*.json")])
        if file:
            config_file.set(file)

    def run_process():
        base_path = Path(base_dir.get())
        config_path = Path(config_file.get())
        if not base_path or not config_path:
            messagebox.showerror("Error", "Directorio base o archivo de configuración no seleccionados.")
            return
        try:
            run_script(base_path, config_path)
            open_file_explorer(base_path)  # Intentar abrir el explorador de archivos en el directorio base
        except Exception as e:
            messagebox.showerror("Error", str(e))

    base_dir = tk.StringVar()
    config_file = tk.StringVar()

    # Componentes GUI para el creador de carpetas y archivos
    tk.Label(root, text="Directorio Base:", bg="#2b2b2b", fg="white", font=("Helvetica", 12)).pack(pady=5)
    tk.Entry(root, textvariable=base_dir, width=70, bg="#1e1e1e", fg="white").pack(pady=5)
    tk.Button(root, text="Seleccionar Directorio Base", command=select_base_dir, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=5)

    tk.Label(root, text="Archivo de Configuración:", bg="#2b2b2b", fg="white", font=("Helvetica", 12)).pack(pady=5)
    tk.Entry(root, textvariable=config_file, width=70, bg="#1e1e1e", fg="white").pack(pady=5)
    tk.Button(root, text="Seleccionar Archivo de Configuración", command=select_config_file, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=5)

    tk.Button(root, text="Crear Estructura", command=run_process, bg="#2196F3", fg="white", font=("Helvetica", 14)).pack(pady=20)

    # Componentes GUI para el sistema de búsqueda y almacenamiento
    tk.Label(root, text="Progreso de Entrenamiento", bg="#2b2b2b", fg="white", font=("Helvetica", 16)).pack(pady=10)
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    content_text = tk.Text(root, width=100, height=20, bg="#1e1e1e", fg="white", font=("Consolas", 12))
    content_text.pack(pady=10)

    figure = plt.Figure(figsize=(8, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax.set_title("Crecimiento de la IA")
    ax.set_xlabel("Iteraciones")
    ax.set_ylabel("Datos Recopilados")
    line, = ax.plot([], [], color="blue")
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().pack(pady=20)

    root.mainloop()

def run_script(base_dir: Path, config_file: Path):
    """Ejecuta el script para crear la estructura de directorios y archivos."""
    if not base_dir.exists():
        raise FileNotFoundError(f"El directorio base no existe: {base_dir.resolve()}")
    
    items = load_config(config_file)
    log_entries = create_structure(base_dir, items)
    
    logging.info("Estructura creada exitosamente.")

    def scrape_and_store():
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(search_and_store, query) for query in SEARCH_QUERIES]
            for future in as_completed(futures):
                try:
                    data = future.result()
                    logging.info(f"Datos almacenados: {data}")
                except Exception as e:
                    logging.error(f"Error en la búsqueda o almacenamiento de datos: {e}")

    threading.Thread(target=scrape_and_store, daemon=True).start()

def search_and_store(query):
    """Realiza la búsqueda y almacena los resultados en MongoDB."""
    base_url = "https://www.bing.com/search"
    params = {
        "q": query,
        "count": 50,  # Número de resultados a recuperar
    }
    response = requests.get(base_url, params=params, timeout=10)
    response.raise_for_status()  # Lanzar excepción para cualquier respuesta de error

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for result in soup.select('li.b_algo'):
        title = result.select_one('h2 a').text if result.select_one('h2 a') else 'Sin título'
        description = result.select_one('p').text if result.select_one('p') else 'Sin descripción'
        link = result.select_one('h2 a')['href'] if result.select_one('h2 a') else 'Sin enlace'
        
        results.append({
            'query': query,
            'title': title,
            'description': description,
            'link': link
        })

    # Insertar los resultados en la colección MongoDB
    if results:
        collection.insert_many(results)
        logging.info(f"Resultados almacenados para la consulta: {query}")
    else:
        logging.warning(f"No se encontraron resultados para la consulta: {query}")

    return results

if __name__ == "__main__":
    gui_setup()
