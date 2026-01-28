# io/voice_pipeline.py
"""
Voice IO Pipeline for JarvisAI v0.0.4
Handles STT (Vosk) and TTS (pyttsx3) in a decoupled, non-blocking architecture.
"""

import threading
import time
from typing import Optional, Callable
from .voice.stt import VoskSTT
from .voice.tts import TTS


class VoiceIOPipeline:
    """
    Voice Input/Output Pipeline
    - STT: Vosk offline
    - TTS: pyttsx3 offline
    - Non-blocking voice loop
    - Fallback to CLI
    - Optional wake word
    """

    def __init__(self, config: dict):
        self.config = config
        self.voice_enabled = config.get("voice_enabled", False)
        self.wake_word = config.get("wake_word", "jarvis")
        self.fallback_to_cli = config.get("fallback_to_cli", True)

        # Components
        self.stt = None
        self.tts = None
        self._eventbus = None
        self._running = threading.Event()
        self._voice_thread = None

        # Callbacks
        self.on_voice_input: Optional[Callable] = None

        if self.voice_enabled:
            self._init_components()

    def _init_components(self):
        """Initialize STT and TTS components"""
        # STT
        self.stt = VoskSTT(wake_word=self.wake_word)

        # TTS
        self.tts = TTS(enabled=True)

    def set_eventbus(self, eventbus):
        """Set eventbus for communication"""
        self._eventbus = eventbus
        if self.stt:
            self.stt._bus = eventbus  # Inject eventbus into STT

    def set_voice_callback(self, callback: Callable):
        """Set callback for voice input processing"""
        self.on_voice_input = callback

    def start(self) -> bool:
        """Start the voice pipeline"""
        if not self.voice_enabled:
            return False

        if not self.stt or not self.stt.is_available():
            if self.fallback_to_cli:
                print("[WARNING] Voice STT not available, falling back to CLI")
                return False
            else:
                raise RuntimeError("Voice STT required but not available")

        self._running.set()
        self._voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
        self._voice_thread.start()

        # Start STT listening
        self.stt.start(self._eventbus)

        return True

    def _voice_loop(self):
        """Main voice processing loop (non-blocking)"""
        while self._running.is_set():
            # Voice processing happens in STT callback via eventbus
            time.sleep(0.1)  # Prevent busy loop

    def speak(self, text: str):
        """Speak text using TTS"""
        if self.tts and self.tts.enabled:
            self.tts.speak(text)
        else:
            print(f"🎤 {text}")  # Fallback to print

    def stop(self):
        """Stop the voice pipeline"""
        self._running.clear()
        if self.stt:
            self.stt.stop()
        if self._voice_thread:
            self._voice_thread.join(timeout=2.0)

    def is_voice_available(self) -> bool:
        """Check if voice components are available"""
        return self.voice_enabled and self.stt and self.stt.is_available()
