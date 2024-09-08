import numpy as np
import pandas as pd
import joblib
import pymongo
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import OneHotEncoder
import tkinter as tk
from tkinter import ttk
import os

# Conectar a MongoDB y obtener datos
def fetch_data_from_mongodb():
    client = pymongo.MongoClient("mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/")
    db = client["JarvisAI"]
    collection = db["web_searches"]
    
    data = pd.DataFrame(list(collection.find()))
    data.drop("_id", axis=1, inplace=True)
    
    # Convertir datos categóricos a numéricos
    categorical_cols = data.select_dtypes(include=['object']).columns
    encoder = OneHotEncoder(sparse_output=False, drop='first')  # Corregido
    encoded_features = encoder.fit_transform(data[categorical_cols])
    
    # Concatenar las características codificadas con el resto de los datos
    numerical_data = pd.concat([data.drop(columns=categorical_cols), pd.DataFrame(encoded_features)], axis=1)
    
    # Asumir que la última columna es la etiqueta
    X = numerical_data.iloc[:, :-1].values
    y = numerical_data.iloc[:, -1].values
    return X, y

# Entrenamiento del modelo
def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'model.pkl')  # Guardar el modelo
    return model

# Predicciones usando el modelo entrenado
def predict_with_model(X_test):
    if not os.path.isfile('model.pkl'):
        raise FileNotFoundError("El archivo del modelo 'model.pkl' no se encuentra.")
    
    model = joblib.load('model.pkl')  # Cargar el modelo
    predictions = model.predict(X_test)
    return predictions

# Generar y guardar código
def generate_code():
    code = """
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Cargar datos
data = pd.read_csv('data.csv')
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

# Entrenar el modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
joblib.dump(model, 'model.pkl')

# Hacer predicciones
X_test = pd.read_csv('test_data.csv').values
model = joblib.load('model.pkl')
predictions = model.predict(X_test)

# Mostrar resultados
print(predictions)
"""
    with open('generated_code.py', 'w') as f:
        f.write(code)
    return 'generated_code.py'

# Crear la interfaz gráfica
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Entrenamiento y Predicción")
        self.geometry("800x600")
        
        # Obtener datos de MongoDB
        self.X, self.y = fetch_data_from_mongodb()
        
        self.create_widgets()
        
    def create_widgets(self):
        self.train_button = ttk.Button(self, text='Iniciar Entrenamiento', command=self.start_training)
        self.train_button.pack(pady=20)
        
        self.predict_button = ttk.Button(self, text='Hacer Predicciones', command=self.start_predictions)
        self.predict_button.pack(pady=20)
        
        self.generate_code_button = ttk.Button(self, text='Generar Código', command=self.generate_code)
        self.generate_code_button.pack(pady=20)
        
        self.results_text = tk.Text(self, wrap=tk.WORD, height=20, width=80)
        self.results_text.pack(padx=10, pady=10)
        
    def start_training(self):
        self.train_button.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        
        # Dividir los datos
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        
        # Entrenar el modelo
        model = train_model(X_train, y_train)
        
        # Evaluar el modelo con validación cruzada
        scores = cross_val_score(model, self.X, self.y, cv=5, scoring='accuracy')
        avg_score = np.mean(scores)
        
        # Evaluar el modelo en el conjunto de prueba
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred)
        
        self.results_text.insert(tk.END, f"Reporte de Clasificación:\n{report}\n")
        self.results_text.insert(tk.END, f"Precisión Media de Validación Cruzada: {avg_score:.2f}\n")
        
    def start_predictions(self):
        self.predict_button.config(state=tk.DISABLED)
        
        # Usar el modelo entrenado para hacer predicciones
        X_train, X_test, _, _ = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        predictions = predict_with_model(X_test)
        
        self.results_text.insert(tk.END, f"Predicciones:\n{predictions}\n")
        
    def generate_code(self):
        self.generate_code_button.config(state=tk.DISABLED)
        
        # Generar y guardar código
        code_file = generate_code()
        
        self.results_text.insert(tk.END, f"Código generado y guardado en '{code_file}'.\n")

if __name__ == "__main__":
    print("Hola Mundo")
    app = App()
    app.mainloop()
