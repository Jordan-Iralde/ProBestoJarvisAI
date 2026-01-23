import pickle
from pprint import pprint

PKL_PATH = "model.pkl"

with open(PKL_PATH, "rb") as f:
    modelo = pickle.load(f)

print("=== INFORMACIÓN GENERAL ===")
print("Tipo:", type(modelo))
print("Clase:", modelo.__class__.__name__)

print("\n=== HIPERPARÁMETROS ===")
pprint(modelo.get_params())

print("\n=== DATOS DEL MODELO ===")
print("Número de features:", modelo.n_features_in_)
print("Clases:", modelo.classes_)

print("\n=== ENSEMBLE ===")
if hasattr(modelo, "estimators_"):
    print("Número de árboles:", len(modelo.estimators_))
    print("Tipo de estimador base:", type(modelo.estimators_[0]))

print("\n=== IMPORTANCIA DE FEATURES ===")
pprint(modelo.feature_importances_)

print("\n=== PRUEBA DE PREDICCIÓN ===")
entrada = [[0] * modelo.n_features_in_]
print("Predicción dummy:", modelo.predict(entrada))
