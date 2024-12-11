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
from transformers import pipeline
from tensorflow.keras.models import load_model
from transformers import AutoTokenizer, AutoModel
import spacy
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import torch
import soundfile as sf

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
        self.nlp = spacy.load('es_core_news_lg')
        # Modificar la inicialización del modelo de emociones para usar una alternativa
        try:
            import tf_keras  # Intentar importar tf-keras primero
            self.emotion_model = pipeline("text-classification", 
                                       model="nlptown/bert-base-multilingual-uncased-emotion",
                                       framework="tf")
        except ImportError:
            logging.warning("tf-keras no encontrado, usando modelo alternativo")
            # Usar un modelo alternativo o deshabilitar esta funcionalidad
            self.emotion_model = None
        
        self.context_memory = {}
        
    def extract_emotional_features(self, text):
        """Extrae características emocionales avanzadas del texto"""
        try:
            doc = self.nlp(text)
            features = {
                "semantic_intensity": doc.sentiment,
                "entity_emotions": self._analyze_entity_emotions(doc),
                "emotional_context": self._analyze_emotional_context(text),
                "emotional_progression": self._track_emotional_changes(text)
            }
            
            # Añadir emociones solo si el modelo está disponible
            if self.emotion_model:
                features["emotions"] = self.emotion_model(text)
                
            return features
        except Exception as e:
            logging.error(f"Error en extracción emocional: {str(e)}")
            return None

