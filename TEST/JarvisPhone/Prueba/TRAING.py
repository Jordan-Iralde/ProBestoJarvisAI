import pymongo
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Configuración de conexión a MongoDB
client = pymongo.MongoClient("mongodb+srv://JarvisUser:2wssnlZhLTw5WuvF4@jorvisai.lrskk.mongodb.net/")
db = client["JarvisAI"]
collection = db["web_searches"]

def fetch_data():
    """Recupera datos de MongoDB."""
    cursor = collection.find({"type": "search_result"})
    return [doc['content'] for doc in cursor]

def train_model(data):
    """Entrena y guarda el modelo."""
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', MultinomialNB())
    ])
    
    # Simulación de entrenamiento; en un caso real, necesitarías etiquetas
    pipeline.fit(data, [1]*len(data))  # Usar etiquetas apropiadas
    
    # Guardar el modelo
    with open('trained_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    print("Modelo entrenado y guardado.")

if __name__ == "__main__":
    data = fetch_data()
    if data:
        train_model(data)
    else:
        print("No hay datos disponibles para entrenar el modelo.")
