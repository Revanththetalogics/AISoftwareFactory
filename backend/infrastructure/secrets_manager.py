"""
Secrets manager for Infrastructure module.

This module provides secure secrets management with support for
environment variables and external secret stores.
"""

import os
from typing import Dict, Optional, Any
from pathlib import Path

from backend.core.logging import get_logger

logger = get_logger(__name__)


class SecretsManager:
    """
    Secrets manager for secure credential handling.
    
    Provides secure access to secrets from environment variables
    and external secret stores.
    """
    
    def __init__(self):
        """Initialize the secrets manager."""
        self._cache: Dict[str, str] = {}
        self._logger = get_logger(__name__)
    
    def get_secret(
        self,
        key: str,
        default: Optional[str] = None,
        required: bool = False
    ) -> Optional[str]:
        """
        Get a secret value.
        
        Args:
            key: Secret key
            default: Default value if not found
            required: Whether the secret is required
            
        Returns:
            Secret value or default
            
        Raises:
            ValueError: If secret is required but not found
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # Check environment
        value = os.getenv(key)
        
        if value is None:
            # Check for file-based secrets (Docker secrets)
            secret_path = Path(f"/run/secrets/{key.lower()}")
            if secret_path.exists():
                value = secret_path.read_text().strip()
        
        if value is None:
            if required:
                raise ValueError(f"Required secret '{key}' not found")
            return default
        
        # Cache the value
        self._cache[key] = value
        
        return value
    
    def set_secret(self, key: str, value: str):
        """
        Set a secret value (for testing only).
        
        Args:
            key: Secret key
            value: Secret value
        """
        self._cache[key] = value
    
    def load_from_file(self, file_path: str) -> Dict[str, str]:
        """
        Load secrets from a .env file.
        
        Args:
            file_path: Path to .env file
            
        Returns:
            Dictionary of loaded secrets
        """
        secrets = {}
        path = Path(file_path)
        
        if not path.exists():
            self._logger.warning("Secrets file not found", path=file_path)
            return secrets
        
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        secrets[key] = value
                        self._cache[key] = value
        
        self._logger.info("Secrets loaded from file", path=file_path, count=len(secrets))
        return secrets
    
    def get_database_url(self) -> Optional[str]:
        """Get database URL from secrets."""
        return self.get_secret("DATABASE_URL")
    
    def get_secret_key(self) -> Optional[str]:
        """Get application secret key."""
        return self.get_secret("SECRET_KEY")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service."""
        return self.get_secret(f"{service.upper()}_API_KEY")
    
    def clear_cache(self):
        """Clear the secrets cache."""
        self._cache.clear()
        self._logger.info("Secrets cache cleared")
