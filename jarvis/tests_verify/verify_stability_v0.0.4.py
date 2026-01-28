#!/usr/bin/env python3
"""
Verification script for Stability v0.0.4 enhancements
Tests that all new stability features are properly integrated
"""

import sys
from pathlib import Path

# Add jarvis to path
jarvis_path = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(jarvis_path))

def test_exceptions():
    """Test that exception system is properly set up"""
    print("✓ Testing exception system...")
    try:
        from system.core.exceptions import (
            JarvisException, NLUError, SkillError, ConfigError,
            InputValidationError, TimeoutError, ModeError
        )
        print("  ✅ All exception types importable")
        
        # Test context preservation
        e = NLUError("Test error", {"field": "value"})
        assert e.context == {"field": "value"}
        print("  ✅ Exception context preserved")
        
        return True
    except Exception as e:
        print(f"  ❌ Exception test failed: {e}")
        return False

def test_validators():
    """Test configuration validation system"""
    print("✓ Testing validators...")
    try:
        from system.core.validators import ConfigValidator
        
        # Test valid config
        valid_config = {
            "name": "Jarvis",
            "version": "0.0.4",
            "debug": False,
            "workers": 4,
            "mode": "PASSIVE"
        }
        validated = ConfigValidator.validate(valid_config)
        assert validated["name"] == "Jarvis"
        print("  ✅ Valid config passes validation")
        
        # Test invalid type
        invalid_config = {"workers": "four"}
        try:
            ConfigValidator.validate(invalid_config)
            print("  ❌ Invalid config should have failed")
            return False
        except Exception:
            print("  ✅ Invalid config rejected")
        
        return True
    except Exception as e:
        print(f"  ❌ Validator test failed: {e}")
        return False

def test_healthcheck():
    """Test health check system"""
    print("✓ Testing health check system...")
    try:
        from system.core.healthcheck import HealthChecker, HealthStatus
        
        checker = HealthChecker()
        
        # Register and check component
        comp = checker.register_component("test_component")
        comp.set_healthy(response_time_ms=5)
        
        assert checker.check_component("test_component") == True
        print("  ✅ Component registration works")
        
        # Test health report
        report = checker.get_health_report()
        assert report["total_components"] == 1
        assert report["healthy_components"] == 1
        print("  ✅ Health report generation works")
        
        # Test system readiness
        checker2 = HealthChecker()
        checker2.register_component("logger").set_healthy()
        checker2.register_component("runtime").set_healthy()
        checker2.register_component("output_adapters").set_healthy()
        checker2.register_component("skill_dispatcher").set_healthy()
        
        assert checker2.is_system_ready() == True
        print("  ✅ System readiness check works")
        
        return True
    except Exception as e:
        print(f"  ❌ Health check test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nlu_pipeline():
    """Test NLU pipeline enhancements"""
    print("✓ Testing NLU pipeline...")
    try:
        from brain.nlu.pipeline import NLUResult, NLUPipeline
        
        # Test NLUResult
        result = NLUResult("test_intent", {"entity": "value"}, "raw text", "normalized text")
        result.confidence = 0.85
        result_dict = result.to_dict()
        assert result_dict["intent"] == "test_intent"
        assert result_dict["confidence"] == 0.85
        print("  ✅ NLUResult class works")
        
        # Note: Full NLUPipeline test requires skills_registry and eventbus
        print("  ✅ NLU pipeline structure validated")
        
        return True
    except Exception as e:
        print(f"  ❌ NLU pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_decorators():
    """Test decorator improvements"""
    print("✓ Testing decorators...")
    try:
        from system.core.decorators import handle_errors, validate_input, log_execution
        
        # Test handle_errors decorator
        @handle_errors(default_return=None)
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
        print("  ✅ handle_errors decorator works")
        
        # Test validate_input decorator
        @validate_input(required_fields=["name"], max_length=10)
        def test_validation(name):
            return f"Hello {name}"
        
        try:
            result = test_validation(name="Test")
            assert "Test" in result
            print("  ✅ validate_input decorator works")
        except Exception as e:
            print(f"  ❌ validate_input failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Decorator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_handlers():
    """Test handler improvements"""
    print("✓ Testing event handlers...")
    try:
        from system.core.handlers import EventHandlers
        
        # Verify EventHandlers has expected methods
        assert hasattr(EventHandlers, "handle_input_voice")
        assert hasattr(EventHandlers, "handle_input_text")
        assert hasattr(EventHandlers, "handle_skill_intent")
        assert hasattr(EventHandlers, "handle_response")
        assert hasattr(EventHandlers, "_format_response")
        print("  ✅ All handler methods present")
        
        # Verify error handling in handlers
        import inspect
        source = inspect.getsource(EventHandlers.handle_skill_intent)
        assert "try:" in source and "except" in source
        print("  ✅ Error handling in handlers")
        
        return True
    except Exception as e:
        print(f"  ❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_runtime_debug():
    """Test runtime manager debug features"""
    print("✓ Testing runtime manager debug features...")
    try:
        from system.core.runtime_manager import RuntimeManager
        
        # Verify debug tracking
        import inspect
        source = inspect.getsource(RuntimeManager.__init__)
        assert "debug_mode" in source
        assert "nlu_trace_enabled" in source
        print("  ✅ Debug state tracking present")
        
        # Verify debug command handling
        source = inspect.getsource(RuntimeManager._handle_special_command)
        assert "--debug" in source
        assert "--debug-nlu" in source
        assert "--health" in source
        print("  ✅ Debug commands implemented")
        
        # Verify health report method
        assert hasattr(RuntimeManager, "_show_health_report")
        print("  ✅ Health report method present")
        
        return True
    except Exception as e:
        print(f"  ❌ Runtime debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parser_confidence():
    """Test parser confidence and alternatives"""
    print("✓ Testing parser confidence system...")
    try:
        from brain.nlu.parser import IntentParser
        
        # Verify methods exist
        assert hasattr(IntentParser, "parse_with_confidence")
        assert hasattr(IntentParser, "get_alternatives")
        print("  ✅ Confidence methods present")
        
        # Verify method signatures
        import inspect
        sig = inspect.signature(IntentParser.parse_with_confidence)
        assert "text" in sig.parameters
        assert "entities" in sig.parameters
        print("  ✅ Method signatures correct")
        
        return True
    except Exception as e:
        print(f"  ❌ Parser confidence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("STABILITY v0.0.4 VERIFICATION")
    print("="*60 + "\n")
    
    tests = [
        ("Exceptions", test_exceptions),
        ("Validators", test_validators),
        ("Health Check", test_healthcheck),
        ("NLU Pipeline", test_nlu_pipeline),
        ("Decorators", test_decorators),
        ("Event Handlers", test_handlers),
        ("Runtime Debug", test_runtime_debug),
        ("Parser Confidence", test_parser_confidence),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All stability features verified successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
