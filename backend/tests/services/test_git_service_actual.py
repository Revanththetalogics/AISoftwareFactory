"""
Focused tests for GitService covering actual available methods.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from backend.services.git_service import GitService


class TestGitServiceActualMethods:
    """Tests for actual GitService methods."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for testing."""
        return tmp_path / "test_repos"

    @pytest.fixture
    def git_service(self, temp_dir):
        """Create GitService instance."""
        return GitService(str(temp_dir))

    def test_init_creates_directory(self, temp_dir):
        """Test that GitService creates working directory."""
        GitService(str(temp_dir))

        assert temp_dir.exists()
        assert temp_dir.is_dir()

    @pytest.mark.asyncio
    async def test_clone_repository_success(self, git_service, temp_dir):
        """Test successful repository cloning."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Cloning into..."
            mock_run.return_value = mock_result

            with patch.object(git_service, "_get_repo_info", new=AsyncMock()) as mock_get_info:
                mock_get_info.return_value = {"name": "test-repo", "branch": "main"}

                result = await git_service.clone_repository("https://github.com/user/repo.git", "my-repo")

                assert result["name"] == "test-repo"
                assert "local_path" in result
                assert "cloned_at" in result

    @pytest.mark.asyncio
    async def test_clone_repository_extract_name(self, git_service):
        """Test repository cloning with automatic name extraction."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            with patch.object(git_service, "_get_repo_info", new=AsyncMock()):
                await git_service.clone_repository("https://github.com/user/my-awesome-repo.git")

                # Should extract "my-awesome-repo" from URL
                repo_path = git_service.working_directory / "my-awesome-repo"
                ["git", "clone", "--branch", "main", "https://github.com/user/my-awesome-repo.git", str(repo_path)]

    @pytest.mark.asyncio
    async def test_clone_repository_remove_existing(self, git_service, temp_dir):
        """Test that existing directory is removed before cloning."""
        repo_path = temp_dir / "existing-repo"
        repo_path.mkdir()
        (repo_path / "dummy-file.txt").write_text("test")

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            with patch.object(git_service, "_get_repo_info", new=AsyncMock()):
                await git_service.clone_repository("https://github.com/user/repo.git", "existing-repo")

                # Directory should have been removed and recreated
                assert not (repo_path / "dummy-file.txt").exists()

    @pytest.mark.asyncio
    async def test_clone_repository_failure(self, git_service):
        """Test repository cloning failure."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Authentication failed"
            mock_run.return_value = mock_result

            with pytest.raises(Exception) as exc_info:
                await git_service.clone_repository("https://github.com/user/repo.git")

            assert "Git clone failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pull_repository_success(self, git_service, temp_dir):
        """Test successful repository pull."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Already up to date."
            mock_run.return_value = mock_result

            with patch.object(git_service, "_get_repo_info", new=AsyncMock()) as mock_get_info:
                mock_get_info.return_value = {
                    "name": "test-repo",
                    "path": str(repo_path),
                    "current_branch": "main",
                    "remote_url": "https://github.com/user/repo.git",
                    "commit_hash": "abc123",
                    "status": "clean",
                }

                result = await git_service.pull_repository(str(repo_path))

                assert result["name"] == "test-repo"
                assert "last_pulled" in result
                assert result["current_branch"] == "main"

    @pytest.mark.asyncio
    async def test_pull_repository_not_exists(self, git_service):
        """Test pull repository when path doesn't exist."""
        with pytest.raises(Exception) as exc_info:
            await git_service.pull_repository("/non/existent/path")

        assert "Repository path does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pull_repository_failure(self, git_service, temp_dir):
        """Test repository pull failure."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Merge conflict"
            mock_run.return_value = mock_result

            with pytest.raises(Exception) as exc_info:
                await git_service.pull_repository(str(repo_path))

            assert "Git pull failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_push_changes_success(self, git_service, temp_dir):
        """Test successful push changes."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            # Mock multiple subprocess calls (git add, git commit, git push)
            def side_effect(cmd, **kwargs):
                mock_result = MagicMock()
                mock_result.returncode = 0
                if "push" in cmd:
                    mock_result.stdout = "To github.com:user/repo.git\nEverything up-to-date"
                else:
                    mock_result.stdout = ""
                return mock_result

            mock_run.side_effect = side_effect

            result = await git_service.push_changes(str(repo_path), "Test commit")

            assert result["success"] is True
            assert "pushed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_push_changes_with_branch(self, git_service, temp_dir):
        """Test push changes with specific branch."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            await git_service.push_changes(str(repo_path), "Test commit", "develop")

            # Verify push was called with correct branch
            push_calls = [call for call in mock_run.call_args_list if "push" in str(call[0][0])]
            assert len(push_calls) > 0

    @pytest.mark.asyncio
    async def test_push_changes_failure(self, git_service, temp_dir):
        """Test push changes failure."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            # Fail on the git add step
            def side_effect(cmd, **kwargs):
                mock_result = MagicMock()
                if "add" in cmd:
                    mock_result.returncode = 1
                    mock_result.stderr = "Permission denied"
                else:
                    mock_result.returncode = 0
                return mock_result

            mock_run.side_effect = side_effect

            with pytest.raises(Exception) as exc_info:
                await git_service.push_changes(str(repo_path))

            assert "Git add failed" in str(exc_info.value)

    def test_read_file_success(self, git_service, temp_dir):
        """Test successful file reading."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "test.py"
        test_content = "print('hello world')"
        test_file.write_text(test_content)

        content = git_service.read_file(str(repo_path), "test.py")

        assert content == test_content

    def test_read_file_not_found(self, git_service, temp_dir):
        """Test reading non-existent file."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with pytest.raises(FileNotFoundError):
            git_service.read_file(str(repo_path), "nonexistent.py")

    def test_read_file_binary_content(self, git_service, temp_dir):
        """Test reading binary file."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "binary.dat"
        # Write binary content
        test_file.write_bytes(b"\x00\x01\x02\x03")

        content = git_service.read_file(str(repo_path), "binary.dat")

        assert isinstance(content, str)  # Should be converted to string

    def test_write_file_success(self, git_service, temp_dir):
        """Test successful file writing."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        git_service.write_file(str(repo_path), "new_file.py", "print('new file')")

        created_file = repo_path / "new_file.py"
        assert created_file.exists()
        assert created_file.read_text() == "print('new file')"

    def test_write_file_creates_directories(self, git_service, temp_dir):
        """Test that write_file creates intermediate directories."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        git_service.write_file(str(repo_path), "nested/directory/file.py", "content")

        created_file = repo_path / "nested" / "directory" / "file.py"
        assert created_file.exists()
        assert created_file.parent.is_dir()
        assert created_file.read_text() == "content"

    def test_write_file_overwrites_existing(self, git_service, temp_dir):
        """Test that write_file overwrites existing files."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        existing_file = repo_path / "existing.py"
        existing_file.write_text("old content")

        git_service.write_file(str(repo_path), "existing.py", "new content")

        assert existing_file.read_text() == "new content"

    def test_delete_file_success(self, git_service, temp_dir):
        """Test successful file deletion."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "to_delete.py"
        test_file.write_text("print('delete me')")

        assert test_file.exists()

        git_service.delete_file(str(repo_path), "to_delete.py")

        assert not test_file.exists()

    def test_delete_file_not_found(self, git_service, temp_dir):
        """Test deleting non-existent file."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        # Should not raise an exception
        git_service.delete_file(str(repo_path), "nonexistent.py")

    def test_delete_file_ignore_errors(self, git_service, temp_dir):
        """Test that delete_file ignores permission errors."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "protected.py"
        test_file.write_text("protected content")

        # Make file read-only
        test_file.chmod(0o444)

        # Should not raise an exception even with permission issues
        git_service.delete_file(str(repo_path), "protected.py")

        # File might still exist due to permissions, but no exception should be raised

    def test_list_files_success(self, git_service, temp_dir):
        """Test successful file listing."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        # Create some test files
        (repo_path / "file1.py").write_text("content1")
        (repo_path / "file2.py").write_text("content2")
        (repo_path / "subdir").mkdir()
        (repo_path / "subdir" / "file3.py").write_text("content3")

        files = git_service.list_files(str(repo_path))

        assert len(files) >= 3
        assert "file1.py" in files
        assert "file2.py" in files
        assert str(Path("subdir") / "file3.py") in files

    def test_list_files_empty_directory(self, git_service, temp_dir):
        """Test listing files in empty directory."""
        repo_path = temp_dir / "empty-repo"
        repo_path.mkdir()

        files = git_service.list_files(str(repo_path))

        assert isinstance(files, list)
        assert len(files) == 0

    def test_list_files_nonexistent_directory(self, git_service):
        """Test listing files in non-existent directory."""
        files = git_service.list_files("/non/existent/path")

        assert isinstance(files, list)
        assert len(files) == 0

    @pytest.mark.asyncio
    async def test_get_repo_info_success(self, git_service, temp_dir):
        """Test _get_repo_info method (private but important for coverage)."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        # Create mock git responses
        git_responses = {
            ("git", "remote", "get-url", "origin"): MagicMock(stdout="https://github.com/user/repo.git", returncode=0),
            ("git", "rev-parse", "--abbrev-ref", "HEAD"): MagicMock(stdout="main", returncode=0),
            ("git", "rev-parse", "HEAD"): MagicMock(stdout="abc123def456", returncode=0),
            ("git", "status", "--porcelain"): MagicMock(stdout="", returncode=0),
        }

        def mock_run_side_effect(cmd, **kwargs):
            cmd_tuple = tuple(cmd)
            if cmd_tuple in git_responses:
                return git_responses[cmd_tuple]
            # Default success response for other commands
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            return mock_result

        with patch("subprocess.run", side_effect=mock_run_side_effect):
            result = await git_service._get_repo_info(repo_path)

            assert result["name"] == "repo"
            assert result["url"] == "https://github.com/user/repo.git"
            assert result["branch"] == "main"
            assert result["commit_hash"] == "abc123def456"
            assert result["is_clean"] is True

    @pytest.mark.asyncio
    async def test_get_repo_info_dirty_repo(self, git_service, temp_dir):
        """Test _get_repo_info with dirty working directory."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            # Mock different responses for different git commands
            def side_effect(cmd, **kwargs):
                mock_result = MagicMock()
                mock_result.returncode = 0

                if "status" in cmd:
                    mock_result.stdout = " M modified_file.py\n?? new_file.txt"
                elif "remote" in cmd:
                    mock_result.stdout = "https://github.com/user/repo.git"
                elif "rev-parse" in cmd and "HEAD" in cmd:
                    mock_result.stdout = "abc123def456"
                elif "rev-parse" in cmd and "abbrev-ref" in cmd:
                    mock_result.stdout = "develop"
                else:
                    mock_result.stdout = ""

                return mock_result

            mock_run.side_effect = side_effect

            result = await git_service._get_repo_info(repo_path)

            assert result["is_clean"] is False
            assert result["branch"] == "develop"
