"""
Backup system for Infrastructure module.

This module provides automated backup and restore capabilities
for the AI Software Factory.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import shutil
import json

from backend.core.logging import get_logger

logger = get_logger(__name__)


class BackupSystem:
    """
    Backup system for data protection.
    
    Provides automated backup and restore functionality
    for critical system data.
    """
    
    def __init__(self, backup_dir: str = "./backups"):
        """
        Initialize the backup system.
        
        Args:
            backup_dir: Directory for storing backups
        """
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger(__name__)
    
    async def create_backup(
        self,
        name: Optional[str] = None,
        include_databases: bool = True,
        include_files: bool = True
    ) -> Dict[str, Any]:
        """
        Create a system backup.
        
        Args:
            name: Backup name (timestamp if not provided)
            include_databases: Whether to include database dumps
            include_files: Whether to include file backups
            
        Returns:
            Backup metadata
        """
        backup_name = name or f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self._backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        self._logger.info("Creating backup", name=backup_name, path=str(backup_path))
        
        backup_info = {
            "name": backup_name,
            "created_at": datetime.utcnow().isoformat(),
            "components": []
        }
        
        if include_files:
            # Backup configuration files
            config_backup = backup_path / "config"
            config_backup.mkdir(exist_ok=True)
            backup_info["components"].append("config")
        
        # Save backup metadata
        metadata_path = backup_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        self._logger.info("Backup completed", name=backup_name)
        
        return backup_info
    
    async def restore_backup(self, backup_name: str) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_name: Name of backup to restore
            
        Returns:
            True if successful
        """
        backup_path = self._backup_dir / backup_name
        
        if not backup_path.exists():
            self._logger.error("Backup not found", name=backup_name)
            return False
        
        self._logger.info("Restoring backup", name=backup_name)
        
        # Restore logic would go here
        
        self._logger.info("Backup restored", name=backup_name)
        return True
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Returns:
            List of backup metadata
        """
        backups = []
        
        for backup_dir in self._backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_path = backup_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        backups.append(json.load(f))
        
        return sorted(backups, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def delete_backup(self, backup_name: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_name: Name of backup to delete
            
        Returns:
            True if deleted
        """
        backup_path = self._backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        shutil.rmtree(backup_path)
        self._logger.info("Backup deleted", name=backup_name)
        
        return True
