"""
Tests for BugDetectorAgent - AI-powered bug detection and analysis.
"""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.testing.agents.bug_detector import (
    BugCategory,
    BugDetectorAgent,
    BugLocation,
    BugPattern,
    BugSeverity,
    DetectedBug,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="""[
        {
            "title": "Potential security issue",
            "category": "security",
            "severity": "high",
            "line_number": 5,
            "description": "Using eval is dangerous",
            "root_cause": "eval executes arbitrary code",
            "suggested_fix": "Use ast.literal_eval instead",
            "confidence": 0.9
        }
    ]""")
    return llm


@pytest.fixture
def bug_detector_agent(mock_llm):
    """Fixture for BugDetectorAgent with mocked LLM."""
    with patch('backend.testing.agents.bug_detector.LLMFactory.create_llm', return_value=mock_llm):
        agent = BugDetectorAgent()
        agent._llm = mock_llm
        return agent


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''def vulnerable_function():
    password = "secret123"
    data = eval(input("Enter data: "))
    try:
        result = 1 / 0
    except:
        pass
    return data
''')
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_syntax_error_file():
    """Create a temporary Python file with syntax error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''def broken_function(
    this is invalid syntax
    return None
''')
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_directory():
    """Create a temporary directory with Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a few Python files
        with open(os.path.join(tmpdir, "file1.py"), "w") as f:
            f.write("def func1():\n    return True\n")
        with open(os.path.join(tmpdir, "file2.py"), "w") as f:
            f.write("def func2():\n    password = 'test'\n    return False\n")
        yield tmpdir


class TestBugSeverityEnum:
    """Tests for BugSeverity enum."""

    def test_all_severity_values(self):
        """Test all BugSeverity values."""
        assert BugSeverity.CRITICAL.value == "critical"
        assert BugSeverity.HIGH.value == "high"
        assert BugSeverity.MEDIUM.value == "medium"
        assert BugSeverity.LOW.value == "low"
        assert BugSeverity.INFO.value == "info"


class TestBugCategoryEnum:
    """Tests for BugCategory enum."""

    def test_all_category_values(self):
        """Test all BugCategory values."""
        assert BugCategory.SYNTAX.value == "syntax"
        assert BugCategory.LOGIC.value == "logic"
        assert BugCategory.SECURITY.value == "security"
        assert BugCategory.PERFORMANCE.value == "performance"
        assert BugCategory.MAINTAINABILITY.value == "maintainability"
        assert BugCategory.TYPE_SAFETY.value == "type_safety"
        assert BugCategory.CONCURRENCY.value == "concurrency"
        assert BugCategory.RESOURCE_LEAK.value == "resource_leak"


class TestBugLocation:
    """Tests for BugLocation dataclass."""

    def test_bug_location_creation(self):
        """Test BugLocation creation."""
        location = BugLocation(
            file_path="/path/to/file.py",
            line_number=10,
            column=5,
            function_name="my_function",
            class_name="MyClass",
        )

        assert location.file_path == "/path/to/file.py"
        assert location.line_number == 10
        assert location.column == 5
        assert location.function_name == "my_function"
        assert location.class_name == "MyClass"

    def test_bug_location_to_dict(self):
        """Test BugLocation serialization."""
        location = BugLocation(
            file_path="/path/to/file.py",
            line_number=10,
            column=None,
            function_name="test_func",
            class_name=None,
        )

        data = location.to_dict()

        assert data["file_path"] == "/path/to/file.py"
        assert data["line_number"] == 10
        assert data["column"] is None
        assert data["function_name"] == "test_func"
        assert data["class_name"] is None


class TestBugPattern:
    """Tests for BugPattern dataclass."""

    def test_bug_pattern_creation(self):
        """Test BugPattern creation."""
        pattern = BugPattern(
            name="test_pattern",
            category=BugCategory.SECURITY,
            severity=BugSeverity.CRITICAL,
            pattern=r'password\s*=',
            description="Hardcoded password",
            suggestion="Use environment variables",
            confidence_boost=0.9,
        )

        assert pattern.name == "test_pattern"
        assert pattern.category == BugCategory.SECURITY
        assert pattern.severity == BugSeverity.CRITICAL
        assert pattern.confidence_boost == 0.9


class TestDetectedBug:
    """Tests for DetectedBug dataclass."""

    def test_detected_bug_creation(self):
        """Test DetectedBug creation."""
        location = BugLocation(
            file_path="/path/file.py",
            line_number=10,
        )

        bug = DetectedBug(
            id="bug_123",
            severity=BugSeverity.HIGH,
            category=BugCategory.SECURITY,
            title="Security Issue",
            description="Found a security vulnerability",
            location=location,
            code_snippet="password = 'secret'",
            root_cause="Hardcoded password",
            suggested_fix="Use environment variables",
            confidence=0.95,
            detection_method="pattern_matching",
            fix_complexity="simple",
            estimated_effort_minutes=15,
        )

        assert bug.id == "bug_123"
        assert bug.severity == BugSeverity.HIGH
        assert bug.category == BugCategory.SECURITY
        assert bug.confidence == 0.95
        assert bug.fix_complexity == "simple"

    def test_detected_bug_to_dict(self):
        """Test DetectedBug serialization."""
        location = BugLocation(
            file_path="/path/file.py",
            line_number=10,
        )

        bug = DetectedBug(
            id="bug_456",
            severity=BugSeverity.MEDIUM,
            category=BugCategory.LOGIC,
            title="Logic Error",
            description="Off-by-one error",
            location=location,
            code_snippet="for i in range(n+1):",
            root_cause="Loop condition wrong",
            suggested_fix="Use range(n)",
            confidence=0.8,
            detection_method="static_analysis",
            fix_complexity="moderate",
            estimated_effort_minutes=30,
            related_bugs=["bug_123"],
        )

        data = bug.to_dict()

        assert data["id"] == "bug_456"
        assert data["severity"] == "medium"
        assert data["category"] == "logic"
        assert data["confidence"] == 0.8
        assert data["related_bugs"] == ["bug_123"]
        assert "detected_at" in data


class TestBugDetectorAgent:
    """Tests for BugDetectorAgent class."""

    def test_agent_initialization(self, bug_detector_agent):
        """Test agent initialization."""
        assert bug_detector_agent.name == "BugDetector"
        assert bug_detector_agent.role == "Security & Quality Analyst"
        assert "static_analysis" in bug_detector_agent.identity.capabilities
        assert "security_scanning" in bug_detector_agent.identity.capabilities

    def test_load_bug_patterns(self, bug_detector_agent):
        """Test bug patterns are loaded."""
        patterns = bug_detector_agent._patterns

        assert len(patterns) > 0

        # Check for specific patterns
        pattern_names = [p.name for p in patterns]
        assert "hardcoded_password" in pattern_names
        assert "bare_except" in pattern_names
        assert "eval_usage" in pattern_names

    @pytest.mark.asyncio
    async def test_execute_task_detect_bugs(self, bug_detector_agent, temp_python_file):
        """Test executing detect_bugs task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_123",
            task_type="detect_bugs",
            description="Find bugs in file",
            context={
                "file_path": temp_python_file,
                "use_static_analysis": True,
                "use_llm_review": True,
                "min_confidence": 0.5,
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.task_id == "task_123"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_security_scan(self, bug_detector_agent, temp_python_file):
        """Test executing security_scan task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_security",
            task_type="security_scan",
            description="Security scan",
            context={
                "file_path": temp_python_file,
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.task_id == "task_security"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_analyze_failure(self, bug_detector_agent, temp_python_file):
        """Test executing analyze_test_failure task type."""
        from backend.agents.base_agent import Task

        bug_detector_agent._llm.generate = AsyncMock(return_value="""{
            "title": "AssertionError",
            "category": "logic",
            "severity": "medium",
            "description": "Test assertion failed",
            "root_cause": "Expected value mismatch",
            "suggested_fix": "Fix the calculation",
            "line_number": 10,
            "confidence": 0.8
        }""")

        task = Task(
            task_id="task_analyze",
            task_type="analyze_test_failure",
            description="Analyze test failure",
            context={
                "test_name": "test_calculation",
                "error_message": "AssertionError: 1 != 2",
                "stack_trace": "Traceback...",
                "code_context": "assert 1 == 2",
                "file_path": temp_python_file,
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.task_id == "task_analyze"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_performance_audit(self, bug_detector_agent, temp_python_file):
        """Test executing performance_audit task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_perf",
            task_type="performance_audit",
            description="Performance audit",
            context={
                "file_path": temp_python_file,
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.task_id == "task_perf"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_unknown_type(self, bug_detector_agent):
        """Test executing unknown task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_unknown",
            task_type="unknown_type",
            description="Unknown",
            context={},
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.status.value == "failed"
        assert "Unknown task type" in result.error

    @pytest.mark.asyncio
    async def test_detect_bugs_in_file(self, bug_detector_agent, temp_python_file):
        """Test detecting bugs in a single file."""
        bugs = await bug_detector_agent.detect_bugs_in_file(
            file_path=temp_python_file,
            use_static_analysis=True,
            use_llm_review=True,
            min_confidence=0.5,
        )

        assert isinstance(bugs, list)
        # Should find patterns like hardcoded_password, eval_usage, bare_except

    @pytest.mark.asyncio
    async def test_detect_bugs_file_not_found(self, bug_detector_agent):
        """Test detecting bugs with non-existent file."""
        bugs = await bug_detector_agent.detect_bugs_in_file(
            file_path="/nonexistent/file.py",
            use_static_analysis=True,
            use_llm_review=False,
        )

        assert bugs == []

    @pytest.mark.asyncio
    async def test_detect_bugs_in_directory(self, bug_detector_agent, temp_directory):
        """Test detecting bugs in directory."""
        results = await bug_detector_agent.detect_bugs_in_directory(
            directory=temp_directory,
            file_patterns=["*.py"],
            use_static_analysis=True,
            use_llm_review=True,
            min_confidence=0.5,
        )

        assert isinstance(results, dict)

    @pytest.mark.asyncio
    async def test_detect_bugs_default_patterns(self, bug_detector_agent, temp_directory):
        """Test detecting bugs with default file patterns."""
        results = await bug_detector_agent.detect_bugs_in_directory(
            directory=temp_directory,
            use_static_analysis=True,
            use_llm_review=False,
        )

        assert isinstance(results, dict)

    @pytest.mark.asyncio
    async def test_analyze_test_failure(self, bug_detector_agent, temp_python_file):
        """Test analyzing a test failure."""
        bug_detector_agent._llm.generate = AsyncMock(return_value="""{
            "title": "Division by zero",
            "category": "logic",
            "severity": "high",
            "description": "Division by zero in calculation",
            "root_cause": "Missing zero check",
            "suggested_fix": "Add check for denominator",
            "line_number": 5,
            "confidence": 0.85
        }""")

        bug = await bug_detector_agent.analyze_test_failure(
            test_name="test_division",
            error_message="ZeroDivisionError: division by zero",
            stack_trace="Traceback (most recent call last):\n  File 'test.py', line 5",
            code_context="result = 10 / value",
            file_path=temp_python_file,
        )

        assert bug is not None
        assert bug.title == "Division by zero"
        assert bug.severity == BugSeverity.HIGH

    @pytest.mark.asyncio
    async def test_analyze_test_failure_llm_error(self, bug_detector_agent, temp_python_file):
        """Test analyze_test_failure when LLM fails."""
        bug_detector_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        bug = await bug_detector_agent.analyze_test_failure(
            test_name="test_fail",
            error_message="Error",
            stack_trace="Trace",
            code_context="code",
            file_path=temp_python_file,
        )

        assert bug is None

    @pytest.mark.asyncio
    async def test_get_bug_statistics(self, bug_detector_agent):
        """Test getting bug statistics."""
        location = BugLocation(file_path="/path/file.py", line_number=10)

        bugs = [
            DetectedBug(
                id="bug_1",
                severity=BugSeverity.CRITICAL,
                category=BugCategory.SECURITY,
                title="Security Issue",
                description="Issue 1",
                location=location,
                code_snippet="code",
                root_cause="cause",
                suggested_fix="fix",
                confidence=0.95,
                detection_method="static_analysis",
                fix_complexity="simple",
                estimated_effort_minutes=15,
            ),
            DetectedBug(
                id="bug_2",
                severity=BugSeverity.HIGH,
                category=BugCategory.LOGIC,
                title="Logic Issue",
                description="Issue 2",
                location=location,
                code_snippet="code",
                root_cause="cause",
                suggested_fix="fix",
                confidence=0.8,
                detection_method="llm_review",
                fix_complexity="moderate",
                estimated_effort_minutes=30,
            ),
            DetectedBug(
                id="bug_3",
                severity=BugSeverity.CRITICAL,
                category=BugCategory.SECURITY,
                title="Another Security Issue",
                description="Issue 3",
                location=location,
                code_snippet="code",
                root_cause="cause",
                suggested_fix="fix",
                confidence=0.92,
                detection_method="static_analysis",
                fix_complexity="simple",
                estimated_effort_minutes=20,
            ),
        ]

        stats = await bug_detector_agent.get_bug_statistics(bugs)

        assert stats["total"] == 3
        assert stats["by_severity"]["critical"] == 2
        assert stats["by_severity"]["high"] == 1
        assert stats["by_category"]["security"] == 2
        assert stats["by_category"]["logic"] == 1
        assert stats["high_confidence_bugs"] == 2
        assert stats["total_estimated_effort_minutes"] == 65

    @pytest.mark.asyncio
    async def test_run_static_analysis_syntax_error(self, bug_detector_agent, temp_syntax_error_file):
        """Test static analysis with syntax error file."""
        with open(temp_syntax_error_file, 'r') as f:
            code = f.read()

        bugs = await bug_detector_agent._run_static_analysis(temp_syntax_error_file, code)

        assert len(bugs) == 1
        assert bugs[0].category == BugCategory.SYNTAX
        assert bugs[0].severity == BugSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_run_static_analysis_eval_detection(self, bug_detector_agent):
        """Test static analysis detects eval usage."""
        code = "data = eval(user_input)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            file_path = f.name

        try:
            bugs = await bug_detector_agent._run_static_analysis(file_path, code)

            # Should detect eval usage
            eval_bugs = [b for b in bugs if "eval" in b.title.lower()]
            assert len(eval_bugs) >= 1
        finally:
            os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_run_pattern_matching(self, bug_detector_agent, temp_python_file):
        """Test pattern matching detection."""
        with open(temp_python_file, 'r') as f:
            code = f.read()

        bugs = await bug_detector_agent._run_pattern_matching(temp_python_file, code)

        assert isinstance(bugs, list)
        # Should find patterns in the test file

    @pytest.mark.asyncio
    async def test_run_llm_review(self, bug_detector_agent, temp_python_file):
        """Test LLM review."""
        with open(temp_python_file, 'r') as f:
            code = f.read()

        bugs = await bug_detector_agent._run_llm_review(temp_python_file, code)

        assert isinstance(bugs, list)

    @pytest.mark.asyncio
    async def test_run_llm_review_error(self, bug_detector_agent, temp_python_file):
        """Test LLM review with error."""
        bug_detector_agent._llm.generate = AsyncMock(side_effect=Exception("LLM failed"))

        with open(temp_python_file, 'r') as f:
            code = f.read()

        bugs = await bug_detector_agent._run_llm_review(temp_python_file, code)

        assert bugs == []

    @pytest.mark.asyncio
    async def test_run_llm_review_invalid_json(self, bug_detector_agent, temp_python_file):
        """Test LLM review with invalid JSON response."""
        bug_detector_agent._llm.generate = AsyncMock(return_value="not valid json")

        with open(temp_python_file, 'r') as f:
            code = f.read()

        bugs = await bug_detector_agent._run_llm_review(temp_python_file, code)

        assert bugs == []

    @pytest.mark.asyncio
    async def test_detect_bugs_task_directory(self, bug_detector_agent, temp_directory):
        """Test _detect_bugs_task with directory."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_dir",
            task_type="detect_bugs",
            description="Scan directory",
            context={
                "directory": temp_directory,
                "file_patterns": ["*.py"],
                "use_static_analysis": True,
                "use_llm_review": False,
                "min_confidence": 0.5,
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.status.value == "completed"
        assert "files_scanned" in result.output

    @pytest.mark.asyncio
    async def test_detect_bugs_task_missing_context(self, bug_detector_agent):
        """Test _detect_bugs_task without file_path or directory."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_missing",
            task_type="detect_bugs",
            description="Missing context",
            context={},
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.status.value == "failed"

    @pytest.mark.asyncio
    async def test_execute_task_exception(self, bug_detector_agent):
        """Test execute_task exception handling."""
        from backend.agents.base_agent import Task

        # Create task that will cause exception
        task = Task(
            task_id="task_exception",
            task_type="detect_bugs",
            description="Will fail",
            context={
                "file_path": None,  # This might cause issues
            },
        )

        result = await bug_detector_agent.execute_task(task)

        assert result.status.value == "failed"

    @pytest.mark.asyncio
    async def test_bugs_sorted_by_severity(self, bug_detector_agent, temp_python_file):
        """Test that bugs are sorted by severity."""
        bugs = await bug_detector_agent.detect_bugs_in_file(
            file_path=temp_python_file,
            use_static_analysis=True,
            use_llm_review=True,
            min_confidence=0.0,  # Include all
        )

        if len(bugs) > 1:
            severity_order = {
                BugSeverity.CRITICAL: 0,
                BugSeverity.HIGH: 1,
                BugSeverity.MEDIUM: 2,
                BugSeverity.LOW: 3,
                BugSeverity.INFO: 4,
            }

            for i in range(len(bugs) - 1):
                assert severity_order[bugs[i].severity] <= severity_order[bugs[i + 1].severity]

    @pytest.mark.asyncio
    async def test_min_confidence_filtering(self, bug_detector_agent, temp_python_file):
        """Test that bugs below confidence threshold are filtered out."""
        all_bugs = await bug_detector_agent.detect_bugs_in_file(
            file_path=temp_python_file,
            use_static_analysis=True,
            use_llm_review=True,
            min_confidence=0.0,
        )

        high_conf_bugs = await bug_detector_agent.detect_bugs_in_file(
            file_path=temp_python_file,
            use_static_analysis=True,
            use_llm_review=True,
            min_confidence=0.9,
        )

        assert len(high_conf_bugs) <= len(all_bugs)
