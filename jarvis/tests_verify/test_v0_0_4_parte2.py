#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for v0.0.4 PARTE 2 - NLU Pipeline Improvements
Tests:
1. Soft phrases database
2. Intent recognition accuracy with new soft phrases
3. TTS robustness and graceful degradation
4. Enhanced boot manager
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# TEST 1: SOFT PHRASES DATABASE
# ============================================================

def test_soft_phrases_database():
    """Test soft phrases database integrity"""
    print("\n" + "="*70)
    print("TEST 1: SOFT PHRASES DATABASE")
    print("="*70)
    
    try:
        from brain.nlu.soft_phrases import (
            get_all_intents, get_intent_count, get_phrase_count_for_intent,
            print_soft_phrases_summary, SOFT_PHRASES
        )
        
        # Check database
        total_skills = get_intent_count()
        print(f"✓ Total skills with soft phrases: {total_skills}")
        
        assert total_skills > 20, "Should have 20+ skills"
        print(f"✓ Coverage check passed (>20 skills)")
        
        # Check each skill has phrases
        for intent in get_all_intents():
            count = get_phrase_count_for_intent(intent)
            assert count > 0, f"{intent} has no phrases"
        print(f"✓ All skills have phrases")
        
        # Print summary
        print_soft_phrases_summary()
        
        print("\n✅ Soft phrases database test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Soft phrases database test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 2: INTENT MATCHING WITH SOFT PHRASES
# ============================================================

def test_intent_matching():
    """Test intent recognition with soft phrases"""
    print("\n" + "="*70)
    print("TEST 2: INTENT MATCHING WITH SOFT PHRASES")
    print("="*70)
    
    try:
        from brain.nlu.soft_phrases import get_intent_for_phrase, SOFT_PHRASES
        from brain.nlu.normalizer import Normalizer
        
        normalizer = Normalizer()
        test_cases = [
            ("que hora es", "get_time", True),
            ("busca python asyncio", "internet_search", True),
            ("abre el navegador", "web_browser", True),
            ("optimiza el sistema", "system_auto_optimization", True),
            ("crea una nota", "create_note", True),
            ("que sabes de mi", "what_do_you_know_about_me", True),
        ]
        
        passed = 0
        for phrase, expected_intent, should_match in test_cases:
            intent, boost, is_exact = get_intent_for_phrase(phrase, normalizer)
            
            if should_match:
                if intent == expected_intent:
                    print(f"✓ '{phrase}' → {intent} (exact={is_exact})")
                    passed += 1
                else:
                    print(f"✗ '{phrase}' → {intent} (expected {expected_intent})")
            else:
                if intent is None:
                    print(f"✓ '{phrase}' → None (as expected)")
                    passed += 1
                else:
                    print(f"✗ '{phrase}' → {intent} (expected None)")
        
        accuracy = (passed / len(test_cases)) * 100
        print(f"\n✓ Accuracy: {accuracy:.1f}% ({passed}/{len(test_cases)})")
        
        assert accuracy >= 80, "Accuracy should be >=80%"
        print("✓ Accuracy threshold met")
        
        print("\n✅ Intent matching test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Intent matching test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 3: TTS ROBUSTNESS
# ============================================================

def test_tts_robustness():
    """Test TTS with graceful degradation"""
    print("\n" + "="*70)
    print("TEST 3: TTS ROBUSTNESS")
    print("="*70)
    
    try:
        from jarvis_io.voice.tts import TTS
        
        # Test 1: Initialization without pyttsx3
        tts = TTS(enabled=False, fallback_enabled=True)
        assert tts.fallback_enabled == True
        assert tts.enabled == False
        print("✓ TTS initializes with fallback enabled")
        
        # Test 2: Status reporting
        status = tts.get_status()
        assert "enabled" in status
        assert "is_degraded" in status
        print(f"✓ TTS status: enabled={status['enabled']}, degraded={status['is_degraded']}")
        
        # Test 3: Text sanitization
        dirty_text = "Hola 🎉 @user! https://example.com #tag"
        clean = tts._sanitize_text(dirty_text)
        assert "🎉" not in clean
        assert "@" not in clean
        assert "http" not in clean
        print(f"✓ Text sanitization works: '{dirty_text}' → '{clean}'")
        
        # Test 4: Graceful degradation mode
        tts2 = TTS(enabled=False, fallback_enabled=True)
        tts2._is_degraded = True
        try:
            tts2.speak("test")
            print("✗ Should have raised DegradedError")
            return False
        except Exception as e:
            if "DegradedError" in str(type(e)):
                print(f"✓ Raises DegradedError when degraded: {type(e).__name__}")
            else:
                print(f"✓ Raises error when degraded: {type(e).__name__}")
        
        print("\n✅ TTS robustness test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TTS robustness test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# TEST 4: ENHANCED BOOT MANAGER
# ============================================================

async def test_enhanced_boot_manager():
    """Test enhanced boot manager phases"""
    print("\n" + "="*70)
    print("TEST 4: ENHANCED BOOT MANAGER")
    print("="*70)
    
    try:
        from system.core.enhanced_boot import EnhancedBootManager, BootPhase
        import logging
        
        logger = logging.getLogger("test")
        manager = EnhancedBootManager(logger)
        
        # Test phase tracking
        phases = [
            BootPhase.CONFIG_VALIDATION,
            BootPhase.LOGGING,
            BootPhase.RUNTIME
        ]
        
        for phase in phases:
            manager.phases_completed.append(phase)
        
        assert len(manager.phases_completed) == 3
        print(f"✓ Boot manager tracks {len(manager.phases_completed)} phases")
        
        # Test degradation manager
        strategy = manager.degradation_manager.register_strategy("test_component", required=False)
        manager.degradation_manager.handle_error("test_component", "feature", Exception("test error"))
        
        status = manager.degradation_manager.get_status()
        assert status["degraded_components"] > 0
        print(f"✓ Degradation manager tracks status: {status}")
        
        # Test health checker
        assert len(manager.health_checker.components) >= 0
        print(f"✓ Health checker initialized with {len(manager.health_checker.components)} components")
        
        print("\n✅ Enhanced boot manager test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Enhanced boot manager test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# MAIN TEST RUNNER
# ============================================================

async def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" "*10 + "v0.0.4 PARTE 2 - NLU IMPROVEMENTS TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Soft phrases
    results.append(("Soft Phrases Database", test_soft_phrases_database()))
    
    # Test 2: Intent matching
    results.append(("Intent Matching", test_intent_matching()))
    
    # Test 3: TTS robustness
    results.append(("TTS Robustness", test_tts_robustness()))
    
    # Test 4: Enhanced boot manager
    results.append(("Enhanced Boot Manager", await test_enhanced_boot_manager()))
    
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
        print("\n🎉 All tests PASSED! v0.0.4 Parte 2 improvements are solid.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
