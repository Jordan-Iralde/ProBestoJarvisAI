import threading
from queue import Queue, Empty
import pyttsx3
import time

class Voz:
    def __init__(self, rate=150, lang='spanish'):
        self.rate = rate
        self.lang = lang
        self._queue = Queue()
        self._tts_queue = Queue()
        self._stop = threading.Event()
        self._interrupt = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._engine = None
        self._thread.start()

    def hablar(self, text):
        self._queue.put(text)

    def hablar_interrupt(self, text):
        self._interrupt.set()
        while not self._queue.empty(): self._queue.get()
        self._queue.put(text)

    def _worker(self):
        while not self._stop.is_set():
            try:
                item = self._queue.get(timeout=0.2)
                if item: self._tts_queue.put(item)
            except Empty:
                continue

    def process_tts(self, max_messages=10):
        if not self._engine:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
            for voice in self._engine.getProperty('voices'):
                if self.lang in (getattr(voice, "name", "") or "").lower():
                    self._engine.setProperty('voice', voice.id)
                    break

        processed = 0
        while processed < max_messages and not self._tts_queue.empty():
            item = self._tts_queue.get()
            if self._interrupt.is_set():
                self._engine.stop()
                self._interrupt.clear()
            self._engine.say(item)
            self._engine.runAndWait()
            processed += 1

    def shutdown(self):
        self._stop.set()
        self._queue.put(None)
        self._thread.join()
        if self._engine:
            self._engine.stop()

voice = Voz()
