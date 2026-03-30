"""
Comprehensive tests for GitService to increase coverage.
"""

import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
from datetime import datetime, UTC

from backend.services.git_service import GitService


class TestGitService:
    """Comprehensive tests for GitService."""

    @pytest.fixture
    def git_service(self):
        """Create GitService instance with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = GitService(temp_dir)
            yield service

    @pytest.fixture
    def mock_subprocess_result(self):
        """Create mock subprocess result."""
        result = MagicMock()
        result.returncode = 0
        result.stdout = "success"
        result.stderr = ""
        return result

    def test_init(self, git_service):
        """Test GitService initialization."""
        assert git_service is not None
        assert hasattr(git_service, 'working_directory')
        assert isinstance(git_service.working_directory, Path)
        assert git_service.working_directory.exists()
        assert hasattr(git_service, '_logger')

    @pytest.mark.asyncio
    async def test_clone_repository_success(self, git_service, mock_subprocess_result):
        """Test cloning repository successfully."""
        with patch('subprocess.run', return_value=mock_subprocess_result) as mock_run:
            with patch.object(git_service, '_get_repo_info', return_value={'name': 'test-repo'}) as mock_get_info:
                result = await git_service.clone_repository(
                    repo_url="https://github.com/user/repo.git",
                    destination_name="my-repo",
                    branch="main"
                )
                
                assert result is not None
                assert isinstance(result, dict)
                assert result['name'] == 'test-repo'
                assert 'local_path' in result
                assert 'cloned_at' in result
                
                # Verify subprocess call
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert call_args[0] == "git"
                assert call_args[1] == "clone"
                assert call_args[3] == "main"  # branch
                assert call_args[4] == "https://github.com/user/repo.git"

    @pytest.mark.asyncio
    async def test_clone_repository_auto_name_extraction(self, git_service, mock_subprocess_result):
        """Test cloning repository with automatic name extraction."""
        with patch('subprocess.run', return_value=mock_subprocess_result):
            with patch.object(git_service, '_get_repo_info', return_value={'name': 'extracted-repo'}):
                result = await git_service.clone_repository(
                    repo_url="https://github.com/user/my-awesome-project.git"
                )
                
                assert result is not None
                assert result['name'] == 'extracted-repo'

    @pytest.mark.asyncio
    async def test_clone_repository_remove_existing(self, git_service, mock_subprocess_result):
        """Test that existing directory is removed before cloning."""
        # Create existing directory
        existing_path = git_service.working_directory / "existing-repo"
        existing_path.mkdir()
        
        with patch('subprocess.run', return_value=mock_subprocess_result):
            with patch.object(git_service, '_get_repo_info', return_value={'name': 'test'}):
                with patch('shutil.rmtree') as mock_rmtree:
                    await git_service.clone_repository(
                        repo_url="https://github.com/user/repo.git",
                        destination_name="existing-repo"
                    )
                    
                    # Should have removed existing directory
                    mock_rmtree.assert_called_once_with(existing_path)

    @pytest.mark.asyncio
    async def test_clone_repository_git_failure(self, git_service):
        """Test cloning repository when git command fails."""
        failed_result = MagicMock()
        failed_result.returncode = 1
        failed_result.stderr = "Authentication failed"
        
        with patch('subprocess.run', return_value=failed_result):
            with pytest.raises(Exception) as exc_info:
                await git_service.clone_repository("https://github.com/user/repo.git")
            
            assert "Git clone failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pull_repository_success(self, git_service, mock_subprocess_result):
        """Test pulling repository successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        with patch('subprocess.run', return_value=mock_subprocess_result) as mock_run:
            with patch.object(git_service, '_get_repo_info', return_value={'name': 'test-repo'}) as mock_get_info:
                result = await git_service.pull_repository(repo_path)
                
                assert result is not None
                assert isinstance(result, dict)
                assert result['name'] == 'test-repo'
                assert 'last_pulled' in result
                
                # Verify subprocess call
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert call_args == ["git", "pull"]
                assert mock_run.call_args[1]['cwd'] == repo_path

    @pytest.mark.asyncio
    async def test_pull_repository_not_exists(self, git_service):
        """Test pulling non-existent repository."""
        non_existent_path = str(git_service.working_directory / "non-existent")
        
        with pytest.raises(Exception) as exc_info:
            await git_service.pull_repository(non_existent_path)
        
        assert "Repository path does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pull_repository_git_failure(self, git_service):
        """Test pulling repository when git command fails."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        failed_result = MagicMock()
        failed_result.returncode = 1
        failed_result.stderr = "Network error"
        
        with patch('subprocess.run', return_value=failed_result):
            with pytest.raises(Exception) as exc_info:
                await git_service.pull_repository(repo_path)
            
            assert "Git pull failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_push_changes_success(self, git_service):
        """Test pushing changes successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Mock successful git commands
        add_result = MagicMock(returncode=0, stdout="", stderr="")
        commit_result = MagicMock(returncode=0, stdout="Committed", stderr="")
        push_result = MagicMock(returncode=0, stdout="Pushed successfully", stderr="")
        
        with patch('subprocess.run', side_effect=[add_result, commit_result, push_result]) as mock_run:
            result = await git_service.push_changes(
                repo_path=repo_path,
                commit_message="Test commit",
                branch="main"
            )
            
            assert result is not None
            assert isinstance(result, dict)
            assert result['success'] is True
            assert result['commit_message'] == "Test commit"
            assert result['branch'] == "main"
            assert 'pushed_at' in result
            assert result['stdout'] == "Pushed successfully"
            
            # Should have called git add, commit, and push
            assert mock_run.call_count == 3

    @pytest.mark.asyncio
    async def test_push_changes_nothing_to_commit(self, git_service):
        """Test pushing changes when there's nothing to commit."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        add_result = MagicMock(returncode=0, stdout="", stderr="")
        commit_result = MagicMock(returncode=1, stdout="nothing to commit", stderr="")
        push_result = MagicMock(returncode=0, stdout="Pushed", stderr="")
        
        with patch('subprocess.run', side_effect=[add_result, commit_result, push_result]):
            result = await git_service.push_changes(repo_path, "Test commit")
            
            assert result is not None
            assert result['success'] is True

    @pytest.mark.asyncio
    async def test_push_changes_git_add_failure(self, git_service):
        """Test pushing changes when git add fails."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        failed_result = MagicMock(returncode=1, stdout="", stderr="Permission denied")
        
        with patch('subprocess.run', return_value=failed_result):
            with pytest.raises(Exception) as exc_info:
                await git_service.push_changes(repo_path, "Test commit")
            
            assert "Git add failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_push_changes_git_commit_failure(self, git_service):
        """Test pushing changes when git commit fails."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        add_result = MagicMock(returncode=0, stdout="", stderr="")
        commit_result = MagicMock(returncode=1, stdout="", stderr="Commit failed")
        
        with patch('subprocess.run', side_effect=[add_result, commit_result]):
            with pytest.raises(Exception) as exc_info:
                await git_service.push_changes(repo_path, "Test commit")
            
            assert "Git commit failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_push_changes_git_push_failure(self, git_service):
        """Test pushing changes when git push fails."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        add_result = MagicMock(returncode=0, stdout="", stderr="")
        commit_result = MagicMock(returncode=0, stdout="Committed", stderr="")
        push_result = MagicMock(returncode=1, stdout="", stderr="Push rejected")
        
        with patch('subprocess.run', side_effect=[add_result, commit_result, push_result]):
            with pytest.raises(Exception) as exc_info:
                await git_service.push_changes(repo_path, "Test commit")
            
            assert "Git push failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_files_success(self, git_service):
        """Test listing files successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create test files and directories
        test_file = Path(repo_path) / "test.txt"
        test_file.write_text("Hello World")
        
        test_dir = Path(repo_path) / "subdir"
        test_dir.mkdir()
        
        subdir_file = test_dir / "nested.txt"
        subdir_file.write_text("Nested content")
        
        with patch.object(git_service, '_is_binary_file', return_value=False):
            result = await git_service.list_files(repo_path)
            
            assert isinstance(result, list)
            assert len(result) == 2  # One directory, one file
            
            # Should be sorted (directories first)
            assert result[0]['type'] == 'directory'
            assert result[0]['name'] == 'subdir'
            assert result[1]['type'] == 'file'
            assert result[1]['name'] == 'test.txt'
            assert result[1]['size'] == len("Hello World")
            assert 'modified' in result[1]
            assert 'path' in result[1]
            assert result[1]['is_binary'] is False

    @pytest.mark.asyncio
    async def test_list_files_relative_path(self, git_service):
        """Test listing files in subdirectory."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        subdir = Path(repo_path) / "subdir"
        subdir.mkdir()
        
        nested_file = subdir / "nested.txt"
        nested_file.write_text("Nested content")
        
        with patch.object(git_service, '_is_binary_file', return_value=False):
            result = await git_service.list_files(repo_path, "subdir")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]['name'] == 'nested.txt'
            # Path separator may vary by OS
            assert 'subdir' in result[0]['path']
            assert 'nested.txt' in result[0]['path']

    @pytest.mark.asyncio
    async def test_list_files_non_existent_path(self, git_service):
        """Test listing files in non-existent path."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        result = await git_service.list_files(repo_path, "non-existent")
        
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_read_file_success(self, git_service):
        """Test reading file successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        test_file = Path(repo_path) / "test.txt"
        content = "Hello World Content"
        test_file.write_text(content)
        
        with patch.object(git_service, '_is_binary_file', return_value=False):
            result = await git_service.read_file(repo_path, "test.txt")
            
            assert result is not None
            assert isinstance(result, dict)
            assert result['path'] == 'test.txt'
            assert result['content'] == content
            assert result['size'] == len(content)
            assert 'modified' in result
            assert result['is_binary'] is False
            assert result['encoding'] == 'utf-8'

    @pytest.mark.asyncio
    async def test_read_file_binary_detection(self, git_service):
        """Test reading file with binary detection."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        test_file = Path(repo_path) / "binary.dat"
        # Write binary content (null bytes)
        test_file.write_bytes(b'\x00\x01\x02\x03')
        
        with patch.object(git_service, '_is_binary_file', return_value=True):
            result = await git_service.read_file(repo_path, "binary.dat")
            
            assert result is not None
            assert result['is_binary'] is True
            assert result['encoding'] == 'binary'
            assert result['content'] is None  # Binary files don't return content

    @pytest.mark.asyncio
    async def test_read_file_unicode_decode_error_handling(self, git_service):
        """Test reading file with unicode decode error handling."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        test_file = Path(repo_path) / "weird_encoding.txt"
        # Write content that will cause UTF-8 decode error
        test_file.write_bytes(b'\xff\xfe\x00\x48')  # Invalid UTF-8 sequence
        
        with patch.object(git_service, '_is_binary_file', return_value=False):
            result = await git_service.read_file(repo_path, "weird_encoding.txt")
            
            assert result is not None
            # Should handle the decode error gracefully
            assert 'content' in result

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, git_service):
        """Test reading non-existent file."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        with pytest.raises(Exception) as exc_info:
            await git_service.read_file(repo_path, "non-existent.txt")
        
        assert "File not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_file_not_a_file(self, git_service):
        """Test reading a directory as file."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        test_dir = Path(repo_path) / "directory"
        test_dir.mkdir()
        
        with pytest.raises(Exception) as exc_info:
            await git_service.read_file(repo_path, "directory")
        
        assert "Not a file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_write_file_success(self, git_service):
        """Test writing file successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        content = "New file content"
        result = await git_service.write_file(repo_path, "new-file.txt", content)
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['path'] == 'new-file.txt'
        assert result['size'] == len(content)
        assert 'modified' in result
        assert 'written_at' in result
        
        # Verify file was actually written
        written_file = Path(repo_path) / "new-file.txt"
        assert written_file.exists()
        assert written_file.read_text() == content

    @pytest.mark.asyncio
    async def test_write_file_create_parents(self, git_service):
        """Test writing file with parent directory creation."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        content = "Nested content"
        result = await git_service.write_file(repo_path, "subdir/nested-file.txt", content)
        
        assert result is not None
        # Parent directory should be created
        parent_dir = Path(repo_path) / "subdir"
        assert parent_dir.exists()

    @pytest.mark.asyncio
    async def test_write_file_no_parent_creation(self, git_service):
        """Test writing file without parent directory creation."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        content = "Content"
        subdir_path = "nonexistent/subdir/file.txt"
        
        with pytest.raises(FileNotFoundError):
            await git_service.write_file(
                repo_path, subdir_path, content, create_parents=False
            )

    @pytest.mark.asyncio
    async def test_delete_file_success(self, git_service):
        """Test deleting file successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create test file
        test_file = Path(repo_path) / "to-delete.txt"
        test_file.write_text("Delete me")
        
        result = await git_service.delete_file(repo_path, "to-delete.txt")
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['path'] == 'to-delete.txt'
        assert 'deleted_at' in result
        
        # Verify file was deleted
        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_delete_directory_success(self, git_service):
        """Test deleting directory successfully."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Create test directory with content
        test_dir = Path(repo_path) / "to-delete-dir"
        test_dir.mkdir()
        nested_file = test_dir / "nested.txt"
        nested_file.write_text("Nested content")
        
        result = await git_service.delete_file(repo_path, "to-delete-dir")
        
        assert result is not None
        assert not test_dir.exists()

    @pytest.mark.asyncio
    async def test_delete_file_not_found(self, git_service):
        """Test deleting non-existent file."""
        repo_path = str(git_service.working_directory / "test-repo")
        os.makedirs(repo_path, exist_ok=True)
        
        with pytest.raises(Exception) as exc_info:
            await git_service.delete_file(repo_path, "non-existent.txt")
        
        assert "File not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_is_binary_file_null_bytes(self):
        """Test binary file detection with null bytes."""
        with patch('builtins.open', mock_open(read_data=b'Some text\x00with null bytes')):
            git_service = GitService()
            result = await git_service._is_binary_file(Path("test.bin"))
            assert result is True

    @pytest.mark.asyncio
    async def test_is_binary_file_valid_utf8(self):
        """Test binary file detection with valid UTF-8."""
        with patch('builtins.open', mock_open(read_data=b'Valid UTF-8 text content')):
            git_service = GitService()
            result = await git_service._is_binary_file(Path("test.txt"))
            assert result is False

    @pytest.mark.asyncio
    async def test_is_binary_file_invalid_utf8(self):
        """Test binary file detection with invalid UTF-8."""
        with patch('builtins.open', mock_open(read_data=b'\xff\xfeInvalid UTF-8')):
            git_service = GitService()
            result = await git_service._is_binary_file(Path("test.bin"))
            assert result is True

    @pytest.mark.asyncio
    async def test_is_binary_file_exception_handling(self):
        """Test binary file detection exception handling."""
        with patch('builtins.open', side_effect=Exception("File error")):
            git_service = GitService()
            result = await git_service._is_binary_file(Path("error.txt"))
            assert result is True  # Should return True on exception

    @pytest.mark.asyncio
    async def test_get_repo_info_success(self, git_service, mock_subprocess_result):
        """Test getting repository info successfully."""
        repo_path = git_service.working_directory / "test-repo"
        repo_path.mkdir()
        
        # Mock git command results
        branch_result = MagicMock(returncode=0, stdout="main\n", stderr="")
        remote_result = MagicMock(returncode=0, stdout="https://github.com/user/repo.git\n", stderr="")
        hash_result = MagicMock(returncode=0, stdout="abc123def456\n", stderr="")
        
        with patch('subprocess.run', side_effect=[branch_result, remote_result, hash_result]):
            result = await git_service._get_repo_info(repo_path)
            
            assert result is not None
            assert isinstance(result, dict)
            assert result['name'] == 'test-repo'
            assert result['path'] == str(repo_path)
            assert result['current_branch'] == 'main'
            assert result['remote_url'] == 'https://github.com/user/repo.git'
            assert result['commit_hash'] == 'abc123def456'
            assert result['status'] == 'clean'

    @pytest.mark.asyncio
    async def test_get_repo_info_git_commands_fail(self, git_service):
        """Test getting repository info when git commands fail."""
        repo_path = git_service.working_directory / "test-repo"
        repo_path.mkdir()
        
        failed_result = MagicMock(returncode=1, stdout="", stderr="Git error")
        
        with patch('subprocess.run', return_value=failed_result):
            result = await git_service._get_repo_info(repo_path)
            
            assert result is not None
            assert result['current_branch'] == 'unknown'
            assert result['remote_url'] is None
            assert result['commit_hash'] == 'unknown'
            # Status defaults to 'clean' in the implementation
            assert result['status'] == 'clean'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])