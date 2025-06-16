import speech_recognition as sr

def transcribir_audio(audio, idioma="es-AR"):
    """Convierte audio a texto usando Google Speech Recognition."""
    recognizer = sr.Recognizer()
    if audio is None:
        print("⚠️ No hay audio para transcribir.")
        return None
    try:
        texto = recognizer.recognize_google(audio, language=idioma)
        print(f"🗣️ Dijiste: {texto}")
        return texto
    except sr.UnknownValueError:
        print("😕 No entendí lo que dijiste.")
        return None
    except sr.RequestError as e:
        print(f"❌ Error de servicio: {e}")
        return None
