import os
import json
import numpy as np
from datetime import datetime
import shutil
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import librosa
import cv2
from PIL import Image
import pandas as pd
from sklearn.preprocessing import StandardScaler
import re
from textblob import TextBlob
from langdetect import detect
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor
import logging
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import soundfile as sf
import threading
import traceback
from config import Config

# Descargar recursos NLTK necesarios
def download_nltk_resources():
    """Descarga los recursos necesarios de NLTK"""
    try:
        resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
                print(f"Recurso NLTK '{resource}' descargado correctamente")
            except Exception as e:
                print(f"Error descargando recurso NLTK '{resource}': {str(e)}")
    except Exception as e:
        print(f"Error general descargando recursos NLTK: {str(e)}")

# Ejecutar descarga de recursos al inicio
print("Verificando recursos NLTK...")
download_nltk_resources()

# === Configuración de rutas y constantes ===
class Config:
    def __init__(self):
        # Rutas base
        self.DESKTOP_PATH = os.path.expanduser("~/Desktop")
        self.JARVIS_DATA_PATH = os.path.join(self.DESKTOP_PATH, "jarvis_data")
        self.DATA_BD_PATH = os.path.join(self.JARVIS_DATA_PATH, "databd")
        self.PREPROCESSED_PATH = os.path.join(self.JARVIS_DATA_PATH, "preprocessed")
        self.CACHE_PATH = os.path.join(self.JARVIS_DATA_PATH, "cache")
        
        # Fecha actual
        self.CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
        self.CURRENT_PREPROCESSED_PATH = os.path.join(self.PREPROCESSED_PATH, self.CURRENT_DATE)
        
        # Crear directorios necesarios
        self.create_directories()
        
        # Configuración de logging
        self.setup_logging()

    def create_directories(self):
        """Crea todas las carpetas necesarias"""
        directories = [
            self.JARVIS_DATA_PATH,
            self.DATA_BD_PATH,
            self.PREPROCESSED_PATH,
            self.CURRENT_PREPROCESSED_PATH,
            self.CACHE_PATH
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def setup_logging(self):
        """Configura el sistema de logging con más detalle"""
        try:
            # Crear directorio para logs
            logs_dir = os.path.join(self.JARVIS_DATA_PATH, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Archivo de log
            log_file = os.path.join(
                logs_dir,
                f'jarvis_preprocessing_{self.CURRENT_DATE}.log'
            )
            
            # Configurar formato
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Handler para archivo
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # Configurar logger
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logger.handlers.clear()
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            logging.info("Sistema de logging iniciado correctamente")
            
        except Exception as e:
            print(f"Error configurando logging: {str(e)}")
            raise

class CacheManager:
    """Gestiona el caché de datos preprocesados"""
    def __init__(self, config):
        self.config = config
        self.cache_dir = config.CACHE_PATH
        self.cache = {}
        self.load_cache()

    def get_hash(self, data):
        """Genera hash único para los datos"""
        return hashlib.md5(str(data).encode()).hexdigest()

    def load_cache(self):
        """Carga caché existente"""
        cache_file = os.path.join(self.cache_dir, 'preprocessing_cache.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.cache = pickle.load(f)

    def save_cache(self):
        """Guarda caché actual"""
        cache_file = os.path.join(self.cache_dir, 'preprocessing_cache.pkl')
        with open(cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def get_cached(self, data):
        """Obtiene datos del caché si existen"""
        data_hash = self.get_hash(data)
        return self.cache.get(data_hash)

    def add_to_cache(self, data, processed_data):
        """Añade datos procesados al caché"""
        data_hash = self.get_hash(data)
        self.cache[data_hash] = processed_data
        self.save_cache()

class EmotionalFeatureExtractor:
    def __init__(self):
        # Intentar cargar el modelo de spaCy
        try:
            self.nlp = spacy.load('es_core_news_lg')
        except OSError:
            logging.warning("Modelo es_core_news_lg no encontrado. Intentando descargar...")
            try:
                os.system('python -m spacy download es_core_news_lg')
                self.nlp = spacy.load('es_core_news_lg')
            except Exception as e:
                logging.error(f"No se pudo cargar el modelo de spaCy: {str(e)}")
                try:
                    self.nlp = spacy.load('es_core_news_sm')
                except:
                    logging.error("No se pudo cargar ningún modelo de spaCy")
                    self.nlp = None
        
        self.context_memory = {}

    def extract_emotional_features(self, text):
        try:
            features = {
                "basic_analysis": TextBlob(text).sentiment.polarity
            }

            if self.nlp is not None:
                doc = self.nlp(text)
                features.update({
                    "semantic_intensity": doc.sentiment,
                    "entity_emotions": self._analyze_entity_emotions(doc),
                    "emotional_context": self._analyze_emotional_context(text)
                })
                
            return features
        except Exception as e:
            logging.error(f"Error en extracción emocional: {str(e)}")
            return {"basic_analysis": 0}

    def _analyze_entity_emotions(self, doc):
        # Implementación simplificada
        return {}

    def _analyze_emotional_context(self, text):
        # Implementación simplificada
        return {}

class AdvancedDataPreprocessor:
    def __init__(self, config=None):
        """Inicializa el preprocesador con configuración"""
        self.config = config or {}
        self.input_folders = self.config.get('data_paths', [])
        self.vectorizer = TfidfVectorizer()
        self.processed_data = None
        self.nlp = None
        self.stop_words = None
        self.max_workers = os.cpu_count() or 4
        self.setup_tools()

    def setup_tools(self):
        """Inicializa herramientas de NLP"""
        try:
            # NLTK
            for resource in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
                try:
                    nltk.download(resource, quiet=True)
                except Exception as e:
                    logging.warning(f"Error descargando {resource}: {e}")
            
            self.stop_words = set(stopwords.words('spanish') + stopwords.words('english'))
            
            # spaCy
            try:
                self.nlp = spacy.load('es_core_news_sm')
            except OSError:
                logging.warning("Descargando modelo de spaCy...")
                os.system('python -m spacy download es_core_news_sm')
                self.nlp = spacy.load('es_core_news_sm')
                
        except Exception as e:
            logging.error(f"Error en setup_tools: {e}")
            raise
        
    def analyze_text(self, text):
        """
        Analiza y vectoriza el texto usando TF-IDF y PCA.
        Retorna solo las características procesadas.
        """
        try:
            # Preprocesar el texto
            processed_text = self.preprocess_text(text)
            
            # Vectorización TF-IDF
            tfidf_features = self.vectorizer.transform([processed_text])
            
            # Aplicar PCA si es necesario
            if self.pca is not None:
                features = self.pca.transform(tfidf_features.toarray())
            else:
                features = tfidf_features.toarray()
            
            return features
            
        except Exception as e:
            logging.error(f"Error en análisis de texto: {str(e)}")
            return None

    def preprocess_text(self, text):
        """
        Preprocesa el texto aplicando varias técnicas de limpieza.
        """
        try:
            # Convertir a minúsculas
            text = text.lower()
            # Eliminar caracteres especiales y números
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\d+', '', text)
            # Tokenización y eliminación de stopwords
            tokens = word_tokenize(text)
            tokens = [token for token in tokens if token not in self.stop_words]
            # Lematización usando spaCy
            doc = self.nlp(' '.join(tokens))
            lemmatized = [token.lemma_ for token in doc]
            # Unir tokens procesados
            processed_text = ' '.join(lemmatized)
            return processed_text
        except Exception as e:
            logging.warning(f"Error en preprocesamiento de texto: {str(e)}")
            return text

    def process_files_parallel(self):
        """Procesa archivos en paralelo"""
        try:
            logging.info("Iniciando procesamiento de archivos...")
            
            for input_folder in self.input_folders:
                logging.info(f"Procesando carpeta: {input_folder}")
                
                # Obtener lista de archivos
                files = self._get_files_to_process(input_folder)
                
                # Procesar en paralelo
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(self._process_file, file) for file in files]
                    
                    # Recolectar resultados
                    for future in futures:
                        try:
                            result = future.result()
                            if result:
                                self.processed_data.extend(result)
                        except Exception as e:
                            logging.error(f"Error procesando archivo: {e}")
            
            return self.processed_data
            
        except Exception as e:
            logging.error(f"Error en procesamiento paralelo: {e}")
            raise

    def _get_files_to_process(self, folder):
        """Obtiene lista de archivos a procesar"""
        files = []
        for root, _, filenames in os.walk(folder):
            for filename in filenames:
                if filename.endswith(('.txt', '.json')):
                    files.append(os.path.join(root, filename))
        return files

    def _process_file(self, file_path):
        """Procesa un archivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Procesar según tipo de archivo
            if file_path.endswith('.json'):
                return self._process_json(content)
            else:
                return self._process_text(content)
                
        except Exception as e:
            logging.error(f"Error procesando {file_path}: {e}")
            return None

    def _process_json(self, content):
        """Procesa contenido JSON"""
        try:
            data = json.loads(content)
            # Implementar procesamiento específico para JSON
            return [self._extract_features(item) for item in data]
        except Exception as e:
            logging.error(f"Error procesando JSON: {e}")
            return None

    def _process_text(self, content):
        """Procesa contenido de texto"""
        try:
            # Preprocesar texto
            processed_text = self.preprocess_text(content)
            
            # Extraer características
            features = self._extract_features(processed_text)
            
            return [features]
        except Exception as e:
            logging.error(f"Error procesando texto: {e}")
            return None

    def _extract_features(self, text):
        """Extrae características del texto"""
        try:
            # Análisis de texto
            features = self.analyze_text(text)
            
            return {
                'text': text,
                'features': features,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error extrayendo características: {e}")
            return None

    def save_results(self, output_dir):
        """Guarda resultados procesados"""
        try:
            if not self.processed_data:
                logging.warning("No hay datos para guardar")
                return False
                
            # Crear DataFrame
            df = pd.DataFrame(self.processed_data)
            
            # Guardar en diferentes formatos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_path = os.path.join(output_dir, f"processed_data_{timestamp}")
            
            # CSV
            df.to_csv(f"{base_path}.csv", index=False)
            
            # Parquet
            df.to_parquet(f"{base_path}.parquet", index=False)  # Guardar en formato Parquet
            
            # Pickle (para mantener tipos de datos complejos)
            with open(f"{base_path}.pkl", 'wb') as f:
                pickle.dump(self.processed_data, f)
                
            logging.info(f"Datos guardados en {output_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Error guardando resultados: {e}")
            return False

    def fit_vectorizer(self, data):
        """Ajusta el vectorizador con los datos proporcionados"""
        self.vectorizer.fit(data)

    def transform_data(self, data):
        """Transforma los datos usando el vectorizador ajustado"""
        if self.vectorizer:
            self.processed_data = self.vectorizer.transform(data)
        else:
            raise ValueError("El vectorizador no está ajustado.")

def main():
    try:
        logging.info("Iniciando preprocesamiento de datos...")
        
        # Configuración
        config_instance = Config()
        preprocessor_config = {
            'data_paths': [config_instance.DATA_BD_PATH],
            'batch_size': 32,
            'max_workers': os.cpu_count() or 4
        }
        
        # Inicializar y ejecutar preprocesador
        preprocessor = AdvancedDataPreprocessor(preprocessor_config)
        preprocessor.process_files_parallel()
        
        # Guardar resultados
        preprocessor.save_results(config_instance.CURRENT_PREPROCESSED_PATH)
        
        logging.info("Preprocesamiento completado exitosamente")
        return True
        
    except Exception as e:
        logging.error(f"Error en el preprocesamiento: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
