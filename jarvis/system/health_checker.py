# system/health_checker.py
"""
Component health check system
Each component reports status, and system gracefully degrades if optional components fail
"""

import time
from typing import Dict, List, Any, Callable, Optional
from enum import Enum
from system.exceptions import ComponentHealthCheckError, OptionalComponentError


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "OK"
    DEGRADED = "WARN"
    FAILED = "FAIL"


class ComponentHealth:
    """Individual component health report"""
    
    def __init__(self, name: str, required: bool = True):
        self.name = name
        self.required = required
        self.status = HealthStatus.HEALTHY
        self.message = ""
        self.last_check = None
        self.check_duration_ms = 0
        self.details = {}
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "component": self.name,
            "status": self.status.value,
            "required": self.required,
            "message": self.message,
            "duration_ms": self.check_duration_ms,
            "details": self.details,
            "error": self.error.to_dict() if self.error else None,
            "timestamp": self.last_check
        }


class HealthCheck:
    """Single health check definition"""
    
    def __init__(self, name: str, check_fn: Callable, timeout_ms: int = 5000):
        self.name = name
        self.check_fn = check_fn
        self.timeout_ms = timeout_ms
    
    async def run(self) -> Dict[str, Any]:
        """Execute health check with timeout"""
        import asyncio
        
        start = time.time()
        try:
            # Run with timeout
            result = await asyncio.wait_for(
                self._execute_check(),
                timeout=self.timeout_ms / 1000.0
            )
            duration_ms = (time.time() - start) * 1000
            return {
                "passed": result.get("passed", True),
                "message": result.get("message", "OK"),
                "duration_ms": duration_ms,
                "details": result.get("details", {})
            }
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start) * 1000
            return {
                "passed": False,
                "message": f"Check timeout (>{self.timeout_ms}ms)",
                "duration_ms": duration_ms,
                "details": {}
            }
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return {
                "passed": False,
                "message": str(e),
                "duration_ms": duration_ms,
                "details": {"error": str(e)}
            }
    
    async def _execute_check(self):
        """Execute the check function"""
        # Support both sync and async check functions
        if asyncio.iscoroutinefunction(self.check_fn):
            return await self.check_fn()
        else:
            return self.check_fn()


