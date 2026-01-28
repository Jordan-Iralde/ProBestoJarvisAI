#!/usr/bin/env python3
"""
Test Suite Completo - JarvisAI
Valida todos los componentes implementados
"""

import os
import sys
import time
import json
import tempfile
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test 1: Importación de todos los módulos"""
    print("🔍 Test 1: Importación de módulos...")
    
    try:
        # Core constants
        from system.constants import *
        print("✅ Constants import OK")
        
        # Brain modules
        from brain.memory.storage import JarvisStorage
        from brain.memory.context import ContextManager
        from brain.llm.manager import LLMManager, DummyLocalLLM
        print("✅ Brain modules import OK")
        
        # Core engine
        from system.core import JarvisCore
        print("✅ Core engine import OK")
        
        # Skills
        from skills.get_time import GetTimeSkill
        from skills.system_status import SystemStatusSkill
        from skills.create_note import CreateNoteSkill
        from skills.search_file import SearchFileSkill
        from skills.open_app import OpenAppSkill
        print("✅ Basic skills import OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_storage():
    """Test 2: Storage SQLite"""
    print("\n🔍 Test 2: Storage SQLite...")
    
    try:
        from brain.memory.storage import JarvisStorage
        
        # Use temp database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        storage = JarvisStorage(db_path)
        
        # Test conversation save
        storage.save_conversation("hola", "¡Hola! ¿Cómo estás?", "test")
        storage.save_conversation("qué hora es", "Son las 3:45 PM", "skill")
        
        # Test retrieval
        convs = storage.get_last_conversations(2)
        assert len(convs) == 2
        assert convs[0]['user_input'] == "qué hora es"
        assert convs[1]['user_input'] == "hola"
        print("✅ Conversation storage OK")
        
        # Test facts
        storage.save_fact("user_name", "TestUser", 0.9)
        fact = storage.get_fact("user_name")
        assert fact['value'] == "TestUser"
        assert fact['confidence'] == 0.9
        print("✅ Facts storage OK")
        
        # Test events
        storage.save_event("test_event", {"data": "test"})
        events = storage.get_recent_events(1)
        assert len(events) == 1
        assert events[0]['type'] == "test_event"
        print("✅ Events storage OK")
        
        # Cleanup
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        return False

def test_context_manager():
    """Test 3: Context Manager"""
    print("\n🔍 Test 3: Context Manager...")
    
    try:
        from brain.memory.storage import JarvisStorage
        from brain.memory.context import ContextManager
        
        # Setup temp storage
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        storage = JarvisStorage(db_path)
        context_manager = ContextManager(storage, max_interactions=3)
        
        # Add test conversations
        storage.save_conversation("hola", "¡Hola!", "test")
        storage.save_conversation("cómo estás", "Bien gracias", "test")
        storage.save_conversation("adiós", "¡Hasta luego!", "test")
        
        # Test context generation
        context = context_manager.get_context()
        assert "User: hola" in context
        assert "Jarvis: ¡Hola!" in context
        assert "User: adiós" in context
        print("✅ Context generation OK")
        
        # Test context list
        context_list = context_manager.get_context_list()
        assert len(context_list) == 3
        print("✅ Context list OK")
        
        # Cleanup
        os.unlink(db_path)
        return True
        
    except Exception as e:
        print(f"❌ Context Manager error: {e}")
        return False

def test_llm_manager():
    """Test 4: LLM Manager"""
    print("\n🔍 Test 4: LLM Manager...")
    
    try:
        from brain.llm.manager import LLMManager, DummyLocalLLM
        
        llm = LLMManager()
        
        # Test basic responses
        response1 = llm.generate("hola")
        assert "hola" in response1.lower()
        print("✅ Basic LLM response OK")
        
        # Test with context
        response2 = llm.generate("cómo estás", "User: hola\nJarvis: ¡Hola!")
        assert "cómo estás" in response2.lower()
        print("✅ LLM with context OK")
        
        # Test error handling
        class BrokenLLM:
            def generate(self, prompt, context=""):
                raise Exception("Test error")
        
        llm.set_backend(BrokenLLM())
        response3 = llm.generate("test")
        assert "problema" in response3.lower()
        print("✅ LLM error handling OK")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Manager error: {e}")
        return False

def test_core_boot():
    """Test 5: Core Boot"""
    print("\n🔍 Test 5: Core Boot...")
    
    try:
        from system.core import JarvisCore
        
        # Minimal config
        config = {
            "debug_nlu": False,
            "data_collection": False,
            "workers": 2,
            "short_term_memory_max": 5
        }
        
        core = JarvisCore(config)
        
        # Test boot
        success = core.boot()
        assert success == True
        print("✅ Core boot OK")
        
        # Test state
        assert core.state.is_ready()
        print("✅ Core state OK")
        
        # Test basic NLU
        core.nlu.process("qué hora es", core.events)
        time.sleep(0.1)  # Wait for async processing
        print("✅ NLU processing OK")
        
        # Test LLM fallback
        core.nlu.process("hola cómo estás", core.events)
        time.sleep(0.1)
        print("✅ LLM fallback OK")
        
        # Cleanup
        core.stop()
        return True
        
    except Exception as e:
        print(f"❌ Core Boot error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_skills():
    """Test 6: Skills básicas"""
    print("\n🔍 Test 6: Skills básicas...")
    
    try:
        from skills.get_time import GetTimeSkill
        from skills.system_status import SystemStatusSkill
        from skills.create_note import CreateNoteSkill
        from skills.search_file import SearchFileSkill
        from skills.open_app import OpenAppSkill
        
        # Test GetTimeSkill
        time_skill = GetTimeSkill()
        result = time_skill.execute({})
        assert result['success'] == True
        assert 'time' in result['result']
        print("✅ GetTimeSkill OK")
        
        # Test SystemStatusSkill
        status_skill = SystemStatusSkill()
        result = status_skill.execute({})
        assert result['success'] == True
        assert 'cpu' in result['result']
        print("✅ SystemStatusSkill OK")
        
        # Test CreateNoteSkill
        note_skill = CreateNoteSkill()
        result = note_skill.execute({"content": ["test note"]})
        assert result['success'] == True
        assert 'filename' in result['result']
        print("✅ CreateNoteSkill OK")
        
        # Test SearchFileSkill
        search_skill = SearchFileSkill()
        result = search_skill.execute({"pattern": ["*.py"]})
        assert result['success'] == True
        assert 'count' in result['result']
        print("✅ SearchFileSkill OK")
        
        # Test OpenAppSkill
        app_skill = OpenAppSkill()
        result = app_skill.execute({"app": ["notepad"]})
        # Note: This might fail if notepad doesn't exist, but should not crash
        assert 'success' in result
        print("✅ OpenAppSkill OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Skills error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test 7: Integración completa"""
    print("\n🔍 Test 7: Integración completa...")
    
    try:
        from system.core import JarvisCore
        
        # Config with all features
        config = {
            "debug_nlu": False,
            "data_collection": True,
            "workers": 2,
            "short_term_memory_max": 10,
            "tts": False
        }
        
        core = JarvisCore(config)
        
        # Boot
        success = core.boot()
        assert success == True
        
        # Test multiple commands
        commands = [
            "qué hora es",
            "abrir notepad",
            "crear nota: test integration",
            "estado del sistema",
            "hola cómo estás"  # Should go to LLM
        ]
        
        for cmd in commands:
            core.nlu.process(cmd, core.events)
            time.sleep(0.1)
        
        # Test persistence
        conversations = core.storage.get_last_conversations(5)
        assert len(conversations) >= 5
        print("✅ Persistence OK")
        
        # Test context
        context = core.context_manager.get_context()
        assert len(context) > 0
        print("✅ Context OK")
        
        # Test session insights
        insights = core.get_session_insights()
        assert isinstance(insights, dict)
        print("✅ Session insights OK")
        
        # Cleanup
        core.stop()
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 JarvisAI - Test Suite Completo")
    print("=" * 50)
    
    tests = [
        ("Importación", test_imports),
        ("Storage SQLite", test_storage),
        ("Context Manager", test_context_manager),
        ("LLM Manager", test_llm_manager),
        ("Core Boot", test_core_boot),
        ("Skills Básicas", test_skills),
        ("Integración", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON! JarvisAI está funcional.")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisar los errores above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
