"""
Comprehensive tests for Testing API routes.

Covers all testing endpoints:
- Test generation
- Bug detection and fixing
- Coverage analysis
- Test health monitoring
- Frontend testing (E2E, visual regression, accessibility)
"""

from datetime import datetime
from enum import Enum
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import HTTPException

from backend.api.dependencies import User
from backend.api.routes.testing import (
    CoverageRequest,
    DetectBugsRequest,
    FixBugRequest,
    GenerateTestsRequest,
    RunTestsRequest,
    analyze_coverage,
    batch_fix,
    detect_bugs,
    fix_bug,
    generate_e2e_tests,
    generate_tests,
    get_auto_fixer,
    get_bug_detector,
    get_coverage_analyzer,
    get_flaky_tests,
    get_frontend_statistics,
    get_frontend_tester,
    get_intelligence_engine,
    get_test_generator,
    get_test_health,
    get_test_runner,
    preview_fix,
    quarantine_test,
    rollback_fix,
    run_accessibility_audit,
    run_full_test_suite,
    run_tests,
    run_visual_regression,
    unquarantine_test,
)


class MockStatus(Enum):
    """Mock status enum."""

    SUCCESS = "success"
    FAILED = "failed"
    PASSED = "passed"


class MockStrategy(Enum):
    """Mock strategy enum."""

    AI = "ai"
    PATTERN = "pattern"


class TestDependencyInjection:
    """Tests for dependency injection functions."""

    @pytest.mark.asyncio
    async def test_get_intelligence_engine(self):
        """Test getting intelligence engine instance."""
        engine = await get_intelligence_engine()
        assert engine is not None

    @pytest.mark.asyncio
    async def test_get_test_generator(self):
        """Test getting test generator agent."""
        agent = await get_test_generator()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_get_bug_detector(self):
        """Test getting bug detector agent."""
        agent = await get_bug_detector()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_get_auto_fixer(self):
        """Test getting auto fixer agent."""
        agent = await get_auto_fixer()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_get_frontend_tester(self):
        """Test getting frontend tester agent."""
        agent = await get_frontend_tester()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_get_test_runner(self):
        """Test getting test runner instance."""
        runner = await get_test_runner()
        assert runner is not None

    @pytest.mark.asyncio
    async def test_get_coverage_analyzer(self):
        """Test getting coverage analyzer instance."""
        analyzer = await get_coverage_analyzer()
        assert analyzer is not None


