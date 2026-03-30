"""
Tests for Simulation Layer.
"""

import pytest

from backend.codegen.simulation import (
    SimulationLayer,
    SimulationReport,
    TestResult,
    TestStatus,
    TestType,
)


class TestTestResult:
    """Test cases for TestResult."""

    def test_result_creation(self):
        """Test creating a test result."""
        result = TestResult(
            test_name="Syntax Check",
            test_type=TestType.SYNTAX,
            status=TestStatus.PASSED,
            message="All good",
        )

        assert result.test_name == "Syntax Check"
        assert result.status == TestStatus.PASSED

    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = TestResult(
            test_name="Test",
            test_type=TestType.UNIT,
            status=TestStatus.PASSED,
        )

        data = result.to_dict()

        assert data["test_name"] == "Test"
        assert data["status"] == "passed"


class TestSimulationReport:
    """Test cases for SimulationReport."""

    def test_report_properties(self):
        """Test report properties."""
        report = SimulationReport(
            project_name="myproject",
            results=[
                TestResult(test_name="T1", test_type=TestType.UNIT, status=TestStatus.PASSED),
                TestResult(test_name="T2", test_type=TestType.UNIT, status=TestStatus.FAILED),
                TestResult(test_name="T3", test_type=TestType.UNIT, status=TestStatus.PASSED),
            ],
        )

        assert report.total_tests == 3
        assert report.passed_tests == 2
        assert report.failed_tests == 1
        assert report.success_rate == pytest.approx(66.67, rel=0.01)

    def test_report_empty(self):
        """Test empty report."""
        report = SimulationReport(project_name="test")

        assert report.total_tests == 0
        assert report.success_rate == 0.0

    def test_report_to_dict(self):
        """Test converting report to dict."""
        report = SimulationReport(
            project_name="myproject",
            results=[TestResult(test_name="T1", test_type=TestType.UNIT, status=TestStatus.PASSED)],
        )

        data = report.to_dict()

        assert data["project_name"] == "myproject"
        assert data["total_tests"] == 1
        assert data["passed_tests"] == 1


class TestSimulationLayer:
    """Test cases for SimulationLayer."""

    def setup_method(self):
        """Create fresh simulation layer."""
        self.sim = SimulationLayer()

    @pytest.mark.asyncio
    async def test_run_simulation(self):
        """Test running full simulation."""
        report = await self.sim.run_simulation("myproject")

        assert report.project_name == "myproject"
        assert report.total_tests > 0
        assert report.completed_at is not None

    @pytest.mark.asyncio
    async def test_run_simulation_filtered(self):
        """Test running simulation with filtered test types."""
        report = await self.sim.run_simulation(
            "myproject",
            test_types=[TestType.SYNTAX, TestType.UNIT],
        )

        assert report.total_tests == 2
        test_types = [r.test_type for r in report.results]
        assert TestType.SYNTAX in test_types
        assert TestType.UNIT in test_types

    @pytest.mark.asyncio
    async def test_validate_python_syntax_valid(self):
        """Test validating valid Python syntax."""
        result = await self.sim.validate_code_syntax(
            "print('hello')",
            "python",
        )

        assert result.status == TestStatus.PASSED
        assert "valid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_validate_python_syntax_invalid(self):
        """Test validating invalid Python syntax."""
        result = await self.sim.validate_code_syntax(
            "def foo(  # incomplete",
            "python",
        )

        assert result.status == TestStatus.FAILED
        assert "error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_validate_json_valid(self):
        """Test validating valid JSON."""
        result = await self.sim.validate_code_syntax(
            '{"key": "value"}',
            "json",
        )

        assert result.status == TestStatus.PASSED

    @pytest.mark.asyncio
    async def test_validate_json_invalid(self):
        """Test validating invalid JSON."""
        result = await self.sim.validate_code_syntax(
            '{"key": invalid}',
            "json",
        )

        assert result.status == TestStatus.FAILED


class TestSimulationReportExtendedCoverage:
    """Tests for extended coverage - line 117 (duration_ms when completed_at is None)."""

    def test_duration_ms_when_completed_at_none_line_117(self):
        """Test line 117: duration_ms returns 0.0 when completed_at is None."""

        report = SimulationReport(
            project_name="test_project",
            results=[],
            # completed_at is None by default
        )

        # Line 117: when completed_at is None, should return 0.0
        assert report.completed_at is None
        assert report.duration_ms == 0.0

    def test_duration_ms_when_completed_at_set(self):
        """Test duration_ms when completed_at is set."""
        from datetime import UTC, datetime, timedelta

        started = datetime.now(UTC)
        completed = started + timedelta(seconds=5)  # 5 seconds = 5000ms

        report = SimulationReport(
            project_name="test_project",
            results=[],
        )
        # Set started_at and completed_at
        report.started_at = started
        report.completed_at = completed

        # Should return duration in milliseconds
        assert report.duration_ms == pytest.approx(5000, rel=0.1)
