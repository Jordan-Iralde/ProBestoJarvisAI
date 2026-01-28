# system/exceptions.py
"""
Jarvis Exception Hierarchy
Specific exceptions for different domains - enables proper error handling and recovery
"""

import traceback
from typing import Optional, Dict, Any


class JarvisException(Exception):
    """Base exception for all Jarvis errors"""
    
    def __init__(self, message: str, code: str = None, context: Dict[str, Any] = None, cause: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause  # Root cause explanation
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for logging/serialization"""
        return {
            "error": self.code,
            "message": self.message,
            "cause": self.cause,
            "context": self.context,
            "type": self.__class__.__name__
        }
    
    def user_message(self) -> str:
        """Friendly message for CLI display"""
        if self.cause:
            return f"⚠️  {self.message}\n   Razón: {self.cause}"
        return f"⚠️  {self.message}"


# ============================================================
# CONFIG & VALIDATION ERRORS
# ============================================================

class ConfigError(JarvisException):
    """Configuration loading/validation error"""
    pass


class ConfigValidationError(ConfigError):
    """Config schema validation failed"""
    
    def __init__(self, field: str, error: str, context: Dict = None):
        msg = f"Config field '{field}' invalid"
        super().__init__(msg, "CONFIG_INVALID", context, f"Field: {field}\nError: {error}")


class MissingConfigError(ConfigError):
    """Required config field missing"""
    
    def __init__(self, field: str):
        msg = f"Missing required config: {field}"
        super().__init__(msg, "CONFIG_MISSING", {}, f"Set '{field}' in config.json")


# ============================================================
# NLU & INTENT ERRORS
# ============================================================

class NLUError(JarvisException):
    """Natural Language Understanding errors"""
    pass


class IntentNotRecognizedError(NLUError):
    """Intent detection failed"""
    
    def __init__(self, text: str, suggestions: list = None, confidence: float = 0.0):
        conf_str = f"(conf: {confidence:.2f})" if confidence > 0 else ""
        msg = f"Intent not recognized: '{text}' {conf_str}".strip()
        context = {
            "input": text,
            "confidence": confidence,
            "suggestions": suggestions or []
        }
        super().__init__(msg, "INTENT_UNKNOWN", context, 
                        f"Confidence too low ({confidence:.2f} < threshold)\nTry being more specific")


class EntityExtractionError(NLUError):
    """Entity extraction failed"""
    
    def __init__(self, text: str, entity_type: str, error: str):
        msg = f"Failed to extract {entity_type} from '{text}'"
        super().__init__(msg, "ENTITY_EXTRACT_FAIL", {"text": text, "entity_type": entity_type}, error)


class PipelineError(NLUError):
    """NLU pipeline processing error"""
    
    def __init__(self, stage: str, error: str):
        msg = f"NLU pipeline failed at stage: {stage}"
        super().__init__(msg, "PIPELINE_FAIL", {"stage": stage}, error)


# ============================================================
# SKILL EXECUTION ERRORS
# ============================================================

class SkillError(JarvisException):
    """Skill execution errors"""
    pass


class SkillNotFoundError(SkillError):
    """Skill not registered"""
    
    def __init__(self, skill_name: str, available: list = None):
        msg = f"Skill not found: {skill_name}"
        context = {"skill": skill_name, "available": available or []}
        super().__init__(msg, "SKILL_NOT_FOUND", context, 
                        f"Skill '{skill_name}' is not registered")


class SkillExecutionError(SkillError):
    """Skill failed during execution"""
    
    def __init__(self, skill_name: str, error: str, context: Dict = None):
        msg = f"Skill '{skill_name}' execution failed"
        ctx = context or {}
        ctx["skill"] = skill_name
        super().__init__(msg, "SKILL_EXEC_FAIL", ctx, error)


class SkillTimeoutError(SkillError):
    """Skill exceeded max execution time"""
    
    def __init__(self, skill_name: str, timeout_ms: int):
        msg = f"Skill '{skill_name}' timeout after {timeout_ms}ms"
        super().__init__(msg, "SKILL_TIMEOUT", {"skill": skill_name, "timeout_ms": timeout_ms},
                        f"Operation took too long (max: {timeout_ms}ms)")


class PreCheckError(SkillError):
    """Pre-execution check failed"""
    
    def __init__(self, skill_name: str, check_name: str, reason: str):
        msg = f"Pre-check failed for {skill_name}: {check_name}"
        super().__init__(msg, "PRECHECK_FAIL", {"skill": skill_name, "check": check_name}, reason)


# ============================================================
# RESOURCE & SYSTEM ERRORS
# ============================================================

class ResourceError(JarvisException):
    """System resource errors"""
    pass


class ComponentInitError(ResourceError):
    """Component initialization failed"""
    
    def __init__(self, component: str, error: str):
        msg = f"Failed to initialize {component}"
        super().__init__(msg, "COMPONENT_INIT_FAIL", {"component": component}, error)


class ComponentHealthCheckError(ResourceError):
    """Component failed health check"""
    
    def __init__(self, component: str, check_result: Dict):
        msg = f"Health check failed for {component}"
        super().__init__(msg, "HEALTH_CHECK_FAIL", {"component": component, "result": check_result},
                        f"Component '{component}' is not operational")


class StorageError(ResourceError):
    """Storage/persistence errors"""
    
    def __init__(self, operation: str, error: str):
        msg = f"Storage operation '{operation}' failed"
        super().__init__(msg, "STORAGE_FAIL", {"operation": operation}, error)


class PermissionError(ResourceError):
    """Permission/access errors"""
    
    def __init__(self, resource: str, operation: str, reason: str):
        msg = f"Permission denied: {operation} on {resource}"
        super().__init__(msg, "PERMISSION_DENIED", {"resource": resource, "operation": operation}, reason)


# ============================================================
# SESSION & CONTEXT ERRORS
# ============================================================

class SessionError(JarvisException):
    """Session management errors"""
    pass


class SessionNotFoundError(SessionError):
    """Session not found"""
    
    def __init__(self, session_id: str):
        msg = f"Session not found: {session_id}"
        super().__init__(msg, "SESSION_NOT_FOUND", {"session_id": session_id}, 
                        f"Session '{session_id}' does not exist or has expired")


class ContextError(JarvisException):
    """Context management errors"""
    
    def __init__(self, operation: str, error: str):
        msg = f"Context operation failed: {operation}"
        super().__init__(msg, "CONTEXT_ERROR", {"operation": operation}, error)


# ============================================================
# BOOT/INITIALIZATION ERRORS
# ============================================================

class BootError(JarvisException):
    """Boot/initialization errors - critical"""
    
    def __init__(self, message: str, context: Dict = None):
        super().__init__(
            message,
            code="BOOT_ERROR",
            context=context or {},
            cause="Boot phase failed - system cannot start"
        )


# ============================================================
# GRACEFUL DEGRADATION ERRORS (non-fatal)
# ============================================================

class DegradedError(JarvisException):
    """Feature works but in degraded mode"""
    
    def __init__(self, feature: str, fallback: str, reason: str):
        msg = f"{feature} degraded - using {fallback}"
        super().__init__(msg, "DEGRADED_MODE", {"feature": feature, "fallback": fallback}, reason)


class OptionalComponentError(ResourceError):
    """Optional component failed - system continues"""
    
    def __init__(self, component: str, error: str, fallback: str = None):
        msg = f"Optional component '{component}' unavailable"
        ctx = {"component": component, "fallback": fallback}
        super().__init__(msg, "OPTIONAL_COMPONENT_FAIL", ctx,
                        f"Using fallback: {fallback or 'none'}")


# ============================================================
# ERROR CONTEXT MANAGER
# ============================================================

class ErrorContext:
    """Contextual error tracking for debugging"""
    
    def __init__(self, operation: str, metadata: Dict = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.errors = []
        self.start_time = None
    
    def add_error(self, exc: JarvisException) -> None:
        """Track an error"""
        self.errors.append({
            "timestamp": __import__('time').time(),
            "error": exc.to_dict()
        })
    
    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return len(self.errors) > 0
    
    def get_summary(self) -> Dict:
        """Get error summary"""
        return {
            "operation": self.operation,
            "error_count": len(self.errors),
            "errors": self.errors,
            "metadata": self.metadata
        }


# ============================================================
# EXCEPTION HIERARCHY REFERENCE
# ============================================================
"""
JarvisException (base)
├─ ConfigError
│  ├─ ConfigValidationError (field invalid)
│  └─ MissingConfigError (field missing)
├─ NLUError
│  ├─ IntentNotRecognizedError (conf too low)
│  ├─ EntityExtractionError (extraction failed)
│  └─ PipelineError (stage failed)
├─ SkillError
│  ├─ SkillNotFoundError (not registered)
│  ├─ SkillExecutionError (execution failed)
│  ├─ SkillTimeoutError (execution timeout)
│  └─ PreCheckError (pre-check failed)
├─ ResourceError
│  ├─ ComponentInitError (init failed)
│  ├─ ComponentHealthCheckError (health check failed)
│  ├─ StorageError (storage operation failed)
│  ├─ PermissionError (access denied)
│  └─ OptionalComponentError (optional component failed)
├─ SessionError
│  ├─ SessionNotFoundError (session not found)
│  └─ ContextError (context operation failed)
└─ DegradedError (non-fatal, using fallback)
"""
