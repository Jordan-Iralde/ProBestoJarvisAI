import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import pymongo
from collections import OrderedDict

# MongoDB Atlas Connection
client = pymongo.MongoClient("mongodb+srv://JarvisUser:2wssnlZhLTw5WuvF4@jorvisai.lrskk.mongodb.net/")
db = client["JarvisAI"]
collection = db["web_searches"]

SEARCH_QUERIES = ["machine learning", "artificial intelligence", "data science"]
NUM_ITERATIONS = 12
SLEEP_INTERVAL = 5

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JarvisPhone")
        self.geometry("1200x900")
        self.configure(bg="#1E1E1E")

        self.create_widgets()
        self.start_training()

    def create_widgets(self):
        # Improved visual styles
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

        self.content_text = tk.Text(self.content_frame, width=100, height=20, bg="#2E2E2E", fg="white", font=('Helvetica', 10))
        self.content_text.pack(pady=10)

        self.figure = plt.Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Crecimiento de la IA", color="white")
        self.ax.set_xlabel("Iteraciones", color="white")
        self.ax.set_ylabel("Datos Recopilados", color="white")
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white') 
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.line, = self.ax.plot([], [], 'c-')
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def start_training(self):
        self.progress_bar["value"] = 0
        threading.Thread(target=self.run_training).start()

    def run_training(self):
        total_iterations = NUM_ITERATIONS
        data_collected = []

        for iteration in range(total_iterations):
            self.progress_bar["value"] += (100 / total_iterations)
            contents = self.fetch_and_display_content()
            contents = self.remove_duplicates(contents)
            data_collected.append(len(contents))
            self.save_data_to_mongo(contents)
            self.update_graph(data_collected)
            time.sleep(SLEEP_INTERVAL)

        self.progress_bar["value"] = 100

    def fetch_web_content(self, query):
        try:
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                snippets = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
                return [snippet.get_text() for snippet in snippets]
            else:
                return []
        except Exception as e:
            return []

    def fetch_and_display_content(self):
        contents = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_web_content, query) for query in SEARCH_QUERIES]
            for future in as_completed(futures):
                content = future.result()
                if content:
                    contents.extend(content)
                    self.content_text.insert(tk.END, f"Content for query:\n")
                    self.content_text.insert(tk.END, "\n".join(content) + "\n\n")
                else:
                    self.content_text.insert(tk.END, "No content fetched for query\n\n")
        return contents

    def remove_duplicates(self, contents):
        return list(OrderedDict.fromkeys(contents))

    def save_data_to_mongo(self, contents):
        normalized_data = [{"query": query, "content": content} for query in SEARCH_QUERIES for content in contents]
        collection.insert_many(normalized_data)

    def update_graph(self, data_collected):
        self.line.set_xdata(range(len(data_collected)))
        self.line.set_ydata(data_collected)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()
