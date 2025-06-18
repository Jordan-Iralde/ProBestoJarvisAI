import speech_recognition as sr
import pyaudio
p = pyaudio.PyAudio()

def escribir_texto():
    comando = input("ingrese texto: ")
    return comando

def capturar_voz(timeout=3, phrase_time_limit=10, idioma="es-AR"):
    if p == 0:
        """Captura audio y lo convierte a texto. Retorna string o '' si falla."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                print("🎙️ Escuchando...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                texto = r.recognize_google(audio, language=idioma)
                print(f"🗣️ Dijiste: {texto}")
                return texto
            except sr.WaitTimeoutError:
                print("⏱️ Tiempo de espera agotado.")
                return ""
            except sr.UnknownValueError:
                print("😕 No entendí lo que dijiste.")
                return ""
            except sr.RequestError as e:
                print(f"❌ Error de servicio: {e}")
                return ""
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                return ""
    else:
        escribir_texto()