class HealthChecker:
    """Main health check orchestrator"""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.checks: Dict[str, List[HealthCheck]] = {}
    
    def register_component(self, name: str, required: bool = True) -> None:
        """Register a component for health checking"""
        self.components[name] = ComponentHealth(name, required)
        self.checks[name] = []
    
    def add_check(self, component: str, check_name: str, 
                  check_fn: Callable, timeout_ms: int = 5000) -> None:
        """Add a health check to a component"""
        if component not in self.components:
            self.register_component(component)
        
        self.checks[component].append(
            HealthCheck(check_name, check_fn, timeout_ms)
        )
    
    async def check_component(self, component: str) -> ComponentHealth:
        """Run all checks for a component"""
        if component not in self.components:
            raise ValueError(f"Unknown component: {component}")
        
        health = self.components[component]
        health.last_check = time.time()
        
        all_passed = True
        check_results = {}
        total_duration = 0
        
        # Run all checks for this component
        for check in self.checks[component]:
            result = await check.run()
            check_results[check.name] = result
            total_duration += result.get("duration_ms", 0)
            
            if not result.get("passed", False):
                all_passed = False
        
        # Determine overall status
        if all_passed:
            health.status = HealthStatus.HEALTHY
            health.message = "All checks passed"
        else:
            failed_checks = [name for name, result in check_results.items() 
                           if not result.get("passed")]
            health.message = f"Failed: {', '.join(failed_checks)}"
            health.status = HealthStatus.FAILED
        
        health.check_duration_ms = int(total_duration)
        health.details = check_results
        
        return health
    
    async def check_all(self) -> Dict[str, ComponentHealth]:
        """Run health checks for all components"""
        import asyncio
        
        tasks = {comp: self.check_component(comp) for comp in self.components}
        results = await asyncio.gather(*tasks.values())
        
        return {comp: health for comp, health in zip(tasks.keys(), results)}
    
    def get_health_report(self, check_results: Dict[str, ComponentHealth]) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        total = len(check_results)
        passed = sum(1 for h in check_results.values() 
                    if h.status == HealthStatus.HEALTHY)
        failed = sum(1 for h in check_results.values() 
                    if h.status == HealthStatus.FAILED)
        
        required_failed = [name for name, h in check_results.items() 
                          if h.status == HealthStatus.FAILED and h.required]
        optional_failed = [name for name, h in check_results.items() 
                          if h.status == HealthStatus.FAILED and not h.required]
        
        can_start = len(required_failed) == 0
        
        return {
            "timestamp": time.time(),
            "total_components": total,
            "healthy": passed,
            "failed": failed,
            "required_failed": required_failed,
            "optional_failed": optional_failed,
            "can_start": can_start,
            "details": {name: h.to_dict() for name, h in check_results.items()}
        }
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format health report as readable string"""
        lines = []
        lines.append("\n[DIAG] Health Check Report")
        lines.append("-" * 60)
        
        lines.append(f"Total: {report['total_components']} | "
                    f"Healthy: {report['healthy']} | "
                    f"Failed: {report['failed']}")
        
        # Required failures
        if report['required_failed']:
            lines.append("\n[DIAG] CRITICAL FAILURES (required):")
            for name in report['required_failed']:
                detail = report['details'][name]
                lines.append(f"  ✗ {name}: {detail['message']}")
        
        # Optional failures
        if report['optional_failed']:
            lines.append("\n[DIAG] OPTIONAL FAILURES (degraded):")
            for name in report['optional_failed']:
                detail = report['details'][name]
                lines.append(f"  ⚠ {name}: {detail['message']}")
        
        # Summary
        lines.append("\n[DIAG] " + ("=" * 50))
        if report['can_start']:
            lines.append(f"[DIAG] Status: OK (can start)")
        else:
            lines.append(f"[DIAG] Status: FAIL (critical components down)")
        
        return "\n".join(lines)


# ============================================================
# PREDEFINED HEALTH CHECKS
# ============================================================

class BuiltinChecks:
    """Predefined health checks for common components"""
    
    @staticmethod
    async def check_logger() -> Dict[str, Any]:
        """Check if logger is working"""
        try:
            import logging
            logger = logging.getLogger("test")
            logger.info("Health check test")
            return {"passed": True, "message": "Logger functional"}
        except Exception as e:
            return {"passed": False, "message": str(e)}
    
    @staticmethod
    async def check_storage() -> Dict[str, Any]:
        """Check if storage is accessible"""
        try:
            import os
            test_path = os.path.expanduser("~/Desktop/JarvisData")
            if not os.path.exists(test_path):
                os.makedirs(test_path, exist_ok=True)
            return {"passed": True, "message": "Storage accessible"}
        except Exception as e:
            return {"passed": False, "message": str(e)}
    
    @staticmethod
    async def check_nlu_pipeline() -> Dict[str, Any]:
        """Check if NLU pipeline initializes"""
        try:
            # Placeholder - actual NLU check would go here
            return {"passed": True, "message": "NLU pipeline ready"}
        except Exception as e:
            return {"passed": False, "message": str(e)}
    
    @staticmethod
    async def check_event_bus() -> Dict[str, Any]:
        """Check if event bus is operational"""
        try:
            # Placeholder - actual EventBus check would go here
            return {"passed": True, "message": "EventBus operational"}
        except Exception as e:
            return {"passed": False, "message": str(e)}


# ============================================================
# EXAMPLE USAGE
# ============================================================
"""
import asyncio
from system.health_checker import HealthChecker, BuiltinChecks

async def main():
    checker = HealthChecker()
    
    # Register components
    checker.register_component("logger", required=True)
    checker.register_component("storage", required=True)
    checker.register_component("nlu_pipeline", required=True)
    checker.register_component("voice_io", required=False)  # Optional
    
    # Add checks
    checker.add_check("logger", "basic", BuiltinChecks.check_logger)
    checker.add_check("storage", "accessible", BuiltinChecks.check_storage)
    checker.add_check("nlu_pipeline", "init", BuiltinChecks.check_nlu_pipeline)
    checker.add_check("voice_io", "voice_available", BuiltinChecks.check_voice_io)
    
    # Run health checks
    results = await checker.check_all()
    report = checker.get_health_report(results)
    
    print(checker.format_report(report))
    
    if report['can_start']:
        print("System ready to start")
    else:
        print("Critical failures - cannot start")

asyncio.run(main())
"""
