# brain/memory/context.py
"""
Context Manager - Generates conversation context from storage
Decoupled from core, easily replaceable for semantic memory.
"""

from typing import List, Dict, Any
from .storage import JarvisStorage


class ContextManager:
    """
    Manages conversation context by retrieving recent interactions.
    Generates short, readable context for LLM prompts.
    """

    def __init__(self, storage: JarvisStorage, max_interactions: int = 5):
        self.storage = storage
        self.max_interactions = max_interactions

    def get_context(self) -> str:
        """
        Get recent conversation context as formatted text.
        Returns empty string if no conversations available.
        """
        conversations = self.storage.get_last_conversations(self.max_interactions)

        if not conversations:
            return ""

        # Format as simple text conversation
        context_lines = []
        for conv in reversed(conversations):  # Oldest first
            context_lines.append(f"User: {conv['user_input']}")
            context_lines.append(f"Jarvis: {conv['response']}")
            context_lines.append("")  # Empty line between conversations

        return "\n".join(context_lines).strip()

    def get_context_list(self) -> List[Dict[str, Any]]:
        """
        Get raw conversation data for more complex processing.
        """
        return self.storage.get_last_conversations(self.max_interactions)
