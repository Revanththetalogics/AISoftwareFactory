"""
ID generation utilities for AI Software Factory.

This module provides functions for generating unique identifiers.
"""

import uuid
from datetime import UTC, datetime


def generate_uuid() -> str:
    """
    Generate a UUID4 string.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_id(prefix: str | None = None) -> str:
    """
    Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    unique_id = uuid.uuid4().hex[:12]
    if prefix:
        return f"{prefix}-{unique_id}"
    return unique_id


def generate_timestamp_id(prefix: str | None = None) -> str:
    """
    Generate an ID with timestamp for sorting.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Timestamp-based ID string
    """
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}-{timestamp}-{unique_id}"
    return f"{timestamp}-{unique_id}"
