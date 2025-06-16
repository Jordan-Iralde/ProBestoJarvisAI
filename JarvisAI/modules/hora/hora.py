from datetime import datetime

def decir_hora():
    hora = datetime.now().strftime("%H:%M")
    return f"Son las {hora}."
