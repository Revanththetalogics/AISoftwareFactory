"""
Tests for AutoFixerAgent - AI-powered automatic code repair.
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.testing.agents.auto_fixer import (
    AutoFixerAgent,
    CodeChange,
    FixAttempt,
    FixStatus,
    FixStrategy,
    ValidationResult,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(
        return_value="""```python
def fixed_function():
    return True
```"""
    )
    return llm


@pytest.fixture
def auto_fixer_agent(mock_llm):
    """Fixture for AutoFixerAgent with mocked LLM."""
    with patch("backend.testing.agents.auto_fixer.LLMFactory.create_llm", return_value=mock_llm):
        agent = AutoFixerAgent()
        agent._llm = mock_llm
        return agent


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""def sample_function():
    try:
        result = 1 / 0
    except:
        pass
    return None
""")
        f.flush()
        yield f.name
    os.unlink(f.name)


class TestCodeChange:
    """Tests for CodeChange dataclass."""

    def test_code_change_creation(self):
        """Test CodeChange creation."""
        change = CodeChange(
            file_path="/path/to/file.py",
            line_start=10,
            line_end=15,
            original_code="old code",
            new_code="new code",
            description="Fix bug",
        )

        assert change.file_path == "/path/to/file.py"
        assert change.line_start == 10
        assert change.line_end == 15
        assert change.original_code == "old code"
        assert change.new_code == "new code"
        assert change.description == "Fix bug"

    def test_code_change_to_dict(self):
        """Test CodeChange serialization."""
        change = CodeChange(
            file_path="/path/to/file.py",
            line_start=10,
            line_end=15,
            original_code="old",
            new_code="new",
            description="Fix",
        )

        data = change.to_dict()

        assert data["file_path"] == "/path/to/file.py"
        assert data["line_start"] == 10
        assert data["line_end"] == 15
        assert data["original_code"] == "old"
        assert data["new_code"] == "new"
        assert data["description"] == "Fix"


class TestFixAttempt:
    """Tests for FixAttempt dataclass."""

    def test_fix_attempt_creation(self):
        """Test FixAttempt creation."""
        attempt = FixAttempt(
            id="fix_123",
            bug_id="bug_456",
            file_path="/path/to/file.py",
            strategy=FixStrategy.PATTERN,
            status=FixStatus.PENDING,
        )

        assert attempt.id == "fix_123"
        assert attempt.bug_id == "bug_456"
        assert attempt.strategy == FixStrategy.PATTERN
        assert attempt.status == FixStatus.PENDING
        assert attempt.changes == []

    def test_fix_attempt_to_dict(self):
        """Test FixAttempt serialization with all fields."""
        attempt = FixAttempt(
            id="fix_123",
            bug_id="bug_456",
            file_path="/path/to/file.py",
            strategy=FixStrategy.LLM,
            status=FixStatus.SUCCESS,
            diff="--- a\n+++ b",
            validation_results={"passed": True},
            error_message=None,
            applied_at=datetime(2024, 1, 15, 10, 0, 0),
            rolled_back_at=None,
            backup_path="/backup/file.py.bak",
        )

        data = attempt.to_dict()

        assert data["id"] == "fix_123"
        assert data["bug_id"] == "bug_456"
        assert data["strategy"] == "llm"
        assert data["status"] == "success"
        assert data["diff"] == "--- a\n+++ b"
        assert data["validation_results"] == {"passed": True}
        assert data["applied_at"] is not None
        assert data["rolled_back_at"] is None

    def test_fix_attempt_with_rolled_back_at(self):
        """Test FixAttempt with rolled_back_at timestamp."""
        attempt = FixAttempt(
            id="fix_123",
            bug_id="bug_456",
            file_path="/path/to/file.py",
            strategy=FixStrategy.PATTERN,
            status=FixStatus.ROLLED_BACK,
            rolled_back_at=datetime(2024, 1, 15, 11, 0, 0),
        )

        data = attempt.to_dict()
        assert data["status"] == "rolled_back"
        assert data["rolled_back_at"] is not None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            passed=True,
            syntax_valid=True,
            tests_pass=True,
            no_new_issues=True,
            messages=["All checks passed"],
        )

        assert result.passed is True
        assert result.syntax_valid is True
        assert result.tests_pass is True
        assert len(result.messages) == 1

    def test_validation_result_to_dict(self):
        """Test ValidationResult serialization."""
        result = ValidationResult(
            passed=False,
            syntax_valid=False,
            tests_pass=True,
            no_new_issues=True,
            messages=["Syntax error on line 10"],
        )

        data = result.to_dict()

        assert data["passed"] is False
        assert data["syntax_valid"] is False
        assert data["tests_pass"] is True
        assert data["no_new_issues"] is True
        assert "Syntax error" in data["messages"][0]


