"""
Context manager for Brain module.

This module provides conversation history and context window management
for maintaining state across interactions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """A message in the conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """A conversation session."""
    conversation_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContextManager:
    """
    Context manager for conversation history.

    Provides context window management with summarization and
    conversation state tracking.
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initialize the context manager.

        Args:
            max_tokens: Maximum tokens in context window
        """
        self._max_tokens = max_tokens
        self._conversations: Dict[str, Conversation] = {}
        self._logger = get_logger(__name__)

    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation.

        Args:
            conversation_id: Optional conversation ID
            metadata: Conversation metadata

        Returns:
            Conversation ID
        """
        conversation_id = conversation_id or str(uuid4())

        conversation = Conversation(
            conversation_id=conversation_id,
            metadata=metadata or {}
        )

        self._conversations[conversation_id] = conversation

        self._logger.info(
            "Conversation created",
            conversation_id=conversation_id
        )

        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Message metadata

        Returns:
            True if added, False if conversation not found
        """
        if conversation_id not in self._conversations:
            return False

        conversation = self._conversations[conversation_id]

        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )

        conversation.messages.append(message)

        # Manage context window
        self._manage_context_window(conversation)

        return True

    def get_context(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation context.

        Args:
            conversation_id: Conversation ID
            max_messages: Maximum messages to return

        Returns:
            List of messages as dictionaries
        """
        if conversation_id not in self._conversations:
            return []

        conversation = self._conversations[conversation_id]
        messages = conversation.messages

        if max_messages:
            messages = messages[-max_messages:]

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """
        Get a summary of the conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Summary text or None
        """
        if conversation_id not in self._conversations:
            return None

        conversation = self._conversations[conversation_id]

        # Simple summary: first user message and message count
        user_messages = [m for m in conversation.messages if m.role == "user"]

        if not user_messages:
            return "Empty conversation"

        first_message = user_messages[0].content[:100]
        return f"Conversation about: {first_message}... ({len(conversation.messages)} messages)"

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            self._logger.info("Conversation deleted", conversation_id=conversation_id)
            return True
        return False

    def _manage_context_window(self, conversation: Conversation):
        """Manage context window size."""
        # Simple token estimation (4 chars per token)
        total_chars = sum(len(m.content) for m in conversation.messages)
        estimated_tokens = total_chars // 4

        if estimated_tokens > self._max_tokens:
            # Remove oldest messages until under limit
            while estimated_tokens > self._max_tokens and len(conversation.messages) > 2:
                removed = conversation.messages.pop(0)
                estimated_tokens -= len(removed.content) // 4

            self._logger.info(
                "Context window managed",
                conversation_id=conversation.conversation_id,
                messages_remaining=len(conversation.messages)
            )
