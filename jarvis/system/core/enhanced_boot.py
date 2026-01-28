# system/core/enhanced_boot.py
"""
Enhanced Boot Manager for v0.0.4 Release
Integrates exception handling, config validation, health checks, and graceful degradation
"""

import time
import logging
from typing import Dict, List, Tuple, Optional

from system.exceptions import (
    BootError, ConfigError, JarvisException, DegradedError
)
from system.config_validator import ConfigValidator, SafeConfig
from system.health_checker import HealthChecker, HealthStatus
from system.graceful_degradation import DegradationManager


class BootPhase:
    """Boot phase definitions"""
    CONFIG_VALIDATION = "config_validation"
    LOGGING = "logging"
    RUNTIME = "runtime"
    COMPONENTS = "components"
    SKILLS = "skills"
    NLU = "nlu"
    HEALTH_CHECK = "health_check"
    FINALIZATION = "finalization"


class EnhancedBootManager:
    """
    Enhanced boot manager with structured phases and error handling
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("JarvisCore.Boot")
        self.phases_completed = []
        self.phases_failed = []
        self.components_registry = {}
        self.degradation_manager = DegradationManager()
        self.health_checker = HealthChecker()
        self.boot_start_time = time.time()
    
    async def boot(self, core_instance, config: Dict) -> Tuple[bool, Dict]:
        """
        Execute enhanced boot sequence
        
        Args:
            core_instance: JarvisCore instance to boot
            config: Configuration dictionary
            
        Returns:
            tuple: (success: bool, report: Dict with boot info)
        """
        boot_report = {
            "timestamp": time.time(),
            "phases": {},
            "components_ok": [],
            "components_failed": [],
            "warnings": [],
            "can_start": True,
            "boot_time_ms": 0
        }
        
        try:
            # PHASE 1: Config Validation
            await self._boot_phase_config_validation(config, boot_report)
            
            # PHASE 2: Logging
            await self._boot_phase_logging(core_instance, boot_report)
            
            # PHASE 3: Runtime
            await self._boot_phase_runtime(core_instance, boot_report)
            
            # PHASE 4: Components
            await self._boot_phase_components(core_instance, boot_report)
            
            # PHASE 5: Skills Registration
            await self._boot_phase_skills(core_instance, boot_report)
            
            # PHASE 6: NLU Pipeline
            await self._boot_phase_nlu(core_instance, boot_report)
            
            # PHASE 7: Health Checks
            await self._boot_phase_health_check(core_instance, boot_report)
            
            # PHASE 8: Finalization
            await self._boot_phase_finalization(core_instance, boot_report)
            
        except BootError as e:
            self.logger.error(f"Critical boot error: {e.user_message()}")
            boot_report["can_start"] = False
            boot_report["error"] = {
                "code": e.code,
                "message": e.user_message(),
                "phase": self.phases_completed[-1] if self.phases_completed else "unknown"
            }
            return False, boot_report
        
        except Exception as e:
            self.logger.error(f"Unexpected boot error: {e}")
            boot_report["can_start"] = False
            boot_report["error"] = {
                "code": "BOOT_UNEXPECTED_ERROR",
                "message": str(e),
                "phase": self.phases_completed[-1] if self.phases_completed else "unknown"
            }
            return False, boot_report
        
        finally:
            boot_report["boot_time_ms"] = int((time.time() - self.boot_start_time) * 1000)
            boot_report["phases"] = {
                "completed": self.phases_completed,
                "failed": self.phases_failed
            }
        
        return True, boot_report
    
    async def _boot_phase_config_validation(self, config: Dict, report: Dict) -> None:
        """Phase 1: Validate configuration"""
        phase = BootPhase.CONFIG_VALIDATION
        
        try:
            self.logger.info("→ Phase 1: Config Validation")
            
            validated_config, errors = ConfigValidator.validate_config(config)
            
            if errors:
                self.logger.warning(f"  Config validation found {len(errors)} issues")
                report["warnings"].extend(errors)
            
            self.phases_completed.append(phase)
            report["phases"][phase] = {"status": "ok", "errors": len(errors)}
            
        except ConfigError as e:
            raise BootError(f"Config validation failed: {e.user_message()}", {
                "phase": phase,
                "original_error": str(e)
            })
    
    async def _boot_phase_logging(self, core, report: Dict) -> None:
        """Phase 2: Initialize logging"""
        phase = BootPhase.LOGGING
        
        try:
            self.logger.info("→ Phase 2: Logging System")
            
            if not hasattr(core, 'logger') or core.logger is None:
                raise BootError("Logger not initialized", {"phase": phase})
            
            self.components_registry["logger"] = {
                "status": "ok",
                "type": "required",
                "version": getattr(core.logger, "version", "unknown")
            }
            
            self.phases_completed.append(phase)
            report["components_ok"].append("logger")
            report["phases"][phase] = {"status": "ok"}
            
        except Exception as e:
            raise BootError(f"Logger initialization failed: {str(e)}", {
                "phase": phase
            })
    
    async def _boot_phase_runtime(self, core, report: Dict) -> None:
        """Phase 3: Initialize runtime (EventBus, Scheduler)"""
        phase = BootPhase.RUNTIME
        
        try:
            self.logger.info("→ Phase 3: Runtime Components")
            
            # Check EventBus
            if not hasattr(core, 'events') or core.events is None:
                raise BootError("EventBus not initialized", {"phase": phase})
            
            self.components_registry["events"] = {
                "status": "ok",
                "type": "required",
                "workers": getattr(core.events, "workers", 0)
            }
            
            # Check Scheduler
            if not hasattr(core, 'scheduler') or core.scheduler is None:
                raise BootError("Scheduler not initialized", {"phase": phase})
            
            self.components_registry["scheduler"] = {
                "status": "ok",
                "type": "required"
            }
            
            self.phases_completed.append(phase)
            report["components_ok"].extend(["events", "scheduler"])
            report["phases"][phase] = {"status": "ok", "components": 2}
            
        except Exception as e:
            raise BootError(f"Runtime initialization failed: {str(e)}", {
                "phase": phase
            })
    
    async def _boot_phase_components(self, core, report: Dict) -> None:
        """Phase 4: Initialize optional components"""
        phase = BootPhase.COMPONENTS
        
        self.logger.info("→ Phase 4: Optional Components")
        
        components_to_check = [
            ("output", "required"),
            ("cli", "required"),
            ("voice_pipeline", "optional"),
            ("tts", "optional"),
            ("stt", "optional"),
            ("storage", "optional"),
            ("context_manager", "optional"),
            ("data_collector", "optional"),
        ]
        
        for component_name, component_type in components_to_check:
            try:
                if hasattr(core, component_name):
                    component = getattr(core, component_name)
                    if component is not None:
                        self.components_registry[component_name] = {
                            "status": "ok",
                            "type": component_type
                        }
                        report["components_ok"].append(component_name)
                        self.logger.debug(f"  ✓ {component_name} initialized")
                    else:
                        if component_type == "required":
                            raise BootError(f"{component_name} is None", {"phase": phase})
                        else:
                            report["warnings"].append(f"{component_name} not available")
                else:
                    if component_type == "required":
                        raise BootError(f"{component_name} not found", {"phase": phase})
                    else:
                        report["warnings"].append(f"{component_name} attribute not found")
                        
            except Exception as e:
                if component_type == "required":
                    raise BootError(f"{component_name} initialization failed: {str(e)}", {
                        "phase": phase
                    })
                else:
                    report["components_failed"].append({
                        "name": component_name,
                        "type": component_type,
                        "error": str(e)
                    })
                    report["warnings"].append(f"Optional {component_name} failed: {str(e)}")
        
        self.phases_completed.append(phase)
        report["phases"][phase] = {
            "status": "ok",
            "ok": len(report["components_ok"]),
            "failed": len(report["components_failed"])
        }
    
    async def _boot_phase_skills(self, core, report: Dict) -> None:
        """Phase 5: Register all skills"""
        phase = BootPhase.SKILLS
        
        try:
            self.logger.info("→ Phase 5: Skills Registration")
            
            if not hasattr(core, 'skill_dispatcher') or core.skill_dispatcher is None:
                raise BootError("SkillDispatcher not initialized", {"phase": phase})
            
            skills_count = len(core.skill_dispatcher.skills)
            self.logger.info(f"  ✓ {skills_count} skills registered")
            
            self.components_registry["skill_dispatcher"] = {
                "status": "ok",
                "type": "required",
                "skills_count": skills_count
            }
            
            self.phases_completed.append(phase)
            report["phases"][phase] = {
                "status": "ok",
                "skills_count": skills_count
            }
            
        except Exception as e:
            raise BootError(f"Skills registration failed: {str(e)}", {
                "phase": phase
            })
    
    async def _boot_phase_nlu(self, core, report: Dict) -> None:
        """Phase 6: Initialize NLU Pipeline"""
        phase = BootPhase.NLU
        
        try:
            self.logger.info("→ Phase 6: NLU Pipeline")
            
            if not hasattr(core, 'nlu') or core.nlu is None:
                raise BootError("NLU Pipeline not initialized", {"phase": phase})
            
            self.components_registry["nlu_pipeline"] = {
                "status": "ok",
                "type": "required",
                "debug": getattr(core.nlu, "debug", False)
            }
            
            # Try a test intent recognition
            try:
                test_input = "hola"
                result = core.nlu.process(test_input, core.events)
                if result and result.intent != "unknown":
                    self.logger.debug(f"  ✓ NLU test recognized: {result.intent}")
                else:
                    report["warnings"].append("NLU test didn't recognize simple input")
            except Exception as test_e:
                self.logger.debug(f"  ⚠ NLU test failed: {test_e}")
            
            self.phases_completed.append(phase)
            report["phases"][phase] = {"status": "ok"}
            
        except Exception as e:
            raise BootError(f"NLU Pipeline initialization failed: {str(e)}", {
                "phase": phase
            })
    
    async def _boot_phase_health_check(self, core, report: Dict) -> None:
        """Phase 7: Health checks on all components"""
        phase = BootPhase.HEALTH_CHECK
        
        try:
            self.logger.info("→ Phase 7: Health Checks")
            
            # Run health checks
            check_results = await self.health_checker.check_all()
            health_report = self.health_checker.get_health_report(check_results)
            
            self.logger.info(f"  ✓ {health_report['healthy']}/{health_report['total_components']} components healthy")
            
            if health_report['required_failed']:
                raise BootError(
                    f"Critical components failed: {', '.join(health_report['required_failed'])}",
                    {"phase": phase, "failed": health_report["required_failed"]}
                )
            
            if health_report['optional_failed']:
                for failed in health_report['optional_failed']:
                    report["warnings"].append(f"Optional component degraded: {failed}")
            
            self.phases_completed.append(phase)
            report["phases"][phase] = health_report
            
        except Exception as e:
            # Health check failures are not critical for boot
            self.logger.warning(f"  ⚠ Health check error: {e}")
            report["warnings"].append(f"Health check incomplete: {str(e)}")
            # Don't raise - health checks are informational
    
    async def _boot_phase_finalization(self, core, report: Dict) -> None:
        """Phase 8: Final preparation and status reporting"""
        phase = BootPhase.FINALIZATION
        
        try:
            self.logger.info("→ Phase 8: Finalization")
            
            # Wire up event handlers if not already done
            if hasattr(core, 'handlers') and core.handlers:
                self.logger.debug("  ✓ Event handlers ready")
            
            # Set boot flag
            core._boot_complete = True
            
            # Summary
            total_ok = len(report["components_ok"])
            total_failed = len(report["components_failed"])
            total_warnings = len(report["warnings"])
            
            self.logger.info(f"  ✓ Boot Complete: {total_ok} OK, {total_failed} failed, {total_warnings} warnings")
            
            if total_warnings > 0:
                self.logger.info(f"  ⚠ Warnings ({total_warnings}):")
                for warning in report["warnings"][:5]:
                    self.logger.info(f"     • {warning}")
                if len(report["warnings"]) > 5:
                    self.logger.info(f"     ... +{len(report['warnings'])-5} more")
            
            report["can_start"] = total_failed == 0
            self.phases_completed.append(phase)
            report["phases"][phase] = {"status": "ok"}
            
        except Exception as e:
            raise BootError(f"Finalization failed: {str(e)}", {
                "phase": phase
            })
    
    def get_boot_report(self) -> Dict:
        """Get formatted boot report"""
        return {
            "phases_completed": self.phases_completed,
            "phases_failed": self.phases_failed,
            "components": self.components_registry,
            "boot_time_ms": int((time.time() - self.boot_start_time) * 1000)
        }
