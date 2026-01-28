# system/graceful_degradation.py
"""
Graceful degradation strategies - components fail gracefully with fallbacks
Ensures Jarvis never crashes, only degrades functionality
"""

from typing import Any, Callable, Optional, TypeVar, Generic
from system.exceptions import JarvisException, DegradedError, OptionalComponentError

T = TypeVar('T')


class Fallback(Generic[T]):
    """Represents a fallback strategy for a component"""
    
    def __init__(self, name: str, default_value: T = None):
        self.name = name
        self.default_value = default_value
        self.fallback_fn: Optional[Callable] = None
        self.is_degraded = False
    
    def set_fallback_fn(self, fn: Callable[..., T]) -> 'Fallback':
        """Set a fallback function"""
        self.fallback_fn = fn
        return self
    
    async def get_value(self, primary_fn: Callable, *args, **kwargs) -> T:
        """
        Try primary function, fall back if it fails
        Returns (value, is_degraded)
        """
        try:
            result = await primary_fn(*args, **kwargs) if hasattr(primary_fn, '__await__') else primary_fn(*args, **kwargs)
            self.is_degraded = False
            return result, False
        except Exception as e:
            # Try fallback function
            if self.fallback_fn:
                try:
                    result = await self.fallback_fn(*args, **kwargs) if hasattr(self.fallback_fn, '__await__') else self.fallback_fn(*args, **kwargs)
                    self.is_degraded = True
                    return result, True
                except Exception as fallback_error:
                    # Return default
                    self.is_degraded = True
                    return self.default_value, True
            else:
                # Return default
                self.is_degraded = True
                return self.default_value, True


class DegradationStrategy:
    """Strategy for how to handle component failures"""
    
    def __init__(self, component_name: str, required: bool = True):
        self.component_name = component_name
        self.required = required
        self.fallbacks = {}
        self.degraded_features = []
    
    def add_fallback(self, feature: str, fallback: Fallback) -> None:
        """Register a fallback for a feature"""
        self.fallbacks[feature] = fallback
    
    def mark_degraded(self, feature: str, reason: str) -> DegradedError:
        """Mark a feature as degraded"""
        self.degraded_features.append(feature)
        fallback_name = self.fallbacks.get(feature, {}).name if feature in self.fallbacks else "none"
        return DegradedError(
            f"{self.component_name}.{feature}",
            fallback_name,
            reason
        )
    
    def can_continue(self) -> bool:
        """Determine if system can continue"""
        if self.required and self.degraded_features:
            return False
        return True
    
    def report(self) -> str:
        """Generate degradation report"""
        if not self.degraded_features:
            return f"[{self.component_name}] All features operational"
        
        status = "FAIL" if self.required else "WARN"
        features = ", ".join(self.degraded_features)
        required_text = "REQUIRED" if self.required else "OPTIONAL"
        return f"[{self.component_name}] {status} - Degraded: {features} ({required_text})"


class DegradationManager:
    """Manages all degradation strategies across system"""
    
    def __init__(self):
        self.strategies: Dict[str, DegradationStrategy] = {}
        self.degradation_history = []
    
    def register_strategy(self, component: str, required: bool = True) -> DegradationStrategy:
        """Register a degradation strategy for a component"""
        strategy = DegradationStrategy(component, required)
        self.strategies[component] = strategy
        return strategy
    
    def handle_error(self, component: str, feature: str, error: Exception, 
                     fallback_action: Callable = None) -> Any:
        """
        Handle an error with graceful degradation
        """
        if component not in self.strategies:
            self.register_strategy(component)
        
        strategy = self.strategies[component]
        
        # Log the degradation event
        degraded_error = strategy.mark_degraded(
            feature,
            f"Error: {str(error)}"
        )
        
        self.degradation_history.append({
            "timestamp": __import__('time').time(),
            "component": component,
            "feature": feature,
            "error": str(error),
            "degraded": True
        })
        
        # Execute fallback if provided
        if fallback_action:
            try:
                return fallback_action()
            except Exception as fallback_error:
                return None
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall degradation status"""
        all_degraded = []
        critical_failures = []
        
        for component, strategy in self.strategies.items():
            if strategy.degraded_features:
                all_degraded.append(component)
                if strategy.required:
                    critical_failures.append(component)
        
        return {
            "total_components": len(self.strategies),
            "degraded_components": len(all_degraded),
            "critical_failures": critical_failures,
            "can_continue": len(critical_failures) == 0,
            "all_degraded": all_degraded,
            "history_length": len(self.degradation_history)
        }
    
    def report(self) -> str:
        """Generate comprehensive degradation report"""
        lines = []
        lines.append("\n[DEGRADATION REPORT]")
        lines.append("-" * 60)
        
        for component, strategy in self.strategies.items():
            lines.append(strategy.report())
        
        status = self.get_status()
        lines.append("\n" + "=" * 60)
        lines.append(f"Total: {status['total_components']} | "
                    f"Degraded: {status['degraded_components']} | "
                    f"Critical: {len(status['critical_failures'])}")
        
        if status['critical_failures']:
            lines.append(f"CRITICAL FAILURES: {', '.join(status['critical_failures'])}")
        
        if status['can_continue']:
            lines.append("Status: CAN CONTINUE (with degradation)")
        else:
            lines.append("Status: CANNOT CONTINUE (critical failures)")
        
        return "\n".join(lines)


# ============================================================
# RETRY WITH EXPONENTIAL BACKOFF
# ============================================================

class RetryStrategy:
    """Retry with exponential backoff for transient failures"""
    
    def __init__(self, max_attempts: int = 3, base_delay_ms: int = 100, max_delay_ms: int = 5000):
        self.max_attempts = max_attempts
        self.base_delay_ms = base_delay_ms
        self.max_delay_ms = max_delay_ms
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retries"""
        import asyncio
        
        last_error = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < self.max_attempts:
                    # Calculate backoff delay
                    delay_ms = min(
                        self.base_delay_ms * (2 ** (attempt - 1)),
                        self.max_delay_ms
                    )
                    await asyncio.sleep(delay_ms / 1000.0)
        
        raise last_error


# ============================================================
# CIRCUIT BREAKER PATTERN
# ============================================================

from enum import Enum
from typing import Dict

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker for failing components"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.last_failure_time = None
    
    async def call(self, operation: Callable, *args, **kwargs) -> Any:
        """Call operation through circuit breaker"""
        import asyncio
        import time
        
        # Check if should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise JarvisException(
                    "Circuit breaker open - operation temporarily unavailable",
                    code="CIRCUIT_OPEN"
                )
        
        try:
            # Execute operation
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
            
            # Success - reset state if in HALF_OPEN
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = __import__('time').time()
            
            # Transition to OPEN if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise


# ============================================================
# EXAMPLE USAGE
# ============================================================
"""
from system.graceful_degradation import DegradationManager, RetryStrategy, CircuitBreaker

# Create manager
degradation = DegradationManager()
voice_strategy = degradation.register_strategy("voice_io", required=False)

# Handle voice failure
try:
    # Try to use voice
    pass
except Exception as e:
    degradation.handle_error("voice_io", "tts", e,
                            fallback_action=lambda: "text_output")

print(degradation.report())

# Retry strategy
retry = RetryStrategy(max_attempts=3)
result = await retry.execute(some_operation)

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5)
result = await breaker.call(external_api_call)
"""
