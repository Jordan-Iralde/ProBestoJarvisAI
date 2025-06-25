import pyttsx3

def hablar(texto: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Velocidad de habla
    engine.setProperty('voice', 'spanish')  # Puede que necesites configurar la voz
    engine.say(texto)
    engine.runAndWait()
