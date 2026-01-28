#!/usr/bin/env python3
"""
Quick integration test for v0.0.4 core improvements
Tests key components without full boot
"""

import sys
from pathlib import Path

jarvis_path = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(jarvis_path))

def test_skill_dispatcher():
    """Test improved skill dispatcher"""
    print("🧪 Testing Skill Dispatcher...")
    try:
        from skills.actions.dispatcher import SkillDispatcher
        
        dispatcher = SkillDispatcher()
        
        # Check new methods exist
        assert hasattr(dispatcher, '_validate_skill_requirements')
        assert hasattr(dispatcher, '_record_execution')
        assert hasattr(dispatcher, 'get_execution_stats')
        assert hasattr(dispatcher, 'get_skill_performance')
        
        # Check stats
        stats = dispatcher.get_execution_stats()
        assert isinstance(stats, dict)
        
        print("  ✅ Skill Dispatcher OK")
        return True
    except Exception as e:
        print(f"  ❌ Skill Dispatcher failed: {e}")
        return False

def test_session_manager():
    """Test improved session manager"""
    print("🧪 Testing Session Manager...")
    try:
        from system.session_manager import SessionManager, Session
        from system.core.exceptions import SessionNotFoundError, ModeError
        
        mgr = SessionManager()
        
        # Create session
        sid = mgr.create_session()
        assert sid is not None
        
        # Get session
        session = mgr.get_session(sid)
        assert session is not None
        
        # Test stats
        stats = mgr.get_session_stats(sid)
        assert "session_id" in stats
        assert "duration_seconds" in stats
        
        # Test new methods
        assert hasattr(mgr, 'close_session')
        assert hasattr(mgr, 'get_all_sessions_stats')
        assert hasattr(session, 'get_duration')
        assert hasattr(session, 'is_inactive_since')
        
        # Test error handling
        try:
            mgr.get_session("invalid_id")
            print("  ❌ Should have raised SessionNotFoundError")
            return False
        except SessionNotFoundError:
            pass  # Expected
        
        print("  ✅ Session Manager OK")
        return True
    except Exception as e:
        print(f"  ❌ Session Manager failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reasoning_engine():
    """Test new reasoning engine"""
    print("🧪 Testing Reasoning Engine...")
    try:
        from brain.reasoning.engine import (
            ReasoningEngine, ReasoningResult, SimpleReasoningRules
        )
        
        engine = ReasoningEngine()
        
        # Test result class
        result = ReasoningResult("test_intent", {"entity": "value"})
        assert result.intent == "test_intent"
        assert result.valid == True
        
        # Test reasoning
        result = engine.reason("test_intent", {})
        assert result is not None
        assert hasattr(result, 'to_dict')
        
        # Test rules
        rule = SimpleReasoningRules.require_entity("test")
        assert callable(rule)
        
        # Test stats
        stats = engine.get_reasoning_stats()
        assert "total_reasonings" in stats
        
        print("  ✅ Reasoning Engine OK")
        return True
    except Exception as e:
        print(f"  ❌ Reasoning Engine failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_manager():
    """Test improved context manager"""
    print("🧪 Testing Context Manager...")
    try:
        from brain.memory.storage import JarvisStorage
        from brain.memory.context import ContextManager
        
        # Use in-memory for testing (or temp file)
        storage = JarvisStorage(":memory:")
        manager = ContextManager(storage)
        
        # Test basic context
        context = manager.get_context()
        assert isinstance(context, str)
        
        # Test new methods
        assert hasattr(manager, 'get_recent_intents')
        assert hasattr(manager, 'get_context_summary')
        assert hasattr(manager, 'clear_cache')
        
        # Test summary
        summary = manager.get_context_summary()
        assert "total_interactions" in summary
        
        print("  ✅ Context Manager OK")
        return True
    except Exception as e:
        print(f"  ❌ Context Manager failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_system():
    """Test improved storage system"""
    print("🧪 Testing Storage System...")
    try:
        from brain.memory.storage import JarvisStorage
        
        storage = JarvisStorage(":memory:")
        
        # Test new methods
        assert hasattr(storage, 'get_storage_stats')
        assert hasattr(storage, 'cleanup_old_conversations')
        assert hasattr(storage, 'get_conversation_summary')
        assert hasattr(storage, 'prune_database')
        
        # Test stats
        stats = storage.get_storage_stats()
        assert "conversations" in stats
        assert "facts" in stats
        assert "events" in stats
        
        # Test summary
        summary = storage.get_conversation_summary()
        assert "total" in summary
        
        print("  ✅ Storage System OK")
        return True
    except Exception as e:
        print(f"  ❌ Storage System failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_diagnostics():
    """Test improved boot diagnostics"""
    print("🧪 Testing Diagnostics...")
    try:
        from core.lifecycle.boot.diagnostics import Diagnostics
        
        # Can't test fully without core instance, but check structure
        assert Diagnostics is not None
        
        # Check methods exist
        assert hasattr(Diagnostics, '_check_logger')
        assert hasattr(Diagnostics, '_check_eventbus')
        assert hasattr(Diagnostics, '_check_input')
        assert hasattr(Diagnostics, '_check_output')
        assert hasattr(Diagnostics, '_check_voice_io')
        assert hasattr(Diagnostics, '_check_nlu')
        assert hasattr(Diagnostics, '_check_skills')
        assert hasattr(Diagnostics, 'get_report')
        
        print("  ✅ Diagnostics OK")
        return True
    except Exception as e:
        print(f"  ❌ Diagnostics failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("v0.0.4 CORE IMPROVEMENTS - INTEGRATION TEST")
    print("="*60 + "\n")
    
    tests = [
        test_skill_dispatcher,
        test_session_manager,
        test_reasoning_engine,
        test_context_manager,
        test_storage_system,
        test_diagnostics,
    ]
    
    results = []
    for test_func in tests:
        try:
            passed = test_func()
            results.append((test_func.__name__, passed))
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        test_name = name.replace("test_", "").replace("_", " ").title()
        print(f"{status:10} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("🎉 All core improvements verified!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
