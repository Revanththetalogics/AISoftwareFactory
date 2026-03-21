"""
Tests for File Manager.
"""

import shutil
import tempfile

import pytest

from backend.codegen.file_manager import FileArtifact, FileManager, ProjectStructure


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

    def test_structure_to_dict_line_80(self):
        """Test ProjectStructure.to_dict() - line 80."""
        structure = ProjectStructure(
            root_path="/project",
            name="myproject",
            files=[
                FileArtifact(path="main.py", content="print('hello')"),
                FileArtifact(path="utils.py", content="def util(): pass"),
            ],
            directories=["tests", "docs"],
        )

        result = structure.to_dict()

        # Line 80: to_dict should return correct structure
        assert result["root_path"] == "/project"
        assert result["name"] == "myproject"
        assert result["file_count"] == 2
        assert result["directory_count"] == 2
        assert len(result["files"]) == 2
        assert result["directories"] == ["tests", "docs"]


class TestFileManagerExtendedCoverage:
    """Tests for extended coverage - lines 260-272, 294, 301, 316-317, 338, 361-362, 388, 414, 434."""

    @pytest.fixture
    def file_manager(self):
        """Create FileManager with temp directory."""
        import tempfile

        from backend.codegen.file_manager import FileManager
        tmpdir = tempfile.mkdtemp()
        manager = FileManager(base_path=tmpdir)
        yield manager
        # Cleanup
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_delete_directory_recursive_lines_260_272(self, file_manager):
        """Test lines 260-272: delete_directory with recursive=True."""
        import os

        # Create a directory with content
        dir_path = "test_delete_dir"
        file_manager.create_directory(dir_path)
        file_manager.write_file(f"{dir_path}/file.txt", "content")

        # Delete recursively
        result = file_manager.delete_directory(dir_path, recursive=True)

        # Lines 265-266: recursive delete
        assert result is True
        full_path = os.path.join(file_manager.base_path, dir_path)
        assert not os.path.exists(full_path)

    def test_delete_directory_non_recursive_lines_267_268(self, file_manager):
        """Test lines 267-268: delete_directory with recursive=False."""

        # Create an empty directory
        dir_path = "test_empty_dir"
        file_manager.create_directory(dir_path)

        # Delete non-recursively (only works on empty dirs)
        result = file_manager.delete_directory(dir_path, recursive=False)

        assert result is True

    def test_delete_directory_not_found(self, file_manager):
        """Test delete_directory when directory doesn't exist."""
        result = file_manager.delete_directory("nonexistent_dir", recursive=True)

        # Lines 262-263: should return False
        assert result is False

    def test_list_files_path_not_exist_line_294(self, file_manager):
        """Test line 294: list_files when path doesn't exist."""
        files = file_manager.list_files("nonexistent_path")

        # Line 293-294: should return empty list
        assert files == []

    def test_list_files_non_recursive_line_301(self, file_manager):
        """Test line 301: list_files with recursive=False."""
        # Create files in directory and subdirectory
        file_manager.write_file("dir/file1.txt", "content1")
        file_manager.write_file("dir/sub/file2.txt", "content2")

        # Non-recursive should only find file1
        files = file_manager.list_files("dir", pattern="*.txt", recursive=False)

        # Line 301: non-recursive glob
        assert len(files) == 1
        assert any("file1.txt" in f.path for f in files)

    def test_list_files_unicode_error_line_316_317(self, file_manager):
        """Test lines 316-317: UnicodeDecodeError handling."""
        import os

        # Create a binary file that can't be read as text
        binary_path = os.path.join(file_manager.base_path, "binary.bin")
        with open(binary_path, 'wb') as f:
            f.write(bytes([0x80, 0x81, 0x82]))  # Invalid UTF-8

        files = file_manager.list_files("", pattern="*.bin")

        # Lines 316-317: Should skip file with UnicodeDecodeError
        assert len(files) == 0  # File was skipped due to decode error

    def test_get_project_structure_not_exist_line_338(self, file_manager):
        """Test line 338: get_project_structure when path doesn't exist."""
        structure = file_manager.get_project_structure("nonexistent_project")

        # Lines 337-341: should return empty structure
        assert structure.name == "nonexistent_project"
        assert len(structure.files) == 0
        assert len(structure.directories) == 0

    def test_get_project_structure_with_unreadable_file_lines_361_362(self, file_manager):
        """Test lines 361-362: exception handling in get_project_structure."""
        import os

        # Create project with readable file
        project_name = "test_project"
        file_manager.create_directory(project_name)
        file_manager.write_file(f"{project_name}/readable.py", "# python file")

        # Create a binary file
        binary_path = os.path.join(file_manager.base_path, project_name, "binary.dat")
        with open(binary_path, 'wb') as f:
            f.write(bytes([0xFF, 0xFE, 0x00, 0x01]))  # Invalid UTF-8

        structure = file_manager.get_project_structure(project_name)

        # Lines 361-362: should skip unreadable files
        assert structure.name == project_name
        # Only the readable file should be included
        file_names = [f.path for f in structure.files]
        assert any("readable.py" in fn for fn in file_names)

    def test_copy_file_source_not_exist_line_388(self, file_manager):
        """Test line 388: copy_file when source doesn't exist."""
        result = file_manager.copy_file("nonexistent.txt", "dest.txt")

        # Lines 387-388: should return None
        assert result is None

    def test_move_file_source_not_exist_line_414(self, file_manager):
        """Test line 414: move_file when source doesn't exist."""
        result = file_manager.move_file("nonexistent.txt", "dest.txt")

        # Lines 413-414: should return None
        assert result is None

    def test_get_file_size_not_exist_line_434(self, file_manager):
        """Test line 434: get_file_size when file doesn't exist."""
        size = file_manager.get_file_size("nonexistent.txt")

        # Lines 433-434: should return 0
        assert size == 0

    def test_copy_file_success(self, file_manager):
        """Test successful copy_file."""
        file_manager.write_file("source.txt", "source content")

        result = file_manager.copy_file("source.txt", "dest.txt")

        assert result is not None
        assert result.content == "source content"

    def test_move_file_success(self, file_manager):
        """Test successful move_file."""
        file_manager.write_file("source.txt", "source content")

        result = file_manager.move_file("source.txt", "moved.txt")

        assert result is not None
        assert result.content == "source content"
        # Original should no longer exist
        assert file_manager.read_file("source.txt") is None
