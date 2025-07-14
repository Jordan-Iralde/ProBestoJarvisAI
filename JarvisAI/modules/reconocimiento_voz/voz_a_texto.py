import speech_recognition as sr

def capturar_voz(timeout=3, phrase_time_limit=10, idioma="es-AR"):
    """Captura audio del micrófono y retorna texto. Retorna '' si falla."""
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎙️ Escuchando...")
            r.adjust_for_ambient_noise(source, duration=0.1)  # Reduce delay
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        texto = r.recognize_google(audio, language=idioma)
        print(f"🗣️ Dijiste: {texto}")
        return texto

    except sr.WaitTimeoutError:
        print("⏱️ No se detectó habla.")
    except sr.UnknownValueError:
        print("😕 No se pudo entender el audio.")
    except sr.RequestError as e:
        print(f"❌ Error al conectar con el servicio: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    return ""
