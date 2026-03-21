"""
File Manager for AI Software Factory.

This module provides file operations for managing generated code artifacts.
"""

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FileArtifact:
    """
    Represents a file artifact.

    Attributes:
        path: File path
        content: File content
        language: Programming language
        created_at: Creation timestamp
        modified_at: Last modification timestamp
        metadata: Additional metadata
    """
    path: str
    content: str = ""
    language: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def filename(self) -> str:
        """Get the filename."""
        return Path(self.path).name

    @property
    def extension(self) -> str:
        """Get the file extension."""
        return Path(self.path).suffix

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "filename": self.filename,
            "extension": self.extension,
            "language": self.language,
            "size": len(self.content),
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ProjectStructure:
    """
    Represents a project structure.

    Attributes:
        root_path: Root directory path
        name: Project name
        files: List of file artifacts
        directories: List of directories
    """
    root_path: str
    name: str
    files: list[FileArtifact] = field(default_factory=list)
    directories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "root_path": self.root_path,
            "name": self.name,
            "file_count": len(self.files),
            "directory_count": len(self.directories),
            "files": [f.to_dict() for f in self.files],
            "directories": self.directories,
        }


class FileManager:
    """
    File manager for code artifacts.

    This class provides:
    - File CRUD operations
    - Directory management
    - Project structure management
    - File search and filtering

    Example:
        >>> manager = FileManager(base_path="/tmp/projects")
        >>> manager.write_file("myproject/main.py", "print('hello')")
        >>> files = manager.list_files("myproject")
    """

    def __init__(self, base_path: str = "./generated"):
        """
        Initialize the file manager.

        Args:
            base_path: Base directory for all projects
        """
        self.base_path = Path(base_path).resolve()
        self._logger = get_logger(__name__)

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

        self._logger.info("File manager initialized", base_path=str(self.base_path))

    def _resolve_path(self, relative_path: str) -> Path:
        """
        Resolve a path relative to base path.

        Args:
            relative_path: Path relative to base

        Returns:
            Absolute Path object
        """
        # Security: prevent directory traversal
        resolved = (self.base_path / relative_path).resolve()

        # Ensure the resolved path is within base_path
        try:
            resolved.relative_to(self.base_path)
        except ValueError as exc:
            raise ValueError(f"Path '{relative_path}' is outside base directory") from exc

        return resolved

    def write_file(
        self,
        relative_path: str,
        content: str,
        language: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> FileArtifact:
        """
        Write content to a file.

        Args:
            relative_path: Path relative to base
            content: File content
            language: Programming language
            metadata: Additional metadata

        Returns:
            FileArtifact representing the written file

        Example:
            >>> artifact = manager.write_file(
            ...     "myproject/main.py",
            ...     "print('hello')",
            ...     language="python"
            ... )
        """
        file_path = self._resolve_path(relative_path)

        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self._logger.info("File written", path=relative_path, size=len(content))

        return FileArtifact(
            path=str(file_path.relative_to(self.base_path)),
            content=content,
            language=language,
            metadata=metadata or {},
        )

    def read_file(self, relative_path: str) -> FileArtifact | None:
        """
        Read a file.

        Args:
            relative_path: Path relative to base

        Returns:
            FileArtifact or None if not found
        """
        file_path = self._resolve_path(relative_path)

        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        stat = file_path.stat()

        return FileArtifact(
            path=str(file_path.relative_to(self.base_path)),
            content=content,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
        )

    def delete_file(self, relative_path: str) -> bool:
        """
        Delete a file.

        Args:
            relative_path: Path relative to base

        Returns:
            True if deleted, False if not found
        """
        file_path = self._resolve_path(relative_path)

        if not file_path.exists():
            return False

        file_path.unlink()
        self._logger.info("File deleted", path=relative_path)

        return True

    def create_directory(self, relative_path: str) -> Path:
        """
        Create a directory.

        Args:
            relative_path: Path relative to base

        Returns:
            Created directory path
        """
        dir_path = self._resolve_path(relative_path)
        dir_path.mkdir(parents=True, exist_ok=True)

        self._logger.info("Directory created", path=relative_path)

        return dir_path

    def delete_directory(self, relative_path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.

        Args:
            relative_path: Path relative to base
            recursive: Whether to delete recursively

        Returns:
            True if deleted, False if not found
        """
        dir_path = self._resolve_path(relative_path)

        if not dir_path.exists():
            return False

        if recursive:
            shutil.rmtree(dir_path)
        else:
            dir_path.rmdir()

        self._logger.info("Directory deleted", path=relative_path, recursive=recursive)

        return True

    def list_files(
        self,
        relative_path: str = "",
        pattern: str = "*",
        recursive: bool = True,
    ) -> list[FileArtifact]:
        """
        List files in a directory.

        Args:
            relative_path: Path relative to base
            pattern: Glob pattern for filtering
            recursive: Whether to search recursively

        Returns:
            List of file artifacts
        """
        dir_path = self._resolve_path(relative_path)

        if not dir_path.exists():
            return []

        files = []

        if recursive:
            path_iterator = dir_path.rglob(pattern)
        else:
            path_iterator = dir_path.glob(pattern)

        for file_path in path_iterator:
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    stat = file_path.stat()

                    files.append(FileArtifact(
                        path=str(file_path.relative_to(self.base_path)),
                        content=content,
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                    ))
                except (OSError, UnicodeDecodeError) as exc:
                    self._logger.warning(
                        "Could not read file",
                        path=str(file_path),
                        error=str(exc),
                    )

        return files

    def get_project_structure(self, project_name: str) -> ProjectStructure:
        """
        Get the structure of a project.

        Args:
            project_name: Name of the project

        Returns:
            ProjectStructure with files and directories
        """
        project_path = self._resolve_path(project_name)

        if not project_path.exists():
            return ProjectStructure(
                root_path=str(project_path.relative_to(self.base_path)),
                name=project_name,
            )

        files = []
        directories = []

        for path in project_path.rglob("*"):
            relative = path.relative_to(self.base_path)

            if path.is_file():
                try:
                    with open(path, encoding="utf-8") as f:
                        content = f.read()

                    stat = path.stat()

                    files.append(FileArtifact(
                        path=str(relative),
                        content=content,
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                    ))
                except (OSError, UnicodeDecodeError):
                    pass
            elif path.is_dir():
                directories.append(str(relative))

        return ProjectStructure(
            root_path=str(project_path.relative_to(self.base_path)),
            name=project_name,
            files=files,
            directories=directories,
        )

    def copy_file(self, source: str, destination: str) -> FileArtifact | None:
        """
        Copy a file.

        Args:
            source: Source path relative to base
            destination: Destination path relative to base

        Returns:
            FileArtifact of the copied file
        """
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)

        if not source_path.exists():
            return None

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_path, dest_path)

        self._logger.info("File copied", source=source, destination=destination)

        return self.read_file(destination)

    def move_file(self, source: str, destination: str) -> FileArtifact | None:
        """
        Move a file.

        Args:
            source: Source path relative to base
            destination: Destination path relative to base

        Returns:
            FileArtifact of the moved file
        """
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)

        if not source_path.exists():
            return None

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(source_path), str(dest_path))

        self._logger.info("File moved", source=source, destination=destination)

        return self.read_file(destination)

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists."""
        return self._resolve_path(relative_path).exists()

    def get_file_size(self, relative_path: str) -> int:
        """Get file size in bytes."""
        file_path = self._resolve_path(relative_path)

        if not file_path.exists():
            return 0

        return file_path.stat().st_size