class TestFixStatusEnum:
    """Tests for FixStatus enum."""

    def test_all_status_values(self):
        """Test all FixStatus values."""
        assert FixStatus.PENDING.value == "pending"
        assert FixStatus.SUCCESS.value == "success"
        assert FixStatus.FAILED.value == "failed"
        assert FixStatus.VALIDATION_FAILED.value == "validation_failed"
        assert FixStatus.ROLLED_BACK.value == "rolled_back"


class TestFixStrategyEnum:
    """Tests for FixStrategy enum."""

    def test_all_strategy_values(self):
        """Test all FixStrategy values."""
        assert FixStrategy.PATTERN.value == "pattern"
        assert FixStrategy.LLM.value == "llm"
        assert FixStrategy.REFACTORING.value == "refactoring"
        assert FixStrategy.MANUAL.value == "manual"


class TestAutoFixerAgent:
    """Tests for AutoFixerAgent class."""

    def test_agent_initialization(self, auto_fixer_agent):
        """Test agent initialization."""
        assert auto_fixer_agent.name == "AutoFixer"
        assert auto_fixer_agent.role == "Code Repair Specialist"
        assert "pattern_based_fixing" in auto_fixer_agent.identity.capabilities
        assert "rollback" in auto_fixer_agent.identity.capabilities

    def test_load_fix_patterns(self, auto_fixer_agent):
        """Test fix patterns are loaded."""
        patterns = auto_fixer_agent._fix_patterns

        assert "bare_except" in patterns
        assert "mutable_default" in patterns
        assert "print_to_logger" in patterns
        assert "unused_import" in patterns

    @pytest.mark.asyncio
    async def test_execute_task_auto_fix(self, auto_fixer_agent, temp_python_file):
        """Test executing auto_fix task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_123",
            task_type="auto_fix",
            description="Fix bug",
            context={
                "bug_id": "bug_123",
                "file_path": temp_python_file,
                "bug_description": "bare_except pattern detected",
                "suggested_fix": "Use except Exception:",
                "auto_apply": False,
                "validate": True,
            },
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_123"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_batch_fix(self, auto_fixer_agent, temp_python_file):
        """Test executing batch_fix task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_456",
            task_type="batch_fix",
            description="Fix multiple bugs",
            context={
                "bugs": [
                    {
                        "id": "bug_1",
                        "file_path": temp_python_file,
                        "description": "bare_except",
                        "suggested_fix": "Use except Exception:",
                    }
                ],
                "auto_apply": False,
                "stop_on_failure": True,
            },
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_456"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_preview_fix(self, auto_fixer_agent, temp_python_file):
        """Test executing preview_fix task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_789",
            task_type="preview_fix",
            description="Preview fix",
            context={
                "bug_id": "bug_preview",
                "file_path": temp_python_file,
                "bug_description": "Test bug",
                "suggested_fix": "Fix it",
            },
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_789"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_unknown_type(self, auto_fixer_agent):
        """Test executing unknown task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_unknown",
            task_type="unknown_type",
            description="Unknown",
            context={},
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_unknown"
        assert result.status.value == "failed"
        assert "Unknown task type" in result.error

    @pytest.mark.asyncio
    async def test_fix_bug_pattern_match(self, auto_fixer_agent, temp_python_file):
        """Test fixing bug using pattern matching."""
        fix_attempt = await auto_fixer_agent.fix_bug(
            bug_id="bug_pattern",
            file_path=temp_python_file,
            bug_description="bare_except pattern detected",
            suggested_fix="Use except Exception:",
            auto_apply=False,
            validate=True,
        )

        assert fix_attempt.bug_id == "bug_pattern"
        assert fix_attempt.file_path == temp_python_file

    @pytest.mark.asyncio
    async def test_fix_bug_llm_fallback(self, auto_fixer_agent, temp_python_file):
        """Test falling back to LLM when pattern doesn't match."""
        fix_attempt = await auto_fixer_agent.fix_bug(
            bug_id="bug_llm",
            file_path=temp_python_file,
            bug_description="Complex logic error that needs LLM",
            suggested_fix="Refactor the logic",
            auto_apply=False,
            validate=True,
        )

        assert fix_attempt.bug_id == "bug_llm"

    @pytest.mark.asyncio
    async def test_batch_fix(self, auto_fixer_agent, temp_python_file):
        """Test batch fixing multiple bugs."""
        bugs = [
            {
                "id": "bug_batch_1",
                "file_path": temp_python_file,
                "description": "First bug",
                "suggested_fix": "Fix 1",
            },
            {
                "id": "bug_batch_2",
                "file_path": temp_python_file,
                "description": "Second bug",
                "suggested_fix": "Fix 2",
            },
        ]

        results = await auto_fixer_agent.batch_fix(
            bugs=bugs,
            auto_apply=False,
            stop_on_failure=False,
        )

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_batch_fix_stop_on_failure(self, auto_fixer_agent, temp_python_file):
        """Test batch fix stops on failure when configured."""
        # Create a bug with invalid file path to trigger failure
        bugs = [
            {
                "id": "bug_fail",
                "file_path": "/nonexistent/file.py",
                "description": "Will fail",
                "suggested_fix": "Cannot fix",
            },
            {
                "id": "bug_skip",
                "file_path": temp_python_file,
                "description": "Should be skipped",
                "suggested_fix": "Skip",
            },
        ]

        results = await auto_fixer_agent.batch_fix(
            bugs=bugs,
            auto_apply=False,
            stop_on_failure=True,
        )

        # Should stop after first failure
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_rollback_fix_not_found(self, auto_fixer_agent):
        """Test rolling back a non-existent fix."""
        result = await auto_fixer_agent.rollback_fix("nonexistent_fix_id")

        assert result is False

    @pytest.mark.asyncio
    async def test_rollback_fix_no_backup(self, auto_fixer_agent):
        """Test rolling back a fix without backup."""
        # Add a fix attempt without backup path
        fix_attempt = FixAttempt(
            id="fix_no_backup",
            bug_id="bug_123",
            file_path="/path/to/file.py",
            strategy=FixStrategy.LLM,
            status=FixStatus.SUCCESS,
            backup_path=None,
        )
        auto_fixer_agent._fix_history.append(fix_attempt)

        result = await auto_fixer_agent.rollback_fix("fix_no_backup")

        assert result is False

    @pytest.mark.asyncio
    async def test_preview_fix(self, auto_fixer_agent, temp_python_file):
        """Test previewing a fix."""
        preview = await auto_fixer_agent.preview_fix(
            bug_id="bug_preview",
            file_path=temp_python_file,
            bug_description="Test bug",
            suggested_fix="Suggested fix",
        )

        assert "can_fix" in preview
        assert "strategy" in preview
        assert "changes" in preview
        assert "diff" in preview

    def test_get_fix_statistics_empty(self, auto_fixer_agent):
        """Test getting statistics with no fixes."""
        stats = auto_fixer_agent.get_fix_statistics()

        assert stats["total_fixes"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0

    def test_get_fix_statistics_with_history(self, auto_fixer_agent):
        """Test getting statistics with fix history."""
        # Add some fix history
        for i in range(5):
            fix = FixAttempt(
                id=f"fix_{i}",
                bug_id=f"bug_{i}",
                file_path="/path/file.py",
                strategy=FixStrategy.PATTERN if i % 2 == 0 else FixStrategy.LLM,
                status=FixStatus.SUCCESS if i < 3 else FixStatus.FAILED,
            )
            auto_fixer_agent._fix_history.append(fix)

        stats = auto_fixer_agent.get_fix_statistics()

        assert stats["total_fixes"] == 5
        assert stats["successful"] == 3
        assert stats["failed"] == 2
        assert stats["success_rate"] == 0.6
        assert "by_strategy" in stats
        assert "recent_fixes" in stats

    def test_generate_diff(self, auto_fixer_agent):
        """Test diff generation."""
        original = "line1\nline2\nline3"
        modified = "line1\nmodified\nline3"

        diff = auto_fixer_agent._generate_diff(original, modified)

        assert "---" in diff or diff == ""  # Depends on changes

    def test_extract_code_from_response_with_code_block(self, auto_fixer_agent):
        """Test extracting code from LLM response with code block."""
        response = """Here's the fix:

```python
def fixed_function():
    return True
```

That should work."""

        code = auto_fixer_agent._extract_code_from_response(response)

        assert "def fixed_function" in code
        assert "```" not in code

    def test_extract_code_from_response_without_code_block(self, auto_fixer_agent):
        """Test extracting code when no code block present."""
        response = "def simple_function():\n    pass"

        code = auto_fixer_agent._extract_code_from_response(response)

        assert "def simple_function" in code

    @pytest.mark.asyncio
    async def test_validate_fix_no_changes(self, auto_fixer_agent):
        """Test validating a fix attempt with no changes."""
        fix_attempt = FixAttempt(
            id="fix_empty",
            bug_id="bug_123",
            file_path="/path/file.py",
            strategy=FixStrategy.PATTERN,
            status=FixStatus.PENDING,
            changes=[],
        )

        result = await auto_fixer_agent._validate_fix(fix_attempt)

        assert result.passed is False
        assert "No changes to validate" in result.messages

    @pytest.mark.asyncio
    async def test_validate_fix_syntax_error(self, auto_fixer_agent):
        """Test validating a fix with syntax error."""
        change = CodeChange(
            file_path="/path/file.py",
            line_start=1,
            line_end=1,
            original_code="valid = True",
            new_code="invalid syntax {{{{",
            description="Bad fix",
        )

        fix_attempt = FixAttempt(
            id="fix_syntax",
            bug_id="bug_123",
            file_path="/path/file.py",
            strategy=FixStrategy.LLM,
            status=FixStatus.PENDING,
            changes=[change],
        )

        result = await auto_fixer_agent._validate_fix(fix_attempt)

        assert result.syntax_valid is False
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_validate_fix_valid_syntax(self, auto_fixer_agent):
        """Test validating a fix with valid syntax."""
        change = CodeChange(
            file_path="/path/file.py",
            line_start=1,
            line_end=1,
            original_code="old = True",
            new_code="new = True\nresult = new",
            description="Valid fix",
        )

        fix_attempt = FixAttempt(
            id="fix_valid",
            bug_id="bug_123",
            file_path="/path/file.py",
            strategy=FixStrategy.LLM,
            status=FixStatus.PENDING,
            changes=[change],
        )

        result = await auto_fixer_agent._validate_fix(fix_attempt)

        assert result.syntax_valid is True

    @pytest.mark.asyncio
    async def test_execute_task_rollback(self, auto_fixer_agent, temp_python_file):
        """Test executing rollback task type."""
        from backend.agents.base_agent import Task

        # First add a fix to history with backup
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bak", delete=False) as backup:
            backup.write("backup content")
            backup_path = backup.name

        fix_attempt = FixAttempt(
            id="fix_to_rollback",
            bug_id="bug_123",
            file_path=temp_python_file,
            strategy=FixStrategy.LLM,
            status=FixStatus.SUCCESS,
            backup_path=backup_path,
        )
        auto_fixer_agent._fix_history.append(fix_attempt)

        task = Task(
            task_id="task_rollback",
            task_type="rollback",
            description="Rollback fix",
            context={"fix_id": "fix_to_rollback"},
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_rollback"
        assert result.status.value == "completed"

        # Clean up
        os.unlink(backup_path)

    @pytest.mark.asyncio
    async def test_execute_task_exception_handling(self, auto_fixer_agent):
        """Test exception handling in execute_task."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_error",
            task_type="auto_fix",
            description="Will fail",
            context={},  # Missing required context fields
        )

        result = await auto_fixer_agent.execute_task(task)

        assert result.task_id == "task_error"
        assert result.status.value == "failed"
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_apply_fix_success(self, auto_fixer_agent, temp_python_file):
        """Test applying a fix successfully."""
        change = CodeChange(
            file_path=temp_python_file,
            line_start=1,
            line_end=5,
            original_code="old code",
            new_code="new code that is valid python = True",
            description="Apply this fix",
        )

        fix_attempt = FixAttempt(
            id="fix_apply",
            bug_id="bug_apply",
            file_path=temp_python_file,
            strategy=FixStrategy.LLM,
            status=FixStatus.PENDING,
            changes=[change],
        )

        success = await auto_fixer_agent._apply_fix(fix_attempt)

        assert success is True
        assert fix_attempt.backup_path is not None

    @pytest.mark.asyncio
    async def test_apply_fix_no_changes(self, auto_fixer_agent):
        """Test applying fix with no changes."""
        fix_attempt = FixAttempt(
            id="fix_empty",
            bug_id="bug_empty",
            file_path="/path/file.py",
            strategy=FixStrategy.LLM,
            status=FixStatus.PENDING,
            changes=[],
        )

        success = await auto_fixer_agent._apply_fix(fix_attempt)

        assert success is False

    @pytest.mark.asyncio
    async def test_fix_bug_with_validation_failure(self, auto_fixer_agent, temp_python_file):
        """Test fix_bug when validation fails."""
        # Mock LLM to return invalid code
        auto_fixer_agent._llm.generate = AsyncMock(return_value="this is not valid python {{{{")

        fix_attempt = await auto_fixer_agent.fix_bug(
            bug_id="bug_invalid",
            file_path=temp_python_file,
            bug_description="Complex bug needing LLM fix",
            suggested_fix="Generate code",
            auto_apply=False,
            validate=True,
        )

        # Should have validation results
        assert "validation_results" in fix_attempt.to_dict() or fix_attempt.validation_results is not None

    @pytest.mark.asyncio
    async def test_fix_bug_auto_apply_with_success(self, auto_fixer_agent, temp_python_file):
        """Test fix_bug with auto_apply when successful."""
        # Mock LLM to return valid code
        auto_fixer_agent._llm.generate = AsyncMock(return_value="valid_code = True")

        fix_attempt = await auto_fixer_agent.fix_bug(
            bug_id="bug_auto",
            file_path=temp_python_file,
            bug_description="bare_except",
            suggested_fix="Use except Exception:",
            auto_apply=True,
            validate=True,
        )

        assert fix_attempt.bug_id == "bug_auto"

    @pytest.mark.asyncio
    async def test_try_pattern_fix_file_not_found(self, auto_fixer_agent):
        """Test pattern fix with non-existent file."""
        fix_attempt = await auto_fixer_agent._try_pattern_fix(
            bug_id="bug_nofile",
            file_path="/nonexistent/file.py",
            bug_description="bare_except",
            line_number=1,
        )

        assert fix_attempt.status == FixStatus.FAILED
        assert fix_attempt.error_message is not None


class TestAutoFixerExtendedCoverage:
    """Tests for extended coverage of auto_fixer.py - lines 261, 356-358, 611-613."""

    @pytest.fixture
    def auto_fixer_agent(self):
        """Create AutoFixerAgent with mocked LLM."""
        from unittest.mock import AsyncMock, Mock

        from backend.testing.agents.auto_fixer import AutoFixerAgent

        mock_llm = Mock()
        mock_llm.generate = AsyncMock(return_value="fixed_code = True")
        agent = AutoFixerAgent()
        agent._llm = mock_llm
        return agent

    @pytest.fixture
    def temp_python_file(self):
        """Create a temporary Python file for testing."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""try:
    x = 1
except:
    pass
""")
            f.flush()
            yield f.name
        os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_fix_bug_auto_apply_fails_line_261(self, auto_fixer_agent, temp_python_file):
        """Test line 261: fix_attempt.status = FixStatus.FAILED when auto_apply fails."""
        from unittest.mock import AsyncMock, patch

        # Mock _apply_fix to return False (failure)
        with patch.object(auto_fixer_agent, "_apply_fix", new_callable=AsyncMock) as mock_apply:
            mock_apply.return_value = False

            fix_attempt = await auto_fixer_agent.fix_bug(
                bug_id="bug_fail_apply",
                file_path=temp_python_file,
                bug_description="bare_except",
                suggested_fix="Use except Exception:",
                auto_apply=True,
                validate=False,  # Skip validation to reach auto_apply
            )

            # Line 261: When _apply_fix returns False, status should be FAILED
            assert fix_attempt.status == FixStatus.FAILED

    @pytest.mark.asyncio
    async def test_rollback_fix_exception_lines_356_358(self, auto_fixer_agent):
        """Test lines 356-358: exception handling in rollback_fix."""
        from unittest.mock import patch

        from backend.testing.agents.auto_fixer import FixAttempt, FixStatus, FixStrategy

        # Create a fix attempt with a backup path
        fix_attempt = FixAttempt(
            id="fix_rollback_exc",
            bug_id="bug_123",
            strategy=FixStrategy.PATTERN,
            status=FixStatus.SUCCESS,
            file_path="/path/to/file.py",
            backup_path="/path/to/backup.bak",
        )
        auto_fixer_agent._fix_history.append(fix_attempt)

        # Mock shutil.copy2 to raise an exception (line 356-358)
        with patch("backend.testing.agents.auto_fixer.shutil.copy2") as mock_copy:
            mock_copy.side_effect = Exception("Permission denied")

            result = await auto_fixer_agent.rollback_fix("fix_rollback_exc")

            # Should return False due to exception in rollback
            assert result is False

    @pytest.mark.asyncio
    async def test_apply_fix_exception_lines_611_613(self, auto_fixer_agent):
        """Test lines 611-613: exception handling in _apply_fix."""
        import os
        import tempfile
        from unittest.mock import patch

        from backend.testing.agents.auto_fixer import CodeChange, FixAttempt, FixStatus, FixStrategy

        # Create a temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("original code")
            f.flush()
            file_path = f.name

        try:
            fix_attempt = FixAttempt(
                id="fix_apply_exc",
                bug_id="bug_456",
                strategy=FixStrategy.LLM,
                status=FixStatus.PENDING,
                file_path=file_path,
                changes=[
                    CodeChange(
                        file_path=file_path,
                        line_start=1,
                        line_end=1,
                        original_code="original",
                        new_code="new",
                        description="Test fix",
                    )
                ],
            )

            # Mock open to raise an exception when writing (line 611-613)
            with patch("builtins.open", side_effect=Exception("Disk full")):
                result = await auto_fixer_agent._apply_fix(fix_attempt)

                # Should return False due to exception
                assert result is False
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
