# system/core/healthcheck.py
"""
Health check system for JarvisCore components
Monitors component status and provides diagnostics
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class ComponentHealth:
    """Health status of a single component"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = HealthStatus.UNKNOWN
        self.last_check = None
        self.error_message = None
        self.error_count = 0
        self.last_error_time = None
        self.response_time_ms = 0
    
    def set_healthy(self, response_time_ms: int = 0):
        """Mark component as healthy"""
        self.status = HealthStatus.HEALTHY
        self.last_check = datetime.now()
        self.response_time_ms = response_time_ms
        self.error_message = None
    
    def set_degraded(self, message: str, response_time_ms: int = 0):
        """Mark component as degraded"""
        self.status = HealthStatus.DEGRADED
        self.last_check = datetime.now()
        self.error_message = message
        self.response_time_ms = response_time_ms
    
    def set_unhealthy(self, message: str):
        """Mark component as unhealthy"""
        self.status = HealthStatus.UNHEALTHY
        self.last_check = datetime.now()
        self.error_message = message
        self.error_count += 1
        self.last_error_time = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_message": self.error_message,
            "error_count": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "response_time_ms": self.response_time_ms
        }


class HealthChecker:
    """Monitors health of all JarvisCore components"""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.checks_executed = 0
        self.last_full_check = None
    
    def register_component(self, name: str) -> ComponentHealth:
        """Register a component for health monitoring"""
        if name not in self.components:
            self.components[name] = ComponentHealth(name)
        return self.components[name]
    
    def check_component(self, name: str) -> bool:
        """Check health of a single component"""
        if name not in self.components:
            return False
        
        component = self.components[name]
        return component.status == HealthStatus.HEALTHY
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health"""
        if not self.components:
            return HealthStatus.UNKNOWN
        
        statuses = [c.status for c in self.components.values()]
        
        # If any component is unhealthy, system is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        
        # If any component is degraded, system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # If all healthy
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.get_overall_health().value,
            "total_components": len(self.components),
            "healthy_components": sum(
                1 for c in self.components.values() 
                if c.status == HealthStatus.HEALTHY
            ),
            "degraded_components": sum(
                1 for c in self.components.values() 
                if c.status == HealthStatus.DEGRADED
            ),
            "unhealthy_components": sum(
                1 for c in self.components.values() 
                if c.status == HealthStatus.UNHEALTHY
            ),
            "components": [c.to_dict() for c in self.components.values()],
            "checks_executed": self.checks_executed,
            "last_full_check": self.last_full_check.isoformat() if self.last_full_check else None
        }
    
    def get_critical_issues(self) -> List[Tuple[str, str]]:
        """Get list of critical issues"""
        return [
            (c.name, c.error_message)
            for c in self.components.values()
            if c.status == HealthStatus.UNHEALTHY and c.error_message
        ]
    
    def is_system_ready(self) -> bool:
        """Check if system is ready for operation"""
        # Require these critical components
        critical = ["logger", "runtime", "output_adapters", "skill_dispatcher"]
        
        for comp_name in critical:
            if comp_name not in self.components:
                return False
            
            component = self.components[comp_name]
            if component.status == HealthStatus.UNHEALTHY:
                return False
        
        # Other components can be degraded but not unhealthy
        for component in self.components.values():
            if component.status == HealthStatus.UNHEALTHY:
                if component.name not in critical:
                    return False
        
        return True
    
    def reset(self):
        """Reset health checker"""
        self.components.clear()
        self.checks_executed = 0
        self.last_full_check = None
