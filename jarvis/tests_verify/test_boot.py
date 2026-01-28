"""Quick boot test - exits after successful boot"""
import json
import sys
import os

# Add jarvis to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from system.core import JarvisCore
    
    print("Loading config...")
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("Creating JarvisCore...")
    core = JarvisCore(config)
    
    print("Starting boot sequence...")
    core.boot()
    
    print("\n" + "="*60)
    print("SUCCESS! System booted successfully")
    print("="*60)
    print("\nSystem Status:")
    print(f"  State: {core.state.get()}")
    print(f"  Skills: {len(core.skill_dispatcher.skills)} registered")
    print(f"  Current Session: {core.current_session_id}")
    print("\nTo start interactive mode, run: python main.py")
    print("="*60)
    
except Exception as e:
    print(f"\nERROR during boot: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
