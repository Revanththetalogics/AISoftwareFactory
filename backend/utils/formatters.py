"""
Formatting utilities for AI Software Factory.

This module provides formatting functions for dates, durations, and other data types.
"""

from datetime import datetime


def format_datetime(dt: datetime | None) -> str | None:
    """
    Format a datetime to ISO string.

    Args:
        dt: Datetime to format

    Returns:
        ISO formatted string or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def format_duration(seconds: int | float) -> str:
    """
    Format duration in seconds to human readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Human readable duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human readable string.

    Args:
        bytes_value: Size in bytes

    Returns:
        Human readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
