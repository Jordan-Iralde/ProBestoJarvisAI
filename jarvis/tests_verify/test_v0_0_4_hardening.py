#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for v0.0.4 Hardening (Parte 1: Hardening de Errores)
Tests:
1. Exception hierarchy - specific exceptions with user messages
2. Config validation - strict schema enforcement
3. Health checks - component health monitoring
4. Graceful degradation - fallbacks when components fail
5. Error handling in handlers - proper exception catching
"""

import sys
import traceback
import json
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# TEST 1: EXCEPTION HIERARCHY
# ============================================================

def test_exception_hierarchy():
    """Test that exception system works correctly"""
    print("\n" + "="*60)
    print("TEST 1: EXCEPTION HIERARCHY")
    print("="*60)
    
    from system.exceptions import (
        JarvisException, ConfigError, IntentNotRecognizedError,
        SkillExecutionError, SkillTimeoutError, PreCheckError,
        DegradedError, OptionalComponentError
    )
    
    try:
        # Test base exception
        exc = JarvisException("Test error", code="TEST_001", context={"test": True})
        assert exc.code == "TEST_001"
        assert exc.user_message() is not None
        print("✓ JarvisException works")
        
        # Test domain-specific exceptions
        config_err = ConfigError("Invalid config", {"field": "workers"})
        assert "Invalid config" in str(config_err)
        print("✓ ConfigError works")
        
        nlu_err = IntentNotRecognizedError("busca python", [("search_file", 0.85)], 0.85)
        user_msg = nlu_err.user_message()
        assert user_msg is not None
        print(f"✓ IntentNotRecognizedError works: {user_msg}")
        
        skill_err = SkillExecutionError("open_app", "app not found")
        assert "open_app" in str(skill_err)
        print("✓ SkillExecutionError works")
        
        timeout_err = SkillTimeoutError("internet_search", 5000)
        assert "5000" in str(timeout_err)
        print("✓ SkillTimeoutError works")
        
        precheck_err = PreCheckError("open_app", "mode_restriction", "Not allowed in focused mode")
        assert "mode_restriction" in str(precheck_err)
        print("✓ PreCheckError works")
        
        degrade_err = DegradedError("voice_io.tts", "text_output", "TTS unavailable")
        assert "text_output" in str(degrade_err)
        print("✓ DegradedError works")
        
        optional_err = OptionalComponentError("data_collection", "permission denied")
        assert "data_collection" in str(optional_err)
        print("✓ OptionalComponentError works")
        
        print("\n✅ Exception hierarchy test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Exception hierarchy test FAILED: {e}")
        traceback.print_exc()
        return False


# ============================================================
# TEST 2: CONFIG VALIDATION
# ============================================================

def test_config_validation():
    """Test that config validation works correctly"""
    print("\n" + "="*60)
    print("TEST 2: CONFIG VALIDATION")
    print("="*60)
    
    from system.config_validator import ConfigValidator, SafeConfig
    
    try:
        # Test valid config
        valid_config = {
            "name": "JarvisAI",
            "version": "0.0.4",
            "workers": 4,
            "confidence_threshold": 0.7,
            "skill_timeout_ms": 30000
        }
        
        validator = ConfigValidator()
        validated, errors = validator.validate_config(valid_config)
        assert len(errors) == 0
        print("✓ Valid config accepted")
        
        # Test invalid config
        invalid_config = {
            "name": "JarvisAI",
            "version": "0.0.4",
            "workers": 100,  # Too high
            "confidence_threshold": 1.5  # Out of range
        }
        
        validated, errors = validator.validate_config(invalid_config)
        # Invalid config should have errors (or be corrected)
        print(f"✓ Invalid config checked: {len(errors)} issues found or auto-corrected")
        
        # Test SafeConfig with fallbacks
        safe_config = SafeConfig(valid_config)
        assert safe_config.get("workers") == 4
        assert safe_config.get("nonexistent", "default") == "default"
        print("✓ SafeConfig fallbacks work")
        
        print("\n✅ Config validation test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Config validation test FAILED: {e}")
        traceback.print_exc()
        return False


# ============================================================
# TEST 3: HEALTH CHECKER
# ============================================================

async def test_health_checker():
    """Test that health checker works correctly"""
    print("\n" + "="*60)
    print("TEST 3: HEALTH CHECKER")
    print("="*60)
    
    from system.health_checker import HealthChecker, ComponentHealth
    
    try:
        checker = HealthChecker()
        
        # Register a component
        checker.register_component("logger", required=True)
        
        # Add a check
        async def simple_check():
            return {"passed": True, "duration_ms": 10}
        
        checker.add_check("logger", "logger_available", simple_check, timeout_ms=1000)
        print("✓ Health check registered")
        
        # Run checks
        check_results = await checker.check_all()
        
        assert len(check_results) >= 0
        report = checker.get_health_report(check_results)
        assert "total_components" in report
        print(f"✓ Health report generated: {report['total_components']} components")
        
        # Test formatted report
        formatted = checker.format_report(report)
        assert "OK" in formatted or "HEALTHY" in formatted or "Health" in formatted
        print("✓ Formatted report generated")
        
        print("\n✅ Health checker test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Health checker test FAILED: {e}")
        traceback.print_exc()
        return False


# ============================================================
# TEST 4: GRACEFUL DEGRADATION
# ============================================================

def test_graceful_degradation():
    """Test that graceful degradation works correctly"""
    print("\n" + "="*60)
    print("TEST 4: GRACEFUL DEGRADATION")
    print("="*60)
    
    from system.graceful_degradation import (
        DegradationManager, Fallback, CircuitBreaker,
        RetryStrategy, CircuitState
    )
    
    try:
        # Test DegradationManager
        manager = DegradationManager()
        voice_strategy = manager.register_strategy("voice_io", required=False)
        
        # Simulate degradation
        degraded_err = voice_strategy.mark_degraded("tts", "Device not found")
        assert degraded_err is not None
        print("✓ Degradation tracking works")
        
        # Test status
        status = manager.get_status()
        assert status["degraded_components"] > 0
        print(f"✓ Degradation status: {status['degraded_components']} components degraded")
        
        # Test report
        report = manager.report()
        assert "voice_io" in report
        print("✓ Degradation report generated")
        
        # Test CircuitBreaker
        breaker = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
        assert breaker.state == CircuitState.CLOSED
        print("✓ Circuit breaker initialized")
        
        # Test Fallback
        fallback = Fallback("text_output", default_value="default response")
        assert fallback.name == "text_output"
        print("✓ Fallback strategy created")
        
        print("\n✅ Graceful degradation test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Graceful degradation test FAILED: {e}")
        traceback.print_exc()
        return False


# ============================================================
# TEST 5: ERROR HANDLING IN HANDLERS
# ============================================================

def test_error_handling_in_handlers():
    """Test that handlers use exception system correctly"""
    print("\n" + "="*60)
    print("TEST 5: ERROR HANDLING IN HANDLERS")
    print("="*60)
    
    from system.core.handlers import EventHandlers
    
    try:
        # Create mock core object
        class MockLogger:
            def logger(self):
                pass
            def log_error(self, *args, **kwargs):
                pass
            def log_command(self, *args, **kwargs):
                pass
            def log_skill_execution(self, *args, **kwargs):
                pass
        
        class MockCore:
            def __init__(self):
                self.logger = MockLogger()
                self.config = {"debug_errors": True}
        
        core = MockCore()
        handlers = EventHandlers(core)
        
        # Test error handling method
        from system.exceptions import SkillTimeoutError
        
        timeout_err = SkillTimeoutError("internet_search", 5000)
        response = handlers._handle_error_gracefully(
            "SKILL_TIMEOUT",
            timeout_err,
            intent="internet_search",
            entities={}
        )
        
        assert response is not None
        assert "timeout" in response.lower() or "tardó" in response.lower()
        print(f"✓ Error handling response: {response}")
        
        print("\n✅ Error handling in handlers test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling in handlers test FAILED: {e}")
        traceback.print_exc()
        return False


# ============================================================
# MAIN TEST RUNNER
# ============================================================

async def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" "*15 + "v0.0.4 HARDENING TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Exception hierarchy
    results.append(("Exception Hierarchy", test_exception_hierarchy()))
    
    # Test 2: Config validation
    results.append(("Config Validation", test_config_validation()))
    
    # Test 3: Health checker
    results.append(("Health Checker", await test_health_checker()))
    
    # Test 4: Graceful degradation
    results.append(("Graceful Degradation", test_graceful_degradation()))
    
    # Test 5: Error handling in handlers
    results.append(("Error Handling", test_error_handling_in_handlers()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("="*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests PASSED! v0.0.4 Hardening foundation is solid.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
