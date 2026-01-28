# system/core/decorators.py
"""
Decorators for JarvisAI
Provides validation, error handling, and execution monitoring
"""

import functools
import time
from typing import Any, Callable, Optional
from .exceptions import InputValidationError, TimeoutError as JarvisTimeoutError


def validate_input(required_fields: list = None, max_length: int = None):
    """
    Decorator to validate input parameters
    
    Args:
        required_fields: List of required parameter names
        max_length: Maximum length for string inputs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in kwargs and not args:
                        raise InputValidationError(
                            f"Required field missing: {field}",
                            {"function": func.__name__, "required": required_fields}
                        )
            
            # Check string length
            if max_length:
                for key, value in kwargs.items():
                    if isinstance(value, str) and len(value) > max_length:
                        raise InputValidationError(
                            f"Input too long for {key}: {len(value)} > {max_length}",
                            {"function": func.__name__, "field": key, "max": max_length}
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_errors(logger=None, default_return=None, reraise=False):
    """
    Decorator for comprehensive error handling
    
    Args:
        logger: Logger instance (optional)
        default_return: Default value if error occurs
        reraise: Whether to re-raise the exception after logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def timeout(seconds: float):
    """
    Decorator to add timeout to function execution
    
    Args:
        seconds: Timeout duration in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            if elapsed > seconds:
                raise JarvisTimeoutError(
                    f"Function {func.__name__} exceeded timeout",
                    {
                        "function": func.__name__,
                        "timeout": seconds,
                        "elapsed": round(elapsed, 3)
                    }
                )
            return result
        return wrapper
    return decorator


def log_execution(logger=None, level="info"):
    """
    Decorator to log function execution
    
    Args:
        logger: Logger instance
        level: Log level (info, debug, warning, error)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if logger:
                log_func = getattr(logger, level, logger.info)
                log_func(f"[EXEC] {func.__name__} started")
            
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                
                if logger:
                    log_func(f"[EXEC] {func.__name__} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start
                if logger:
                    logger.error(f"[EXEC] {func.__name__} failed after {elapsed:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 0.5, backoff: float = 1.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator


def require_mode(*allowed_modes):
    """
    Decorator to check if operation is allowed in current mode
    
    Args:
        allowed_modes: List of allowed modes (SAFE, PASSIVE, ACTIVE, ANALYSIS)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            from core.modes import OperationalMode
            from .exceptions import ModeError
            
            current_mode = self.core.mode_controller.current_mode if hasattr(self, 'core') else None
            
            if current_mode and current_mode not in allowed_modes:
                raise ModeError(
                    f"Operation {func.__name__} not allowed in {current_mode} mode",
                    {"function": func.__name__, "allowed_modes": allowed_modes, "current": str(current_mode)}
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
