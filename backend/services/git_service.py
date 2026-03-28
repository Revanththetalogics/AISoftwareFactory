"""
Git Repository Management Service.

Provides Git operations for file synchronization including clone, pull, push,
and file operations within repositories.
"""

import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class GitService:
    """
    Git repository management service.

    Handles Git operations for file synchronization with remote repositories.
    """

    def __init__(self, working_directory: str = "./repositories"):
        """
        Initialize the Git service.

        Args:
            working_directory: Directory to store cloned repositories
        """
        self.working_directory = Path(working_directory)
        self.working_directory.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger(__name__)

    async def clone_repository(
        self,
        repo_url: str,
        destination_name: str | None = None,
        branch: str = "main"
    ) -> dict[str, Any]:
        """
        Clone a Git repository.

        Args:
            repo_url: Repository URL (HTTPS or SSH)
            destination_name: Local folder name (defaults to repo name)
            branch: Branch to checkout

        Returns:
            Repository information
        """
        try:
            # Extract repo name from URL if not provided
            if not destination_name:
                repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
                destination_name = repo_name

            repo_path = self.working_directory / destination_name

            # Remove existing directory if it exists
            if repo_path.exists():
                shutil.rmtree(repo_path)

            # Clone repository
            cmd = ["git", "clone", "--branch", branch, repo_url, str(repo_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.working_directory)
            )

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            # Get repository info
            repo_info = await self._get_repo_info(repo_path)
            repo_info.update({
                "local_path": str(repo_path),
                "cloned_at": datetime.now(UTC).isoformat()
            })

            self._logger.info(
                "Repository cloned successfully",
                repo_url=repo_url,
                local_path=str(repo_path)
            )

            return repo_info
        except Exception as e:
            self._logger.error("Failed to clone repository", error=str(e), repo_url=repo_url)
            raise

    async def pull_repository(self, repo_path: str) -> dict[str, Any]:
        """
        Pull latest changes from a repository.

        Args:
            repo_path: Local repository path

        Returns:
            Updated repository information
        """
        try:
            path = Path(repo_path)
            if not path.exists():
                raise Exception(f"Repository path does not exist: {repo_path}")

            # Pull changes
            cmd = ["git", "pull"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(path)
            )

            if result.returncode != 0:
                raise Exception(f"Git pull failed: {result.stderr}")

            # Get updated info
            repo_info = await self._get_repo_info(path)
            repo_info["last_pulled"] = datetime.now(UTC).isoformat()

            self._logger.info("Repository pulled successfully", local_path=repo_path)
            return repo_info
        except Exception as e:
            self._logger.error("Failed to pull repository", error=str(e), repo_path=repo_path)
            raise

    async def push_changes(
        self,
        repo_path: str,
        commit_message: str = "Auto-commit from ThetaAI",
        branch: str = "main"
    ) -> dict[str, Any]:
        """
        Push changes to remote repository.

        Args:
            repo_path: Local repository path
            commit_message: Commit message
            branch: Target branch

        Returns:
            Push result information
        """
        try:
            path = Path(repo_path)
            if not path.exists():
                raise Exception(f"Repository path does not exist: {repo_path}")

            # Add all changes
            add_cmd = ["git", "add", "."]
            add_result = subprocess.run(
                add_cmd,
                capture_output=True,
                text=True,
                cwd=str(path)
            )

            if add_result.returncode != 0:
                raise Exception(f"Git add failed: {add_result.stderr}")

            # Commit changes
            commit_cmd = ["git", "commit", "-m", commit_message]
            commit_result = subprocess.run(
                commit_cmd,
                capture_output=True,
                text=True,
                cwd=str(path)
            )

            # If nothing to commit, that's fine
            if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout.lower():
                raise Exception(f"Git commit failed: {commit_result.stderr}")

            # Push changes
            push_cmd = ["git", "push", "origin", branch]
            push_result = subprocess.run(
                push_cmd,
                capture_output=True,
                text=True,
                cwd=str(path)
            )

            if push_result.returncode != 0:
                raise Exception(f"Git push failed: {push_result.stderr}")

            result = {
                "success": True,
                "commit_message": commit_message,
                "branch": branch,
                "pushed_at": datetime.now(UTC).isoformat(),
                "stdout": push_result.stdout
            }

            self._logger.info("Changes pushed successfully", local_path=repo_path)
            return result
        except Exception as e:
            self._logger.error("Failed to push changes", error=str(e), repo_path=repo_path)
            raise

    async def list_files(self, repo_path: str, relative_path: str = ".") -> list[dict[str, Any]]:
        """
        List files in a repository directory.

        Args:
            repo_path: Local repository path
            relative_path: Relative path within repository

        Returns:
            List of file information
        """
        try:
            base_path = Path(repo_path)
            target_path = base_path / relative_path

            if not target_path.exists():
                return []

            files = []
            for item in target_path.iterdir():
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                    "path": str(item.relative_to(base_path)),
                    "is_binary": await self._is_binary_file(item) if item.is_file() else False
                })

            # Sort directories first, then files
            files.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            return files
        except Exception as e:
            self._logger.error("Failed to list files", error=str(e), repo_path=repo_path)
            raise

    async def read_file(self, repo_path: str, file_path: str) -> dict[str, Any]:
        """
        Read file content from repository.

        Args:
            repo_path: Local repository path
            file_path: Path to file within repository

        Returns:
            File content and metadata
        """
        try:
            full_path = Path(repo_path) / file_path

            if not full_path.exists():
                raise Exception(f"File not found: {file_path}")

            if not full_path.is_file():
                raise Exception(f"Not a file: {file_path}")

            # Check if binary file
            is_binary = await self._is_binary_file(full_path)

            content = None
            if not is_binary:
                try:
                    content = full_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # Try different encodings
                    try:
                        content = full_path.read_text(encoding='latin-1')
                    except UnicodeDecodeError:
                        content = "[Binary file - content not readable]"

            stat = full_path.stat()

            return {
                "path": file_path,
                "content": content,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                "is_binary": is_binary,
                "encoding": "binary" if is_binary else "utf-8"
            }
        except Exception as e:
            self._logger.error("Failed to read file", error=str(e), file_path=file_path)
            raise

    async def write_file(
        self,
        repo_path: str,
        file_path: str,
        content: str,
        create_parents: bool = True
    ) -> dict[str, Any]:
        """
        Write file content to repository.

        Args:
            repo_path: Local repository path
            file_path: Path to file within repository
            content: File content
            create_parents: Create parent directories if they don't exist

        Returns:
            Write result information
        """
        try:
            full_path = Path(repo_path) / file_path

            if create_parents:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            full_path.write_text(content, encoding='utf-8')

            stat = full_path.stat()

            result = {
                "path": file_path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                "written_at": datetime.now(UTC).isoformat()
            }

            self._logger.info("File written successfully", file_path=file_path)
            return result
        except Exception as e:
            self._logger.error("Failed to write file", error=str(e), file_path=file_path)
            raise

    async def delete_file(self, repo_path: str, file_path: str) -> dict[str, Any]:
        """
        Delete file from repository.

        Args:
            repo_path: Local repository path
            file_path: Path to file within repository

        Returns:
            Delete result information
        """
        try:
            full_path = Path(repo_path) / file_path

            if not full_path.exists():
                raise Exception(f"File not found: {file_path}")

            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()

            result = {
                "path": file_path,
                "deleted_at": datetime.now(UTC).isoformat()
            }

            self._logger.info("File deleted successfully", file_path=file_path)
            return result
        except Exception as e:
            self._logger.error("Failed to delete file", error=str(e), file_path=file_path)
            raise

    async def _get_repo_info(self, repo_path: Path) -> dict[str, Any]:
        """Get repository information."""
        try:
            # Get current branch
            branch_cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
            branch_result = subprocess.run(
                branch_cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_path)
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Get remote URL
            remote_cmd = ["git", "remote", "get-url", "origin"]
            remote_result = subprocess.run(
                remote_cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_path)
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else None

            # Get commit hash
            hash_cmd = ["git", "rev-parse", "HEAD"]
            hash_result = subprocess.run(
                hash_cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_path)
            )
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"

            return {
                "name": repo_path.name,
                "path": str(repo_path),
                "current_branch": current_branch,
                "remote_url": remote_url,
                "commit_hash": commit_hash,
                "status": "clean"  # Simplified status
            }
        except Exception:
            return {
                "name": repo_path.name,
                "path": str(repo_path),
                "current_branch": "unknown",
                "remote_url": None,
                "commit_hash": "unknown",
                "status": "unknown"
            }

    async def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            # Read first 1024 bytes
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)

            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True

            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True
        except Exception:
            return True
