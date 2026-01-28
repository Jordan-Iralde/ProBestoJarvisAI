#!/usr/bin/env python3
"""
Quick test to validate v0.0.4 integration fixes
Tests special commands and basic functionality
"""

import sys
import os

# Add jarvis to path
sys.path.insert(0, os.path.dirname(__file__))

from system.core import JarvisCore

def test_v004_integration():
    """Test v0.0.4 integration"""
    
    print("=" * 60)
    print("v0.0.4 Integration Test")
    print("=" * 60)
    
    try:
        # Load config
        import json
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Disable voice for testing
        config['tts'] = False
        config['voice_enabled'] = False
        
        print("\n[1/4] Creating JarvisCore...")
        core = JarvisCore(config)
        print("✓ JarvisCore created")
        
        print("\n[2/4] Booting system...")
        core.boot()
        print("✓ Boot complete")
        
        print("\n[3/4] Testing methods...")
        
        # Test get_available_skills
        print("  Testing get_available_skills()...")
        skills = core.get_available_skills()
        print(f"  ✓ Found {len(skills)} skills")
        
        # Test get_system_status
        print("  Testing get_system_status()...")
        status = core.get_system_status()
        if 'system' in status:
            print(f"  ✓ CPU: {status['system'].get('cpu_percent', 0):.1f}%")
        
        # Test debug mode
        print("  Testing debug mode...")
        state = core.toggle_debug_mode()
        print(f"  ✓ Debug toggled to: {state}")
        
        print("\n[4/4] Testing special commands...")
        
        # Test SpecialCommandsHandler
        from system.core.special_commands import SpecialCommandsHandler
        handler = SpecialCommandsHandler(core)
        
        test_commands = [
            '--debug',
            '--skills',
            '--status',
            'skills',
            'status',
        ]
        
        for cmd in test_commands:
            if handler.is_special_command(cmd):
                response = handler.handle_command(cmd)
                print(f"  ✓ '{cmd}' → OK (response length: {len(response)})")
            else:
                print(f"  ✗ '{cmd}' → Not recognized")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
        core.stop()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_v004_integration()
    sys.exit(0 if success else 1)
