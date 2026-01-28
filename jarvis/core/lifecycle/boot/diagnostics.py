# core/lifecycle/boot/diagnostics.py
"""
Boot Diagnostics v0.0.4
Comprehensive component health checks at startup
"""

import time
from typing import Dict, Any, Tuple


class Diagnostics:
    """
    Runs diagnostic checks on all major components
    Features:
    - Component availability checks
    - Basic functionality tests
    - Graceful degradation guidance
    - Performance monitoring
    """
    
    def __init__(self, core):
        self.core = core
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.warnings: list = []
        self.critical_failures: list = []

    def run(self) -> bool:
        """
        Run all diagnostics
        
        Returns:
            True if all critical components pass, False otherwise
        """
        self.results = {}
        self.warnings = []
        self.critical_failures = []
        
        # Critical components (must pass)
        critical_checks = [
            ("logger", self._check_logger),
            ("event_bus", self._check_eventbus),
            ("input_adapter", self._check_input),
            ("output_adapter", self._check_output),
        ]
        
        # Optional components (degradation OK)
        optional_checks = [
            ("scheduler", self._check_scheduler),
            ("voice_io", self._check_voice_io),
            ("nlu_pipeline", self._check_nlu),
            ("skill_dispatcher", self._check_skills),
        ]
        
        # Run critical checks
        for name, check_func in critical_checks:
            try:
                passed, message = check_func()
                self.results[name] = (passed, message)
                
                if not passed:
                    self.critical_failures.append((name, message))
                    self.core._log("DIAG", f"[FAIL] Critical check failed: {name} - {message}")
                else:
                    self.core._log("DIAG", f"[OK] Critical check passed: {name}")
            except Exception as e:
                self.results[name] = (False, str(e))
                self.critical_failures.append((name, str(e)))
                self.core._log("DIAG", f"[FAIL] Critical check exception: {name} - {str(e)}")
        
        # Run optional checks
        for name, check_func in optional_checks:
            try:
                passed, message = check_func()
                self.results[name] = (passed, message)
                
                if not passed:
                    self.warnings.append((name, message))
                    self.core._log("DIAG", f"[WARN] Optional component degraded: {name} - {message}")
                else:
                    self.core._log("DIAG", f"[OK] Optional component OK: {name}")
            except Exception as e:
                self.results[name] = (False, str(e))
                self.warnings.append((name, str(e)))
                self.core._log("DIAG", f"[WARN] Optional check exception: {name} - {str(e)}")
        
        # Summary
        all_passed = len(self.critical_failures) == 0
        passed_count = sum(1 for _, (p, _) in self.results.items() if p)
        total_count = len(self.results)
        
        summary = f"Diagnostics: {passed_count}/{total_count} passed"
        if self.critical_failures:
            summary += f" | {len(self.critical_failures)} critical failures"
        if self.warnings:
            summary += f" | {len(self.warnings)} warnings"
        
        self.core._log("DIAG", summary)
        
        if not all_passed:
            raise RuntimeError(f"Diagnostics failed: {self.critical_failures}")
        
        return all_passed

    def _check_logger(self) -> Tuple[bool, str]:
        """Check logger availability"""
        try:
            logger = getattr(self.core, 'logger', None)
            if not logger:
                return False, "Logger not initialized"
            
            # Test logging
            logger.logger.info("[DIAG] Logger test")
            return True, "Logger operational"
        except Exception as e:
            return False, f"Logger error: {str(e)}"

    def _check_eventbus(self) -> Tuple[bool, str]:
        """Check event bus availability"""
        try:
            eb = self.core.events
            if not eb:
                return False, "Event bus not initialized"
            
            # Test start/stop cycle if needed
            was_started = getattr(eb, "_started", False)
            if not was_started:
                eb.start()
                time.sleep(0.01)
                eb.stop()
            
            return True, "Event bus operational"
        except Exception as e:
            return False, f"Event bus error: {str(e)}"

    def _check_scheduler(self) -> Tuple[bool, str]:
        """Check scheduler availability"""
        try:
            sched = self.core.scheduler
            if not sched:
                return False, "Scheduler not initialized"
            
            was_running = getattr(sched, "_running", None) and sched._running.is_set()
            if not was_running:
                sched.start()
                time.sleep(0.01)
                sched.stop()
            
            return True, "Scheduler operational"
        except Exception as e:
            return False, f"Scheduler error: {str(e)}"

    def _check_input(self) -> Tuple[bool, str]:
        """Check input adapter availability"""
        try:
            inp = getattr(self.core, 'input', None)
            if not inp:
                return False, "Input adapter not initialized"
            
            # Check it's callable
            if not hasattr(inp, 'process_text'):
                return False, "Input adapter missing process_text method"
            
            return True, "Input adapter operational"
        except Exception as e:
            return False, f"Input adapter error: {str(e)}"

    def _check_output(self) -> Tuple[bool, str]:
        """Check output adapter availability"""
        try:
            out = getattr(self.core, 'output', None)
            if not out:
                return False, "Output adapter not initialized"
            
            # Check it's callable
            if not hasattr(out, 'send'):
                return False, "Output adapter missing send method"
            
            return True, "Output adapter operational"
        except Exception as e:
            return False, f"Output adapter error: {str(e)}"

    def _check_voice_io(self) -> Tuple[bool, str]:
        """Check voice I/O availability"""
        try:
            voice = getattr(self.core, 'voice_pipeline', None)
            if not voice:
                return False, "Voice pipeline not initialized"
            
            # Check if voice is available
            if hasattr(voice, 'is_voice_available'):
                available = voice.is_voice_available()
                if available:
                    return True, "Voice I/O available"
                else:
                    return False, "Voice I/O not available (Vosk/TTS missing)"
            
            return True, "Voice pipeline exists (availability unknown)"
        except Exception as e:
            return False, f"Voice I/O error: {str(e)}"

    def _check_nlu(self) -> Tuple[bool, str]:
        """Check NLU pipeline availability"""
        try:
            nlu = getattr(self.core, 'nlu', None)
            if not nlu:
                return False, "NLU pipeline not initialized"
            
            if not hasattr(nlu, 'process'):
                return False, "NLU pipeline missing process method"
            
            return True, "NLU pipeline operational"
        except Exception as e:
            return False, f"NLU error: {str(e)}"

    def _check_skills(self) -> Tuple[bool, str]:
        """Check skill dispatcher availability"""
        try:
            dispatcher = getattr(self.core, 'skill_dispatcher', None)
            if not dispatcher:
                return False, "Skill dispatcher not initialized"
            
            if not hasattr(dispatcher, 'dispatch'):
                return False, "Skill dispatcher missing dispatch method"
            
            skills_count = len(dispatcher.list_skills())
            if skills_count == 0:
                return False, "No skills registered"
            
            return True, f"Skill dispatcher operational ({skills_count} skills)"
        except Exception as e:
            return False, f"Skill dispatcher error: {str(e)}"

    def get_report(self) -> Dict[str, Any]:
        """Get diagnostic report"""
        return {
            "timestamp": time.time(),
            "results": self.results,
            "warnings": self.warnings,
            "critical_failures": self.critical_failures,
            "passed": sum(1 for _, (p, _) in self.results.items() if p),
            "total": len(self.results)
        }
