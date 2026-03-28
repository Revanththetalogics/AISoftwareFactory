"""
Tests for BackupSystem in infrastructure module.

Covers all uncovered lines: 49-60, 85-140, 152-234, 247-265, 277-316, 328-363, 372-405, 414-423, 435-443, 448, 453, 458
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestBackupSystemInit:
    """Tests for BackupSystem initialization (lines 49-60)."""

    def test_init_with_defaults(self, tmp_path):
        """Test initialization with default settings."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            assert backup._backup_dir == Path(str(tmp_path / "backups"))
            assert backup._retention_days == 30
            assert backup._schedule == '0 2 * * *'
            assert backup._enabled is True

    def test_init_with_custom_values(self, tmp_path):
        """Test initialization with custom values."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem(
                backup_dir=str(tmp_path / "custom_backups"),
                retention_days=7,
                schedule='0 0 * * *'
            )

            assert backup._backup_dir == Path(str(tmp_path / "custom_backups"))
            assert backup._retention_days == 7
            assert backup._schedule == '0 0 * * *'

    def test_init_creates_backup_directory(self, tmp_path):
        """Test that init creates backup directory if not exists."""
        backup_dir = tmp_path / "new_backups"
        assert not backup_dir.exists()

        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(backup_dir)
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            BackupSystem()

            assert backup_dir.exists()


class TestCreateBackup:
    """Tests for create_backup method (lines 85-140)."""

    @pytest.mark.asyncio
    async def test_create_backup_disabled(self, tmp_path):
        """Test create_backup when system is disabled."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = False
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()
            result = await backup.create_backup()

            assert result["status"] == "disabled"
            assert result["message"] == "Backup system is disabled"

    @pytest.mark.asyncio
    async def test_create_backup_with_name(self, tmp_path):
        """Test create_backup with custom name."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_backup_database', new_callable=AsyncMock) as mock_db, \
                 patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock) as mock_cleanup:
                mock_db.return_value = {"success": True, "file": "/test/db.sql"}
                mock_cleanup.return_value = 0

                result = await backup.create_backup(name="custom_backup")

                assert result["name"] == "custom_backup"
                assert result["status"] == "completed"
                assert "database" in result["components"]
                assert "config" in result["components"]

    @pytest.mark.asyncio
    async def test_create_backup_without_name(self, tmp_path):
        """Test create_backup generates timestamp name."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_backup_database', new_callable=AsyncMock) as mock_db, \
                 patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock):
                mock_db.return_value = {"success": True, "file": "/test/db.sql"}

                result = await backup.create_backup()

                assert result["name"].startswith("backup_")

    @pytest.mark.asyncio
    async def test_create_backup_db_failure(self, tmp_path):
        """Test create_backup with database backup failure."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_backup_database', new_callable=AsyncMock) as mock_db, \
                 patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock):
                mock_db.return_value = {"success": False, "error": "Connection failed"}

                result = await backup.create_backup()

                assert result["status"] == "partial"
                assert "Connection failed" in result["errors"]

    @pytest.mark.asyncio
    async def test_create_backup_exception(self, tmp_path):
        """Test create_backup handles exceptions."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_backup_database', new_callable=AsyncMock) as mock_db, \
                 patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock):
                mock_db.side_effect = Exception("Unexpected error")

                result = await backup.create_backup()

                assert result["status"] == "failed"
                assert "Unexpected error" in result["errors"]

    @pytest.mark.asyncio
    async def test_create_backup_without_databases(self, tmp_path):
        """Test create_backup with include_databases=False."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock):
                result = await backup.create_backup(include_databases=False)

                assert "database" not in result["components"]
                assert "config" in result["components"]

    @pytest.mark.asyncio
    async def test_create_backup_without_files(self, tmp_path):
        """Test create_backup with include_files=False."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            with patch.object(backup, '_backup_database', new_callable=AsyncMock) as mock_db, \
                 patch.object(backup, '_cleanup_old_backups', new_callable=AsyncMock):
                mock_db.return_value = {"success": True}

                result = await backup.create_backup(include_files=False)

                assert "config" not in result["components"]


