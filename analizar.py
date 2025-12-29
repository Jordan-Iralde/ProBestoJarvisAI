import pickle
import inspect

pkl_path = 'tu_modelo.pkl'  # cambia por el nombre real

try:
    with open(pkl_path, 'rb') as f:
        obj = pickle.load(f)
    
    print("TIPO:", type(obj).__name__)
    print("\nOBJETO COMPLETO:\n", obj)
    
    print("\nATRIBUTOS INTERNOS:")
    for name, value in inspect.getmembers(obj):
        if not name.startswith('__'):
            print(f"{name}: {type(value).__name__} → {value}")
    
    if hasattr(obj, 'predict'):
        print("\nES MODELO PREDICTIVO → prueba: obj.predict([[1, 2, 3]])")

except Exception as e:
    print("ERROR:", e)