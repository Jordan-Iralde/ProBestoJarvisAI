import pandas as pd
import numpy as np
import tensorflow as tf
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para cargar datos
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        logging.info('Data loaded successfully.')
        return data
    except Exception as e:
        logging.error(f'Error loading data: {e}')
        return None

# Función para preprocesar los datos
def preprocess_data(data):
    try:
        # Lista de columnas que el modelo espera
        columns_to_keep = [
            'Age', 'Fare', 'Sex', 'sibsp', 'Parch', 'Pclass', 'Embarked',
            'zero', 'zero.1', 'zero.2', 'zero.3', 'zero.4', 'zero.5', 'zero.6',
            'zero.7', 'zero.8', 'zero.9', 'zero.10', 'zero.11', 'zero.12', 'zero.13',
            'zero.14', 'zero.15', 'zero.16', 'zero.17', 'zero.18'
        ]

        # Asegúrate de que solo se seleccionen las columnas necesarias
        if set(columns_to_keep).issubset(data.columns):
            X = data[columns_to_keep]
        else:
            missing_cols = set(columns_to_keep) - set(data.columns)
            logging.error(f'Missing columns: {missing_cols}')
            return pd.DataFrame()

        # Verificar el número de características después de la selección
        if X.shape[1] != 27:
            logging.error(f'Error: Expected 27 features, but found {X.shape[1]}.')
            return pd.DataFrame()

        return X
    except Exception as e:
        logging.error(f'Error preprocessing data: {e}')
        return pd.DataFrame()

# Función para entrenar el modelo
def train_model():
    try:
        # Cargar datos de entrenamiento
        data = load_data(r'JarvisPhone\data\titanic.csv')
        if data is None:
            logging.error('Data loading failed. Exiting training.')
            return

        # Preprocesar datos
        X = preprocess_data(data)
        if X.empty:
            logging.error('No data available for training.')
            return

        # Definir etiquetas (asegúrate de que '2urvived' sea la etiqueta correcta)
        y = data['2urvived']

        # Definir el modelo (ajusta la arquitectura según sea necesario)
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(27,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        # Compilar el modelo
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Entrenar el modelo
        model.fit(X, y, epochs=10, batch_size=32)

        # Guardar el modelo en formato Keras (recomendado)
        model.save('results/model.keras')
        logging.info('Model trained and saved successfully.')
    except Exception as e:
        logging.error(f'Error during training: {e}')

# Función para hacer predicciones
def make_predictions():
    try:
        # Cargar el modelo
        model = tf.keras.models.load_model('results/model.keras')
        logging.info('Model loaded successfully.')

        # Obtener el número de características que el modelo espera
        input_shape = model.input_shape[1]  # Asumiendo que el modelo tiene una sola entrada
        logging.info(f'Expected input shape: {input_shape}')

        # Cargar y preparar datos
        data = load_data('JarvisPhone/data/titanic.csv')
        if data is None:
            logging.error('Data loading failed. Exiting prediction.')
            return

        # Preprocesar datos
        X = preprocess_data(data)
        if X.empty:
            logging.error('No data available for prediction.')
            return

        if X.shape[1] != input_shape:
            logging.error(f'Error: Expected input shape of {input_shape}, but got shape of {X.shape[1]}.')
            return

        # Hacer predicciones
        y_pred = model.predict(X)
        data['Predictions'] = y_pred
        print(data.head())  # Puedes ajustar esto para guardar o mostrar de la forma que prefieras
        logging.info('Predictions made successfully.')
    except Exception as e:
        logging.error(f'Error during prediction: {e}')

# Ejecutar el entrenamiento y la predicción
if __name__ == '__main__':
    train_model()
    make_predictions()
