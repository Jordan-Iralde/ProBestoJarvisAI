import os
import json
from datetime import datetime
import shutil

# === Configuración de rutas ===
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
JARVIS_DATA_PATH = os.path.join(DESKTOP_PATH, "jarvis_data")
DATA_BD_PATH = os.path.join(JARVIS_DATA_PATH, "databd")
PREPROCESSED_PATH = os.path.join(JARVIS_DATA_PATH, "preprocessed")

# Obtener la fecha actual para la carpeta
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_PREPROCESSED_PATH = os.path.join(PREPROCESSED_PATH, CURRENT_DATE)

def create_folder_structure():
    """Crea la estructura de carpetas necesaria para el preprocesamiento"""
    folders = {
        "texto": os.path.join(CURRENT_PREPROCESSED_PATH, "texto"),
        "audio": os.path.join(CURRENT_PREPROCESSED_PATH, "audio"),
        "imagen": os.path.join(CURRENT_PREPROCESSED_PATH, "imagen")
    }
    
    for folder in folders.values():
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"Carpeta creada/verificada: {folder}")
        except Exception as e:
            print(f"Error creando carpeta {folder}: {str(e)}")
            raise
    
    return folders

def preprocess_text_file(file_path):
    """Preprocesa un archivo de texto"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Aquí puedes agregar cualquier preprocesamiento específico del texto
            # Por ejemplo, formateo, limpieza, etc.
            return content
    except Exception as e:
        print(f"Error preprocesando archivo {file_path}: {str(e)}")
        return None

def process_files():
    """Procesa los archivos existentes en databd"""
    print(f"Iniciando preprocesamiento de datos para {CURRENT_DATE}...")
    
    try:
        folders = create_folder_structure()
        files_processed = {
            "texto": 0,
            "audio": 0,
            "imagen": 0
        }
        errors = 0

        # Procesar archivos de texto
        texto_path = os.path.join(DATA_BD_PATH, "texto")
        if os.path.exists(texto_path):
            for filename in os.listdir(texto_path):
                try:
                    source_path = os.path.join(texto_path, filename)
                    if os.path.isfile(source_path):
                        # Preprocesar y guardar el archivo
                        content = preprocess_text_file(source_path)
                        if content:
                            dest_path = os.path.join(folders["texto"], filename)
                            with open(dest_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            files_processed["texto"] += 1
                            print(f"Archivo procesado: {filename}")
                except Exception as e:
                    errors += 1
                    print(f"Error procesando {filename}: {str(e)}")

        # Copiar archivos de audio e imagen (sin preprocesamiento por ahora)
        for media_type in ["audio", "imagen"]:
            source_dir = os.path.join(DATA_BD_PATH, media_type)
            if os.path.exists(source_dir):
                for filename in os.listdir(source_dir):
                    try:
                        source_path = os.path.join(source_dir, filename)
                        if os.path.isfile(source_path):
                            dest_path = os.path.join(folders[media_type], filename)
                            shutil.copy2(source_path, dest_path)
                            files_processed[media_type] += 1
                            print(f"Archivo copiado: {filename}")
                    except Exception as e:
                        errors += 1
                        print(f"Error copiando {filename}: {str(e)}")

        # Resumen del procesamiento
        print("\nResumen del preprocesamiento:")
        print(f"Archivos de texto procesados: {files_processed['texto']}")
        print(f"Archivos de audio copiados: {files_processed['audio']}")
        print(f"Archivos de imagen copiados: {files_processed['imagen']}")
        print(f"Errores encontrados: {errors}")
        print(f"\nLos archivos preprocesados se encuentran en: {CURRENT_PREPROCESSED_PATH}")

    except Exception as e:
        print(f"Error durante el preprocesamiento: {str(e)}")
        raise

def main():
    """Función principal"""
    try:
        process_files()
    except Exception as e:
        print(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    main()
