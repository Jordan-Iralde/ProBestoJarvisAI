# system/session_manager.py
"""
Multi-Session Runtime Manager for JarvisAI v0.0.4
Handles multiple concurrent sessions with independent contexts.
Features:
- Thread-safe operations
- Session lifecycle management
- Mode enforcement
- Activity tracking
- History consolidation
"""

import threading
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from system.core.exceptions import SessionNotFoundError, ModeError


@dataclass
class Session:
    """Represents a single user session"""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    history: list = field(default_factory=list)
    mode: str = "ACTIVE"  # SAFE, PASSIVE, ACTIVE, ANALYSIS
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)  # Custom metadata

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def add_to_history(self, entry: dict):
        """Add entry to session history (keep last 100)"""
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        
        self.history.append(entry)
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def get_duration(self) -> timedelta:
        """Get session duration"""
        return self.last_activity - self.created_at
    
    def is_inactive_since(self, minutes: int) -> bool:
        """Check if session inactive for N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return self.last_activity < cutoff


class SessionManager:
    """
    Manages multiple concurrent sessions
    Thread-safe operations with error handling
    """
    
    VALID_MODES = ["SAFE", "PASSIVE", "ACTIVE", "ANALYSIS"]

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._default_mode = "ACTIVE"

    def create_session(self, initial_context: Optional[Dict] = None, mode: str = None) -> str:
        """
        Create a new session and return session_id
        
        Args:
            initial_context: Optional initial context
            mode: Optional initial mode (default: ACTIVE)
            
        Returns:
            Session ID
            
        Raises:
            ModeError: If mode is invalid
        """
        if mode and mode not in self.VALID_MODES:
            raise ModeError(
                f"Invalid mode: {mode}",
                {"mode": mode, "valid_modes": self.VALID_MODES}
            )
        
        with self._lock:
            session_id = str(uuid.uuid4())
            session = Session(
                session_id=session_id,
                context=initial_context or {},
                mode=mode or self._default_mode
            )
            self._sessions[session_id] = session
            return session_id

    def get_session(self, session_id: str) -> Session:
        """
        Get session by ID
        
        Raises:
            SessionNotFoundError: If session not found
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(
                    f"Session not found: {session_id}",
                    {"session_id": session_id, "available": list(self._sessions.keys())}
                )
            return session

    def update_session_context(self, session_id: str, key: str, value: Any):
        """Update session context"""
        session = self.get_session(session_id)
        with self._lock:
            session.context[key] = value
            session.update_activity()

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context"""
        session = self.get_session(session_id)
        with self._lock:
            return session.context.copy()

    def add_session_history(self, session_id: str, entry: dict):
        """Add entry to session history"""
        session = self.get_session(session_id)
        with self._lock:
            session.add_to_history(entry)
            session.update_activity()

    def set_session_mode(self, session_id: str, mode: str):
        """
        Set operational mode for session
        
        Raises:
            SessionNotFoundError: If session not found
            ModeError: If mode is invalid
        """
        if mode not in self.VALID_MODES:
            raise ModeError(
                f"Invalid mode: {mode}",
                {"mode": mode, "valid_modes": self.VALID_MODES}
            )

        session = self.get_session(session_id)
        with self._lock:
            old_mode = session.mode
            session.mode = mode
            session.update_activity()
            
            # Log mode change in history
            session.add_to_history({
                "type": "mode_change",
                "old_mode": old_mode,
                "new_mode": mode
            })

    def get_session_mode(self, session_id: str) -> str:
        """Get current mode for session"""
        session = self.get_session(session_id)
        return session.mode

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        with self._lock:
            return [
                {
                    "session_id": s.session_id,
                    "created_at": s.created_at.isoformat(),
                    "last_activity": s.last_activity.isoformat(),
                    "mode": s.mode,
                    "duration_seconds": s.get_duration().total_seconds()
                }
                for s in self._sessions.values()
                if s.active
            ]

    def close_session(self, session_id: str, reason: str = None):
        """Close a session"""
        session = self.get_session(session_id)
        with self._lock:
            session.active = False
            session.add_to_history({
                "type": "session_closed",
                "reason": reason or "user_initiated"
            })

    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove sessions inactive for more than max_age_hours
        
        Returns:
            Number of sessions removed
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            to_remove = [
                sid for sid, s in self._sessions.items()
                if s.last_activity < cutoff
            ]
            for sid in to_remove:
                self._sessions[sid].active = False
            return len(to_remove)

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        session = self.get_session(session_id)
        
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "duration_seconds": session.get_duration().total_seconds(),
            "mode": session.mode,
            "active": session.active,
            "context_keys": len(session.context),
            "history_entries": len(session.history),
            "context_size_bytes": len(str(session.context).encode())
        }

    def get_all_sessions_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all sessions"""
        with self._lock:
            return [self.get_session_stats(sid) for sid in self._sessions.keys()]