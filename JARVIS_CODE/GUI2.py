import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import pymongo
import os
import logging
from dotenv import load_dotenv
from itertools import combinations
import time

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
collection = db["honey"]

# Archivo de palabras
WORDS_FILE = 'spanish_words.txt'

def load_spanish_words(file_path):
    """Carga palabras desde un archivo y las devuelve como lista."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().splitlines()
        logging.info(f"{len(words)} palabras cargadas desde el archivo.")
        return words
    except FileNotFoundError:
        logging.error("El archivo de palabras no se encontró.")
        return []

def save_new_words(new_words):
    """Guarda nuevas palabras en el archivo sin duplicar."""
    try:
        with open(WORDS_FILE, 'a', encoding='utf-8') as file:
            for word in new_words:
                file.write(word + '\n')
        logging.info(f"{len(new_words)} nuevas palabras añadidas a spanish_words.txt.")
    except Exception as e:
        logging.error(f"Error al guardar palabras en el archivo: {e}")

def generate_search_queries(words, max_length=5):
    """Genera combinaciones de palabras para formar oraciones bajo demanda."""
    for length in range(1, max_length + 1):
        for comb in combinations(words, length):
            query = ' '.join(comb)
            yield query

def fetch_web_content(query):
    """Realiza una búsqueda en la web y devuelve el contenido."""
    session = requests.Session()
    try:
        # Usamos DuckDuckGo para evitar restricciones de Google
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(search_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = [result.get_text() for result in soup.find_all('a', {'class': 'result__a'})]
        logging.info(f"Se encontraron {len(results)} resultados para la consulta: {query}")
        return results
    except requests.RequestException as e:
        logging.error(f"Error al buscar el contenido para '{query}': {e}")
        return []

def extract_keywords(content):
    """Extrae palabras clave utilizando TF-IDF y convierte el resultado a una lista para evitar problemas de codificación."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_df=0.8, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(content)
    features = vectorizer.get_feature_names_out()
    return features[:10].tolist()  # Devuelve las 10 principales palabras clave como lista

def update_keywords_in_mongo(new_keywords):
    """Actualiza MongoDB con nuevas palabras clave y guarda en el archivo."""
    for keyword in new_keywords:
        if not collection.find_one({'keywords': keyword}):
            collection.insert_one({'keywords': keyword})
            logging.info(f"Palabra clave '{keyword}' añadida a MongoDB.")
    save_new_words(new_keywords)

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

    def start_training(self):
        self.train_button.config(state='disabled')
        threading.Thread(target=self.run_infinite_search, daemon=True).start()

    def run_infinite_search(self):
        """Búsqueda continua que extrae, guarda y actualiza palabras clave indefinidamente."""
        words = load_spanish_words(WORDS_FILE)
        while True:
            for query in generate_search_queries(words):
                results = fetch_web_content(query)
                if results:
                    new_keywords = extract_keywords(results)
                    update_keywords_in_mongo(new_keywords)
            time.sleep(10)  # Ajusta el intervalo de búsqueda según necesidad

    def show_graph(self):
        """Muestra un gráfico con datos recopilados (este método se puede personalizar según los datos)."""
        pass

if __name__ == '__main__':
    app = SearchApp()
    app.mainloop()
