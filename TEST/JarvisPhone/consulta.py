from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import simpledialog, messagebox
import os

# Configura tu clave API de SerpAPI
serpapi_api_key = "8a1bb6b90ec305cc723b928471217e90d4b5fcc6b6430f137ccee81e2a96b7c1"

def obtener_contenido_completo(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = "\n".join(paragraph.get_text() for paragraph in paragraphs)
        return full_text[:3000]
    except Exception as e:
        return f"Error al obtener contenido: {e}"

def buscar_en_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_api_key,
        "num": 5
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    respuesta_completa = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            title = result.get("title", "No hay título disponible.")
            snippet = result.get("snippet", "No hay descripción disponible.")
            link = result.get("link", "No hay enlace disponible.")
            full_text = obtener_contenido_completo(link)
            respuesta_completa.append(f"Título: {title}\nDescripción: {snippet}\nEnlace: {link}\nTexto Completo:\n{full_text}\n")

    if respuesta_completa:
        return "\n".join(respuesta_completa)
    else:
        return "No se encontraron resultados."

def guardar_informacion(info, archivo="informacion_google.txt"):
    with open(archivo, "a", encoding='utf-8') as file:
        file.write(info + "\n")

# Configura la interfaz gráfica
def consulta_google():
    while True:
        pregunta = simpledialog.askstring("Consulta", "Ingrese su pregunta:")
        if not pregunta:
            break
        
        respuesta = buscar_en_google(pregunta)
        guardar_informacion(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n", nombre_archivo)
        
        messagebox.showinfo("Resultado", f"Pregunta: {pregunta}\nRespuesta:\n{respuesta}")

# Nombre del archivo de salida
nombre_archivo = "C:/Users/ProaLaFalda/Desktop/informacion_google.txt"

# Crea la ventana principal
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Ejecuta la función de consulta
consulta_google()

print("Consultas completadas y guardadas.")
