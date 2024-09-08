# Crear un nuevo archivo load_model.py en la carpeta models
import tensorflow as tf

def load_model(model_path):
    model = tf.keras.models.load_model(model_path)
    return model

if __name__ == "__main__":
    model = load_model('models/titanic_model.h5')
    print("Model loaded successfully")