class TestGenerateTestsEndpoint:
    """Tests for POST /testing/generate-tests endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock test generator agent."""
        agent = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_generate_tests_success(self, mock_user, mock_agent):
        """Test successful test generation."""
        mock_test = Mock()
        mock_test.to_dict.return_value = {"name": "test_function", "type": "unit", "code": "def test_function(): pass"}
        mock_agent.generate_tests_for_file.return_value = [mock_test, mock_test]

        request = GenerateTestsRequest(
            file_path="src/module.py", include_edge_cases=True, include_error_cases=True, include_property_tests=False
        )

        response = await generate_tests(request=request, current_user=mock_user, agent=mock_agent)

        assert response.tests_generated == 2
        assert response.file_path == "src/module.py"
        mock_agent.generate_tests_for_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tests_error(self, mock_user, mock_agent):
        """Test test generation error handling."""
        mock_agent.generate_tests_for_file.side_effect = Exception("Generation failed")

        request = GenerateTestsRequest(file_path="src/module.py")

        with pytest.raises(HTTPException) as exc_info:
            await generate_tests(request=request, current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500


class TestDetectBugsEndpoint:
    """Tests for POST /testing/detect-bugs endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock bug detector agent."""
        agent = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_detect_bugs_in_directory(self, mock_user, mock_agent):
        """Test detecting bugs in directory."""
        mock_bug = Mock()
        mock_bug.to_dict.return_value = {"id": "bug-1", "type": "security", "severity": "high"}
        mock_agent.detect_bugs_in_directory.return_value = {"file1.py": [mock_bug], "file2.py": [mock_bug]}
        mock_agent.get_bug_statistics.return_value = {"by_severity": {"high": 2}, "by_category": {"security": 2}}

        request = DetectBugsRequest(directory="src/", use_static_analysis=True, use_llm_review=True, min_confidence=0.7)

        response = await detect_bugs(request=request, current_user=mock_user, agent=mock_agent)

        assert response.bugs_found == 2
        assert response.directory == "src/"
        mock_agent.detect_bugs_in_directory.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_bugs_in_file(self, mock_user, mock_agent):
        """Test detecting bugs in a specific file."""
        mock_bug = Mock()
        mock_bug.to_dict.return_value = {"id": "bug-1", "type": "logic", "severity": "medium"}
        mock_agent.detect_bugs_in_file.return_value = [mock_bug]
        mock_agent.get_bug_statistics.return_value = {"by_severity": {"medium": 1}, "by_category": {"logic": 1}}

        request = DetectBugsRequest(
            file_path="src/module.py", use_static_analysis=True, use_llm_review=False, min_confidence=0.5
        )

        response = await detect_bugs(request=request, current_user=mock_user, agent=mock_agent)

        assert response.bugs_found == 1
        assert response.file_path == "src/module.py"

    @pytest.mark.asyncio
    async def test_detect_bugs_no_path_provided(self, mock_user, mock_agent):
        """Test detect bugs without file_path or directory."""
        request = DetectBugsRequest()

        with pytest.raises(HTTPException) as exc_info:
            await detect_bugs(request=request, current_user=mock_user, agent=mock_agent)

        # All exceptions are wrapped in 500 by the error handler
        assert exc_info.value.status_code == 500
        assert "Either file_path or directory must be provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_detect_bugs_error(self, mock_user, mock_agent):
        """Test detect bugs error handling."""
        mock_agent.detect_bugs_in_file.side_effect = Exception("Detection failed")

        request = DetectBugsRequest(file_path="src/module.py")

        with pytest.raises(HTTPException) as exc_info:
            await detect_bugs(request=request, current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500


class TestFixBugEndpoint:
    """Tests for POST /testing/fix-bug endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock auto fixer agent."""
        agent = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_fix_bug_success(self, mock_user, mock_agent):
        """Test successful bug fix."""
        mock_fix = Mock()
        mock_fix.id = "fix-123"
        mock_fix.bug_id = "bug-456"
        mock_fix.status = MockStatus.SUCCESS
        mock_fix.strategy = MockStrategy.AI
        mock_fix.diff = "- old\n+ new"
        mock_fix.validation_results = {"passed": True}

        mock_agent.fix_bug.return_value = mock_fix

        request = FixBugRequest(
            bug_id="bug-456",
            file_path="src/module.py",
            bug_description="Null pointer exception",
            suggested_fix="Add null check",
            line_number=42,
            auto_apply=False,
        )

        response = await fix_bug(request=request, current_user=mock_user, agent=mock_agent)

        assert response.fix_id == "fix-123"
        assert response.bug_id == "bug-456"
        assert response.validation_passed is True

    @pytest.mark.asyncio
    async def test_fix_bug_error(self, mock_user, mock_agent):
        """Test bug fix error handling."""
        mock_agent.fix_bug.side_effect = Exception("Fix failed")

        request = FixBugRequest(bug_id="bug-456", file_path="src/module.py", bug_description="Bug")

        with pytest.raises(HTTPException) as exc_info:
            await fix_bug(request=request, current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500


class TestBatchFixEndpoint:
    """Tests for POST /testing/batch-fix endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock auto fixer agent."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_batch_fix(self, mock_user, mock_agent):
        """Test batch fix endpoint."""
        response = await batch_fix(
            bug_ids=["bug-1", "bug-2", "bug-3"], auto_apply=False, current_user=mock_user, agent=mock_agent
        )

        assert response["status"] == "not_implemented"
        assert response["bug_ids"] == ["bug-1", "bug-2", "bug-3"]


class TestPreviewFixEndpoint:
    """Tests for POST /testing/preview-fix endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock auto fixer agent."""
        agent = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_preview_fix_success(self, mock_user, mock_agent):
        """Test successful fix preview."""
        mock_agent.preview_fix.return_value = {"diff": "- old\n+ new", "confidence": 0.85, "impact": "low"}

        request = FixBugRequest(
            bug_id="bug-456", file_path="src/module.py", bug_description="Bug description", line_number=42
        )

        response = await preview_fix(request=request, current_user=mock_user, agent=mock_agent)

        assert response["diff"] == "- old\n+ new"
        mock_agent.preview_fix.assert_called_once()

    @pytest.mark.asyncio
    async def test_preview_fix_error(self, mock_user, mock_agent):
        """Test preview fix error handling."""
        mock_agent.preview_fix.side_effect = Exception("Preview failed")

        request = FixBugRequest(bug_id="bug-456", file_path="src/module.py", bug_description="Bug")

        with pytest.raises(HTTPException) as exc_info:
            await preview_fix(request=request, current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500


class TestRollbackFixEndpoint:
    """Tests for POST /testing/rollback-fix/{fix_id} endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock auto fixer agent."""
        agent = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_rollback_fix_success(self, mock_user, mock_agent):
        """Test successful rollback."""
        mock_agent.rollback_fix.return_value = True

        response = await rollback_fix(fix_id="fix-123", current_user=mock_user, agent=mock_agent)

        assert response["fix_id"] == "fix-123"
        assert response["rolled_back"] is True

    @pytest.mark.asyncio
    async def test_rollback_fix_not_found(self, mock_user, mock_agent):
        """Test rollback when fix not found."""
        mock_agent.rollback_fix.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await rollback_fix(fix_id="nonexistent", current_user=mock_user, agent=mock_agent)

        # All exceptions are wrapped in 500 by the error handler
        assert exc_info.value.status_code == 500
        assert "Fix not found" in exc_info.value.detail or "rollback failed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_rollback_fix_error(self, mock_user, mock_agent):
        """Test rollback error handling."""
        mock_agent.rollback_fix.side_effect = Exception("Rollback failed")

        with pytest.raises(HTTPException) as exc_info:
            await rollback_fix(fix_id="fix-123", current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500


class TestRunTestsEndpoint:
    """Tests for POST /testing/run-tests endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_runner(self):
        """Create mock test runner."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_run_tests_success(self, mock_user, mock_runner):
        """Test successful test run."""
        request = RunTestsRequest(test_suite="unit", file_pattern="test_*.py", max_retries=3, parallel_workers=4)

        response = await run_tests(request=request, current_user=mock_user, runner=mock_runner)

        assert response.suite_name == "unit"
        assert response.total_tests == 0  # Placeholder response

    @pytest.mark.asyncio
    async def test_run_tests_default_suite(self, mock_user, mock_runner):
        """Test run tests with default suite name."""
        request = RunTestsRequest()

        response = await run_tests(request=request, current_user=mock_user, runner=mock_runner)

        assert response.suite_name == "default"

    @pytest.mark.asyncio
    async def test_run_tests_exception(self, mock_user):
        """Test run tests exception handling (covers lines 403-405)."""
        request = RunTestsRequest(test_suite="unit")
        mock_runner = AsyncMock()

        # Patch RunTestsResponse to raise an exception when instantiated
        with patch("backend.api.routes.testing.RunTestsResponse") as mock_response:
            mock_response.side_effect = Exception("Test creation error")

            with pytest.raises(HTTPException) as exc_info:
                await run_tests(request=request, current_user=mock_user, runner=mock_runner)

            assert exc_info.value.status_code == 500
            assert "Test creation error" in exc_info.value.detail


class TestAnalyzeCoverageEndpoint:
    """Tests for POST /testing/analyze-coverage endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_analyzer(self):
        """Create mock coverage analyzer."""
        analyzer = AsyncMock()
        return analyzer

    @pytest.mark.asyncio
    async def test_analyze_coverage_success(self, mock_user, mock_analyzer):
        """Test successful coverage analysis."""
        mock_report = Mock()
        mock_report.timestamp = datetime.now()
        mock_report.overall_coverage = 85.5
        mock_report.overall_branch_coverage = 78.2
        mock_report.files = []
        mock_report.files_by_coverage_level = {"high": [], "medium": [], "low": []}

        mock_analyzer.analyze_coverage.return_value = mock_report
        mock_analyzer.identify_coverage_gaps.return_value = []

        request = CoverageRequest(source_path="src/", test_path="tests/", run_mutation_testing=False)

        response = await analyze_coverage(request=request, current_user=mock_user, analyzer=mock_analyzer)

        assert response.overall_coverage == 85.5
        assert response.overall_branch_coverage == 78.2

    @pytest.mark.asyncio
    async def test_analyze_coverage_with_mutation(self, mock_user, mock_analyzer):
        """Test coverage analysis with mutation testing."""
        mock_file = Mock()
        mock_file.file_path = "src/module.py"

        mock_report = Mock()
        mock_report.timestamp = datetime.now()
        mock_report.overall_coverage = 85.5
        mock_report.overall_branch_coverage = 78.2
        mock_report.files = [mock_file]
        mock_report.files_by_coverage_level = {"high": [], "medium": [], "low": []}

        mock_mutation = Mock()
        mock_mutation.killed = True

        mock_analyzer.analyze_coverage.return_value = mock_report
        mock_analyzer.identify_coverage_gaps.return_value = []
        mock_analyzer.run_mutation_testing.return_value = [mock_mutation, mock_mutation]

        request = CoverageRequest(source_path="src/", run_mutation_testing=True)

        response = await analyze_coverage(request=request, current_user=mock_user, analyzer=mock_analyzer)

        assert response.mutation_score == 100.0

    @pytest.mark.asyncio
    async def test_analyze_coverage_error(self, mock_user, mock_analyzer):
        """Test coverage analysis error handling."""
        mock_analyzer.analyze_coverage.side_effect = Exception("Analysis failed")

        request = CoverageRequest(source_path="src/")

        with pytest.raises(HTTPException) as exc_info:
            await analyze_coverage(request=request, current_user=mock_user, analyzer=mock_analyzer)

        assert exc_info.value.status_code == 500


class TestGetTestHealthEndpoint:
    """Tests for GET /testing/health endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_engine(self):
        """Create mock intelligence engine."""
        engine = Mock()
        engine.get_test_health_report.return_value = {
            "summary": {"health_score": 85},
            "flaky_tests": [],
            "recent_bugs": [],
            "recent_fixes": [],
        }
        return engine

    @pytest.fixture
    def mock_analyzer(self):
        """Create mock coverage analyzer."""
        analyzer = Mock()
        analyzer.get_coverage_statistics.return_value = {"overall": 80}
        analyzer.get_coverage_trend = AsyncMock(return_value=[])
        return analyzer

    @pytest.fixture
    def mock_runner(self):
        """Create mock test runner."""
        runner = Mock()
        runner.get_execution_statistics.return_value = {"total_runs": 100}
        return runner

    @pytest.mark.asyncio
    async def test_get_test_health_success(self, mock_user, mock_engine, mock_analyzer, mock_runner):
        """Test successful health report."""
        response = await get_test_health(
            current_user=mock_user, engine=mock_engine, analyzer=mock_analyzer, runner=mock_runner
        )

        assert "summary" in response.model_dump()
        mock_engine.get_test_health_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_test_health_error(self, mock_user, mock_engine, mock_analyzer, mock_runner):
        """Test health report error handling."""
        mock_engine.get_test_health_report.side_effect = Exception("Report failed")

        with pytest.raises(HTTPException) as exc_info:
            await get_test_health(
                current_user=mock_user, engine=mock_engine, analyzer=mock_analyzer, runner=mock_runner
            )

        assert exc_info.value.status_code == 500


class TestFlakyTestsEndpoints:
    """Tests for flaky test management endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_runner(self):
        """Create mock test runner."""
        runner = Mock()
        return runner

    @pytest.mark.asyncio
    async def test_get_flaky_tests(self, mock_user, mock_runner):
        """Test getting flaky tests."""
        mock_flaky = Mock()
        mock_flaky.to_dict.return_value = {"test_id": "test-1", "flake_rate": 0.3}
        mock_runner.get_flaky_tests.return_value = [mock_flaky]

        response = await get_flaky_tests(current_user=mock_user, runner=mock_runner)

        assert response["count"] == 1
        assert len(response["flaky_tests"]) == 1

    @pytest.mark.asyncio
    async def test_quarantine_test_success(self, mock_user, mock_runner):
        """Test quarantining a test."""
        mock_runner.quarantine_test.return_value = True

        response = await quarantine_test(
            test_id="test-123", reason="Flaky test", current_user=mock_user, runner=mock_runner
        )

        assert response["test_id"] == "test-123"
        assert response["quarantined"] is True

    @pytest.mark.asyncio
    async def test_quarantine_test_not_found(self, mock_user, mock_runner):
        """Test quarantining non-existent test."""
        mock_runner.quarantine_test.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await quarantine_test(test_id="nonexistent", reason="", current_user=mock_user, runner=mock_runner)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_unquarantine_test_success(self, mock_user, mock_runner):
        """Test removing test from quarantine."""
        mock_runner.unquarantine_test.return_value = True

        response = await unquarantine_test(test_id="test-123", current_user=mock_user, runner=mock_runner)

        assert response["test_id"] == "test-123"
        assert response["unquarantined"] is True

    @pytest.mark.asyncio
    async def test_unquarantine_test_not_found(self, mock_user, mock_runner):
        """Test unquarantining non-existent test."""
        mock_runner.unquarantine_test.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await unquarantine_test(test_id="nonexistent", current_user=mock_user, runner=mock_runner)

        assert exc_info.value.status_code == 404


class TestFrontendTestingEndpoints:
    """Tests for frontend testing endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_agent(self):
        """Create mock frontend tester agent."""
        # Use MagicMock, not AsyncMock, for synchronous methods
        agent = MagicMock()
        agent.generate_e2e_tests_from_flow = AsyncMock()
        agent.run_visual_regression_test = AsyncMock()
        agent.run_accessibility_audit = AsyncMock()
        agent.get_test_statistics = MagicMock()  # Sync method
        return agent

    @pytest.mark.asyncio
    async def test_generate_e2e_tests_success(self, mock_user, mock_agent):
        """Test E2E test generation."""
        mock_test = Mock()
        mock_test.to_dict.return_value = {"name": "test_login", "steps": []}
        mock_agent.generate_e2e_tests_from_flow.return_value = [mock_test]

        response = await generate_e2e_tests(
            page_path="/login",
            user_flow=["click login", "enter credentials", "submit"],
            page_description="Login page",
            current_user=mock_user,
            agent=mock_agent,
        )

        assert response["page_path"] == "/login"
        assert response["tests_generated"] == 1

    @pytest.mark.asyncio
    async def test_generate_e2e_tests_error(self, mock_user, mock_agent):
        """Test E2E test generation error handling."""
        mock_agent.generate_e2e_tests_from_flow.side_effect = Exception("Generation failed")

        with pytest.raises(HTTPException) as exc_info:
            await generate_e2e_tests(page_path="/login", user_flow=["click"], current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_run_visual_regression_success(self, mock_user, mock_agent):
        """Test visual regression test."""
        mock_result = Mock()
        mock_result.status = MockStatus.PASSED
        mock_result.to_dict.return_value = {"page": "/home", "diff": 0.01}
        mock_agent.run_visual_regression_test.return_value = [mock_result, mock_result]

        response = await run_visual_regression(
            page_path="/home",
            viewports=[{"width": 1920, "height": 1080}],
            threshold=0.1,
            current_user=mock_user,
            agent=mock_agent,
        )

        assert response["page_path"] == "/home"
        assert response["tests_run"] == 2
        assert response["passed"] == 2

    @pytest.mark.asyncio
    async def test_run_visual_regression_error(self, mock_user, mock_agent):
        """Test visual regression error handling."""
        mock_agent.run_visual_regression_test.side_effect = Exception("Visual test failed")

        with pytest.raises(HTTPException) as exc_info:
            await run_visual_regression(page_path="/home", current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_run_accessibility_audit_success(self, mock_user, mock_agent):
        """Test accessibility audit."""
        mock_agent.run_accessibility_audit.return_value = {"violations": [], "passes": 50, "score": 95}

        response = await run_accessibility_audit(page_path="/home", current_user=mock_user, agent=mock_agent)

        assert response["score"] == 95

    @pytest.mark.asyncio
    async def test_run_accessibility_audit_error(self, mock_user, mock_agent):
        """Test accessibility audit error handling."""
        mock_agent.run_accessibility_audit.side_effect = Exception("Audit failed")

        with pytest.raises(HTTPException) as exc_info:
            await run_accessibility_audit(page_path="/home", current_user=mock_user, agent=mock_agent)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_frontend_statistics(self, mock_user, mock_agent):
        """Test getting frontend statistics."""
        mock_agent.get_test_statistics.return_value = {"total_tests": 100, "pass_rate": 0.95}

        # get_frontend_statistics is async but calls sync agent method
        response = await get_frontend_statistics(current_user=mock_user, agent=mock_agent)

        assert response["total_tests"] == 100


class TestRunFullTestSuite:
    """Tests for POST /testing/run-full-suite endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

    @pytest.fixture
    def mock_engine(self):
        """Create mock intelligence engine."""
        return Mock()

    @pytest.mark.asyncio
    async def test_run_full_suite(self, mock_user, mock_engine):
        """Test running full test suite in background."""
        from fastapi import BackgroundTasks

        background_tasks = BackgroundTasks()

        response = await run_full_test_suite(
            background_tasks=background_tasks, current_user=mock_user, engine=mock_engine
        )

        assert response["status"] == "started"
        assert "background" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_run_full_suite_background_task(self, mock_user, mock_engine):
        """Test that background task runs correctly (covers lines 656-658)."""
        from fastapi import BackgroundTasks

        # Create a real BackgroundTasks object and capture the task
        background_tasks = BackgroundTasks()

        response = await run_full_test_suite(
            background_tasks=background_tasks, current_user=mock_user, engine=mock_engine
        )

        assert response["status"] == "started"

        # Execute the background tasks - this runs the run_suite function
        # which covers lines 656-658
        await background_tasks()  # This executes all queued tasks
