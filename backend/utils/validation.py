"""
Enhanced Input Validation Utilities.

This module provides additional validation utilities for securing API inputs
and preventing common security vulnerabilities.
"""

import ipaddress
import re
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.networks import EmailStr

from backend.core.exceptions import ValidationError

# SSRF Protection - Blocked IP ranges
BLOCKED_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),       # Private Class A
    ipaddress.ip_network('172.16.0.0/12'),    # Private Class B
    ipaddress.ip_network('192.168.0.0/16'),   # Private Class C
    ipaddress.ip_network('127.0.0.0/8'),      # Loopback
    ipaddress.ip_network('169.254.0.0/16'),   # Link-local
    ipaddress.ip_network('0.0.0.0/8'),        # Current network
    ipaddress.ip_network('224.0.0.0/4'),      # Multicast
    ipaddress.ip_network('240.0.0.0/4'),      # Reserved
    ipaddress.ip_network('::1/128'),          # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),         # IPv6 unique local
    ipaddress.ip_network('fe80::/10'),        # IPv6 link-local
]


class SanitizedString(str):
    """String that has been sanitized for security."""
    pass


def sanitize_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize input string to prevent injection attacks.

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized string

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be a string")

    if len(value) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length}")

    # Remove potentially dangerous characters
    # Allow alphanumeric, spaces, and common punctuation
    sanitized = re.sub(r'[<>"\'`;]', '', value)

    # Prevent directory traversal
    sanitized = re.sub(r'\.\./', '', sanitized)
    sanitized = re.sub(r'\\\.', '', sanitized)

    return sanitized.strip()


def validate_email_format(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid
    """
    try:
        # This will raise if invalid
        EmailStr.validate(email)
        return True
    except Exception:
        return False


def validate_url_format(url: str) -> bool:
    """
    Validate URL format and check for malicious patterns.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid and safe
    """
    try:
        parsed = urlparse(url)

        # Check for valid scheme
        if parsed.scheme not in ['http', 'https']:
            return False

        # Check for localhost/loopback addresses
        if parsed.hostname in ['localhost', '127.0.0.1', '::1']:
            return False

        # Check for private IP ranges
        if parsed.hostname and re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', parsed.hostname):
            return False

        return True
    except Exception:
        return False


def validate_url_safe(url: str) -> bool:
    """
    Validate URL is safe from SSRF attacks.

    This function performs comprehensive SSRF protection by:
    1. Validating URL scheme (only http/https)
    2. Resolving the hostname to IP
    3. Checking if the resolved IP is in blocked private ranges

    Args:
        url: URL to validate

    Returns:
        bool: True if URL is safe from SSRF attacks

    Raises:
        ValidationError: If URL is potentially dangerous

    Example:
        >>> validate_url_safe("https://example.com")
        True
        >>> validate_url_safe("http://192.168.1.1/admin")
        False
    """
    try:
        parsed = urlparse(url)

        # Check for valid scheme
        if parsed.scheme not in ['http', 'https']:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Block localhost variants
        if hostname.lower() in ['localhost', 'localhost.localdomain']:
            return False

        # Resolve hostname to IP for comprehensive check
        try:
            # Get all IP addresses for the hostname
            addr_info = socket.getaddrinfo(hostname, None)

            for info in addr_info:
                ip_str = info[4][0]
                try:
                    ip = ipaddress.ip_address(ip_str)

                    # Check against all blocked ranges
                    for blocked in BLOCKED_IP_RANGES:
                        if ip in blocked:
                            return False

                except ValueError:
                    # Invalid IP format, skip
                    continue

        except socket.gaierror:
            # DNS resolution failed - could be malicious or just unreachable
            # Be cautious and allow (validation will fail at connection time)
            pass
        except socket.timeout:
            # DNS timeout - allow to proceed
            pass

        return True

    except Exception:
        return False


def is_ip_in_blocked_range(ip_str: str) -> bool:
    """
    Check if an IP address is in a blocked private range.

    Args:
        ip_str: IP address string

    Returns:
        bool: True if IP is in a blocked range
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for blocked in BLOCKED_IP_RANGES:
            if ip in blocked:
                return True
        return False
    except ValueError:
        return False


class SecureProjectCreate(BaseModel):
    """
    Enhanced project creation model with security validation.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project name"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Project description"
    )
    requirements: Optional[str] = Field(
        None,
        max_length=5000,
        description="Project requirements"
    )

    @field_validator('name')
    def validate_name(cls, v):
        """Validate and sanitize project name."""
        sanitized = sanitize_input(v, max_length=100)
        if not re.match(r'^[a-zA-Z0-9 _\-\.]+$', sanitized):
            raise ValidationError("Project name contains invalid characters")
        return sanitized

    @field_validator('description')
    def validate_description(cls, v):
        """Validate and sanitize project description."""
        return sanitize_input(v, max_length=2000)

    @field_validator('requirements')
    def validate_requirements(cls, v):
        """Validate and sanitize requirements."""
        if v is not None:
            return sanitize_input(v, max_length=5000)
        return v


class SecureDeploymentRequest(BaseModel):
    """
    Enhanced deployment request with security validation.
    """
    project_id: str = Field(..., min_length=1, max_length=50)
    environment: str = Field(..., pattern="^(dev|staging|production)$")
    version: str = Field(..., pattern=r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$')
    config: Optional[Dict[str, Any]] = None

    @field_validator('project_id')
    def validate_project_id(cls, v):
        """Validate project ID format."""
        if not re.match(r'^[a-zA-Z0-9\-_]+$', v):
            raise ValidationError("Invalid project ID format")
        return v

    @model_validator(mode='after')
    def validate_config_security(self):
        """Validate configuration doesn't contain sensitive data."""
        if self.config:
            # Check for common sensitive keys
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            for key, value in self.config.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in sensitive_keys):
                    raise ValidationError(f"Configuration contains sensitive key: {key}")
        return self


class RateLimitConfig(BaseModel):
    """
    Rate limiting configuration for API endpoints.
    """
    requests_per_minute: int = Field(60, ge=1, le=1000)
    requests_per_hour: int = Field(1000, ge=1, le=10000)
    burst_limit: int = Field(10, ge=1, le=100)


# Common validation patterns
VALIDATION_PATTERNS = {
    'project_name': r'^[a-zA-Z0-9 _\-\.]{1,100}$',
    'version': r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$',
    'identifier': r'^[a-zA-Z0-9\-_]{1,50}$',
    'environment': r'^(dev|staging|production)$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}


def validate_pattern(value: str, pattern_name: str) -> bool:
    """
    Validate value against predefined pattern.

    Args:
        value: Value to validate
        pattern_name: Name of validation pattern

    Returns:
        bool: True if valid
    """
    pattern = VALIDATION_PATTERNS.get(pattern_name)
    if not pattern:
        return False
    return bool(re.match(pattern, value))


def batch_validate_fields(data: Dict[str, Any], validations: Dict[str, str]) -> List[str]:
    """
    Batch validate multiple fields against patterns.

    Args:
        data: Data dictionary to validate
        validations: Field name to pattern name mapping

    Returns:
        List[str]: List of validation error messages
    """
    errors = []

    for field_name, pattern_name in validations.items():
        if field_name in data:
            value = data[field_name]
            if isinstance(value, str) and not validate_pattern(value, pattern_name):
                errors.append(f"Invalid {field_name}: {value}")

    return errors
