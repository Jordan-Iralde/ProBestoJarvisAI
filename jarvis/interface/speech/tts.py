# interface/speech/tts.py
class TTS:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._engine = None

        if not self.enabled:
            return

        try:
            import pyttsx3  # optional dependency

            self._engine = pyttsx3.init()
        except Exception:
            # Si pyttsx3 no está disponible, degradar a no-op
            self.enabled = False
            self._engine = None

    def speak(self, text: str):
        if not self.enabled or not text:
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            # no-op si hay error en runtime
            return
