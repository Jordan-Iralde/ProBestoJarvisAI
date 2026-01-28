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

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Count conversations
                conv_count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                fact_count = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
                event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                
                # Get oldest and newest conversations
                oldest = conn.execute(
                    "SELECT timestamp FROM conversations ORDER BY id ASC LIMIT 1"
                ).fetchone()
                newest = conn.execute(
                    "SELECT timestamp FROM conversations ORDER BY id DESC LIMIT 1"
                ).fetchone()
        
        return {
            "conversations": conv_count,
            "facts": fact_count,
            "events": event_count,
            "oldest_interaction": oldest[0] if oldest else None,
            "newest_interaction": newest[0] if newest else None
        }

    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Delete conversations older than N days
        
        Returns:
            Number of rows deleted
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM conversations WHERE timestamp < ?",
                    (cutoff,)
                )
                deleted = cursor.rowcount
                conn.commit()
        
        return deleted

    def get_conversation_summary(self, limit: int = 50) -> Dict[str, Any]:
        """Get conversation summary statistics"""
        conversations = self.get_last_conversations(limit)
        
        if not conversations:
            return {
                "total": 0,
                "avg_response_length": 0,
                "avg_input_length": 0,
                "sources": {}
            }
        
        sources = {}
        total_response_length = 0
        total_input_length = 0
        
        for conv in conversations:
            source = conv.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
            total_response_length += len(conv.get("response", ""))
            total_input_length += len(conv.get("user_input", ""))
        
        return {
            "total": len(conversations),
            "avg_response_length": total_response_length // len(conversations) if conversations else 0,
            "avg_input_length": total_input_length // len(conversations) if conversations else 0,
            "sources": sources
        }

    def prune_database(self) -> Dict[str, int]:
        """
        Prune database by removing old data
        
        Returns:
            Dict with number of rows deleted per table
        """
        results = {
            "conversations_deleted": self.cleanup_old_conversations(days=30),
            "events_pruned": 0
        }
        
        # Also keep events pruned
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Keep only last 500 events
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM events"
                ).fetchone()
                total_events = cursor[0]
                
                if total_events > 500:
                    # Delete oldest events
                    to_delete = total_events - 500
                    cursor = conn.execute(
                        "DELETE FROM events WHERE id IN (SELECT id FROM events ORDER BY id ASC LIMIT ?)",
                        (to_delete,)
                    )
                    results["events_pruned"] = cursor.rowcount
                    conn.commit()
        
        return results
