# core/modes.py
"""
Operational Modes for JarvisAI v0.0.4
Defines behavior for different operational modes.
"""

from typing import Dict, Any, Optional
from enum import Enum


class OperationalMode(Enum):
    """Available operational modes"""
    SAFE = "SAFE"          # Default: no dangerous actions
    PASSIVE = "PASSIVE"    # Only responds to queries
    ACTIVE = "ACTIVE"      # Proposes and executes actions
    ANALYSIS = "ANALYSIS"  # Deep reflection and evaluation


class ModeController:
    """
    Controls operational modes and their behaviors
    """

    def __init__(self):
        self.mode_handlers: Dict[str, callable] = {
            "SAFE": self._handle_safe,
            "PASSIVE": self._handle_passive,
            "ACTIVE": self._handle_active,
            "ANALYSIS": self._handle_analysis
        }
        self.current_mode = "SAFE"

    def set_mode(self, mode: str):
        """Set operational mode"""
        if mode not in self.mode_handlers:
            raise ValueError(f"Unknown mode: {mode}")
        self.current_mode = mode

    def get_mode(self) -> str:
        """Get current operational mode"""
        return self.current_mode

    def can_execute_action(self, action: str, context: Dict[str, Any] = None) -> bool:
        """Check if action can be executed in current mode"""
        if context is None:
            context = {}
        handler = self.mode_handlers.get(self.current_mode)
        if handler:
            return handler(action, context)
        return False

    def handle(self, action: str, context: Dict[str, Any]) -> bool:
        """Handle action with mode-specific logic"""
        return self.can_execute_action(action, context)

    def _handle_safe(self, action: str, context: Dict[str, Any]) -> bool:
        """SAFE mode: no dangerous actions"""
        dangerous = ["delete", "uninstall", "shutdown", "restart", "format"]
        return not any(d in action.lower() for d in dangerous)

    def _handle_passive(self, action: str, context: Dict[str, Any]) -> bool:
        """PASSIVE mode: only responds to queries"""
        return "query" in action.lower() or "read" in action.lower()

    def _handle_active(self, action: str, context: Dict[str, Any]) -> bool:
        """ACTIVE mode: allows most actions"""
        return True

    def _handle_analysis(self, action: str, context: Dict[str, Any]) -> bool:
        """ANALYSIS mode: deep reflection"""
        return "analyze" in action.lower() or "evaluate" in action.lower()
