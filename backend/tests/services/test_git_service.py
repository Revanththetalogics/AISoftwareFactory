"""
Comprehensive tests for GitService to improve coverage from 13% to 90%+.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from backend.services.git_service import GitService


class TestGitService:
    """Tests for GitService class."""

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

    def test_init_with_default_directory(self):
        """Test GitService with default directory."""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            GitService()

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

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

                # Verify subprocess was called correctly
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "git" in call_args
                assert "clone" in call_args
                assert "--branch" in call_args
                assert "main" in call_args

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
                expected_cmd = [
                    "git",
                    "clone",
                    "--branch",
                    "main",
                    "https://github.com/user/my-awesome-repo.git",
                    str(repo_path),
                ]

                call_args = mock_run.call_args[0][0]
                assert call_args == expected_cmd

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
                mock_run.assert_called_once()

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
            assert "Authentication failed" in str(exc_info.value)

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

            result = await git_service.pull_repository(str(repo_path))

            assert "status" in result
            assert "name" in result
            mock_run.assert_called_once()

            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "pull" in call_args

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
    async def test_get_repo_info_success(self, git_service, temp_dir):
        """Test successful repository info retrieval."""
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
        """Test repository info with dirty working directory."""
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

    @pytest.mark.asyncio
    async def test_commit_changes_success(self, git_service, temp_dir):
        """Test successful commit changes."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = await git_service.commit_changes(str(repo_path), "Test commit message")

            assert result["success"] is True
            assert "committed" in result["message"].lower()

            # Should have called git add and git commit
            assert mock_run.call_count >= 2

    @pytest.mark.asyncio
    async def test_commit_changes_with_files(self, git_service, temp_dir):
        """Test commit changes with specific files."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = await git_service.commit_changes(str(repo_path), "Test commit", files=["file1.py", "file2.py"])

            assert result["success"] is True
            # Verify specific files were added
            add_calls = [call for call in mock_run.call_args_list if "add" in str(call)]
            assert len(add_calls) > 0

    @pytest.mark.asyncio
    async def test_push_changes_success(self, git_service, temp_dir):
        """Test successful push changes."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "To github.com:user/repo.git\nEverything up-to-date"
            mock_run.return_value = mock_result

            result = await git_service.push_changes(str(repo_path))

            assert result["success"] is True
            assert "pushed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_push_changes_failure(self, git_service, temp_dir):
        """Test push changes failure."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Permission denied"
            mock_run.return_value = mock_result

            with pytest.raises(Exception) as exc_info:
                await git_service.push_changes(str(repo_path))

            assert "Git push failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_branch_success(self, git_service, temp_dir):
        """Test successful branch creation."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = await git_service.create_branch(str(repo_path), "feature/new-feature")

            assert result["success"] is True
            assert result["branch_name"] == "feature/new-feature"

    @pytest.mark.asyncio
    async def test_checkout_branch_success(self, git_service, temp_dir):
        """Test successful branch checkout."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = await git_service.checkout_branch(str(repo_path), "develop")

            assert result["success"] is True
            assert result["branch_name"] == "develop"

    @pytest.mark.asyncio
    async def test_list_branches(self, git_service, temp_dir):
        """Test listing repository branches."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "* main\n  develop\n  feature/branch1"
            mock_run.return_value = mock_result

            result = await git_service.list_branches(str(repo_path))

            assert len(result["branches"]) == 3
            assert "main" in result["branches"]
            assert "develop" in result["branches"]
            assert "feature/branch1" in result["branches"]
            assert result["current_branch"] == "main"

    @pytest.mark.asyncio
    async def test_get_file_content_success(self, git_service, temp_dir):
        """Test successful file content retrieval."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "test.py"
        test_file.write_text("print('hello world')")

        content = await git_service.get_file_content(str(repo_path), "test.py")

        assert content == "print('hello world')"

    @pytest.mark.asyncio
    async def test_get_file_content_not_found(self, git_service, temp_dir):
        """Test file content retrieval for non-existent file."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with pytest.raises(FileNotFoundError):
            await git_service.get_file_content(str(repo_path), "nonexistent.py")

    @pytest.mark.asyncio
    async def test_write_file_content_success(self, git_service, temp_dir):
        """Test successful file writing."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        await git_service.write_file_content(str(repo_path), "new_file.py", "print('new file')")

        created_file = repo_path / "new_file.py"
        assert created_file.exists()
        assert created_file.read_text() == "print('new file')"

    @pytest.mark.asyncio
    async def test_delete_file_success(self, git_service, temp_dir):
        """Test successful file deletion."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        test_file = repo_path / "to_delete.py"
        test_file.write_text("print('delete me')")

        assert test_file.exists()

        await git_service.delete_file(str(repo_path), "to_delete.py")

        assert not test_file.exists()

    def test_is_git_repository_true(self, git_service, temp_dir):
        """Test checking if directory is a git repository (true case)."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        result = git_service.is_git_repository(str(repo_path))

        assert result is True

    def test_is_git_repository_false(self, git_service, temp_dir):
        """Test checking if directory is a git repository (false case)."""
        repo_path = temp_dir / "not-a-repo"
        repo_path.mkdir()

        result = git_service.is_git_repository(str(repo_path))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_status_success(self, git_service, temp_dir):
        """Test getting repository status."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "On branch main\nChanges not staged for commit:\n  modified:   file1.py"
            mock_run.return_value = mock_result

            result = await git_service.get_status(str(repo_path))

            assert "branch" in result
            assert "changes" in result
            assert result["is_clean"] is False

    @pytest.mark.asyncio
    async def test_get_commit_history(self, git_service, temp_dir):
        """Test getting commit history."""
        repo_path = temp_dir / "test-repo"
        repo_path.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "abc123 Author One <author1@example.com> 2026-03-29 10:00:00 +0000 Initial commit\n"
            mock_result.stdout += "def456 Author Two <author2@example.com> 2026-03-29 11:00:00 +0000 Second commit"
            mock_run.return_value = mock_result

            result = await git_service.get_commit_history(str(repo_path), limit=10)

            assert len(result["commits"]) == 2
            assert result["commits"][0]["hash"] == "abc123"
            assert result["commits"][1]["hash"] == "def456"
            assert result["total_commits"] == 2
