# io/voice/tts.py
"""Text-to-speech implementation v0.0.4 with graceful degradation"""

import re
import logging
from typing import Optional
from system.exceptions import DegradedError, OptionalComponentError


class TTS:
    """
    Text-to-speech engine with optional pyttsx3
    Supports graceful degradation and fallback strategies
    """

    def __init__(self, enabled: bool = False, fallback_enabled: bool = True):
        """
        Initialize TTS with optional graceful degradation
        
        Args:
            enabled: Whether to enable TTS at all
            fallback_enabled: Whether to use text fallback if pyttsx3 fails
        """
        self.enabled = enabled
        self.fallback_enabled = fallback_enabled
        self._engine = None
        self._is_degraded = False
        self._error_count = 0
        self._max_errors_before_degradation = 3
        self.logger = logging.getLogger(__name__)

        if not self.enabled:
            return

        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self.logger.debug("TTS engine initialized with pyttsx3")
        except ImportError:
            self.logger.warning("pyttsx3 not installed - TTS disabled")
            self._is_degraded = True
            self.enabled = False
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            self._is_degraded = True
            self.enabled = False

    def speak(self, text: str, rate: int = 150, volume: float = 0.9) -> bool:
        """
        Speak text with error handling
        
        Args:
            text: Text to speak
            rate: Speech rate (default 150)
            volume: Volume 0.0-1.0 (default 0.9)
            
        Returns:
            bool: True if successful, False if degraded
            
        Raises:
            DegradedError: If TTS is degraded but has fallback
            OptionalComponentError: If TTS is completely unavailable
        """
        if not text or not isinstance(text, str):
            return False

        # Clean text for TTS
        text = self._sanitize_text(text)
        
        # If TTS is disabled, raise appropriate error
        if not self.enabled:
            if self._is_degraded and self.fallback_enabled:
                raise DegradedError(
                    "voice_io.tts",
                    "text_output",
                    "TTS engine not available"
                )
            else:
                raise OptionalComponentError(
                    "text_to_speech",
                    "TTS not enabled in config"
                )

        # Try to speak
        try:
            if self._engine is None:
                self._error_count += 1
                if self._error_count >= self._max_errors_before_degradation:
                    self._is_degraded = True
                    raise DegradedError(
                        "voice_io.tts",
                        "text_output",
                        "TTS engine unavailable after multiple errors"
                    )
                return False

            # Set speech properties
            try:
                self._engine.setProperty("rate", max(50, min(rate, 300)))
                self._engine.setProperty("volume", max(0.0, min(1.0, volume)))
            except Exception as e:
                self.logger.debug(f"Could not set TTS properties: {e}")

            # Speak
            self._engine.say(text)
            self._engine.runAndWait()
            
            # Reset error count on success
            self._error_count = 0
            return True

        except DegradedError:
            raise
        except OptionalComponentError:
            raise
        except Exception as e:
            self.logger.error(f"TTS speaking error: {e}")
            self._error_count += 1
            
            if self._error_count >= self._max_errors_before_degradation:
                self._is_degraded = True
                if self.fallback_enabled:
                    raise DegradedError(
                        "voice_io.tts",
                        "text_output",
                        f"TTS failed: {str(e)}"
                    )
            
            return False

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text for TTS (remove emojis, special chars, etc.)
        
        Args:
            text: Raw text
            
        Returns:
            str: Sanitized text safe for TTS
        """
        try:
            # Remove emojis
            text = text.encode('ascii', 'ignore').decode('ascii')
            
            # Remove multiple spaces
            text = re.sub(r'\s+', ' ', text)
            
            # Remove URLs
            text = re.sub(r'http[s]?://\S+', '', text)
            
            # Remove special punctuation that TTS might struggle with
            text = re.sub(r'[_\-\*\#\$\%\&\@\^\~]', ' ', text)
            
            return text.strip()
        except Exception as e:
            self.logger.debug(f"Text sanitization error: {e}")
            return text.strip()

    def set_rate(self, rate: int = 150) -> bool:
        """
        Set speech rate
        
        Args:
            rate: Rate in words per minute (50-300)
            
        Returns:
            bool: True if successful
        """
        if not self._engine:
            return False
        
        try:
            rate = max(50, min(rate, 300))
            self._engine.setProperty("rate", rate)
            return True
        except Exception as e:
            self.logger.warning(f"Could not set TTS rate: {e}")
            return False

    def set_volume(self, volume: float = 1.0) -> bool:
        """
        Set volume
        
        Args:
            volume: Volume 0.0-1.0
            
        Returns:
            bool: True if successful
        """
        if not self._engine:
            return False
        
        try:
            volume = max(0.0, min(1.0, volume))
            self._engine.setProperty("volume", volume)
            return True
        except Exception as e:
            self.logger.warning(f"Could not set TTS volume: {e}")
            return False

    def set_voice(self, voice_id: int = 0) -> bool:
        """
        Set voice
        
        Args:
            voice_id: Voice ID (0-N depending on available voices)
            
        Returns:
            bool: True if successful
        """
        if not self._engine:
            return False
        
        try:
            voices = self._engine.getProperty("voices")
            if 0 <= voice_id < len(voices):
                self._engine.setProperty("voice", voices[voice_id].id)
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Could not set TTS voice: {e}")
            return False

    def list_voices(self) -> list:
        """Get available voices"""
        if not self._engine:
            return []
        
        try:
            voices = self._engine.getProperty("voices")
            return [
                {
                    "id": i,
                    "name": v.name,
                    "languages": getattr(v, "languages", [])
                }
                for i, v in enumerate(voices)
            ]
        except Exception as e:
            self.logger.warning(f"Could not list TTS voices: {e}")
            return []

    def get_status(self) -> dict:
        """Get TTS status"""
        return {
            "enabled": self.enabled,
            "is_degraded": self._is_degraded,
            "error_count": self._error_count,
            "has_engine": self._engine is not None,
            "fallback_enabled": self.fallback_enabled,
            "voices_available": len(self.list_voices())
        }

    def reset(self) -> None:
        """Reset TTS state"""
        self._error_count = 0
        self._is_degraded = False
        try:
            if self._engine:
                self._engine.stop()
        except Exception as e:
            self.logger.debug(f"Error stopping engine: {e}")
