#!/usr/bin/env python3
"""Test v0.0.6 boot with new skills: AdaptiveMemory, AppFinder, InternetSearch, SkillTesting"""

import os
import sys
import time
import json

# Add jarvis to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_boot_v0_0_6():
    """Test JarvisCore boot with v0.0.6 features"""
    print("\n" + "="*80)
    print("JARVIS v0.0.6 BOOT TEST - New Features Integration")
    print("="*80)
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print("❌ config.json not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Disable voice and data collection for testing
    config["tts"] = False
    config["voice_enabled"] = False
    config["data_collection"] = False
    config["web_dashboard"] = False
    config["workers"] = 2
    
    try:
        print("\n[1] Importing JarvisCore...")
        from system.core import JarvisCore
        print("    ✅ Import successful")
        
        print("\n[2] Initializing JarvisCore...")
        core = JarvisCore(config)
        print("    ✅ Initialization successful")
        
        print("\n[3] Checking new components...")
        checks = [
            ("adaptive_memory", hasattr(core, 'adaptive_memory')),
            ("storage", hasattr(core, 'storage')),
            ("context_manager", hasattr(core, 'context_manager')),
            ("llm_manager", hasattr(core, 'llm_manager')),
        ]
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"    {status} core.{name}: {result}")
        
        if not all(result for _, result in checks):
            print("❌ Some components missing")
            return False
        
        print("\n[4] Checking new skills are registered...")
        new_skills = [
            "open_app_advanced",
            "internet_search",
            "stackoverflow_search",
            "github_search",
            "skill_testing"
        ]
        
        registered_skills = core.skill_dispatcher.skills
        print(f"    Total skills registered: {len(registered_skills)}")
        
        for skill_name in new_skills:
            is_registered = skill_name in registered_skills
            status = "✅" if is_registered else "❌"
            print(f"    {status} {skill_name}: {is_registered}")
        
        missing = [s for s in new_skills if s not in registered_skills]
        if missing:
            print(f"❌ Missing skills: {missing}")
            return False
        
        print("\n[5] Testing AdaptiveMemory API...")
        try:
            # Test record_correction
            core.adaptive_memory.record_correction("obsidian", "open_app", {"app": "obsidian"})
            print("    ✅ record_correction works")
            
            # Test record_app_path
            core.adaptive_memory.record_app_path("obsidian", "C:\\Users\\yo\\AppData\\Local\\Obsidian\\Obsidian.exe")
            print("    ✅ record_app_path works")
            
            # Test get_app_path
            path = core.adaptive_memory.get_app_path("obsidian")
            print(f"    ✅ get_app_path works (found: {bool(path)})")
            
            # Test record_success
            core.adaptive_memory.record_success("open obsidian", "open_app", {"app": "obsidian"}, {"confidence": 0.95})
            print("    ✅ record_success works")
            
            # Test stats
            stats = core.adaptive_memory.get_stats()
            print(f"    ✅ get_stats works: {len(stats)} metrics")
            
        except Exception as e:
            print(f"    ❌ AdaptiveMemory error: {e}")
            return False
        
        print("\n[6] Testing AppFinder API...")
        try:
            from skills.productivity.open_app_advanced import AppFinder
            finder = AppFinder()
            
            # Test find_app
            result = finder.find_app("notepad")
            print(f"    ✅ AppFinder.find_app works (found: {bool(result)})")
            
        except Exception as e:
            print(f"    ❌ AppFinder error: {e}")
            return False
        
        print("\n[7] Testing InternetSearch API...")
        try:
            from skills.research.internet_search import InternetSearchSkill
            search = InternetSearchSkill()
            # Just test instantiation, don't make network calls
            print("    ✅ InternetSearchSkill instantiated")
        except Exception as e:
            print(f"    ❌ InternetSearchSkill error: {e}")
            return False
        
        print("\n[8] Testing SkillTesting API...")
        try:
            from skills.system.skill_testing import SkillTestingSkill
            testing = SkillTestingSkill()
            print("    ✅ SkillTestingSkill instantiated")
        except Exception as e:
            print(f"    ❌ SkillTestingSkill error: {e}")
            return False
        
        print("\n[9] Booting JarvisCore...")
        core.boot()
        print("    ✅ Boot successful")
        
        print("\n[10] Verifying all 23 skills are available...")
        all_skills = core.skill_dispatcher.skills
        print(f"    Total registered: {len(all_skills)}")
        
        required_skills = [
            "open_app", "get_time", "system_status", "create_note",
            "search_file", "summarize_recent_activity", "summarize_last_session",
            "analyze_session_value", "research_and_contextualize", "analyze_system_health",
            "what_do_you_know_about_me", "evaluate_user_session", "auto_programming",
            "system_auto_optimization", "learning_engine", "research_skill",
            "context_awareness", "manage_resources",
            # v0.0.6 new
            "open_app_advanced", "internet_search", "stackoverflow_search",
            "github_search", "skill_testing"
        ]
        
        missing = [s for s in required_skills if s not in all_skills]
        if missing:
            print(f"    ❌ Missing: {missing}")
            return False
        
        print(f"    ✅ All {len(required_skills)} skills registered!")
        
        print("\n[11] Testing adaptive_memory persistence...")
        try:
            # Export and reimport
            exported = core.adaptive_memory.export_learning()
            print(f"    ✅ Exported learning data: {len(exported)} items")
        except Exception as e:
            print(f"    ❌ Export error: {e}")
            return False
        
        print("\n[12] Stopping JarvisCore...")
        core.stop()
        time.sleep(0.5)
        print("    ✅ Stop successful")
        
        print("\n" + "="*80)
        print("✅ v0.0.6 BOOT TEST PASSED - All features integrated!")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Boot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boot_v0_0_6()
    sys.exit(0 if success else 1)
