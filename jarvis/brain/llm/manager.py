# brain/llm/manager.py
"""
LLM Manager - Local-first LLM interface with pluggable backends
Strategy pattern for easy backend switching.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    def generate(self, prompt: str, context: str) -> str:
        """Generate response from prompt and context."""
        pass


class DummyLocalLLM(LLMBackend):
    """
    Dummy local LLM using simple rules and templates.
    Replace with real local LLM (llama.cpp, ollama) when available.
    """

    def generate(self, prompt: str, context: str) -> str:
        """Generate response using basic rules."""
        prompt_lower = prompt.lower()

        # Simple rule-based responses
        if "hola" in prompt_lower or "hello" in prompt_lower:
            return "¡Hola! Soy Jarvis, tu asistente personal. ¿En qué puedo ayudarte?"

        if "como estas" in prompt_lower or "how are you" in prompt_lower:
            return "Estoy funcionando perfectamente, gracias por preguntar. ¿Qué necesitas?"

        if "ayuda" in prompt_lower or "help" in prompt_lower:
            return "Puedo ayudarte con tareas como abrir aplicaciones, consultar la hora, ver el estado del sistema, crear notas o buscar archivos. ¿Qué te gustaría hacer?"

        if "gracias" in prompt_lower or "thank" in prompt_lower:
            return "¡De nada! Estoy aquí para ayudarte cuando lo necesites."

        # Default response with context awareness
        if context:
            return f"Entiendo tu consulta sobre '{prompt}'. Basándome en nuestras conversaciones anteriores, ¿podrías darme más detalles?"
        else:
            return f"He recibido tu mensaje: '{prompt}'. Soy un asistente básico por ahora, pero puedo ayudarte con comandos específicos como 'hora', 'abrir chrome', etc."


class LLMManager:
    """
    LLM Manager with pluggable backends.
    Local-first design, no external API dependencies.
    """

    def __init__(self, backend: Optional[LLMBackend] = None):
        self.backend = backend or DummyLocalLLM()
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str, context: str = "") -> str:
        """
        Generate response using current backend.

        Args:
            prompt: User input
            context: Conversation context (optional)

        Returns:
            Generated response
        """
        try:
            self.logger.debug(f"Generating response for prompt: {prompt[:100]}...")
            if context:
                self.logger.debug(f"Context length: {len(context)} chars")

            response = self.backend.generate(prompt, context)

            self.logger.debug(f"Generated response: {response[:100]}...")
            return response

        except Exception as e:
            self.logger.error(f"LLM generation error: {e}")
            return "Lo siento, tuve un problema generando una respuesta. ¿Puedes intentarlo de nuevo?"

    def set_backend(self, backend: LLMBackend):
        """Switch LLM backend."""
        self.backend = backend
        self.logger.info(f"Switched to backend: {type(backend).__name__}")
