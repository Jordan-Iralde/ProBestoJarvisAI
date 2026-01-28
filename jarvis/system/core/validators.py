# system/core/validators.py
"""
Configuration and input validators for JarvisAI
Ensures data integrity and system stability
"""

from typing import Dict, List, Any, Optional
from .exceptions import ConfigValidationError, InputValidationError


class ConfigValidator:
    """Validates Jarvis configuration against schema"""
    
    # Configuration schema
    SCHEMA = {
        "name": {"type": str, "required": True, "default": "Jarvis"},
        "version": {"type": str, "required": True, "default": "0.0.4"},
        "debug": {"type": bool, "required": False, "default": False},
        "debug_nlu": {"type": bool, "required": False, "default": False},
        "debug_errors": {"type": bool, "required": False, "default": True},
        "voice_enabled": {"type": bool, "required": False, "default": False},
        "tts": {"type": bool, "required": False, "default": False},
        "data_collection": {"type": bool, "required": False, "default": False},
        "use_colors": {"type": bool, "required": False, "default": True},
        "short_term_memory_max": {"type": int, "required": False, "default": 20, "min": 5, "max": 100},
        "workers": {"type": int, "required": False, "default": 4, "min": 1, "max": 16},
        "crash_on_error": {"type": bool, "required": False, "default": False},
        "mode": {"type": str, "required": False, "default": "PASSIVE", "values": ["SAFE", "PASSIVE", "ACTIVE", "ANALYSIS"]},
        "wake_word": {"type": str, "required": False, "default": "jarvis", "min_length": 3, "max_length": 50},
    }
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration dictionary
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validated configuration with defaults filled in
            
        Raises:
            ConfigValidationError: If validation fails
        """
        validated = {}
        errors = []
        
        # Check required fields and types
        for key, schema_def in cls.SCHEMA.items():
            value = config.get(key)
            
            # Check required
            if schema_def.get("required", False) and value is None:
                errors.append(f"Required field missing: {key}")
                continue
            
            # Use default if missing
            if value is None:
                validated[key] = schema_def.get("default")
                continue
            
            # Check type
            expected_type = schema_def.get("type")
            if not isinstance(value, expected_type):
                errors.append(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                continue
            
            # Check numeric constraints
            if expected_type == int:
                if "min" in schema_def and value < schema_def["min"]:
                    errors.append(f"Value for '{key}' too small: {value} < {schema_def['min']}")
                    continue
                if "max" in schema_def and value > schema_def["max"]:
                    errors.append(f"Value for '{key}' too large: {value} > {schema_def['max']}")
                    continue
            
            # Check string constraints
            if expected_type == str:
                if "min_length" in schema_def and len(value) < schema_def["min_length"]:
                    errors.append(f"'{key}' too short: {len(value)} < {schema_def['min_length']}")
                    continue
                if "max_length" in schema_def and len(value) > schema_def["max_length"]:
                    errors.append(f"'{key}' too long: {len(value)} > {schema_def['max_length']}")
                    continue
                if "values" in schema_def and value not in schema_def["values"]:
                    errors.append(
                        f"Invalid value for '{key}': {value} not in {schema_def['values']}"
                    )
                    continue
            
            validated[key] = value
        
        # Check for unknown fields
        for key in config:
            if key not in cls.SCHEMA:
                # Add warning but don't fail
                validated[key] = config[key]
        
        # Raise if there were errors
        if errors:
            raise ConfigValidationError(
                f"Configuration validation failed: {len(errors)} error(s)",
                {"errors": errors}
            )
        
        return validated


class InputValidator:
    """Validates user input"""
    
    MAX_INPUT_LENGTH = 10000
    MIN_INPUT_LENGTH = 1
    
    @classmethod
    def validate_text_input(cls, text: str) -> str:
        """
        Validate text input from user
        
        Args:
            text: Input text
            
        Returns:
            Validated and cleaned text
            
        Raises:
            InputValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise InputValidationError(
                f"Input must be string, got {type(text).__name__}",
                {"input_type": type(text).__name__}
            )
        
        # Check length
        if len(text) < cls.MIN_INPUT_LENGTH:
            raise InputValidationError(
                f"Input too short: {len(text)} < {cls.MIN_INPUT_LENGTH}",
                {"length": len(text), "min": cls.MIN_INPUT_LENGTH}
            )
        
        if len(text) > cls.MAX_INPUT_LENGTH:
            raise InputValidationError(
                f"Input too long: {len(text)} > {cls.MAX_INPUT_LENGTH}",
                {"length": len(text), "max": cls.MAX_INPUT_LENGTH}
            )
        
        # Clean whitespace but preserve meaning
        cleaned = text.strip()
        
        if not cleaned:
            raise InputValidationError(
                "Input is empty after stripping whitespace",
                {"original": text, "cleaned": cleaned}
            )
        
        return cleaned
    
    @classmethod
    def validate_intent(cls, intent: str) -> str:
        """Validate intent name"""
        if not isinstance(intent, str):
            raise InputValidationError(f"Intent must be string, got {type(intent).__name__}")
        
        if not intent or len(intent) < 2:
            raise InputValidationError(f"Intent too short: '{intent}'")
        
        # Intent should be lowercase with underscores
        if not all(c.isalnum() or c == '_' for c in intent):
            raise InputValidationError(
                f"Intent contains invalid characters: {intent}",
                {"valid_characters": "alphanumeric and underscore"}
            )
        
        return intent.lower()
    
    @classmethod
    def validate_entities(cls, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entities dictionary"""
        if not isinstance(entities, dict):
            raise InputValidationError(f"Entities must be dict, got {type(entities).__name__}")
        
        # Max entity count
        if len(entities) > 50:
            raise InputValidationError(
                f"Too many entities: {len(entities)} > 50",
                {"count": len(entities), "max": 50}
            )
        
        # Validate each entity value
        validated = {}
        for key, value in entities.items():
            if not isinstance(key, str):
                raise InputValidationError(f"Entity key must be string: {key}")
            
            # Allow str, int, float, bool, list, dict
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise InputValidationError(
                    f"Invalid entity value type for '{key}': {type(value).__name__}",
                    {"entity": key, "type": type(value).__name__}
                )
            
            validated[key] = value
        
        return validated


class StateValidator:
    """Validates state transitions"""
    
    VALID_STATES = {"INIT", "BOOTING", "READY", "RUNNING", "STOPPING", "STOPPED"}
    
    @classmethod
    def validate_state(cls, state: str) -> bool:
        """Check if state is valid"""
        return state in cls.VALID_STATES
    
    @classmethod
    def validate_transition(cls, from_state: str, to_state: str) -> bool:
        """Check if state transition is valid"""
        valid_transitions = {
            "INIT": {"BOOTING"},
            "BOOTING": {"READY", "STOPPED"},
            "READY": {"RUNNING", "STOPPING"},
            "RUNNING": {"READY", "STOPPING"},
            "STOPPING": {"STOPPED"},
            "STOPPED": {"INIT"}
        }
        
        if from_state not in valid_transitions:
            return False
        
        return to_state in valid_transitions[from_state]