class TestBackupDatabase:
    """Tests for _backup_database method (lines 152-234)."""

    @pytest.mark.asyncio
    async def test_backup_database_success(self, tmp_path):
        """Test successful database backup."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 0
                mock_process.communicate = AsyncMock(return_value=(b"", b""))
                mock_exec.return_value = mock_process

                result = await backup._backup_database(backup_path)

                assert result["success"] is True
                assert "file" in result

    @pytest.mark.asyncio
    async def test_backup_database_failure(self, tmp_path):
        """Test database backup failure."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 1
                mock_process.communicate = AsyncMock(return_value=(b"", b"Connection refused"))
                mock_exec.return_value = mock_process

                result = await backup._backup_database(backup_path)

                assert result["success"] is False
                assert "Connection refused" in result["error"]

    @pytest.mark.asyncio
    async def test_backup_database_timeout(self, tmp_path):
        """Test database backup timeout."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec, \
                 patch('asyncio.wait_for', side_effect=TimeoutError()):
                mock_process = AsyncMock()
                mock_exec.return_value = mock_process

                result = await backup._backup_database(backup_path)

                assert result["success"] is False
                assert "timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_backup_database_pg_dump_not_found(self, tmp_path):
        """Test database backup when pg_dump not found."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError()):
                result = await backup._backup_database(backup_path)

                assert result["success"] is False
                assert "pg_dump not found" in result["error"]

    @pytest.mark.asyncio
    async def test_backup_database_generic_exception(self, tmp_path):
        """Test database backup with generic exception."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', side_effect=Exception("Network error")):
                result = await backup._backup_database(backup_path)

                assert result["success"] is False
                assert "Network error" in result["error"]

    @pytest.mark.asyncio
    async def test_backup_database_with_password(self, tmp_path):
        """Test database backup sets PGPASSWORD when password present."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:secret@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 0
                mock_process.communicate = AsyncMock(return_value=(b"", b""))
                mock_exec.return_value = mock_process

                await backup._backup_database(backup_path)

                # Verify env was passed with PGPASSWORD
                call_kwargs = mock_exec.call_args
                assert 'env' in call_kwargs.kwargs
                assert call_kwargs.kwargs['env'].get('PGPASSWORD') == 'secret'


class TestRestoreBackup:
    """Tests for restore_backup and _restore_database (lines 247-316)."""

    @pytest.mark.asyncio
    async def test_restore_backup_not_found(self, tmp_path):
        """Test restore_backup when backup doesn't exist."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            result = await backup.restore_backup("nonexistent_backup")

            assert result is False

    @pytest.mark.asyncio
    async def test_restore_backup_success(self, tmp_path):
        """Test successful backup restore."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)

            with patch.object(backup, '_restore_database', new_callable=AsyncMock) as mock_restore:
                mock_restore.return_value = True

                result = await backup.restore_backup("test_backup")

                assert result is True
                mock_restore.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_backup_without_database(self, tmp_path):
        """Test restore_backup with restore_database=False."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)

            with patch.object(backup, '_restore_database', new_callable=AsyncMock) as mock_restore:
                result = await backup.restore_backup("test_backup", restore_database=False)

                assert result is True
                mock_restore.assert_not_called()

    @pytest.mark.asyncio
    async def test_restore_backup_exception(self, tmp_path):
        """Test restore_backup handles exceptions."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)

            with patch.object(backup, '_restore_database', new_callable=AsyncMock) as mock_restore:
                mock_restore.side_effect = Exception("Restore failed")

                result = await backup.restore_backup("test_backup")

                assert result is False

    @pytest.mark.asyncio
    async def test_restore_database_success(self, tmp_path):
        """Test _restore_database success."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()
            # Create dump file
            (backup_path / "testdb.sql").write_text("-- SQL DUMP")

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 0
                mock_process.communicate = AsyncMock(return_value=(b"", b""))
                mock_exec.return_value = mock_process

                result = await backup._restore_database(backup_path)

                assert result is True

    @pytest.mark.asyncio
    async def test_restore_database_dump_not_found(self, tmp_path):
        """Test _restore_database when dump file not found."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()

            result = await backup._restore_database(backup_path)

            assert result is False

    @pytest.mark.asyncio
    async def test_restore_database_failure(self, tmp_path):
        """Test _restore_database failure."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            backup_path = tmp_path / "test_backup"
            backup_path.mkdir()
            (backup_path / "testdb.sql").write_text("-- SQL DUMP")

            with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 1
                mock_process.communicate = AsyncMock(return_value=(b"", b"Error"))
                mock_exec.return_value = mock_process

                result = await backup._restore_database(backup_path)

                assert result is False


class TestVerifyBackup:
    """Tests for verify_backup method (lines 328-363)."""

    @pytest.mark.asyncio
    async def test_verify_backup_not_found(self, tmp_path):
        """Test verify_backup when backup doesn't exist."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            result = await backup.verify_backup("nonexistent")

            assert result["valid"] is False
            assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_verify_backup_metadata_missing(self, tmp_path):
        """Test verify_backup when metadata is missing."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory without metadata
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)

            result = await backup.verify_backup("test_backup")

            assert result["valid"] is False
            assert "Metadata missing" in result["error"]

    @pytest.mark.asyncio
    async def test_verify_backup_valid_with_database(self, tmp_path):
        """Test verify_backup with valid database component."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory with metadata and dump
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)
            metadata = {"components": ["database", "config"], "created_at": datetime.now(UTC).isoformat()}
            (backup_path / "metadata.json").write_text(json.dumps(metadata))
            (backup_path / "testdb.sql").write_text("-- SQL")
            (backup_path / "config").mkdir()

            result = await backup.verify_backup("test_backup")

            assert result["valid"] is True
            assert result["components"]["database"] is True
            assert result["components"]["config"] is True

    @pytest.mark.asyncio
    async def test_verify_backup_missing_database_dump(self, tmp_path):
        """Test verify_backup with missing database dump."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            settings.DATABASE_URL = 'postgresql://user:pass@localhost:5432/testdb'
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup directory with metadata but no dump
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)
            metadata = {"components": ["database"], "created_at": datetime.now(UTC).isoformat()}
            (backup_path / "metadata.json").write_text(json.dumps(metadata))

            result = await backup.verify_backup("test_backup")

            assert result["valid"] is False
            assert result["components"]["database"] is False

    @pytest.mark.asyncio
    async def test_verify_backup_exception(self, tmp_path):
        """Test verify_backup handles exceptions."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup with invalid JSON
            backup_path = tmp_path / "backups" / "test_backup"
            backup_path.mkdir(parents=True)
            (backup_path / "metadata.json").write_text("invalid json")

            result = await backup.verify_backup("test_backup")

            assert result["valid"] is False
            assert "error" in result


