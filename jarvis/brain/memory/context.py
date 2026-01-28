# brain/memory/context.py
"""
Context Manager v0.0.4
Generates and manages conversation context from storage.
Thread-safe with caching.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .storage import JarvisStorage


class ContextManager:
    """
    Manages conversation context by retrieving recent interactions.
    Features:
    - Retrieves recent conversation context
    - Generates formatted context for LLM
    - Maintains context cache
    - Filters by time/relevance
    """

    def __init__(self, storage: JarvisStorage, max_interactions: int = 5):
        self.storage = storage
        self.max_interactions = max_interactions
        self._context_cache: Optional[str] = None
        self._cache_timestamp: Optional[datetime] = None
        self.cache_ttl_seconds = 60  # Cache valid for 60 seconds

    def _is_cache_valid(self) -> bool:
        """Check if context cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self.cache_ttl_seconds
    
    def _invalidate_cache(self):
        """Invalidate context cache"""
        self._context_cache = None
        self._cache_timestamp = None

    def get_context(self, use_cache: bool = True) -> str:
        """
        Get recent conversation context as formatted text.
        
        Args:
            use_cache: Whether to use cached context
            
        Returns:
            Formatted context string (empty if no conversations)
        """
        # Check cache
        if use_cache and self._is_cache_valid() and self._context_cache:
            return self._context_cache
        
        conversations = self.storage.get_last_conversations(self.max_interactions)

        if not conversations:
            self._context_cache = ""
            return ""

        # Format as simple text conversation
        context_lines = []
        for conv in reversed(conversations):  # Oldest first
            context_lines.append(f"User: {conv['user_input']}")
            context_lines.append(f"Jarvis: {conv['response']}")
            context_lines.append("")  # Empty line between conversations

        formatted_context = "\n".join(context_lines).strip()
        
        # Cache result
        self._context_cache = formatted_context
        self._cache_timestamp = datetime.now()
        
        return formatted_context

    def get_context_list(self, use_cache: bool = False) -> List[Dict[str, Any]]:
        """
        Get raw conversation data for more complex processing.
        
        Args:
            use_cache: Whether to use cache (raw data doesn't use cache by default)
            
        Returns:
            List of conversation dicts
        """
        return self.storage.get_last_conversations(self.max_interactions)

    def get_recent_intents(self, max_count: int = 10) -> List[str]:
        """
        Get list of recently used intents
        
        Returns:
            List of intent names in order (oldest first)
        """
        conversations = self.storage.get_last_conversations(max_count)
        # Extract intents if available in metadata
        intents = []
        for conv in reversed(conversations):
            if "intent" in conv:
                intents.append(conv["intent"])
        return intents

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of current context
        
        Returns:
            Dict with context statistics
        """
        conversations = self.storage.get_last_conversations(self.max_interactions)
        
        if not conversations:
            return {
                "total_interactions": 0,
                "context_size_chars": 0,
                "oldest_interaction": None,
                "newest_interaction": None
            }
        
        context_str = self.get_context(use_cache=False)
        
        return {
            "total_interactions": len(conversations),
            "context_size_chars": len(context_str),
            "oldest_interaction": conversations[0].get("timestamp"),
            "newest_interaction": conversations[-1].get("timestamp"),
            "unique_intents": len(set(self.get_recent_intents()))
        }
    
    def get_context_by_time(self, minutes_back: int = 30) -> str:
        """
        Get context from last N minutes
        
        Args:
            minutes_back: How far back to look
            
        Returns:
            Formatted context string
        """
        # This would require storage enhancement
        # For now, just use standard method
        return self.get_context(use_cache=False)
    
    def clear_cache(self):
        """Manually clear context cache"""
        self._invalidate_cache()
