"""
Security utilities for AI Software Factory.

This module provides security-related functions for password hashing,
verification, and path sanitization.
"""

import os
import re

import bcrypt

from backend.core.exceptions import ValidationError


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    # bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    # bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def sanitize_file_path(path: str, base_dir: str) -> str:
    """
    Sanitize file path to prevent directory traversal attacks.

    This function ensures that the given path stays within the specified
    base directory, preventing attackers from accessing files outside
    the intended directory using ../ sequences or symbolic links.

    Args:
        path: The path to sanitize (can be relative or absolute)
        base_dir: The base directory that the path must stay within

    Returns:
        str: The sanitized absolute path

    Raises:
        ValidationError: If path traversal is detected or path is invalid

    Example:
        >>> sanitize_file_path("subdir/file.txt", "/data")
        '/data/subdir/file.txt'
        >>> sanitize_file_path("../etc/passwd", "/data")
        ValidationError: Path traversal detected
    """
    if not path:
        raise ValidationError("Path cannot be empty")

    if not base_dir:
        raise ValidationError("Base directory cannot be empty")

    # Normalize backslashes to forward slashes for consistent handling
    normalized_path = path.replace('\\', '/')

    # Normalize and resolve the base directory
    abs_base = os.path.abspath(os.path.normpath(base_dir))

    # Join the path with base and normalize
    joined_path = os.path.join(base_dir, normalized_path)
    abs_path = os.path.abspath(os.path.normpath(joined_path))

    # Ensure path stays within base directory
    # Use os.path.commonpath for more reliable comparison
    try:
        common = os.path.commonpath([abs_base, abs_path])
        if common != abs_base:
            raise ValidationError(
                f"Path traversal detected: {path}",
                details={"path": path, "base_dir": base_dir}
            )
    except ValueError as exc:
        # Paths on different drives (Windows) or other issues
        raise ValidationError(
            f"Invalid path: {path}",
            details={"path": path, "base_dir": base_dir}
        ) from exc

    return abs_path


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to remove dangerous characters.

    This function removes or replaces characters that could be dangerous
    in filenames, including path separators and null bytes.

    Args:
        filename: The filename to sanitize
        max_length: Maximum allowed length for the filename

    Returns:
        str: The sanitized filename

    Raises:
        ValidationError: If filename is empty or contains only invalid chars

    Example:
        >>> sanitize_filename("my_file.txt")
        'my_file.txt'
        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove other dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)

    # Remove leading/trailing dots and spaces (Windows issues)
    filename = filename.strip('. ')

    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)

    # Truncate if too long
    if len(filename) > max_length:
        # Preserve extension if possible
        name, ext = os.path.splitext(filename)
        if ext and len(ext) <= 10:  # Reasonable extension length
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext
        else:
            filename = filename[:max_length]

    if not filename:
        raise ValidationError("Filename contains only invalid characters")

    return filename


def is_safe_path(path: str, base_dir: str) -> bool:
    """
    Check if a path is safe (stays within base directory).

    This is a non-raising version of sanitize_file_path for use in
    boolean checks.

    Args:
        path: The path to check
        base_dir: The base directory

    Returns:
        bool: True if path is safe, False otherwise
    """
    try:
        sanitize_file_path(path, base_dir)
        return True
    except (ValidationError, ValueError):
        return False
