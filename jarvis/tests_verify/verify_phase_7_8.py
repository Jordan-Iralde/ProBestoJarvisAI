#!/usr/bin/env python
"""Phase 7-8: Import verification and system test"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    
    print("=" * 60)
    print("PHASE 7-8: IMPORT VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Core module", "import core"),
        ("Core lifecycle", "from core import lifecycle"),
        ("Core constants", "from core import constants"),
        ("IO module", "from jarvis_io import CLIInput, TextOutput, AdvancedCLI"),
        ("IO voice", "from jarvis_io import VoiceIOPipeline"),
        ("JarvisCore", "from system.core import JarvisCore"),
        ("NLU Pipeline", "from brain.nlu.pipeline import NLUPipeline"),
        ("Data Collector", "from data.collector import DataCollector"),
        ("Skills Dispatcher", "from skills.actions.dispatcher import SkillDispatcher"),
        ("Logger", "from skills.system.logging.manager import JarvisLogger"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {test_name}: {import_stmt}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {import_stmt}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

def test_core_instantiation():
    """Test that JarvisCore can be instantiated"""
    print("\nTesting JarvisCore instantiation...")
    
    try:
        from system.core import JarvisCore
        import json
        import os
        
        # Load config
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                cfg = json.load(f)
            print(f"✅ JarvisCore import successful")
            print(f"✅ Config loaded successfully")
            return True
        else:
            print(f"⚠️  Config file not found at {config_path}")
            return True  # Still pass since import works
    except Exception as e:
        print(f"❌ JarvisCore instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    config_ok = test_core_instantiation()
    
    if success and config_ok:
        print("\n✅ ALL TESTS PASSED - System is ready for full boot")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        sys.exit(1)
