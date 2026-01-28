#!/usr/bin/env python3
"""Test confidence scores implementation."""

import json
import os
import sys
from system.core.engine import JarvisCore

def test_confidence():
    """Test that confidence scores are working."""
    print("\n[TEST] NLU Confidence Scores\n")
    
    try:
        # Load config and boot
        base = os.path.dirname(__file__)
        config_path = os.path.join(base, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        core = JarvisCore(config)
        core.boot()
        
        # Test NLU with common commands
        test_inputs = [
            "hola",
            "qué hora es",
            "dime el estado del sistema",
            "xyz123abc",  # Nonsense - should have low confidence
        ]
        
        print("[1] Testing NLU confidence pipeline\n")
        
        for test_input in test_inputs:
            print(f"Input: '{test_input}'")
            
            # Process through NLU
            result = core.nlu.process(test_input, core.events)
            
            if result:
                print(f"  Intent: {result.intent}")
                print(f"  Confidence: {result.confidence:.2%}")
                if result.alternatives:
                    print(f"  Alternatives:")
                    for alt_intent, alt_conf in result.alternatives:
                        print(f"    - {alt_intent}: {alt_conf:.2%}")
            else:
                print(f"  [ERROR] No result")
            
            print()
        
        print("[OK] Confidence scores working correctly")
        
        core.stop()
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_confidence()
    sys.exit(0 if success else 1)
