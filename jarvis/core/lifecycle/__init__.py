# core/lifecycle/__init__.py
"""Lifecycle management for JarvisAI core"""

from .boot import Initializer, Diagnostics, ModuleLoader
from .runtime import RuntimeState, EventBus, EventExecutor, Scheduler, IOChannel
from .consent import load_consent, save_consent, get_or_request_data_collection_consent

__all__ = [
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
]
