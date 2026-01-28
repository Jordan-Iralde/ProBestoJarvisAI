#!/usr/bin/env python
"""
Quick boot test for v0.0.4 improvements
"""
import sys
import os

# Add jarvis directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

def test_boot():
    try:
        print("[TEST] Starting boot test...")
        from system.core import JarvisCore
        import json
        
        # Load minimal config
        config = {
            "name": "JarvisAI",
            "version": "0.0.4",
            "debug_nlu": False,
            "tts": False,
            "voice_enabled": False,
            "short_term_memory_max": 20,
            "data_collection": False,
            "workers": 2
        }
        
        print("[TEST] Initializing JarvisCore...")
        core = JarvisCore(config=config)
        
        print("[TEST] Checking components...")
        print(f"  - Logger: {hasattr(core, 'logger')}")
        print(f"  - NLU: {hasattr(core, 'nlu')}")
        print(f"  - Context Manager: {hasattr(core, 'context_manager')}")
        print(f"  - Session Manager: {hasattr(core, 'session_manager')}")
        print(f"  - Event Bus: {hasattr(core, 'events')}")
        print(f"  - Input adapter: {hasattr(core, 'input')}")
        print(f"  - Output adapter: {hasattr(core, 'output')}")
        
        # Check if NLU has context manager
        if hasattr(core, 'nlu') and core.nlu:
            print(f"  - NLU has context: {hasattr(core.nlu, 'context')}")
        else:
            print("  - NLU not initialized (expected)")
        
        print("[TEST] Boot test PASSED")
        return True
        
    except Exception as e:
        print(f"[TEST] Boot test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boot()
    sys.exit(0 if success else 1)
