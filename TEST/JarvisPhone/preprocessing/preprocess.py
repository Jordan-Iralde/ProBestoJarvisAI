import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_preprocess_data(file_path):
    # Cargar el archivo CSV
    data = pd.read_csv(file_path)
    
    # Renombrar la columna si es necesario
    if '2urvived' in data.columns:
        data = data.rename(columns={'2urvived': 'Survived'})
    
    # Asegurarse de que la columna 'Survived' existe
    if 'Survived' not in data.columns:
        raise KeyError("Column 'Survived' not found in the data")
    
    # Separar características (X) y etiquetas (y)
    X = data.drop('Survived', axis=1)
    y = data['Survived']
    
    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test
