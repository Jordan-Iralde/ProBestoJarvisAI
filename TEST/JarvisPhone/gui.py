import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

SEARCH_QUERIES = ["machine learning", "artificial intelligence", "data science"]
NUM_ITERATIONS = 12
SLEEP_INTERVAL = 5  # Simulate sleep interval for testing

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JarvisPhone")
        self.geometry("1000x800")
        self.configure(bg="black")

        self.create_widgets()

    def create_widgets(self):
        self.progress_label = tk.Label(self, text="Progreso de Entrenamiento", bg="black", fg="white")
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.start_button = tk.Button(self, text="Iniciar Entrenamiento", command=self.start_training)
        self.start_button.pack(pady=10)

        self.content_label = tk.Label(self, text="Contenidos Recuperados", bg="black", fg="white")
        self.content_label.pack(pady=10)

        self.content_text = tk.Text(self, width=80, height=20, bg="black", fg="white")
        self.content_text.pack(pady=10)

        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Crecimiento de la IA")
        self.ax.set_xlabel("Iteraciones")
        self.ax.set_ylabel("Datos Recopilados")
        self.line, = self.ax.plot([], [], 'r-')
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
            data_collected.append(len(contents))
            self.update_graph(data_collected)
            time.sleep(SLEEP_INTERVAL)  # Simulating training time

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

    def update_graph(self, data_collected):
        self.line.set_xdata(range(len(data_collected)))
        self.line.set_ydata(data_collected)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()
