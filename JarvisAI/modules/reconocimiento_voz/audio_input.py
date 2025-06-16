import speech_recognition as sr

def obtener_audio(timeout=5, phrase_time_limit=10):
    """Captura audio desde el micrófono. Retorna objeto AudioData o None."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Escuchando...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("✅ Audio capturado.")
            return audio
        except sr.WaitTimeoutError:
            print("⏱️ Tiempo de espera agotado.")
            return None
        except Exception as e:
            print(f"❌ Error al capturar audio: {e}")
            return None
