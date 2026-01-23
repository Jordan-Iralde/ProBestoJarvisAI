# interface/speech/stt.py
import json
import queue
import threading
import time
from typing import Optional

class VoskSTT:
    """
    STT offline con Vosk + wake word obligatoria "jarvis".
    Si Vosk no está disponible, degrada a no-op.
    """
    def __init__(self, model_path: Optional[str] = None, wake_word: str = "jarvis"):
        self.wake_word = wake_word.lower()
        self._model = None
        self._recognizer = None
        self._mic = None
        self._q = queue.Queue()
        self._thread = None
        self._running = threading.Event()

        try:
            import vosk
            import sounddevice as sd
            self.vosk = vosk
            self.sd = sd
        except Exception:
            self.vosk = None
            self.sd = None
            return

        try:
            if model_path:
                self._model = vosk.Model(model_path)
            else:
                # Intentar usar modelo preinstalado en español (vosk-model-es-0.42)
                self._model = vosk.Model("model")
        except Exception:
            self._model = None

        if self._model:
            self._recognizer = vosk.KaldiRecognizer(self._model, 16000)

    def _callback(self, indata, frames, time_info, status):
        if self._running.is_set():
            self._q.put(bytes(indata))

    def _listen_loop(self):
        try:
            with self.sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._callback
            ):
                while self._running.is_set():
                    data = self._q.get()
                    if self._recognizer.AcceptWaveform(data):
                        result = json.loads(self._recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            # Wake word obligatoria
                            if text.lower().startswith(self.wake_word):
                                # Quitar wake word del texto
                                command = text[len(self.wake_word):].strip()
                                if command:
                                    self._emit_voice_event(command)
        except Exception:
            pass

    def _emit_voice_event(self, command: str):
        # Aquí se inyectará el EventBus desde el core
        if hasattr(self, "_bus"):
            self._bus.emit("input.voice", {"text": command})

    def start(self, eventbus):
        if not self.vosk or not self._model:
            return False
        self._bus = eventbus
        self._running.set()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=2.0)

    @staticmethod
    def is_available() -> bool:
        try:
            import vosk
            import sounddevice
            return True
        except Exception:
            return False
