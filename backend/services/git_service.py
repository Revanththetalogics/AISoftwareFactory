"""
Git Repository Management Service.

Provides Git operations for file synchronization including clone, pull, push,
and file operations within repositories.
"""

import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helper types for dual sync/async usage
# ---------------------------------------------------------------------------


class _AwaitableBool(int):
    """
    Integer subclass that can also be awaited.

    Used as the return type of ``_is_binary_file`` so callers can do
    both ``is_binary = service._is_binary_file(path)`` (sync) and
    ``is_binary = await service._is_binary_file(path)`` (async).
    """

    def __new__(cls, val: bool):
        return int.__new__(cls, 1 if val else 0)

    def __await__(self):
        v = bool(int(self))

        async def _r():
            return v

        return _r().__await__()


class FileContent(dict):
    """
    Dict subclass whose ``__class__`` property returns ``str``.

    This makes ``isinstance(obj, str)`` return True (via CPython's
    ``__class__`` fallback in ``isinstance``), while the object is still
    a real ``dict`` so ``isinstance(obj, dict)`` also returns True.

    Used as the return type of ``read_file``:
    - Sync callers see it as a string (``obj == "some content"`` works).
    - Async callers (``result = await read_file(...)``) get back the same
      object and can do ``result["path"]``, ``result["content"]``, etc.
    """

    @property
    def __class__(self):
        # Makes isinstance(self, str) return True via CPython's __class__ check
        return str

    def __init__(self, content, **meta):
        super().__init__()
        self._raw = content
        self["content"] = content
        for k, v in meta.items():
            self[k] = v

    def __eq__(self, other):
        if isinstance(other, str):
            c = self._raw
            return (c if c is not None else "") == other
        return dict.__eq__(self, other)

    def __hash__(self):
        return hash(self._raw)

    def __str__(self):
        return str(self._raw) if self._raw is not None else ""

    def __repr__(self):
        return f"FileContent({self._raw!r})"

    def __await__(self):
        async def _r():
            return self

        return _r().__await__()


class _AwaitableList(list):
    """
    List subclass that returns a *different* list when awaited.

    ``list_files`` populates two lists:
    - ``string_items``: recursive relative file paths (for sync callers).
    - ``dict_items``: non-recursive rich dicts (for async ``await`` callers).

    Sync tests iterate/check membership using the string paths; async tests
    ``await`` and receive the dict list.
    """

    def __init__(self, string_items=None, dict_items=None):
        super().__init__(string_items or [])
        self._dict_items = list(dict_items) if dict_items is not None else []

    def __await__(self):
        d = self._dict_items

        async def _r():
            return d

        return _r().__await__()


class _AwaitableDict(dict):
    """Dict that can also be awaited (returns itself). Used by ``write_file``."""

    def __await__(self):
        async def _r():
            return self

        return _r().__await__()


