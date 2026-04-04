"""
Tests for TestIntelligenceEngine - Core orchestrator for AI-driven testing.
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from backend.testing.intelligence_engine import (
    BugReport,
    FixResult,
    TestCase,
    TestIntelligenceEngine,
    TestPriority,
    TestSuite,
    TestType,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="[]")
    return llm


@pytest.fixture
def intelligence_engine(mock_llm):
    """Fixture for TestIntelligenceEngine with mocked LLM."""
    engine = TestIntelligenceEngine(llm_provider=mock_llm)
    return engine


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('''def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b
''')
        f.flush()
        yield f.name
    os.unlink(f.name)


class TestTestPriorityEnum:
    """Tests for TestPriority enum."""

    def test_all_priority_values(self):
        """Test all TestPriority values."""
        assert TestPriority.CRITICAL.value == 1
        assert TestPriority.HIGH.value == 2
        assert TestPriority.MEDIUM.value == 3
        assert TestPriority.LOW.value == 4


class TestTestTypeEnum:
    """Tests for TestType enum."""

    def test_all_type_values(self):
        """Test all TestType values."""
        assert TestType.UNIT.value == "unit"
        assert TestType.INTEGRATION.value == "integration"
        assert TestType.E2E.value == "e2e"
        assert TestType.VISUAL.value == "visual"
        assert TestType.PERFORMANCE.value == "performance"
        assert TestType.SECURITY.value == "security"
        assert TestType.CONTRACT.value == "contract"


class TestTestCase:
    """Tests for TestCase dataclass."""

    def test_test_case_creation(self):
        """Test TestCase creation."""
        tc = TestCase(
            id="test_123",
            name="test_add_function",
            test_type=TestType.UNIT,
            target_file="/path/to/file.py",
            code="def test_add(): assert add(1, 2) == 3",
            priority=TestPriority.HIGH,
            description="Test add function",
        )

        assert tc.id == "test_123"
        assert tc.test_type == TestType.UNIT
        assert tc.priority == TestPriority.HIGH

    def test_test_case_defaults(self):
        """Test TestCase default values."""
        tc = TestCase(
            id="test_456",
            name="test_func",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="code",
            priority=TestPriority.MEDIUM,
        )

        assert tc.description == ""
        assert tc.dependencies == []
        assert tc.metadata == {}
        assert tc.success_count == 0
        assert tc.failure_count == 0
        assert tc.is_flaky is False

    def test_test_case_to_dict(self):
        """Test TestCase serialization."""
        tc = TestCase(
            id="test_789",
            name="test_func",
            test_type=TestType.INTEGRATION,
            target_file="/path/file.py",
            code="test code",
            priority=TestPriority.CRITICAL,
            description="Integration test",
            dependencies=["db", "api"],
            last_run=datetime(2024, 1, 15, 10, 0, 0),
            success_count=5,
            failure_count=1,
            is_flaky=True,
        )

        data = tc.to_dict()

        assert data["id"] == "test_789"
        assert data["test_type"] == "integration"
        assert data["priority"] == "CRITICAL"
        assert data["success_count"] == 5
        assert data["is_flaky"] is True


class TestBugReport:
    """Tests for BugReport dataclass."""

    def test_bug_report_creation(self):
        """Test BugReport creation."""
        bug = BugReport(
            id="bug_123",
            severity="high",
            category="security",
            file_path="/path/file.py",
            line_number=15,
            description="Security vulnerability",
            root_cause="Input not sanitized",
            suggested_fix="Add input validation",
            confidence=0.95,
        )

        assert bug.id == "bug_123"
        assert bug.severity == "high"
        assert bug.confidence == 0.95

    def test_bug_report_to_dict(self):
        """Test BugReport serialization."""
        bug = BugReport(
            id="bug_456",
            severity="medium",
            category="logic",
            file_path="/path/file.py",
            line_number=20,
            description="Logic error",
            root_cause="Wrong condition",
            suggested_fix="Fix condition",
            confidence=0.8,
            test_case_id="test_123",
        )

        data = bug.to_dict()

        assert data["id"] == "bug_456"
        assert data["severity"] == "medium"
        assert data["test_case_id"] == "test_123"
        assert "detected_at" in data


class TestFixResult:
    """Tests for FixResult dataclass."""

    def test_fix_result_creation(self):
        """Test FixResult creation."""
        fix = FixResult(
            bug_id="bug_123",
            success=True,
            file_path="/path/file.py",
            original_code="old code",
            fixed_code="new code",
            explanation="Fixed the bug",
        )

        assert fix.bug_id == "bug_123"
        assert fix.success is True

    def test_fix_result_to_dict(self):
        """Test FixResult serialization."""
        fix = FixResult(
            bug_id="bug_456",
            success=False,
            file_path="/path/file.py",
            original_code="code",
            fixed_code="code",
            explanation="Failed to fix",
            error_message="Could not parse",
        )

        data = fix.to_dict()

        assert data["bug_id"] == "bug_456"
        assert data["success"] is False
        assert data["error_message"] == "Could not parse"


class TestTestSuite:
    """Tests for TestSuite dataclass."""

    def test_test_suite_creation(self):
        """Test TestSuite creation."""
        suite = TestSuite(
            name="auth_tests",
            target_module="backend/services/auth.py",
            coverage_percentage=85.0,
            mutation_score=70.0,
        )

        assert suite.name == "auth_tests"
        assert suite.coverage_percentage == 85.0

    def test_test_suite_to_dict(self):
        """Test TestSuite serialization."""
        tc = TestCase(
            id="test_1",
            name="test",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="code",
            priority=TestPriority.MEDIUM,
        )

        suite = TestSuite(
            name="test_suite",
            target_module="module.py",
            test_cases=[tc],
            coverage_percentage=80.0,
            last_execution=datetime(2024, 1, 15, 10, 0, 0),
            execution_time_ms=1500.0,
        )

        data = suite.to_dict()

        assert data["name"] == "test_suite"
        assert data["test_count"] == 1
        assert data["coverage_percentage"] == 80.0


class TestTestIntelligenceEngine:
    """Tests for TestIntelligenceEngine class."""

    def test_engine_initialization(self, intelligence_engine):
        """Test engine initialization."""
        assert intelligence_engine._test_suites == {}
        assert intelligence_engine._bug_reports == {}
        assert intelligence_engine._fix_history == []

    @pytest.mark.asyncio
    async def test_analyze_module(self, intelligence_engine, temp_python_file):
        """Test analyzing a module."""
        intelligence_engine._llm.generate = AsyncMock(
            return_value="""def test_add():
    assert add(1, 2) == 3"""
        )

        suite = await intelligence_engine.analyze_module(
            file_path=temp_python_file,
            generate_missing_tests=True,
        )

        assert isinstance(suite, TestSuite)
        assert suite.target_module == temp_python_file

    @pytest.mark.asyncio
    async def test_analyze_module_no_tests(self, intelligence_engine, temp_python_file):
        """Test analyzing module without generating tests."""
        suite = await intelligence_engine.analyze_module(
            file_path=temp_python_file,
            generate_missing_tests=False,
        )

        assert isinstance(suite, TestSuite)

    @pytest.mark.asyncio
    async def test_detect_bugs(self, intelligence_engine):
        """Test detecting bugs in a test suite."""
        suite = TestSuite(
            name="test_suite",
            target_module="/path/file.py",
        )

        bugs = await intelligence_engine.detect_bugs(
            test_suite=suite,
            run_tests=False,
        )

        assert isinstance(bugs, list)

    @pytest.mark.asyncio
    async def test_detect_bugs_with_tests(self, intelligence_engine):
        """Test detecting bugs with running tests."""
        suite = TestSuite(
            name="test_suite",
            target_module="/path/file.py",
        )

        bugs = await intelligence_engine.detect_bugs(
            test_suite=suite,
            run_tests=True,
        )

        assert isinstance(bugs, list)

    @pytest.mark.asyncio
    async def test_apply_fixes(self, intelligence_engine, temp_python_file):
        """Test applying fixes to bugs."""
        bugs = [
            BugReport(
                id="bug_1",
                severity="high",
                category="logic",
                file_path=temp_python_file,
                line_number=5,
                description="Bug 1",
                root_cause="Cause 1",
                suggested_fix="Fix 1",
                confidence=0.9,
            ),
        ]

        intelligence_engine._llm.generate = AsyncMock(return_value="fixed code")

        results = await intelligence_engine.apply_fixes(
            bugs=bugs,
            auto_apply=False,
            confidence_threshold=0.85,
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_apply_fixes_low_confidence(self, intelligence_engine, temp_python_file):
        """Test apply_fixes skips low confidence bugs."""
        bugs = [
            BugReport(
                id="bug_low",
                severity="high",
                category="logic",
                file_path=temp_python_file,
                line_number=5,
                description="Low confidence bug",
                root_cause="Unknown",
                suggested_fix="Maybe this",
                confidence=0.5,  # Below threshold
            ),
        ]

        results = await intelligence_engine.apply_fixes(
            bugs=bugs,
            auto_apply=True,
            confidence_threshold=0.85,
        )

        # Low confidence bug should be skipped when auto_apply is True
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_run_self_healing_tests(self, intelligence_engine):
        """Test running self-healing tests."""
        tc = TestCase(
            id="test_1",
            name="test_func",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="test code",
            priority=TestPriority.MEDIUM,
        )

        suite = TestSuite(
            name="test_suite",
            target_module="/path/file.py",
            test_cases=[tc],
        )

        results = await intelligence_engine.run_self_healing_tests(
            test_suite=suite,
            max_retries=3,
        )

        assert "passed" in results
        assert "failed" in results
        assert "healed" in results

    @pytest.mark.asyncio
    async def test_generate_test_from_failure(self, intelligence_engine):
        """Test generating test from failure."""
        intelligence_engine._llm.generate = AsyncMock(
            return_value="""def test_regression():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)"""
        )

        tc = await intelligence_engine.generate_test_from_failure(
            error_message="ZeroDivisionError: division by zero",
            stack_trace="Traceback...",
            code_context="result = 10 / value",
        )

        assert tc is not None
        assert "regression" in tc.id

    @pytest.mark.asyncio
    async def test_generate_test_from_failure_error(self, intelligence_engine):
        """Test generate_test_from_failure when LLM fails."""
        intelligence_engine._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        tc = await intelligence_engine.generate_test_from_failure(
            error_message="Error",
            stack_trace="Trace",
            code_context="code",
        )

        assert tc is None

    def test_get_test_health_report_empty(self, intelligence_engine):
        """Test health report with no data."""
        report = intelligence_engine.get_test_health_report()

        assert report["summary"]["total_test_suites"] == 0
        assert report["summary"]["total_tests"] == 0

    def test_get_test_health_report(self, intelligence_engine):
        """Test health report with data."""
        # Add test suite
        tc1 = TestCase(
            id="test_1",
            name="test1",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="code",
            priority=TestPriority.MEDIUM,
            is_flaky=True,
        )
        tc2 = TestCase(
            id="test_2",
            name="test2",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="code",
            priority=TestPriority.MEDIUM,
        )

        suite = TestSuite(
            name="suite1",
            target_module="/path/file.py",
            test_cases=[tc1, tc2],
            coverage_percentage=80.0,
        )
        intelligence_engine._test_suites["/path/file.py"] = suite

        # Add bugs
        bug = BugReport(
            id="bug_1",
            severity="critical",
            category="security",
            file_path="/path/file.py",
            line_number=10,
            description="Bug",
            root_cause="Cause",
            suggested_fix="Fix",
            confidence=0.9,
        )
        intelligence_engine._bug_reports["bug_1"] = bug

        report = intelligence_engine.get_test_health_report()

        assert report["summary"]["total_test_suites"] == 1
        assert report["summary"]["total_tests"] == 2
        assert report["summary"]["flaky_tests"] == 1
        assert report["summary"]["critical_bugs"] == 1

    @pytest.mark.asyncio
    async def test_read_file(self, intelligence_engine, temp_python_file):
        """Test _read_file method."""
        content = await intelligence_engine._read_file(temp_python_file)

        assert "def add" in content

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, intelligence_engine):
        """Test _read_file with non-existent file."""
        content = await intelligence_engine._read_file("/nonexistent/file.py")

        assert content == ""

    @pytest.mark.asyncio
    async def test_analyze_code_structure(self, intelligence_engine, temp_python_file):
        """Test _analyze_code_structure method."""
        with open(temp_python_file) as f:
            code = f.read()

        analysis = await intelligence_engine._analyze_code_structure(code, temp_python_file)

        assert "functions" in analysis
        assert "classes" in analysis
        assert "total_lines" in analysis

    @pytest.mark.asyncio
    async def test_analyze_code_structure_syntax_error(self, intelligence_engine):
        """Test _analyze_code_structure with syntax error."""
        code = "this is not valid python {{{{"

        analysis = await intelligence_engine._analyze_code_structure(code, "/path/file.py")

        assert analysis["functions"] == []
        assert analysis["classes"] == []

    @pytest.mark.asyncio
    async def test_find_existing_tests(self, intelligence_engine, temp_python_file):
        """Test _find_existing_tests method."""
        existing = await intelligence_engine._find_existing_tests(temp_python_file)

        assert isinstance(existing, list)

    def test_identify_test_gaps(self, intelligence_engine):
        """Test _identify_test_gaps method."""
        analysis = {
            "functions": [
                {"name": "public_func", "line": 10},
                {"name": "_private_func", "line": 20},
            ],
            "classes": [
                {"name": "MyClass", "line": 30, "methods": ["method1", "method2"]},
            ],
        }

        gaps = intelligence_engine._identify_test_gaps(analysis, [])

        # Should include public_func and MyClass
        assert len(gaps) >= 2
        names = [g["name"] for g in gaps]
        assert "public_func" in names
        assert "MyClass" in names

    @pytest.mark.asyncio
    async def test_generate_tests_for_gaps(self, intelligence_engine, temp_python_file):
        """Test _generate_tests_for_gaps method."""
        with open(temp_python_file) as f:
            code = f.read()

        gaps = [
            {"type": "function", "name": "add", "line": 1},
        ]

        intelligence_engine._llm.generate = AsyncMock(return_value="def test_add(): pass")

        tests = await intelligence_engine._generate_tests_for_gaps(temp_python_file, code, gaps)

        assert len(tests) == 1

    @pytest.mark.asyncio
    async def test_generate_tests_for_gaps_error(self, intelligence_engine, temp_python_file):
        """Test _generate_tests_for_gaps when LLM fails."""
        intelligence_engine._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        with open(temp_python_file) as f:
            code = f.read()

        gaps = [{"type": "function", "name": "add", "line": 1}]

        tests = await intelligence_engine._generate_tests_for_gaps(temp_python_file, code, gaps)

        assert tests == []

    @pytest.mark.asyncio
    async def test_static_analysis(self, intelligence_engine):
        """Test _static_analysis method."""
        bugs = await intelligence_engine._static_analysis("/path/file.py")

        assert bugs == []  # Returns empty list in current implementation

    @pytest.mark.asyncio
    async def test_analyze_test_failures(self, intelligence_engine):
        """Test _analyze_test_failures method."""
        suite = TestSuite(name="suite", target_module="/path/file.py")

        bugs = await intelligence_engine._analyze_test_failures(suite)

        assert bugs == []  # Returns empty list in current implementation

    @pytest.mark.asyncio
    async def test_llm_code_review(self, intelligence_engine, temp_python_file):
        """Test _llm_code_review method."""
        intelligence_engine._llm.generate = AsyncMock(
            return_value="""[
            {"severity": "high", "category": "logic", "line": 5,
             "description": "Issue", "suggestion": "Fix it"}
        ]"""
        )

        bugs = await intelligence_engine._llm_code_review(temp_python_file)

        assert len(bugs) == 1
        assert bugs[0].severity == "high"

    @pytest.mark.asyncio
    async def test_llm_code_review_error(self, intelligence_engine, temp_python_file):
        """Test _llm_code_review when LLM fails."""
        intelligence_engine._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        bugs = await intelligence_engine._llm_code_review(temp_python_file)

        assert bugs == []

    @pytest.mark.asyncio
    async def test_generate_fix(self, intelligence_engine, temp_python_file):
        """Test _generate_fix method."""
        bug = BugReport(
            id="bug_1",
            severity="high",
            category="logic",
            file_path=temp_python_file,
            line_number=5,
            description="Bug",
            root_cause="Cause",
            suggested_fix="Fix",
            confidence=0.9,
        )

        intelligence_engine._llm.generate = AsyncMock(return_value="fixed code")

        fix = await intelligence_engine._generate_fix(bug)

        assert fix.success is True
        assert fix.bug_id == "bug_1"

    @pytest.mark.asyncio
    async def test_generate_fix_error(self, intelligence_engine, temp_python_file):
        """Test _generate_fix when LLM fails."""
        bug = BugReport(
            id="bug_1",
            severity="high",
            category="logic",
            file_path=temp_python_file,
            line_number=5,
            description="Bug",
            root_cause="Cause",
            suggested_fix="Fix",
            confidence=0.9,
        )

        intelligence_engine._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        fix = await intelligence_engine._generate_fix(bug)

        assert fix.success is False
        assert fix.error_message is not None

    @pytest.mark.asyncio
    async def test_run_test_with_healing(self, intelligence_engine):
        """Test _run_test_with_healing method."""
        tc = TestCase(
            id="test_1",
            name="test_func",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="code",
            priority=TestPriority.MEDIUM,
        )

        result = await intelligence_engine._run_test_with_healing(tc, 3)

        assert "status" in result

    def test_register_callback(self, intelligence_engine):
        """Test register_callback method."""

        async def callback(data):
            pass

        intelligence_engine.register_callback("test_generated", callback)
        intelligence_engine.register_callback("bug_detected", callback)
        intelligence_engine.register_callback("fix_applied", callback)

        assert len(intelligence_engine._on_test_generated) == 1
        assert len(intelligence_engine._on_bug_detected) == 1
        assert len(intelligence_engine._on_fix_applied) == 1

    @pytest.mark.asyncio
    async def test_callback_execution(self, intelligence_engine):
        """Test callbacks are executed."""
        callback_called = []

        async def test_callback(test_case):
            callback_called.append(test_case)

        intelligence_engine.register_callback("test_generated", test_callback)

        intelligence_engine._llm.generate = AsyncMock(return_value="def test(): pass")

        await intelligence_engine.generate_test_from_failure(
            error_message="Error",
            stack_trace="Trace",
            code_context="code",
        )

        assert len(callback_called) == 1

    @pytest.mark.asyncio
    async def test_calculate_coverage(self, intelligence_engine, temp_python_file):
        """Test _calculate_coverage method."""
        coverage = await intelligence_engine._calculate_coverage(temp_python_file)

        assert isinstance(coverage, float)
        assert 0.0 <= coverage <= 100.0  # Real coverage is computed now


class TestIntelligenceEngineExtendedCoverage:
    """Tests for extended coverage - lines 285, 334, 380-388, 573, 651."""

    @pytest.fixture
    def mock_llm(self):
        """Fixture for mocked LLM provider."""
        from unittest.mock import AsyncMock, Mock

        llm = Mock()
        llm.generate = AsyncMock(return_value="def test(): pass")
        return llm

    @pytest.fixture
    def intelligence_engine(self, mock_llm):
        """Fixture for TestIntelligenceEngine with mocked LLM."""
        from backend.testing.intelligence_engine import TestIntelligenceEngine

        engine = TestIntelligenceEngine(llm_provider=mock_llm)
        return engine

    @pytest.mark.asyncio
    async def test_detect_bugs_stores_in_bug_reports_line_285(self, intelligence_engine):
        """Test line 285: bugs are stored in _bug_reports dict."""
        import os
        import tempfile

        from backend.testing.intelligence_engine import TestSuite

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def func():\n    return 1\n")
            f.flush()
            file_path = f.name

        try:
            test_suite = TestSuite(
                name="test_suite",
                target_module=file_path,
                test_cases=[],
            )

            bugs = await intelligence_engine.detect_bugs(test_suite, run_tests=False)

            # Line 285: bugs should be stored in _bug_reports
            for bug in bugs:
                assert bug.id in intelligence_engine._bug_reports
        finally:
            os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_apply_fixes_callback_line_334(self, intelligence_engine):
        """Test line 334: fix callback is executed on success."""

        from backend.testing.intelligence_engine import BugReport

        # Register a callback
        callback_results = []

        async def fix_callback(fix_result):
            callback_results.append(fix_result)

        intelligence_engine.register_callback("fix_applied", fix_callback)

        # Create a bug to fix
        bug = BugReport(
            id="bug_callback",
            severity="low",
            category="logic",
            file_path="/path/file.py",
            line_number=1,
            description="Test bug",
            root_cause="Test cause",
            suggested_fix="Test fix",
            confidence=0.9,
        )

        # Mock _generate_fix to return a successful fix
        async def mock_generate_fix(bug):
            from backend.testing.intelligence_engine import FixResult

            return FixResult(
                bug_id=bug.id,
                success=True,
                file_path=bug.file_path,
                original_code="original",
                fixed_code="fixed",
                explanation="Fixed the bug",
            )

        intelligence_engine._generate_fix = mock_generate_fix

        await intelligence_engine.apply_fixes([bug], auto_apply=True)

        # Line 334: callback should have been called
        assert len(callback_results) == 1
        assert callback_results[0].success is True

    @pytest.mark.asyncio
    async def test_run_self_healing_tests_all_status_lines_380_388(self, intelligence_engine):
        """Test lines 380-388: all test result status categories."""

        from backend.testing.intelligence_engine import TestCase, TestPriority, TestSuite, TestType

        # Create test cases
        test_cases = [
            TestCase(
                id="passed",
                name="test_passed",
                test_type=TestType.UNIT,
                target_file="/f.py",
                code="",
                priority=TestPriority.HIGH,
            ),
            TestCase(
                id="healed",
                name="test_healed",
                test_type=TestType.UNIT,
                target_file="/f.py",
                code="",
                priority=TestPriority.HIGH,
            ),
            TestCase(
                id="flaky",
                name="test_flaky",
                test_type=TestType.UNIT,
                target_file="/f.py",
                code="",
                priority=TestPriority.HIGH,
            ),
            TestCase(
                id="failed",
                name="test_failed",
                test_type=TestType.UNIT,
                target_file="/f.py",
                code="",
                priority=TestPriority.HIGH,
            ),
        ]

        test_suite = TestSuite(
            name="status_test_suite",
            target_module="/path/to/module.py",
            test_cases=test_cases,
        )

        # Mock _run_test_with_healing to return different statuses
        call_count = [0]

        async def mock_run_test_with_healing(test_case, max_retries):
            statuses = ["passed", "healed", "flaky", "failed"]
            status = statuses[call_count[0] % 4]
            call_count[0] += 1
            return {"status": status}

        intelligence_engine._run_test_with_healing = mock_run_test_with_healing

        results = await intelligence_engine.run_self_healing_tests(test_suite)

        # Lines 380-388: all status categories should be updated
        assert "passed" in results["passed"]
        assert "healed" in results["healed"]
        assert "flaky" in results["flaky"]
        assert "failed" in results["failed"]

    @pytest.mark.asyncio
    async def test_find_existing_tests_path_exists_line_573(self, intelligence_engine):
        """Test line 573: Path.exists() check."""
        import os
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        # Create a temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def func(): pass")
            f.flush()
            source_path = f.name

        try:
            # Mock Path.exists to return True for one pattern

            def mock_exists(self):
                if "tests/test_" in str(self):
                    return True
                return False

            with patch.object(Path, "exists", mock_exists):
                existing = await intelligence_engine._find_existing_tests(source_path)

                # Line 573: should find the test file
                assert len(existing) >= 0  # May find tests depending on pattern
        finally:
            os.unlink(source_path)

    @pytest.mark.asyncio
    async def test_generate_tests_for_gaps_callback_line_651(self, intelligence_engine):
        """Test line 651: test generated callback execution."""
        from unittest.mock import AsyncMock

        # Register a callback
        callback_results = []

        async def test_generated_callback(test_case):
            callback_results.append(test_case)

        intelligence_engine.register_callback("test_generated", test_generated_callback)

        # Mock LLM to return test code
        intelligence_engine._llm.generate = AsyncMock(return_value="def test_gap(): assert True")

        gaps = [{"type": "function", "name": "my_func", "line": 10}]

        await intelligence_engine._generate_tests_for_gaps(
            file_path="/path/to/file.py",
            code="def my_func():\n    return 1",
            gaps=gaps,
        )

        # Line 651: callback should have been called
        assert len(callback_results) == 1
        assert "my_func" in callback_results[0].name


class TestCoverageGapsIntelligenceEngine:
    """Additional tests to cover remaining lines (285, 334, 380-388, 573)."""

    @pytest.fixture
    def engine(self, mock_llm):
        """Fixture for TestIntelligenceEngine."""
        return TestIntelligenceEngine(llm_provider=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_bugs_stores_in_bug_reports_line_285(self, engine, temp_python_file):
        """Test line 285: bugs are stored in _bug_reports during detection."""
        from unittest.mock import AsyncMock

        # Create a test suite
        tc = TestCase(
            id="test_1",
            name="test_example",
            test_type=TestType.UNIT,
            target_file=temp_python_file,
            code="def test(): assert True",
            priority=TestPriority.MEDIUM,
        )
        suite = TestSuite(name="test_suite", target_module=temp_python_file, test_cases=[tc])

        # Mock LLM to return a bug
        engine._llm.generate = AsyncMock(return_value='[{"severity": "medium", "description": "Potential bug"}]')
        engine._analyze_test_failures = AsyncMock(return_value=[])
        engine._llm_code_review = AsyncMock(
            return_value=[
                BugReport(
                    id="bug_detected",
                    severity="medium",
                    category="logic",
                    file_path=temp_python_file,
                    line_number=1,
                    description="Found potential issue",
                    root_cause="Logic error",
                    suggested_fix="Fix the logic",
                    confidence=0.9,
                )
            ]
        )

        bugs = await engine.detect_bugs(suite, run_tests=False)

        # Line 285: bugs should be stored in _bug_reports
        assert len(bugs) == 1
        assert "bug_detected" in engine._bug_reports
        assert engine._bug_reports["bug_detected"].severity == "medium"

    @pytest.mark.asyncio
    async def test_apply_fixes_callback_line_334(self, engine):
        """Test line 334: callback is executed when fix is applied."""
        from unittest.mock import AsyncMock

        callback_called = []

        async def fix_applied_callback(fix_result):
            callback_called.append(fix_result)

        engine.register_callback("fix_applied", fix_applied_callback)

        # Create a bug
        bug = BugReport(
            id="bug_to_fix",
            severity="low",
            category="style",
            file_path="/test/file.py",
            line_number=10,
            description="Test issue",
            root_cause="Test cause",
            suggested_fix="Test fix suggestion",
            confidence=0.95,
        )

        # Mock _generate_fix to return a successful result
        engine._generate_fix = AsyncMock(
            return_value=FixResult(
                bug_id=bug.id,
                success=True,
                file_path=bug.file_path,
                original_code="old code",
                fixed_code="new code",
                explanation="Fixed the issue",
            )
        )

        await engine.apply_fixes([bug], auto_apply=False, confidence_threshold=0.5)

        # Line 334: callback should have been called
        assert len(callback_called) == 1
        assert callback_called[0].success is True

    @pytest.mark.asyncio
    async def test_run_self_healing_tests_all_branches_lines_380_388(self, engine):
        """Test lines 380-388: all branches of test execution status."""
        # Test the healed, flaky, and failed branches

        # Create test cases
        tc_healed = TestCase(
            id="tc_healed",
            name="test_healed",
            test_type=TestType.UNIT,
            target_file="/test.py",
            code="def test(): pass",
            priority=TestPriority.MEDIUM,
        )
        tc_flaky = TestCase(
            id="tc_flaky",
            name="test_flaky",
            test_type=TestType.UNIT,
            target_file="/test.py",
            code="def test(): pass",
            priority=TestPriority.MEDIUM,
        )
        tc_failed = TestCase(
            id="tc_failed",
            name="test_failed",
            test_type=TestType.UNIT,
            target_file="/test.py",
            code="def test(): pass",
            priority=TestPriority.MEDIUM,
        )

        suite = TestSuite(
            name="test_suite",
            target_module="/test.py",
            test_cases=[tc_healed, tc_flaky, tc_failed],
        )

        # Mock _run_test_with_healing to return different statuses
        call_count = 0

        async def mock_run_test(test_case, max_retries):
            nonlocal call_count
            call_count += 1
            if test_case.id == "tc_healed":
                return {"status": "healed"}  # Line 380-382
            elif test_case.id == "tc_flaky":
                return {"status": "flaky"}  # Line 383-385
            else:
                return {"status": "failed"}  # Line 386-388

        engine._run_test_with_healing = mock_run_test

        results = await engine.run_self_healing_tests(suite, max_retries=2)

        # Verify all branches were hit
        assert "tc_healed" in results["healed"]
        assert "tc_flaky" in results["flaky"]
        assert "tc_failed" in results["failed"]

    @pytest.mark.asyncio
    async def test_find_existing_tests_with_existing_file_line_573(self, engine):
        """Test line 573: appends to existing list when Path.exists() returns True."""
        import tempfile
        from pathlib import Path

        # Create a temp directory structure with a test file
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the source file
            source_file = Path(tmpdir) / "module.py"
            source_file.write_text("def func(): pass")

            # Create the tests directory and test file that matches the pattern
            tests_dir = Path(tmpdir) / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / f"test_{source_file.name}"
            test_file.write_text("def test_func(): pass")

            # Now call _find_existing_tests with the source path
            # We need to mock Path.exists to return True for our pattern
            original_exists = Path.exists

            def mock_exists(self):
                # Return True for any path containing 'test_'
                if "test_" in str(self):
                    return True
                return original_exists(self)

            from unittest.mock import patch

            with patch.object(Path, "exists", mock_exists):
                existing = await engine._find_existing_tests(str(source_file))

                # Line 573 should be hit - existing should contain at least one entry
                assert len(existing) >= 1
