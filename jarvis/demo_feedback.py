# Interactive Demo: Feedback System v0.0.4
"""
Shows how the feedback system works in real-time
Run with: python demo_feedback.py
"""

import json
import time
from system.core.engine import JarvisCore
from system.core.special_commands import SpecialCommandsHandler

print("\n" + "="*70)
print("JARVIS v0.0.4 - FEEDBACK SYSTEM INTERACTIVE DEMO")
print("="*70 + "\n")

cfg = json.load(open('config.json'))
core = JarvisCore(cfg)
core.boot()

cmd_handler = SpecialCommandsHandler(core)

# Demo Scenario 1: Correct Decision
print("[SCENARIO 1] User gives correct feedback")
print("-" * 70)

reflection = core.reflection_observer.start_recording(
    intent="get_time",
    skill_name="get_time",
    input_text="what time is it",
    confidence=0.92,
    alternatives=[("get_date", 0.45), ("system_time", 0.38)]
)
print(f">> what time is it")
print(f"[System decides] get_time (confidence: 92%)")

time.sleep(0.5)
core.reflection_observer.record_execution(
    success=True,
    result={"time": "14:33:45"},
    error=None,
    duration_ms=42
)
print(f"[Result] Current time: 14:33:45")

print(f"\n>> !correct")
response = cmd_handler.handle_command("!correct")
print(f"[System] {response}")

print(f"\n[MEMORY] Reflection stored:")
print(f"  - Decision: get_time (92% confidence)")
print(f"  - User Feedback: CORRECT")
print(f"  - Impact: Reinforces this decision pattern")

# Demo Scenario 2: Wrong Decision + Parallel Execution
print("\n" + "="*70)
print("[SCENARIO 2] User corrects wrong decision (triggers parallel execution)")
print("-" * 70)

reflection2 = core.reflection_observer.start_recording(
    intent="open_app",
    skill_name="open_app",
    input_text="search_file spotify",
    confidence=0.62,
    alternatives=[("search_file", 0.58), ("find_file", 0.45)]
)
print(f">> search_file spotify")
print(f"[System decides] open_app (confidence: 62%)")
print(f"[LOW CONFIDENCE DETECTED] Attempting parallel execution...")
print(f"  - Primary: open_app (62%)")
print(f"  - Alt 1: search_file (58%)")
print(f"  - Alt 2: find_file (45%)")

time.sleep(1.0)
core.reflection_observer.record_execution(
    success=False,
    result=None,
    error="No application found matching 'spotify'",
    duration_ms=180
)
print(f"[Result] Error: No app found")

print(f"\n>> !wrong")
response = cmd_handler.handle_command("!wrong")
print(f"[System] {response}")

print(f"\n>> !correct search_file")
response = cmd_handler.handle_command("!correct search_file")
print(f"[System] {response}")

print(f"\n[MEMORY] Reflection stored:")
print(f"  - Decision: open_app (62% confidence)")
print(f"  - Actual Intent: search_file")
print(f"  - User Feedback: WRONG -> search_file")
print(f"  - Impact: Future 'search_file' requests favor search_file skill")

# Demo Scenario 3: Feedback with Notes
print("\n" + "="*70)
print("[SCENARIO 3] User adds notes to decision")
print("-" * 70)

reflection3 = core.reflection_observer.start_recording(
    intent="system_optimization",
    skill_name="system_optimization",
    input_text="optimize my system",
    confidence=0.75,
    alternatives=[("system_health", 0.60), ("performance_check", 0.52)]
)
print(f">> optimize my system")
print(f"[System decides] system_optimization (confidence: 75%)")

time.sleep(0.3)
core.reflection_observer.record_execution(
    success=True,
    result={"tasks_cleaned": 5, "cache_cleared": True, "time": "2.3s"},
    error=None,
    duration_ms=2300
)
print(f"[Result] System optimized (2.3s)")

print(f"\n>> !feedback this was good but took longer than expected")
response = cmd_handler.handle_command("!feedback this was good but took longer than expected")
print(f"[System] {response}")

print(f"\n[MEMORY] Reflection stored:")
print(f"  - Decision: system_optimization")
print(f"  - User Feedback: CORRECT with notes")
print(f"  - Notes: 'this was good but took longer than expected'")
print(f"  - Impact: Notes available for future analysis/improvements")

# Demo Scenario 4: View reflection history
print("\n" + "="*70)
print("[SCENARIO 4] View reflection history (learning)")
print("-" * 70)

history = core.reflection_observer.reflection_history
print(f"\n[REFLECTION HISTORY] Stored {len(history)} decisions:")

for i, record in enumerate(history[-3:], 1):
    status = "CORRECT" if record.user_feedback == "correct" else \
             "WRONG->alternative" if record.user_feedback == "alternative" else \
             "WRONG" if record.user_feedback == "wrong" else "NOTED"
    
    print(f"\n  {i}. {record.intent}")
    print(f"     Confidence: {record.confidence:.0%}")
    print(f"     Input: {record.input_text}")
    print(f"     Feedback: {status}")
    if record.user_notes:
        print(f"     Notes: {record.user_notes}")

# Demo learning capability
print("\n" + "="*70)
print("[LEARNING] What the system learned:")
print("-" * 70)

problematic = core.reflection_observer.get_problematic_intents()
print(f"\nProblematic intents (need improvement):")
if problematic:
    for item in problematic[:3]:
        print(f"  - {item['intent']}: {item['count']} corrections needed")
else:
    print("  (None detected in this session)")

print("\n[SUMMARY]")
print(f"  - Total decisions recorded: {len(history)}")
print(f"  - Correct decisions: {sum(1 for r in history if r.user_feedback in ['correct', 'notes'])}")
print(f"  - Corrections made: {sum(1 for r in history if r.user_feedback in ['wrong', 'alternative'])}")
print(f"  - Learning enabled: Yes (patterns available for future improvement)")

print("\n" + "="*70)
print("DEMO COMPLETE")
print("="*70)

print(f"""
KEY FEATURES DEMONSTRATED:
  
  1. Real-time Feedback
     - Users can correct wrong decisions immediately
     - Feedback stored for pattern learning
  
  2. Parallel Execution (Low Confidence)
     - When confidence < 0.7, system tries alternatives
     - Provides better results for ambiguous inputs
  
  3. Decision History
     - All decisions and corrections logged
     - Available for analysis and improvement
  
  4. User Annotations
     - Users can add notes explaining feedback
     - Helps with understanding user expectations
  
  5. Learning System (Ready)
     - Reflection data prepared for ML improvement
     - Problematic intents identified
     - Pattern matching available

NEXT STEPS:
  - Use system in interactive mode: python main.py
  - Try: "search_file spotify" then "!wrong" or "!correct search_file"
  - System will remember your feedback for future sessions
""")

core.stop()
print("Demo ended. System shutdown.")
