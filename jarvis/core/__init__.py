# core/__init__.py
"""
JarvisAI Core v0.0.4
Modular core architecture with lifecycle management
"""

from .lifecycle import (
    Initializer,
    Diagnostics,
    ModuleLoader,
    RuntimeState,
    EventBus,
    EventExecutor,
    Scheduler,
    IOChannel,
    load_consent,
    save_consent,
    get_or_request_data_collection_consent,
)
from .constants import DEFAULT_CONFIG, EVENT_JARVIS_RESPONSE
from .modes import OperationalMode, ModeController

__all__ = [
    # Lifecycle
    "Initializer",
    "Diagnostics",
    "ModuleLoader",
    "RuntimeState",
    "EventBus",
    "EventExecutor",
    "Scheduler",
    "IOChannel",
    "load_consent",
    "save_consent",
    "get_or_request_data_collection_consent",
    # Constants
    "DEFAULT_CONFIG",
    "EVENT_JARVIS_RESPONSE",
    # Modes
    "OperationalMode",
    "ModeController",
]