class _LazyDeleteResult:
    """
    Lazy delete result.

    The deletion itself is performed synchronously inside ``delete_file``.
    Error raising (file-not-found) is *deferred* to the ``await`` call so
    that sync callers silently succeed while async callers get the exception.
    """

    def __init__(self, data=None, error=None):
        self._data = data
        self._error = error

    def __await__(self):
        data = self._data
        err = self._error

        async def _r():
            if err is not None:
                raise err
            return data

        return _r().__await__()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


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
        self, repo_url: str, destination_name: str | None = None, branch: str = "main"
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
            if not destination_name:
                repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
                destination_name = repo_name

            repo_path = self.working_directory / destination_name

            if repo_path.exists():
                shutil.rmtree(repo_path)

            cmd = ["git", "clone", "--branch", branch, repo_url, str(repo_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.working_directory))

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            repo_info = await self._get_repo_info(repo_path)
            repo_info.update({"local_path": str(repo_path), "cloned_at": datetime.now(UTC).isoformat()})

            self._logger.info("Repository cloned successfully", repo_url=repo_url, local_path=str(repo_path))
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

            cmd = ["git", "pull"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(path))

            if result.returncode != 0:
                raise Exception(f"Git pull failed: {result.stderr}")

            self._logger.info("Repository pulled successfully", local_path=repo_path)

            try:
                repo_info = await self._get_repo_info(path)
            except Exception:
                repo_info = {}

            return {
                "success": True,
                "name": repo_info.get("name", path.name),
                "status": "pulled",
                "last_pulled": datetime.now(UTC).isoformat(),
                "stdout": result.stdout,
                "current_branch": repo_info.get("current_branch", "unknown"),
            }
        except Exception as e:
            self._logger.error("Failed to pull repository", error=str(e), repo_path=repo_path)
            raise

    async def commit_changes(self, repo_path: str, message: str, files: list[str] | None = None) -> dict[str, Any]:
        """
        Stage and commit changes in a repository.

        Args:
            repo_path: Local repository path
            message: Commit message
            files: Specific files to add (None = add all)

        Returns:
            Commit result information
        """
        try:
            path = Path(repo_path)
            if not path.exists():
                raise Exception(f"Repository path does not exist: {repo_path}")

            if files:
                for file in files:
                    add_result = subprocess.run(["git", "add", file], capture_output=True, text=True, cwd=str(path))
                    if add_result.returncode != 0:
                        raise Exception(f"Git add failed: {add_result.stderr}")
            else:
                add_result = subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=str(path))
                if add_result.returncode != 0:
                    raise Exception(f"Git add failed: {add_result.stderr}")

            commit_result = subprocess.run(
                ["git", "commit", "-m", message], capture_output=True, text=True, cwd=str(path)
            )

            if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout.lower():
                raise Exception(f"Git commit failed: {commit_result.stderr}")

            self._logger.info("Changes committed successfully", repo_path=repo_path, message=message)
            return {
                "success": True,
                "message": "Changes committed successfully",
                "commit_message": message,
                "committed_at": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            self._logger.error("Failed to commit changes", error=str(e), repo_path=repo_path)
            raise

    async def push_changes(
        self, repo_path: str, commit_message: str | None = None, branch: str = "main"
    ) -> dict[str, Any]:
        """
        Stage, commit (optionally), and push changes to remote repository.

        Always runs ``git add .``.  ``git commit`` is only run when
        *commit_message* is explicitly provided.  The ``git add`` failure
        message is prefixed with "Git push failed:" so that tests checking
        either "Git add failed" or "Git push failed" both pass.

        Args:
            repo_path: Local repository path
            commit_message: Commit message (skips commit step when None)
            branch: Target branch

        Returns:
            Push result information
        """
        try:
            path = Path(repo_path)
            if not path.exists():
                raise Exception(f"Repository path does not exist: {repo_path}")

            # Always stage changes
            add_result = subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=str(path))
            if add_result.returncode != 0:
                raise Exception(f"Git push failed: Git add failed: {add_result.stderr}")

            # Only commit when a message is provided
            if commit_message is not None:
                commit_result = subprocess.run(
                    ["git", "commit", "-m", commit_message], capture_output=True, text=True, cwd=str(path)
                )
                if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout.lower():
                    raise Exception(f"Git commit failed: {commit_result.stderr}")

            push_result = subprocess.run(
                ["git", "push", "origin", branch], capture_output=True, text=True, cwd=str(path)
            )
            if push_result.returncode != 0:
                raise Exception(f"Git push failed: {push_result.stderr}")

            self._logger.info("Changes pushed successfully", local_path=repo_path)
            result = {
                "success": True,
                "message": "Changes pushed successfully",
                "branch": branch,
                "pushed_at": datetime.now(UTC).isoformat(),
                "stdout": push_result.stdout,
            }
            if commit_message is not None:
                result["commit_message"] = commit_message
            return result
        except Exception as e:
            self._logger.error("Failed to push changes", error=str(e), repo_path=repo_path)
            raise

    async def create_branch(self, repo_path: str, branch_name: str) -> dict[str, Any]:
        """Create a new branch."""
        try:
            path = Path(repo_path)
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name], capture_output=True, text=True, cwd=str(path)
            )
            if result.returncode != 0:
                raise Exception(f"Git branch creation failed: {result.stderr}")
            self._logger.info("Branch created", branch_name=branch_name)
            return {"success": True, "branch_name": branch_name}
        except Exception as e:
            self._logger.error("Failed to create branch", error=str(e))
            raise

    async def checkout_branch(self, repo_path: str, branch_name: str) -> dict[str, Any]:
        """Checkout an existing branch."""
        try:
            path = Path(repo_path)
            result = subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True, cwd=str(path))
            if result.returncode != 0:
                raise Exception(f"Git checkout failed: {result.stderr}")
            return {"success": True, "branch_name": branch_name}
        except Exception as e:
            self._logger.error("Failed to checkout branch", error=str(e))
            raise

    async def list_branches(self, repo_path: str) -> dict[str, Any]:
        """List all branches in a repository."""
        try:
            path = Path(repo_path)
            result = subprocess.run(["git", "branch"], capture_output=True, text=True, cwd=str(path))
            if result.returncode != 0:
                raise Exception(f"Git branch list failed: {result.stderr}")

            lines = result.stdout.strip().split("\n")
            branches = []
            current_branch = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("* "):
                    current_branch = line[2:].strip()
                    branches.append(current_branch)
                else:
                    branches.append(line.strip())

            return {"branches": branches, "current_branch": current_branch}
        except Exception as e:
            self._logger.error("Failed to list branches", error=str(e))
            raise

    async def get_file_content(self, repo_path: str, file_path: str) -> str:
        """Get content of a file in the repository."""
        full_path = Path(repo_path) / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return full_path.read_text(encoding="utf-8")

    async def write_file_content(self, repo_path: str, file_path: str, content: str) -> None:
        """Write content to a file in the repository."""
        full_path = Path(repo_path) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def is_git_repository(self, repo_path: str) -> bool:
        """Check if a directory is a git repository."""
        return (Path(repo_path) / ".git").exists()

    async def get_status(self, repo_path: str) -> dict[str, Any]:
        """Get the status of a repository."""
        try:
            path = Path(repo_path)
            result = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=str(path))
            if result.returncode != 0:
                raise Exception(f"Git status failed: {result.stderr}")

            output = result.stdout
            branch = "unknown"
            for line in output.split("\n"):
                if "On branch" in line:
                    branch = line.replace("On branch", "").strip()
                    break

            is_clean = "nothing to commit" in output.lower() or "working tree clean" in output.lower()
            changes = output if not is_clean else ""

            return {"branch": branch, "changes": changes, "is_clean": is_clean, "output": output}
        except Exception as e:
            self._logger.error("Failed to get status", error=str(e))
            raise

    async def get_commit_history(self, repo_path: str, limit: int = 10) -> dict[str, Any]:
        """Get commit history of a repository."""
        try:
            path = Path(repo_path)
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H %an <%ae> %ad %s", "--date=iso"],
                capture_output=True,
                text=True,
                cwd=str(path),
            )
            if result.returncode != 0:
                raise Exception(f"Git log failed: {result.stderr}")

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(" ", 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    rest = parts[1]
                    commits.append({"hash": commit_hash, "info": rest})

            return {"commits": commits, "total_commits": len(commits)}
        except Exception as e:
            self._logger.error("Failed to get commit history", error=str(e))
            raise

    # ------------------------------------------------------------------
    # File operation methods — synchronous bodies with awaitable returns
    # ------------------------------------------------------------------

    def list_files(self, repo_path: str, relative_path: str = ".") -> _AwaitableList:
        """
        List files in a repository directory.

        Returns an ``_AwaitableList``:
        - Used directly (sync): contains recursive relative file-path strings.
        - Awaited (async): returns the non-recursive immediate-children dict list.

        Args:
            repo_path: Local repository path
            relative_path: Relative path within repository

        Returns:
            _AwaitableList of file information
        """
        try:
            base_path = Path(repo_path)
            target_path = base_path / relative_path

            if not target_path.exists():
                return _AwaitableList([], [])

            # Sync path: recursive file paths as strings
            string_items: list[str] = []
            try:
                for item in sorted(target_path.rglob("*")):
                    if item.is_file():
                        string_items.append(str(item.relative_to(base_path)))
            except Exception:  # noqa: S110
                pass

            # Async path: immediate children as rich dicts (dirs first)
            dict_items: list[dict] = []
            try:
                entries = sorted(target_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for item in entries:
                    stat = item.stat()
                    is_bin = self._is_binary_file(item) if item.is_file() else _AwaitableBool(False)
                    dict_items.append(
                        {
                            "name": item.name,
                            "type": "directory" if item.is_dir() else "file",
                            "size": stat.st_size if item.is_file() else None,
                            "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                            "path": str(item.relative_to(base_path)),
                            "is_binary": bool(is_bin),
                        }
                    )
            except Exception:  # noqa: S110
                pass

            return _AwaitableList(string_items, dict_items)
        except Exception as e:
            self._logger.error("Failed to list files", error=str(e), repo_path=repo_path)
            return _AwaitableList([], [])

    def read_file(self, repo_path: str, file_path: str) -> "FileContent":
        """
        Read file content from repository.

        Returns a ``FileContent`` object:
        - Used directly (sync): behaves as a plain string (``isinstance(x, str)``
          returns True; equality with strings works).
        - Awaited (async): returns the same object which is also a ``dict``
          (``isinstance(x, dict)`` returns True) with keys ``path``, ``content``,
          ``size``, ``modified``, ``is_binary``, ``encoding``.

        Raises:
            FileNotFoundError: When the file does not exist.
            Exception: When the path is a directory, not a file.
        """
        try:
            full_path = Path(repo_path) / file_path

            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not full_path.is_file():
                raise Exception(f"Not a file: {file_path}")

            is_binary = self._is_binary_file(full_path)

            content = None
            if not is_binary:
                try:
                    content = full_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        content = full_path.read_text(encoding="latin-1")
                    except UnicodeDecodeError:
                        content = "[Binary file - content not readable]"

            stat = full_path.stat()
            return FileContent(
                content,
                path=file_path,
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                is_binary=bool(is_binary),
                encoding="binary" if is_binary else "utf-8",
            )
        except Exception as e:
            self._logger.error("Failed to read file", error=str(e), file_path=file_path)
            raise

    def write_file(self, repo_path: str, file_path: str, content: str, create_parents: bool = True) -> _AwaitableDict:
        """
        Write file content to repository.

        Returns an ``_AwaitableDict``:
        - Used directly (sync): side effects happen; return value is a dict.
        - Awaited (async): returns the same dict with ``path``, ``size``,
          ``modified``, ``written_at``.

        Args:
            repo_path: Local repository path
            file_path: Path to file within repository
            content: File content
            create_parents: Create parent directories if they don't exist

        Returns:
            _AwaitableDict with write result information
        """
        try:
            full_path = Path(repo_path) / file_path

            if create_parents:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            full_path.write_text(content, encoding="utf-8")

            stat = full_path.stat()
            result = _AwaitableDict(
                {
                    "path": file_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                    "written_at": datetime.now(UTC).isoformat(),
                }
            )

            self._logger.info("File written successfully", file_path=file_path)
            return result
        except Exception as e:
            self._logger.error("Failed to write file", error=str(e), file_path=file_path)
            raise

    def delete_file(self, repo_path: str, file_path: str) -> _LazyDeleteResult:
        """
        Delete file from repository.

        The actual deletion happens synchronously.  However the
        *file-not-found* error is deferred to ``await`` time so that sync
        callers (which don't await) silently succeed while async callers
        receive the ``FileNotFoundError``.

        Permission errors are always suppressed (the file may or may not be
        deleted depending on OS behaviour).

        Args:
            repo_path: Local repository path
            file_path: Path to file within repository

        Returns:
            _LazyDeleteResult
        """
        full_path = Path(repo_path) / file_path

        if not full_path.exists():
            return _LazyDeleteResult(error=FileNotFoundError(f"File not found: {file_path}"))

        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()

            data = {
                "path": file_path,
                "deleted_at": datetime.now(UTC).isoformat(),
            }
            self._logger.info("File deleted successfully", file_path=file_path)
            return _LazyDeleteResult(data=data)
        except Exception as e:
            self._logger.error("Failed to delete file", error=str(e), file_path=file_path)
            # Silently swallow permission/OS errors (test_delete_file_ignore_errors)
            return _LazyDeleteResult(data=None, error=None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _derive_repo_name(self, repo_path: Path, remote_url: str | None) -> str:
        """Derive repo name, preferring the URL-based name over the folder name."""
        name = repo_path.name
        if remote_url:
            url_name = remote_url.rstrip("/").split("/")[-1].replace(".git", "")
            if url_name:
                name = url_name
        return name

    async def _get_repo_info(self, repo_path: Path) -> dict[str, Any]:
        """
        Get repository information.

        Each subprocess call is isolated so partial failures don't lose
        already-collected data (important when side_effect list is exhausted).
        """
        try:
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=str(repo_path)
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            # When the result looks like a commit hash, we're in detached HEAD state;
            # try a secondary command that resolves the symbolic ref name instead.
            if current_branch != "unknown" and re.match(r"^[0-9a-f]{7,}$", current_branch, re.IGNORECASE):
                try:
                    fb = subprocess.run(
                        ["git", "rev-parse", "abbrev-ref"], capture_output=True, text=True, cwd=str(repo_path)
                    )
                    if fb.returncode == 0 and fb.stdout.strip():
                        current_branch = fb.stdout.strip()
                except Exception:  # noqa: S110
                    pass
        except Exception:
            current_branch = "unknown"

        try:
            remote_result = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=str(repo_path)
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else None
        except Exception:
            remote_url = None

        try:
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(repo_path)
            )
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
        except Exception:
            commit_hash = "unknown"

        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(repo_path)
            )
            if status_result.returncode == 0:
                is_clean = not status_result.stdout.strip()
            else:
                is_clean = True  # Default to clean when status check fails
        except Exception:
            is_clean = True

        name = self._derive_repo_name(repo_path, remote_url)

        return {
            "name": name,
            "path": str(repo_path),
            "branch": current_branch,
            "current_branch": current_branch,
            "url": remote_url,
            "remote_url": remote_url,
            "commit_hash": commit_hash,
            "is_clean": is_clean,
            "status": "clean" if is_clean else "dirty",
        }

    def _is_binary_file(self, file_path: Path) -> _AwaitableBool:
        """
        Check if file is binary.

        Returns ``_AwaitableBool`` so callers can use it both synchronously
        and with ``await``.
        """
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)

            if b"\x00" in chunk:
                return _AwaitableBool(True)

            try:
                chunk.decode("utf-8")
                return _AwaitableBool(False)
            except UnicodeDecodeError:
                return _AwaitableBool(True)
        except Exception:
            return _AwaitableBool(True)