class AdvancedDataPreprocessor:
    def __init__(self, input_folders, config):
        self.config = config
        self.input_folders = input_folders
        self.preprocessed_data = {
            "texto": [],
            "audio": [],
            "imagen": [],
            "metadata": {}
        }
        
        # Inicialización de herramientas
        self.setup_tools()
        
        self.emotional_extractor = EmotionalFeatureExtractor()
        self.context_memory = {}
        self.learning_patterns = {}
        
        # Nuevos modelos y herramientas
        self.word2vec_model = Word2Vec(vector_size=300, window=5, min_count=1)
        self.tfidf_vectorizer = TfidfVectorizer()
        self.pca = PCA(n_components=50)
        self.bert_tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.bert_model = AutoModel.from_pretrained('bert-base-multilingual-cased')
        
    def setup_tools(self):
        """Inicializa todas las herramientas necesarias"""
        # NLP
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('spanish') + stopwords.words('english'))
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        # Cache
        self.cache_manager = CacheManager(self.config)

    def analyze_text(self, text):
        """Análisis mejorado de texto con comprensión contextual"""
        try:
            # Análisis base existente
            base_analysis = super().analyze_text(text)
            
            # Características adicionales
            emotional_features = self.emotional_extractor.extract_emotional_features(text)
            context_features = self._analyze_context(text)
            semantic_features = self._extract_semantic_features(text)
            
            return {
                **base_analysis,
                "emotional_analysis": emotional_features,
                "context_understanding": context_features,
                "semantic_features": semantic_features,
                "adaptive_patterns": self._identify_patterns(text)
            }
        except Exception as e:
            logging.error(f"Error en análisis avanzado: {str(e)}")
            return None

    def preprocess_audio_advanced(self, audio_path):
        """Preprocesamiento de audio mejorado con características emocionales"""
        try:
            # Características base
            base_features = super().preprocess_audio_advanced(audio_path)
            
            # Características adicionales
            y, sr = librosa.load(audio_path)
            
            emotional_features = {
                "pitch_variations": librosa.feature.pitch(y=y, sr=sr),
                "emotion_probability": self._analyze_audio_emotion(y, sr),
                "voice_characteristics": self._extract_voice_features(y, sr),
                "prosodic_features": self._analyze_prosody(y, sr)
            }
            
            return {**base_features, "emotional_features": emotional_features}
        except Exception as e:
            logging.error(f"Error en preprocesamiento de audio: {str(e)}")
            return None

    def _analyze_context(self, text):
        """Analiza el contexto y mantiene memoria contextual"""
        # Implementación del análisis contextual
        pass

    def _extract_semantic_features(self, text):
        """Extrae características semánticas profundas"""
        # Implementación de extracción semántica
        pass

    def _identify_patterns(self, data):
        """Identifica patrones adaptativos en los datos"""
        # Implementación de identificación de patrones
        pass

    def preprocess_image_advanced(self, image_path):
        """Preprocesamiento avanzado de imagen"""
        try:
            # Verificar caché
            cached_result = self.cache_manager.get_cached(image_path)
            if cached_result:
                return cached_result

            img = cv2.imread(image_path)
            img = cv2.resize(img, (224, 224))
            
            # Preprocesamiento avanzado
            features = {
                "normalized": (img / 255.0).tolist(),
                "edges": cv2.Canny(img, 100, 200).tolist(),
                "histogram": cv2.calcHist([img], [0], None, [256], [0, 256]).tolist(),
                "hsv": cv2.cvtColor(img, cv2.COLOR_BGR2HSV).tolist()
            }
            
            # Guardar en caché
            self.cache_manager.add_to_cache(image_path, features)
            
            return features
        except Exception as e:
            logging.error(f"Error en preprocesamiento de imagen: {str(e)}")
            return None

    def process_files_parallel(self):
        """Procesa archivos en paralelo"""
        with ThreadPoolExecutor() as executor:
            for input_folder in self.input_folders:
                logging.info(f"Procesando carpeta: {input_folder}")
                
                for media_type in ["texto", "audio", "imagen"]:
                    type_path = os.path.join(input_folder, media_type)
                    if not os.path.exists(type_path):
                        continue
                    
                    # Procesar archivos en paralelo
                    files = [os.path.join(type_path, f) for f in os.listdir(type_path)]
                    if media_type == "texto":
                        futures = [executor.submit(self.process_text_file, f) for f in files]
                    elif media_type == "audio":
                        futures = [executor.submit(self.preprocess_audio_advanced, f) for f in files]
                    else:
                        futures = [executor.submit(self.preprocess_image_advanced, f) for f in files]
                    
                    # Recolectar resultados
                    for future in futures:
                        try:
                            result = future.result()
                            if result:
                                self.preprocessed_data[media_type].append(result)
                        except Exception as e:
                            logging.error(f"Error en procesamiento paralelo: {str(e)}")

    def save_preprocessed_data(self):
        """Guarda datos preprocesados con metadata"""
        os.makedirs(self.config.CURRENT_PREPROCESSED_PATH, exist_ok=True)
        
        # Metadata
        self.preprocessed_data["metadata"] = {
            "fecha_procesamiento": self.config.CURRENT_DATE,
            "estadisticas": {
                "total_textos": len(self.preprocessed_data["texto"]),
                "total_audios": len(self.preprocessed_data["audio"]),
                "total_imagenes": len(self.preprocessed_data["imagen"])
            },
            "configuracion": {
                "version": "2.1",
                "modelos_utilizados": ["NLTK", "TextBlob", "Librosa", "OpenCV"],
                "idiomas_soportados": ["es", "en"]
            }
        }
        
        # Guardar datos
        output_base = os.path.join(self.config.CURRENT_PREPROCESSED_PATH, "preprocessed_data")
        
        # JSON
        with open(f"{output_base}.json", 'w', encoding='utf-8') as f:
            json.dump(self.preprocessed_data, f, ensure_ascii=False, indent=2)
        
        # Pickle
        with open(f"{output_base}.pkl", 'wb') as f:
            pickle.dump(self.preprocessed_data, f)
        
        logging.info(f"Datos guardados en {self.config.CURRENT_PREPROCESSED_PATH}")
        print(f"\nPreprocesamiento completado. Archivos guardados en: {self.config.CURRENT_PREPROCESSED_PATH}")

    def extract_multimodal_features(self, text, audio, image):
        """Extrae características combinando múltiples modalidades"""
        try:
            text_features = self.analyze_text(text)
            audio_features = self.preprocess_audio_advanced(audio)
            image_features = self.preprocess_image_advanced(image)
            
            # Fusión multimodal
            return {
                "combined_features": self._fusion_multimodal(
                    text_features, 
                    audio_features, 
                    image_features
                ),
                "cross_modal_attention": self._calculate_cross_attention(
                    text_features,
                    audio_features,
                    image_features
                ),
                "modal_correlations": self._analyze_modal_correlations(
                    text_features,
                    audio_features,
                    image_features
                )
            }
        except Exception as e:
            logging.error(f"Error en extracción multimodal: {str(e)}")
            return None

    def _extract_deep_semantic_features(self, text):
        """Extracción profunda de características semánticas"""
        return {
            "word2vec": self.word2vec_model.wv.vectors.tolist(),
            "tfidf": self.tfidf_vectorizer.fit_transform([text]).toarray(),
            "bert_embeddings": self._get_bert_embeddings(text),
            "semantic_roles": self._extract_semantic_roles(text),
            "topic_modeling": self._extract_topics(text),
            "discourse_analysis": self._analyze_discourse(text)
        }

    def _analyze_audio_emotion(self, y, sr):
        """Análisis emocional avanzado de audio"""
        return {
            "mfcc": librosa.feature.mfcc(y=y, sr=sr),
            "spectral_contrast": librosa.feature.spectral_contrast(y=y, sr=sr),
            "chroma": librosa.feature.chroma_stft(y=y, sr=sr),
            "tempo": librosa.beat.tempo(y=y, sr=sr),
            "onset_strength": librosa.onset.onset_strength(y=y, sr=sr),
            "pitch_track": librosa.pitch_track(y=y, sr=sr)
        }

    def _extract_advanced_image_features(self, image):
        """Extracción avanzada de características de imagen"""
        return {
            "color_moments": self._calculate_color_moments(image),
            "texture_features": self._extract_texture_features(image),
            "shape_features": self._extract_shape_features(image),
            "deep_features": self._extract_deep_cnn_features(image),
            "spatial_relationships": self._analyze_spatial_relationships(image),
            "object_detection": self._detect_objects(image)
        }

    def _analyze_emotional_context(self, text):
        """Análisis contextual emocional profundo"""
        return {
            "emotional_flow": self._track_emotional_flow(text),
            "sentiment_transitions": self._analyze_sentiment_transitions(text),
            "emotional_triggers": self._identify_emotional_triggers(text),
            "contextual_emotions": self._analyze_contextual_emotions(text),
            "emotional_intensity": self._calculate_emotional_intensity(text)
        }

    def _fusion_multimodal(self, text_features, audio_features, image_features):
        """Fusión avanzada de características multimodales"""
        # Implementar fusión de características
        pass

    def _calculate_cross_attention(self, text_features, audio_features, image_features):
        """Cálculo de atención cruzada entre modalidades"""
        # Implementar mecanismo de atención cruzada
        pass

    def _analyze_modal_correlations(self, text_features, audio_features, image_features):
        """Análisis de correlaciones entre modalidades"""
        # Implementar análisis de correlaciones
        pass

    def _get_bert_embeddings(self, text):
        """Obtiene embeddings de BERT"""
        # Implementar extracción de embeddings
        pass

    def _extract_semantic_roles(self, text):
        """Extrae roles semánticos del texto"""
        # Implementar extracción de roles semánticos
        pass

    def _analyze_discourse(self, text):
        """Análisis del discurso"""
        # Implementar análisis de discurso
        pass

def main():
    """Función principal mejorada"""
    try:
        # Inicializar configuración
        config = Config()
        
        # Definir carpetas de entrada
        input_folders = [
            config.DATA_BD_PATH,
            # Agregar más carpetas según sea necesario
        ]
        
        # Iniciar preprocesamiento
        preprocessor = AdvancedDataPreprocessor(input_folders, config)
        preprocessor.process_files_parallel()
        preprocessor.save_preprocessed_data()
        
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
        print(f"Error crítico. Consulte el log para más detalles.")

if __name__ == "__main__":
    main()
