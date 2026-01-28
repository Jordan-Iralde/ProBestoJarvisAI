# io/voice/stt.py
"""Speech-to-text implementation using Vosk"""

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

    def is_available(self) -> bool:
        """Check if STT is available and ready"""
        return self.vosk is not None and self._model is not None and self._recognizer is not None

    def _callback(self, indata, frames, time_info, status):
        if self._running.is_set():
            self._q.put(bytes(indata))

    def _listen_loop(self):
        try:
            with self.sd.RawInputStream(
                channels=1, samplerate=16000, blocksize=8000, callback=self._callback
            ):
                while self._running.is_set():
                    data = self._q.get()
                    if self._recognizer.AcceptWaveform(data):
                        result_json = self._recognizer.Result()
                        result = json.loads(result_json)
                        if "result" in result:
                            # Full result
                            text = " ".join(r["conf"] for r in result["result"])
                            if text and self.wake_word in text.lower():
                                return text
                    else:
                        partial_json = self._recognizer.PartialResult()
                        partial = json.loads(partial_json)
                        if "partial" in partial:
                            text = partial["partial"]
                            if text and self.wake_word in text.lower():
                                return text
        except Exception:
            pass

    def start(self):
        """Start listening"""
        if not self._model or not self._recognizer:
            return

        self._running.set()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop listening"""
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=1)

    def is_listening(self) -> bool:
        return self._running.is_set()
