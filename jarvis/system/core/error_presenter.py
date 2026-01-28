# system/core/error_presenter.py
"""
Error Presenter v0.0.4 - Convert exceptions to user-friendly, actionable messages
Shows: Reason + What was happening + Suggestion for recovery
"""

from typing import Dict, Optional, List
from system.exceptions import JarvisException, IntentNotRecognizedError, SkillExecutionError


class ErrorPresenter:
    """
    Formats exceptions into user-friendly messages with context and suggestions
    
    Output format:
    {
        'reason': 'Why it failed (specific root cause)',
        'context': 'What was being attempted',
        'suggestion': 'How to recover or workaround',
        'user_message': 'Full user-friendly message for CLI'
    }
    """
    
    # Map exception types to user-friendly reasons
    REASON_MAP = {
        'IntentNotRecognizedError': 'No entendí lo que dijiste',
        'SkillExecutionError': 'El comando no pudo ejecutarse',
        'SkillTimeoutError': 'La operación tardó demasiado',
        'PreCheckError': 'No puedo hacer esto ahora',
        'DegradedError': 'Modo limitado activo',
        'ConfigError': 'Problema en la configuración',
        'BootError': 'Error al iniciar',
    }
    
    SUGGESTION_MAP = {
        'IntentNotRecognizedError': [
            'Probá con otro comando',
            'Di ayuda para ver opciones',
            'Sé más específico en lo que pedís'
        ],
        'SkillExecutionError': [
            'Probá nuevamente',
            'Verificá que los datos sean correctos',
            'Si persiste, reiniciá la aplicación'
        ],
        'SkillTimeoutError': [
            'Probá una operación más simple',
            'Reiniciá el sistema',
            'Reducí la cantidad de datos'
        ],
        'PreCheckError': [
            'Cambiá el modo operacional (modo PASSIVE)',
            'Verificá los permisos necesarios',
            'Intentá más tarde'
        ],
        'DegradedError': [
            'Algunas funciones están limitadas',
            'Verificá las dependencias',
            'Consultá la documentación'
        ]
    }
    
    @classmethod
    def format_error(cls, error: Exception, context: Dict = None) -> Dict:
        """
        Convert exception to formatted error info
        
        Args:
            error: The exception that occurred
            context: Additional context (intent, raw input, entities, etc)
            
        Returns:
            Dict with reason, context, suggestion, user_message
        """
        context = context or {}
        error_type = type(error).__name__
        
        reason = cls.REASON_MAP.get(error_type, 'Ocurrió un error')
        
        # Get appropriate suggestions
        suggestions = cls.SUGGESTION_MAP.get(error_type, [
            'Intentá de nuevo',
            'Consultá la documentación'
        ])
        suggestion = suggestions[0]  # Pick first suggestion
        
        # Build context description
        context_description = cls._build_context_description(error, context)
        
        # Build full user message
        user_message = cls._build_user_message(reason, context_description, suggestion)
        
        return {
            'reason': reason,
            'context': context_description,
            'suggestion': suggestion,
            'user_message': user_message,
            'error_type': error_type,
            'all_suggestions': suggestions
        }
    
    @classmethod
    def _build_context_description(cls, error: Exception, context: Dict) -> str:
        """Build a description of what was happening when error occurred"""
        descriptions = []
        
        # Add what we were trying to do
        if 'intent' in context:
            descriptions.append(f"intentaba ejecutar '{context['intent']}'")
        
        if 'raw_input' in context:
            descriptions.append(f"procesaba: '{context['raw_input']}'")
        elif 'raw' in context:
            descriptions.append(f"procesaba: '{context['raw']}'")
        
        if 'mode' in context:
            descriptions.append(f"modo: {context['mode']}")
        
        if descriptions:
            return " - ".join(descriptions).capitalize()
        
        return "procesando tu solicitud"
    
    @classmethod
    def _build_user_message(cls, reason: str, context: str, suggestion: str) -> str:
        """Build the complete user-facing error message"""
        return f"{reason}. {context}. {suggestion}."
    
    @classmethod
    def format_skill_error(cls, skill_name: str, error: Exception, 
                          input_entities: Dict = None) -> Dict:
        """Format error from skill execution"""
        context = {
            'intent': skill_name,
            'raw_input': str(input_entities) if input_entities else None
        }
        return cls.format_error(error, context)
    
    @classmethod
    def format_nlu_error(cls, raw_input: str, error: Exception) -> Dict:
        """Format error from NLU processing"""
        context = {'raw_input': raw_input}
        return cls.format_error(error, context)
    
    @classmethod
    def get_diagnostic_info(cls, error: Exception) -> str:
        """Get diagnostic information for logging"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # For Jarvis exceptions, include the payload
        if isinstance(error, JarvisException):
            payload_info = f" | payload: {error.payload}" if hasattr(error, 'payload') else ""
            return f"{error_type}: {error_msg}{payload_info}"
        
        return f"{error_type}: {error_msg}"