class TestCleanupOldBackups:
    """Tests for _cleanup_old_backups method (lines 372-405)."""

    @pytest.mark.asyncio
    async def test_cleanup_old_backups(self, tmp_path):
        """Test cleanup removes old backups."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 7
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create old backup
            old_backup = tmp_path / "backups" / "old_backup"
            old_backup.mkdir(parents=True)
            old_date = (datetime.now(UTC) - timedelta(days=10)).isoformat()
            (old_backup / "metadata.json").write_text(json.dumps({"created_at": old_date}))

            # Create recent backup
            new_backup = tmp_path / "backups" / "new_backup"
            new_backup.mkdir(parents=True)
            new_date = datetime.now(UTC).isoformat()
            (new_backup / "metadata.json").write_text(json.dumps({"created_at": new_date}))

            removed = await backup._cleanup_old_backups()

            assert removed == 1
            assert not old_backup.exists()
            assert new_backup.exists()

    @pytest.mark.asyncio
    async def test_cleanup_skips_non_directories(self, tmp_path):
        """Test cleanup skips non-directory items."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 7
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create a file (not directory)
            (tmp_path / "backups" / "file.txt").write_text("test")

            removed = await backup._cleanup_old_backups()

            assert removed == 0

    @pytest.mark.asyncio
    async def test_cleanup_skips_without_metadata(self, tmp_path):
        """Test cleanup skips backups without metadata."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 7
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup without metadata
            backup_dir = tmp_path / "backups" / "no_metadata"
            backup_dir.mkdir(parents=True)

            removed = await backup._cleanup_old_backups()

            assert removed == 0
            assert backup_dir.exists()

    @pytest.mark.asyncio
    async def test_cleanup_handles_invalid_metadata(self, tmp_path):
        """Test cleanup handles invalid metadata gracefully."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 7
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup with invalid metadata
            backup_dir = tmp_path / "backups" / "invalid_backup"
            backup_dir.mkdir(parents=True)
            (backup_dir / "metadata.json").write_text("invalid json")

            removed = await backup._cleanup_old_backups()

            assert removed == 0


class TestListBackups:
    """Tests for list_backups method (lines 414-423)."""

    def test_list_backups(self, tmp_path):
        """Test listing backups."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backups
            for i, name in enumerate(["backup1", "backup2"]):
                backup_dir = tmp_path / "backups" / name
                backup_dir.mkdir(parents=True)
                (backup_dir / "metadata.json").write_text(json.dumps({
                    "name": name,
                    "created_at": f"2024-01-0{i+1}T00:00:00"
                }))

            result = backup.list_backups()

            assert len(result) == 2
            assert result[0]["name"] == "backup2"  # Most recent first

    def test_list_backups_empty(self, tmp_path):
        """Test listing backups when none exist."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            result = backup.list_backups()

            assert result == []


class TestDeleteBackup:
    """Tests for delete_backup method (lines 435-443)."""

    def test_delete_backup_success(self, tmp_path):
        """Test successful backup deletion."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            # Create backup
            backup_dir = tmp_path / "backups" / "test_backup"
            backup_dir.mkdir(parents=True)

            result = backup.delete_backup("test_backup")

            assert result is True
            assert not backup_dir.exists()

    def test_delete_backup_not_found(self, tmp_path):
        """Test delete_backup when backup doesn't exist."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            result = backup.delete_backup("nonexistent")

            assert result is False


class TestBackupProperties:
    """Tests for property methods (lines 448, 453, 458)."""

    def test_is_enabled_property(self, tmp_path):
        """Test is_enabled property."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            assert backup.is_enabled is True

    def test_retention_days_property(self, tmp_path):
        """Test retention_days property."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 14
            settings.BACKUP_SCHEDULE = '0 2 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            assert backup.retention_days == 14

    def test_schedule_property(self, tmp_path):
        """Test schedule property."""
        with patch('backend.infrastructure.backup_system.get_settings') as mock_settings, \
             patch('backend.infrastructure.backup_system.get_logger') as mock_logger:
            settings = Mock()
            settings.BACKUP_DIR = str(tmp_path / "backups")
            settings.BACKUP_RETENTION_DAYS = 30
            settings.BACKUP_SCHEDULE = '0 3 * * *'
            settings.BACKUP_ENABLED = True
            mock_settings.return_value = settings
            mock_logger.return_value = Mock()

            from backend.infrastructure.backup_system import BackupSystem
            backup = BackupSystem()

            assert backup.schedule == '0 3 * * *'
