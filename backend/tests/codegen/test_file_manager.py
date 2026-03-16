"""
Tests for File Manager.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from backend.codegen.file_manager import FileManager, FileArtifact, ProjectStructure


class TestFileManager:
    """Test cases for FileManager."""
    
    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = FileManager(base_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        assert self.manager.base_path.exists()
    
    def test_write_file(self):
        """Test writing a file."""
        artifact = self.manager.write_file(
            "test.py",
            "print('hello')",
            language="python",
        )
        
        assert artifact.path == "test.py"
        assert artifact.content == "print('hello')"
        assert (self.manager.base_path / "test.py").exists()
    
    def test_read_file(self):
        """Test reading a file."""
        self.manager.write_file("test.py", "print('hello')")
        
        artifact = self.manager.read_file("test.py")
        
        assert artifact is not None
        assert artifact.content == "print('hello')"
    
    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        artifact = self.manager.read_file("nonexistent.py")
        
        assert artifact is None
    
    def test_delete_file(self):
        """Test deleting a file."""
        self.manager.write_file("test.py", "content")
        
        result = self.manager.delete_file("test.py")
        
        assert result is True
        assert not (self.manager.base_path / "test.py").exists()
    
    def test_delete_file_not_found(self):
        """Test deleting non-existent file."""
        result = self.manager.delete_file("nonexistent.py")
        
        assert result is False
    
    def test_create_directory(self):
        """Test creating a directory."""
        path = self.manager.create_directory("subdir/nested")
        
        assert path.exists()
        assert path.is_dir()
    
    def test_list_files(self):
        """Test listing files."""
        self.manager.write_file("file1.py", "content1")
        self.manager.write_file("file2.py", "content2")
        self.manager.write_file("subdir/file3.py", "content3")
        
        files = self.manager.list_files()
        
        assert len(files) == 3
        paths = [f.path for f in files]
        assert "file1.py" in paths
        assert "file2.py" in paths
        # Handle both forward and backslash separators (Windows)
        assert any("subdir" in p and "file3.py" in p for p in paths)
    
    def test_list_files_with_pattern(self):
        """Test listing files with pattern."""
        self.manager.write_file("test.py", "content")
        self.manager.write_file("test.txt", "content")
        
        files = self.manager.list_files(pattern="*.py")
        
        assert len(files) == 1
        assert files[0].path == "test.py"
    
    def test_get_project_structure(self):
        """Test getting project structure."""
        self.manager.write_file("main.py", "content")
        self.manager.write_file("utils/helpers.py", "content")
        self.manager.create_directory("tests")
        
        structure = self.manager.get_project_structure(".")
        
        assert len(structure.files) == 2
        assert len(structure.directories) >= 2  # utils and tests
    
    def test_copy_file(self):
        """Test copying a file."""
        self.manager.write_file("source.py", "content")
        
        artifact = self.manager.copy_file("source.py", "dest.py")
        
        assert artifact is not None
        assert artifact.content == "content"
        assert (self.manager.base_path / "dest.py").exists()
    
    def test_move_file(self):
        """Test moving a file."""
        self.manager.write_file("source.py", "content")
        
        artifact = self.manager.move_file("source.py", "dest.py")
        
        assert artifact is not None
        assert artifact.content == "content"
        assert not (self.manager.base_path / "source.py").exists()
        assert (self.manager.base_path / "dest.py").exists()
    
    def test_file_exists(self):
        """Test checking file existence."""
        self.manager.write_file("test.py", "content")
        
        assert self.manager.file_exists("test.py") is True
        assert self.manager.file_exists("nonexistent.py") is False
    
    def test_get_file_size(self):
        """Test getting file size."""
        content = "Hello, World!"
        self.manager.write_file("test.py", content)
        
        size = self.manager.get_file_size("test.py")
        
        assert size == len(content)
    
    def test_path_security(self):
        """Test path traversal protection."""
        with pytest.raises(ValueError):
            self.manager.write_file("../outside.py", "content")


class TestFileArtifact:
    """Test cases for FileArtifact."""
    
    def test_artifact_properties(self):
        """Test artifact properties."""
        artifact = FileArtifact(
            path="subdir/test.py",
            content="print('hello')",
        )
        
        assert artifact.filename == "test.py"
        assert artifact.extension == ".py"
    
    def test_artifact_to_dict(self):
        """Test converting artifact to dict."""
        artifact = FileArtifact(
            path="test.py",
            content="print('hello')",
            language="python",
        )
        
        result = artifact.to_dict()
        
        assert result["path"] == "test.py"
        assert result["filename"] == "test.py"
        assert result["language"] == "python"
        assert result["size"] == 14


class TestProjectStructure:
    """Test cases for ProjectStructure."""
    
    def test_structure_creation(self):
        """Test creating project structure."""
        structure = ProjectStructure(
            root_path="/project",
            name="myproject",
            files=[FileArtifact(path="main.py")],
            directories=["tests"],
        )
        
        assert structure.name == "myproject"
        assert len(structure.files) == 1
        assert len(structure.directories) == 1
