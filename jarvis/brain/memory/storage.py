# brain/memory/storage.py
"""
Storage Module - SQLite-based persistence for JarvisAI
Thread-safe basic implementation using sqlite3 standard library.
"""

import sqlite3
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional


class JarvisStorage:
    """
    SQLite storage for conversations, facts, and events.
    Creates database automatically if it doesn't exist.
    """

    def __init__(self, db_path: str = "jarvis_data.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        response TEXT NOT NULL,
                        source TEXT DEFAULT 'unknown'
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS facts (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        confidence REAL DEFAULT 1.0,
                        updated_at TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        type TEXT NOT NULL,
                        payload TEXT  -- JSON string
                    )
                """)

                conn.commit()

    def save_conversation(self, user_input: str, response: str, source: str = "unknown"):
        """Save a conversation interaction."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO conversations (timestamp, user_input, response, source) VALUES (?, ?, ?, ?)",
                    (datetime.now().isoformat(), user_input, response, source)
                )
                conn.commit()

    def get_last_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get last N conversations."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT timestamp, user_input, response, source FROM conversations ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()

        return [
            {
                "timestamp": row[0],
                "user_input": row[1],
                "response": row[2],
                "source": row[3]
            }
            for row in rows
        ]

    def get_conversations_since(self, since_timestamp: float) -> List[Dict[str, Any]]:
        """Get conversations since a specific timestamp."""
        import time
        since_iso = datetime.fromtimestamp(since_timestamp).isoformat()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT timestamp, user_input, response, source FROM conversations WHERE timestamp >= ? ORDER BY timestamp ASC",
                    (since_iso,)
                )
                rows = cursor.fetchall()

        return [
            {
                "timestamp": row[0],
                "user_input": row[1],
                "response": row[2],
                "source": row[3]
            }
            for row in rows
        ]

    def save_fact(self, key: str, value: str, confidence: float = 1.0):
        """Save or update a fact."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO facts (key, value, confidence, updated_at) VALUES (?, ?, ?, ?)",
                    (key, value, confidence, datetime.now().isoformat())
                )
                conn.commit()

    def get_fact(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a fact by key."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value, confidence, updated_at FROM facts WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

        if row:
            return {
                "value": row[0],
                "confidence": row[1],
                "updated_at": row[2]
            }
        return None

    def save_event(self, event_type: str, payload: Dict[str, Any]):
        """Save an event."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO events (timestamp, type, payload) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), event_type, json.dumps(payload))
                )
                conn.commit()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT timestamp, type, payload FROM events ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()

        return [
            {
                "timestamp": row[0],
                "type": row[1],
                "payload": json.loads(row[2]) if row[2] else {}
            }
            for row in rows
        ]
