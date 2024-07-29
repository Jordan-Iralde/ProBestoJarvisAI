import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging

# Configuración de logging
logging.basicConfig(filename='train.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_and_prepare_data(filepath):
    try:
        # Cargar datos
        data = pd.read_csv(filepath, encoding='utf-8')
        logging.info('Data loaded successfully.')

        # Verificar y corregir nombres de columnas
        if '2urvived' in data.columns:
            data.rename(columns={'2urvived': 'Survived'}, inplace=True)
        else:
            logging.error('Expected column "Survived" not found in the data.')
            return None, None

        # Separar características y objetivo
        X = data.drop(columns=['Survived'])
        y = data['Survived']
        return X, y
    except Exception as e:
        logging.error(f'Error loading and preparing data: {e}')
        return None, None

def build_model(input_shape):
    try:
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_shape,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    except Exception as e:
        logging.error(f'Error building model: {e}')
        return None

def train_model():
    try:
        # Cargar y preparar datos
        X, y = load_and_prepare_data('JarvisPhone/data/titanic.csv')
        if X is None or y is None:
            logging.error('Data preparation failed. Exiting training.')
            return

        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Construir y entrenar el modelo
        model = build_model(X_train.shape[1])
        if model is None:
            logging.error('Model creation failed. Exiting training.')
            return

        model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))
        
        # Guardar el modelo en el formato .keras
        model.save('results/model.keras')
        logging.info('Model trained and saved successfully.')
    except Exception as e:
        logging.error(f'Error during training: {e}')

if __name__ == "__main__":
    train_model()
