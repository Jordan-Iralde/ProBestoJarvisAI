# system/core/exceptions.py
"""
Custom exception classes for JarvisAI
Provides specific exception types for better error handling
"""


class JarvisException(Exception):
    """Base exception for all Jarvis errors"""
    def __init__(self, message: str, context: dict = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class BootError(JarvisException):
    """Boot sequence failed"""
    pass


class NLUError(JarvisException):
    """NLU pipeline error"""
    pass


class SkillError(JarvisException):
    """Skill execution error"""
    pass


class SkillNotFoundError(SkillError):
    """Requested skill not registered"""
    pass


class SkillTimeoutError(SkillError):
    """Skill execution timeout"""
    pass


class SkillDependencyError(SkillError):
    """Skill dependency missing or failed"""
    pass


class ConfigError(JarvisException):
    """Configuration error"""
    pass


class ConfigValidationError(ConfigError):
    """Configuration validation failed"""
    pass


class MemoryError(JarvisException):
    """Memory system error"""
    pass


class MemoryQueryError(MemoryError):
    """Memory query failed"""
    pass


class SessionError(JarvisException):
    """Session management error"""
    pass


class SessionNotFoundError(SessionError):
    """Session not found"""
    pass


class StateError(JarvisException):
    """State machine error"""
    pass


class ModeError(JarvisException):
    """Mode control error"""
    pass


class VoiceIOError(JarvisException):
    """Voice I/O error"""
    pass


class STTError(VoiceIOError):
    """Speech-to-text error"""
    pass


class TTSError(VoiceIOError):
    """Text-to-speech error"""
    pass


class InputValidationError(JarvisException):
    """Input validation error"""
    pass


class TimeoutError(JarvisException):
    """Operation timeout"""
    pass


class ComponentNotAvailableError(JarvisException):
    """Required component not available"""
    pass
