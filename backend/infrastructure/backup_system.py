"""
Backup system for Infrastructure module.

This module provides automated backup and restore capabilities
for the AI Software Factory, including PostgreSQL database backups.
"""

import asyncio
import json
import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class BackupSystem:
    """
    Backup system for data protection.

    Provides automated backup and restore functionality
    for critical system data including PostgreSQL databases.

    Attributes:
        _backup_dir: Directory for storing backups
        _retention_days: Number of days to retain backups
        _schedule: Cron schedule for automated backups
    """

    def __init__(
        self,
        backup_dir: str | None = None,
        retention_days: int | None = None,
        schedule: str | None = None,
    ):
        """
        Initialize the backup system.

        Args:
            backup_dir: Directory for storing backups (default from config)
            retention_days: Days to retain backups (default from config)
            schedule: Cron schedule for backups (default from config)
        """
        settings = get_settings()

        self._backup_dir = Path(backup_dir or getattr(settings, 'BACKUP_DIR', './backups'))
        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._retention_days = retention_days or getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        self._schedule = schedule or getattr(settings, 'BACKUP_SCHEDULE', '0 2 * * *')
        self._enabled = getattr(settings, 'BACKUP_ENABLED', True)

        self._logger = get_logger(__name__)

        self._logger.info(
            "Backup system initialized",
            backup_dir=str(self._backup_dir),
            retention_days=self._retention_days,
            schedule=self._schedule,
            enabled=self._enabled,
        )

    async def create_backup(
        self,
        name: str | None = None,
        include_databases: bool = True,
        include_files: bool = True
    ) -> dict[str, Any]:
        """
        Create a system backup.

        Args:
            name: Backup name (timestamp if not provided)
            include_databases: Whether to include database dumps
            include_files: Whether to include file backups

        Returns:
            Backup metadata
        """
        if not self._enabled:
            self._logger.warning("Backup system is disabled")
            return {"status": "disabled", "message": "Backup system is disabled"}

        backup_name = name or f"backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        backup_path = self._backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        self._logger.info("Creating backup", name=backup_name, path=str(backup_path))

        backup_info = {
            "name": backup_name,
            "created_at": datetime.now(UTC).isoformat(),
            "components": [],
            "status": "in_progress",
            "errors": [],
        }

        try:
            # Backup PostgreSQL database
            if include_databases:
                db_result = await self._backup_database(backup_path)
                if db_result["success"]:
                    backup_info["components"].append("database")
                else:
                    backup_info["errors"].append(db_result.get("error", "Database backup failed"))

            # Backup configuration files
            if include_files:
                config_backup = backup_path / "config"
                config_backup.mkdir(exist_ok=True)
                backup_info["components"].append("config")

            backup_info["status"] = "completed" if not backup_info["errors"] else "partial"

        except Exception as e:
            backup_info["status"] = "failed"
            backup_info["errors"].append(str(e))
            self._logger.error("Backup failed", name=backup_name, error=str(e))

        # Save backup metadata
        metadata_path = backup_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(backup_info, f, indent=2)

        self._logger.info(
            "Backup completed",
            name=backup_name,
            status=backup_info["status"],
            components=backup_info["components"],
        )

        # Run retention cleanup
        await self._cleanup_old_backups()

        return backup_info

    async def _backup_database(self, backup_path: Path) -> dict[str, Any]:
        """
        Backup PostgreSQL database using pg_dump.

        Args:
            backup_path: Path to store the backup

        Returns:
            Result dictionary with success status
        """
        settings = get_settings()
        db_url = settings.DATABASE_URL

        try:
            # Parse database URL
            # Format: postgresql://user:password@host:port/database
            from urllib.parse import urlparse
            parsed = urlparse(db_url)

            db_host = parsed.hostname or 'localhost'
            db_port = str(parsed.port or 5432)
            db_name = parsed.path.lstrip('/') if parsed.path else 'ai_factory'
            db_user = parsed.username or 'postgres'
            db_password = parsed.password or ''

            dump_file = backup_path / f"{db_name}.sql"

            # Set environment for pg_dump
            env = os.environ.copy()
            if db_password:
                env['PGPASSWORD'] = db_password

            # Run pg_dump
            cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-d', db_name,
                '-f', str(dump_file),
                '--verbose',
                '--format=plain',
                '--no-owner',
                '--no-privileges',
            ]

            self._logger.info(
                "Running database backup",
                database=db_name,
                host=db_host,
            )

            # Execute pg_dump asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300,  # 5 minute timeout
            )

            if process.returncode == 0:
                self._logger.info(
                    "Database backup completed",
                    database=db_name,
                    file=str(dump_file),
                )
                return {"success": True, "file": str(dump_file)}
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                self._logger.error(
                    "Database backup failed",
                    database=db_name,
                    error=error_msg,
                )
                return {"success": False, "error": error_msg}

        except TimeoutError:
            self._logger.error("Database backup timed out")
            return {"success": False, "error": "Backup timed out"}
        except FileNotFoundError:
            self._logger.warning(
                "pg_dump not found - database backup skipped",
                hint="Install PostgreSQL client tools to enable database backups",
            )
            return {"success": False, "error": "pg_dump not found"}
        except Exception as e:
            self._logger.error("Database backup error", error=str(e))
            return {"success": False, "error": str(e)}

    async def restore_backup(self, backup_name: str, restore_database: bool = True) -> bool:
        """
        Restore from a backup.

        Args:
            backup_name: Name of backup to restore
            restore_database: Whether to restore the database

        Returns:
            True if successful
        """
        backup_path = self._backup_dir / backup_name

        if not backup_path.exists():
            self._logger.error("Backup not found", name=backup_name)
            return False

        self._logger.info("Restoring backup", name=backup_name)

        try:
            # Restore database if requested
            if restore_database:
                await self._restore_database(backup_path)

            self._logger.info("Backup restored", name=backup_name)
            return True

        except Exception as e:
            self._logger.error("Restore failed", name=backup_name, error=str(e))
            return False

    async def _restore_database(self, backup_path: Path) -> bool:
        """
        Restore PostgreSQL database from backup.

        Args:
            backup_path: Path to the backup directory

        Returns:
            True if successful
        """
        settings = get_settings()
        db_url = settings.DATABASE_URL

        from urllib.parse import urlparse
        parsed = urlparse(db_url)

        db_host = parsed.hostname or 'localhost'
        db_port = str(parsed.port or 5432)
        db_name = parsed.path.lstrip('/') if parsed.path else 'ai_factory'
        db_user = parsed.username or 'postgres'
        db_password = parsed.password or ''

        dump_file = backup_path / f"{db_name}.sql"

        if not dump_file.exists():
            self._logger.warning("Database dump not found in backup")
            return False

        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        cmd = [
            'psql',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-f', str(dump_file),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await process.communicate()
        return process.returncode == 0

    async def verify_backup(self, backup_name: str) -> dict[str, Any]:
        """
        Verify backup integrity.

        Args:
            backup_name: Name of backup to verify

        Returns:
            Verification result
        """
        backup_path = self._backup_dir / backup_name

        if not backup_path.exists():
            return {"valid": False, "error": "Backup not found"}

        metadata_path = backup_path / "metadata.json"
        if not metadata_path.exists():
            return {"valid": False, "error": "Metadata missing"}

        try:
            with open(metadata_path) as f:
                metadata = json.load(f)

            # Check each component
            components_valid = True
            component_status = {}

            if "database" in metadata.get("components", []):
                db_name = get_settings().DATABASE_URL.split('/')[-1]
                dump_file = backup_path / f"{db_name}.sql"
                component_status["database"] = dump_file.exists()
                if not dump_file.exists():
                    components_valid = False

            if "config" in metadata.get("components", []):
                config_dir = backup_path / "config"
                component_status["config"] = config_dir.exists()

            return {
                "valid": components_valid,
                "metadata": metadata,
                "components": component_status,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def _cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period.

        Returns:
            Number of backups removed
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=self._retention_days)
        removed_count = 0

        for backup_dir in self._backup_dir.iterdir():
            if not backup_dir.is_dir():
                continue

            metadata_path = backup_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                created_at = datetime.fromisoformat(metadata.get("created_at", ""))

                if created_at < cutoff_date:
                    shutil.rmtree(backup_dir)
                    removed_count += 1
                    self._logger.info(
                        "Removed old backup",
                        name=backup_dir.name,
                        created_at=created_at.isoformat(),
                    )

            except Exception as e:
                self._logger.warning(
                    "Error processing backup for cleanup",
                    backup=backup_dir.name,
                    error=str(e),
                )

        return removed_count

    def list_backups(self) -> list[dict[str, Any]]:
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

    @property
    def is_enabled(self) -> bool:
        """Check if backup system is enabled."""
        return self._enabled

    @property
    def retention_days(self) -> int:
        """Get backup retention period in days."""
        return self._retention_days

    @property
    def schedule(self) -> str:
        """Get backup cron schedule."""
        return self._schedule

