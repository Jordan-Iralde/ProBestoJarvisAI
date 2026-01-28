#!/usr/bin/env python3
"""Quick interactive test of Jarvis core functionality."""

import sys
import time
import json
import os
from system.core.engine import JarvisCore

def load_config():
    """Load Jarvis configuration."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "config.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_interactive():
    """Test interactive commands."""
    print("\n" + "="*60)
    print("🤖 Jarvis Interactive Test")
    print("="*60 + "\n")
    
    try:
        # Create and boot
        print("[1/3] Creating JarvisCore...")
        config = load_config()
        core = JarvisCore(config)
        print("✓ Core created\n")
        
        print("[2/3] Booting system...")
        core.boot()
        print("✓ Boot complete\n")
        
        print("[3/3] Testing interactive commands...\n")
        
        # Test commands through event bus
        test_commands = [
            "hola",
            "--status",
            "--skills",
            "--debug on",
            "--debug off"
        ]
        
        for cmd in test_commands:
            print(f"  >> {cmd}")
            # Emit input text event
            core.event_bus.emit("EVENT_INPUT_TEXT", {"text": cmd, "source": "cli"})
            time.sleep(0.3)  # Give time for event processing
            print()
        
        print("="*60)
        print("✅ All interactive tests completed!")
        print("="*60)
        
        # Cleanup
        core.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_interactive()
    sys.exit(0 if success else 1)
