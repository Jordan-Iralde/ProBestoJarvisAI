#!/usr/bin/env python3
"""Test error presenter."""

from system.core.error_presenter import ErrorPresenter
from system.exceptions import IntentNotRecognizedError, SkillExecutionError

print("[TEST] Error Presenter\n")

# Test 1: Unknown intent error
print("Test 1: Unknown Intent")
error = IntentNotRecognizedError("xyz123")
result = ErrorPresenter.format_error(error, {'intent': 'unknown_skill'})
print(f"  Reason: {result['reason']}")
print(f"  Suggestion: {result['suggestion']}")
print(f"  Message: {result['user_message']}")
print()

# Test 2: Skill execution error
print("Test 2: Skill Execution Error")
error = SkillExecutionError("Failed to open app", "open_app")
result = ErrorPresenter.format_error(error, {'intent': 'open_app', 'raw': 'abre firefox'})
print(f"  Reason: {result['reason']}")
print(f"  Suggestion: {result['suggestion']}")
print(f"  Message: {result['user_message']}")
print()

print("[OK] Error Presenter working")
