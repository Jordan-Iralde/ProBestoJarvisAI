# system/config_validator.py
"""
Strict configuration validation with schema enforcement
Prevents invalid configs from causing runtime errors
"""

import json
from typing import Dict, Any, List, Optional, Type
from system.exceptions import ConfigValidationError, MissingConfigError


class ConfigSchema:
    """Schema definition for configuration validation"""
    
    def __init__(self):
        self.rules = {}
    
    def add_field(self, name: str, field_type: Type, required: bool = False, 
                  default: Any = None, validator: callable = None, options: list = None):
        """Add a field to the schema"""
        self.rules[name] = {
            "type": field_type,
            "required": required,
            "default": default,
            "validator": validator,
            "options": options
        }
    
    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate config against schema"""
        validated = {}
        errors = []
        
        for field_name, rules in self.rules.items():
            try:
                # Check required fields
                if rules["required"] and field_name not in config:
                    raise MissingConfigError(field_name)
                
                # Get value or use default
                if field_name in config:
                    value = config[field_name]
                else:
                    value = rules["default"]
                
                # Skip if None and not required
                if value is None and not rules["required"]:
                    continue
                
                # Type checking
                if value is not None and not isinstance(value, rules["type"]):
                    raise ConfigValidationError(
                        field_name,
                        f"Expected {rules['type'].__name__}, got {type(value).__name__}",
                        {"value": value, "expected_type": rules["type"].__name__}
                    )
                
                # Options validation (enum-like)
                if rules["options"] and value is not None and value not in rules["options"]:
                    raise ConfigValidationError(
                        field_name,
                        f"Value must be one of: {rules['options']}",
                        {"value": value, "allowed": rules["options"]}
                    )
                
                # Custom validator
                if rules["validator"] and value is not None:
                    try:
                        if not rules["validator"](value):
                            raise ConfigValidationError(
                                field_name,
                                "Custom validation failed",
                                {"value": value}
                            )
                    except ConfigValidationError:
                        raise
                    except Exception as e:
                        raise ConfigValidationError(
                            field_name,
                            f"Validator error: {str(e)}",
                            {"value": value}
                        )
                
                validated[field_name] = value
            
            except (ConfigValidationError, MissingConfigError) as e:
                errors.append(e)
        
        # Return errors list for checking in validator
        if hasattr(self, '_errors'):
            self._errors = errors
        
        return validated


class ConfigValidator:
    """Main configuration validator"""
    
    @staticmethod
    def build_schema() -> ConfigSchema:
        """Build the Jarvis config schema"""
        schema = ConfigSchema()
        
        # Core settings
        schema.add_field("name", str, required=True)
        schema.add_field("version", str, required=True)
        
        # Voice settings
        schema.add_field("tts", bool, required=False, default=False)
        schema.add_field("voice_enabled", bool, required=False, default=False)
        schema.add_field("stt_language", str, required=False, default="es-ES")
        
        # System settings
        schema.add_field("data_collection", bool, required=False, default=False)
        schema.add_field("web_dashboard", bool, required=False, default=False)
        schema.add_field("workers", int, required=False, default=4,
                        validator=lambda x: 1 <= x <= 16)  # 1-16 workers
        
        # Memory settings
        schema.add_field("memory_max_size_mb", int, required=False, default=100,
                        validator=lambda x: x > 0)  # Must be positive
        schema.add_field("session_timeout_minutes", int, required=False, default=30,
                        validator=lambda x: x > 0)
        
        # NLU settings
        schema.add_field("confidence_threshold", float, required=False, default=0.5,
                        validator=lambda x: 0.0 <= x <= 1.0)  # 0-1 range
        schema.add_field("nlu_language", str, required=False, default="es")
        
        # Logging settings
        schema.add_field("log_level", str, required=False, default="INFO",
                        options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        schema.add_field("log_directory", str, required=False, default="logs")
        
        # Execution settings
        schema.add_field("skill_timeout_ms", int, required=False, default=30000,
                        validator=lambda x: x > 0)
        schema.add_field("max_retry_attempts", int, required=False, default=3,
                        validator=lambda x: x >= 0)
        
        # Debug settings
        schema.add_field("debug_mode", bool, required=False, default=False)
        schema.add_field("trace_nlu", bool, required=False, default=False)
        
        return schema
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple:
        """
        Validate config against schema
        Returns (validated_config, errors_list)
        """
        schema = ConfigValidator.build_schema()
        try:
            validated = schema.validate(config)
            return validated, []
        except (ConfigValidationError, MissingConfigError) as e:
            return config, [str(e)]
        except Exception as e:
            return config, [str(e)]
    
    @staticmethod
    def validate_from_file(filepath: str) -> Dict[str, Any]:
        """Load and validate config from JSON file"""
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            raise ConfigValidationError(
                "config.json",
                "File not found",
                {"filepath": filepath}
            )
        except json.JSONDecodeError as e:
            raise ConfigValidationError(
                "config.json",
                "Invalid JSON",
                {"error": str(e), "filepath": filepath}
            )
        
        return ConfigValidator.validate_config(config)
    
    @staticmethod
    def get_validation_errors(config: Dict[str, Any]) -> List[str]:
        """Get all validation errors without raising (for reporting)"""
        errors = []
        schema = ConfigValidator.build_schema()
        
        try:
            schema.validate(config)
        except ConfigValidationError as e:
            errors.append(f"  • {e.code}: {e.message} ({e.cause})")
        except MissingConfigError as e:
            errors.append(f"  • {e.code}: {e.message}")
        
        return errors


class SafeConfig:
    """Wrapper around validated config with fallback values"""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._schema = ConfigValidator.build_schema()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with fallback"""
        if key in self._config:
            return self._config[key]
        
        # Try schema default
        if key in self._schema.rules:
            return self._schema.rules[key]["default"]
        
        return default
    
    def get_validated(self, key: str, expected_type: Type = None) -> Any:
        """Get config value with type checking"""
        value = self.get(key)
        
        if expected_type and value is not None and not isinstance(value, expected_type):
            raise ConfigValidationError(
                key,
                f"Expected {expected_type.__name__}, got {type(value).__name__}",
                {"value": value}
            )
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Dict-like access"""
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._config
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return self._config.copy()


# ============================================================
# EXAMPLE USAGE
# ============================================================
"""
from system.config_validator import ConfigValidator, SafeConfig

# Validate from file
try:
    config_dict = ConfigValidator.validate_from_file("config.json")
    config = SafeConfig(config_dict)
    
    # Safe access with defaults
    log_level = config.get("log_level", "INFO")
    workers = config.get_validated("workers", int)
    
except ConfigValidationError as e:
    print(e.user_message())
    exit(1)
"""
