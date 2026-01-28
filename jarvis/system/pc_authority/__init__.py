"""
PC Authority Module
Complete control over system processes, keyboard/mouse tracking, and system resources
"""

from .process_monitor import ProcessMonitor, ProcessInfo, ProcessSnapshot
from .background_task_manager import BackgroundTaskManager, BackgroundTask, TaskStatus, TaskResult
from .comprehension_scorer import ComprehensionScorer, ComprehensionResult, ComprehensionLevel
from .system_authority import (
    SystemAuthorityController,
    KeyboardTracker,
    MouseTracker,
    KeyboardEvent,
    MouseEvent,
    SystemResourceSnapshot
)

__all__ = [
    'ProcessMonitor',
    'ProcessInfo',
    'ProcessSnapshot',
    'BackgroundTaskManager',
    'BackgroundTask',
    'TaskStatus',
    'TaskResult',
    'ComprehensionScorer',
    'ComprehensionResult',
    'ComprehensionLevel',
    'SystemAuthorityController',
    'KeyboardTracker',
    'MouseTracker',
    'KeyboardEvent',
    'MouseEvent',
    'SystemResourceSnapshot'
]
