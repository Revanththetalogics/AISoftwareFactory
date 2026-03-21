"""
Comprehensive tests for Simulation module - full coverage.

Tests all simulation components including:
- ReportGenerator (JSON, Markdown, HTML)
- IntegrationTester (test cases, API workflow)
- SimulationOrchestrator (full workflow)
- PerformanceTester (load tests, benchmarks)
- TestRunner (full suite execution)
- Sandbox (Python, JavaScript, unsupported languages, timeouts)
- SecurityScanner (patterns, AST, dependencies, report)
- ValidationEngine (rules, custom rules, exception handling)
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.simulation.integration_tester import IntegrationTester, TestCase
from backend.simulation.performance_tester import PerformanceResult, PerformanceTester
from backend.simulation.report_generator import ReportGenerator
from backend.simulation.sandbox import Sandbox, SandboxResult
from backend.simulation.security_scanner import SecurityIssue, SecurityScanner
from backend.simulation.simulation_orchestrator import SimulationConfig, SimulationOrchestrator
from backend.simulation.test_runner import TestRunner, TestSuiteResult
from backend.simulation.validation_engine import (
    ValidationEngine,
    ValidationResult,
    ValidationRule,
    ValidationStatus,
)

# =============================================================================
# ReportGenerator Tests
# =============================================================================


class TestReportGenerator:
    """Comprehensive tests for ReportGenerator - covering lines 31-33, 50-57, 74-112, 129-182."""

    def test_init_creates_output_dir(self, tmp_path):
        """Test that __init__ creates output directory."""
        output_dir = tmp_path / "reports"
        generator = ReportGenerator(output_dir=str(output_dir))
        assert output_dir.exists()
        assert generator._output_dir == output_dir

    def test_generate_json_with_default_filename(self, tmp_path):
        """Test JSON generation with auto-generated filename."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {"summary": {"total_tests": 5, "passed": 4, "failed": 1}}

        filepath = generator.generate_json(results)

        assert Path(filepath).exists()
        assert filepath.endswith(".json")

    def test_generate_json_with_custom_filename(self, tmp_path):
        """Test JSON generation with custom filename."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {"summary": {"total_tests": 10}}

        filepath = generator.generate_json(results, filename="custom_report.json")

        assert "custom_report.json" in filepath
        assert Path(filepath).exists()

    def test_generate_markdown_with_summary(self, tmp_path):
        """Test Markdown generation with summary section."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {
            "summary": {
                "total_tests": 10,
                "passed": 8,
                "failed": 2,
                "success_rate": 0.8,
                "duration_seconds": 5.5,
            }
        }

        filepath = generator.generate_markdown(results)

        assert Path(filepath).exists()
        content = Path(filepath).read_text()
        assert "# Simulation Test Report" in content
        assert "Total Tests:** 10" in content
        assert "Passed:** 8" in content
        assert "80.0%" in content

    def test_generate_markdown_with_results(self, tmp_path):
        """Test Markdown generation with detailed results."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {
            "results": [
                {"test": "test_1", "success": True, "details": {"key1": "value1"}},
                {"test": "test_2", "success": False, "details": {"error": "failed"}},
            ]
        }

        filepath = generator.generate_markdown(results)

        content = Path(filepath).read_text(encoding="utf-8")
        assert "## Detailed Results" in content
        assert "✅ test_1" in content
        assert "❌ test_2" in content
        assert "key1:** value1" in content

    def test_generate_markdown_default_filename(self, tmp_path):
        """Test Markdown generation with auto-generated filename."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {}

        filepath = generator.generate_markdown(results)

        assert filepath.endswith(".md")

    def test_generate_html_full_report(self, tmp_path):
        """Test HTML report generation with all sections."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {
            "summary": {
                "total_tests": 5,
                "passed": 4,
                "failed": 1,
                "success_rate": 0.8,
                "duration_seconds": 2.5,
            },
            "results": [
                {"test": "test_pass", "success": True},
                {"test": "test_fail", "success": False},
            ],
        }

        filepath = generator.generate_html(results)

        assert Path(filepath).exists()
        content = Path(filepath).read_text()
        assert "<!DOCTYPE html>" in content
        assert "<title>Simulation Test Report</title>" in content
        assert "Total Tests: 5" in content
        assert 'class="passed">test_pass' in content
        assert 'class="failed">test_fail' in content
        assert "80.0%" in content

    def test_generate_html_custom_filename(self, tmp_path):
        """Test HTML generation with custom filename."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {"summary": {}}

        filepath = generator.generate_html(results, filename="my_report.html")

        assert "my_report.html" in filepath

    def test_generate_html_empty_results(self, tmp_path):
        """Test HTML generation with empty results."""
        generator = ReportGenerator(output_dir=str(tmp_path))
        results = {}

        filepath = generator.generate_html(results)

        content = Path(filepath).read_text()
        assert "N/A" in content


# =============================================================================
# IntegrationTester Tests
# =============================================================================


class TestIntegrationTester:
    """Comprehensive tests for IntegrationTester - covering lines 45-46, 55-56, 68-120, 134-140, 157-188."""

    def test_init(self):
        """Test IntegrationTester initialization."""
        tester = IntegrationTester()
        assert tester._test_cases == {}

    def test_register_test(self):
        """Test registering a test case."""
        tester = IntegrationTester()
        test_case = TestCase(
            name="test_1",
            execute=AsyncMock(return_value={}),
            validate=AsyncMock(return_value={"success": True}),
        )

        tester.register_test(test_case)

        assert "test_1" in tester._test_cases

    @pytest.mark.asyncio
    async def test_run_test_not_found(self):
        """Test running a non-existent test."""
        tester = IntegrationTester()

        result = await tester.run_test("non_existent")

        assert result.success is False
        assert result.error == "Test not found"
        assert result.duration == 0

    @pytest.mark.asyncio
    async def test_run_test_success(self):
        """Test successful test execution."""
        tester = IntegrationTester()
        test_case = TestCase(
            name="test_success",
            execute=AsyncMock(return_value={"data": "result"}),
            validate=AsyncMock(return_value={"success": True, "validated": True}),
        )
        tester.register_test(test_case)

        result = await tester.run_test("test_success")

        assert result.success is True
        assert result.duration > 0
        assert result.details["validated"] is True

    @pytest.mark.asyncio
    async def test_run_test_with_setup_and_teardown(self):
        """Test execution with setup and teardown functions."""
        tester = IntegrationTester()
        setup_called = []
        teardown_called = []

        async def setup():
            setup_called.append(True)

        async def teardown():
            teardown_called.append(True)

        test_case = TestCase(
            name="test_with_lifecycle",
            setup=setup,
            execute=AsyncMock(return_value={}),
            validate=AsyncMock(return_value={"success": True}),
            teardown=teardown,
        )
        tester.register_test(test_case)

        await tester.run_test("test_with_lifecycle")

        assert len(setup_called) == 1
        assert len(teardown_called) == 1

    @pytest.mark.asyncio
    async def test_run_test_exception_with_teardown(self):
        """Test that teardown runs even on exception."""
        tester = IntegrationTester()
        teardown_called = []

        async def teardown():
            teardown_called.append(True)

        test_case = TestCase(
            name="test_exception",
            execute=AsyncMock(side_effect=RuntimeError("Test error")),
            validate=AsyncMock(),
            teardown=teardown,
        )
        tester.register_test(test_case)

        result = await tester.run_test("test_exception")

        assert result.success is False
        assert "Test error" in result.error
        assert len(teardown_called) == 1

    @pytest.mark.asyncio
    async def test_run_test_teardown_failure(self):
        """Test handling of teardown failure."""
        tester = IntegrationTester()

        async def failing_teardown():
            raise RuntimeError("Teardown failed")

        test_case = TestCase(
            name="test_teardown_fail",
            execute=AsyncMock(side_effect=RuntimeError("Execution error")),
            validate=AsyncMock(),
            teardown=failing_teardown,
        )
        tester.register_test(test_case)

        result = await tester.run_test("test_teardown_fail")

        assert result.success is False
        assert "Execution error" in result.error

    @pytest.mark.asyncio
    async def test_run_all_tests(self):
        """Test running all registered tests."""
        tester = IntegrationTester()

        for i in range(3):
            test_case = TestCase(
                name=f"test_{i}",
                execute=AsyncMock(return_value={}),
                validate=AsyncMock(return_value={"success": True}),
            )
            tester.register_test(test_case)

        results = await tester.run_all_tests()

        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_test_api_workflow_success(self):
        """Test API workflow testing with successful responses."""
        tester = IntegrationTester()
        workflow = [
            {"method": "GET", "path": "/health", "expected_status": 200},
            {"method": "POST", "path": "/api/items", "expected_status": 201},
        ]

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()

            # Create responses for each workflow step
            responses = []
            for step in workflow:
                resp = AsyncMock()
                resp.status = step["expected_status"]
                resp.__aenter__ = AsyncMock(return_value=resp)
                resp.__aexit__ = AsyncMock()
                responses.append(resp)

            mock_session.request = MagicMock(side_effect=responses)
            mock_session_cls.return_value = mock_session

            result = await tester.test_api_workflow("http://localhost:8000", workflow)

            assert result.success is True
            assert result.name == "api_workflow"

    @pytest.mark.asyncio
    async def test_test_api_workflow_status_mismatch(self):
        """Test API workflow with status code mismatch."""
        tester = IntegrationTester()
        workflow = [{"method": "GET", "path": "/health", "expected_status": 200}]

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()

            mock_resp = AsyncMock()
            mock_resp.status = 500  # Unexpected status
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock()

            mock_session.request = MagicMock(return_value=mock_resp)
            mock_session_cls.return_value = mock_session

            result = await tester.test_api_workflow("http://localhost:8000", workflow)

            assert result.success is False
            assert "Expected 200, got 500" in result.error

    @pytest.mark.asyncio
    async def test_test_api_workflow_exception(self):
        """Test API workflow with connection error."""
        tester = IntegrationTester()
        workflow = [{"method": "GET", "path": "/health"}]

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(side_effect=Exception("Connection refused"))
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session

            result = await tester.test_api_workflow("http://localhost:8000", workflow)

            assert result.success is False
            assert "Connection refused" in result.error


# =============================================================================
# SimulationOrchestrator Tests
# =============================================================================


class TestSimulationOrchestrator:
    """Comprehensive tests for SimulationOrchestrator - covering lines 30-31, 44-47, 68-135, 147."""

    def test_simulation_config_post_init(self):
        """Test SimulationConfig __post_init__ sets default output_formats."""
        config = SimulationConfig()
        assert config.output_formats == ["json", "markdown"]

    def test_simulation_config_custom_formats(self):
        """Test SimulationConfig with custom output_formats."""
        config = SimulationConfig(output_formats=["html"])
        assert config.output_formats == ["html"]

    def test_init(self):
        """Test SimulationOrchestrator initialization."""
        orchestrator = SimulationOrchestrator()
        assert orchestrator._test_runner is not None
        assert orchestrator._validator is not None
        assert orchestrator._reporter is not None

    @pytest.mark.asyncio
    async def test_run_simulation_full_workflow(self, tmp_path):
        """Test complete simulation workflow."""
        orchestrator = SimulationOrchestrator()
        orchestrator._reporter._output_dir = tmp_path

        code = """
def hello():
    return "Hello"
"""
        config = SimulationConfig(
            run_security_scan=True,
            run_performance_test=True,
            run_integration_test=True,
            generate_reports=True,
            output_formats=["json", "markdown", "html"],
        )

        with patch.object(
            orchestrator._test_runner,
            "run_full_suite",
            new_callable=AsyncMock,
        ) as mock_run:
            from datetime import datetime

            mock_run.return_value = TestSuiteResult(
                suite_name="test_suite",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=2,
                failed=0,
                skipped=0,
                results=[],
            )

            with patch.object(
                orchestrator._test_runner,
                "generate_report",
            ) as mock_report:
                mock_report.return_value = {
                    "summary": {"success_rate": 1.0, "failed": 0},
                    "results": [],
                }

                result = await orchestrator.run_simulation(code, "python", config=config)

        assert result["status"] == "completed"
        assert "simulation_id" in result
        assert "tests" in result
        assert "validation" in result
        assert len(result["reports"]) == 3  # json, markdown, html

    @pytest.mark.asyncio
    async def test_run_simulation_without_reports(self, tmp_path):
        """Test simulation without report generation."""
        orchestrator = SimulationOrchestrator()
        orchestrator._reporter._output_dir = tmp_path

        code = "x = 1"
        config = SimulationConfig(
            run_security_scan=True,
            generate_reports=False,
        )

        with patch.object(
            orchestrator._test_runner,
            "run_full_suite",
            new_callable=AsyncMock,
        ) as mock_run:
            from datetime import datetime

            mock_run.return_value = TestSuiteResult(
                suite_name="test_suite",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=1,
                failed=0,
                skipped=0,
                results=[],
            )

            with patch.object(orchestrator._test_runner, "generate_report") as mock_report:
                mock_report.return_value = {"summary": {}, "results": []}

                result = await orchestrator.run_simulation(code, config=config)

        assert result["reports"] == []

    def test_get_simulation_summary(self):
        """Test getting simulation summary."""
        orchestrator = SimulationOrchestrator()
        results = {
            "simulation_id": "sim_123",
            "status": "completed",
            "validation": {"overall_status": "pass", "score": 95},
            "tests": {"summary": {"success_rate": 0.9}},
            "reports": [{"format": "json"}, {"format": "markdown"}],
        }

        summary = orchestrator.get_simulation_summary(results)

        assert summary["simulation_id"] == "sim_123"
        assert summary["status"] == "completed"
        assert summary["overall_pass"] is True
        assert summary["test_success_rate"] == 0.9
        assert summary["validation_score"] == 95
        assert summary["reports_generated"] == 2


# =============================================================================
# PerformanceTester Tests
# =============================================================================


class TestPerformanceTester:
    """Comprehensive tests for PerformanceTester - covering lines 45, 68-113, 144-168, 172-191."""

    def test_init(self):
        """Test PerformanceTester initialization."""
        tester = PerformanceTester()
        assert tester._logger is not None

    @pytest.mark.asyncio
    async def test_load_test_success(self):
        """Test successful load test execution."""
        tester = PerformanceTester()
        call_count = 0

        async def sample_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)

        result = await tester.load_test(sample_operation, requests=10, concurrency=5)

        assert result.requests == 10
        assert result.errors == 0
        assert result.throughput > 0
        assert result.avg_latency > 0
        assert result.median_latency > 0
        assert result.min_latency > 0
        assert result.max_latency > 0
        assert result.p95_latency > 0
        assert result.p99_latency > 0
        assert call_count == 10

    @pytest.mark.asyncio
    async def test_load_test_all_failures(self):
        """Test load test when all requests fail."""
        tester = PerformanceTester()

        async def failing_operation():
            raise RuntimeError("Test failure")

        result = await tester.load_test(failing_operation, requests=5, concurrency=2)

        assert result.requests == 5
        assert result.errors == 5
        assert result.avg_latency == 0
        assert result.throughput == 0

    @pytest.mark.asyncio
    async def test_load_test_partial_failures(self):
        """Test load test with partial failures."""
        tester = PerformanceTester()
        call_count = 0

        async def partial_fail_operation():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise RuntimeError("Partial failure")
            await asyncio.sleep(0.001)

        result = await tester.load_test(partial_fail_operation, requests=10, concurrency=2)

        assert result.errors == 5
        assert result.avg_latency > 0  # Some succeeded

    @pytest.mark.asyncio
    async def test_benchmark_api(self):
        """Test API benchmark functionality."""
        tester = PerformanceTester()
        endpoints = [
            {"name": "health", "method": "GET", "path": "/health"},
            {"name": "status", "method": "GET", "path": "/status"},
        ]

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()

            mock_resp = AsyncMock()
            mock_resp.text = AsyncMock(return_value="OK")
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock()

            mock_session.request = MagicMock(return_value=mock_resp)
            mock_session_cls.return_value = mock_session

            results = await tester.benchmark_api("http://localhost:8000", endpoints)

            assert "health" in results
            assert "status" in results

    def test_generate_report(self):
        """Test performance report generation."""
        tester = PerformanceTester()
        results = {
            "endpoint1": PerformanceResult(
                operation="test",
                requests=100,
                total_time=5.0,
                avg_latency=0.05,
                median_latency=0.04,
                min_latency=0.01,
                max_latency=0.2,
                p95_latency=0.15,
                p99_latency=0.18,
                errors=2,
                throughput=20.0,
            ),
            "endpoint2": PerformanceResult(
                operation="test2",
                requests=50,
                total_time=2.5,
                avg_latency=0.04,
                median_latency=0.03,
                min_latency=0.01,
                max_latency=0.1,
                p95_latency=0.08,
                p99_latency=0.09,
                errors=0,
                throughput=20.0,
            ),
        }

        report = tester.generate_report(results)

        assert report["summary"]["total_tests"] == 2
        assert report["summary"]["total_requests"] == 150
        assert report["summary"]["total_errors"] == 2
        assert "endpoint1" in report["details"]
        assert "endpoint2" in report["details"]
        assert report["details"]["endpoint1"]["avg_latency_ms"] == 50.0


# =============================================================================
# TestRunner Tests
# =============================================================================


class TestTestRunner:
    """Comprehensive tests for TestRunner - covering lines 43-47, 66-120, 132-135."""

    def test_init(self):
        """Test TestRunner initialization."""
        runner = TestRunner()
        assert runner._sandbox is not None
        assert runner._security is not None
        assert runner._performance is not None
        assert runner._integration is not None

    @pytest.mark.asyncio
    async def test_run_full_suite_all_pass(self):
        """Test full suite run with all tests passing."""
        runner = TestRunner()
        code = """
def hello():
    return "Hello"
"""

        with patch.object(
            runner._sandbox,
            "execute",
            new_callable=AsyncMock,
            return_value=SandboxResult(
                success=True, stdout="Hello", stderr="", exit_code=0, execution_time=0.1
            ),
        ):
            with patch.object(
                runner._security, "scan_code", new_callable=AsyncMock, return_value=[]
            ):
                result = await runner.run_full_suite(code, "python")

        assert result.passed >= 2
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_run_full_suite_sandbox_failure(self):
        """Test full suite with sandbox failure."""
        runner = TestRunner()
        code = "raise Error"

        with patch.object(
            runner._sandbox,
            "execute",
            new_callable=AsyncMock,
            return_value=SandboxResult(
                success=False, stdout="", stderr="Error", exit_code=1, execution_time=0.1
            ),
        ):
            with patch.object(
                runner._security, "scan_code", new_callable=AsyncMock, return_value=[]
            ):
                result = await runner.run_full_suite(code, "python")

        assert result.failed >= 1

    @pytest.mark.asyncio
    async def test_run_full_suite_security_issues(self):
        """Test full suite with critical security issues."""
        runner = TestRunner()
        code = "eval(user_input)"

        with patch.object(
            runner._sandbox,
            "execute",
            new_callable=AsyncMock,
            return_value=SandboxResult(
                success=True, stdout="", stderr="", exit_code=0, execution_time=0.1
            ),
        ):
            with patch.object(
                runner._security,
                "scan_code",
                new_callable=AsyncMock,
                return_value=[
                    SecurityIssue(
                        severity="critical", category="eval", message="Dangerous eval"
                    )
                ],
            ):
                result = await runner.run_full_suite(code, "python")

        assert result.failed >= 1

    @pytest.mark.asyncio
    async def test_run_full_suite_with_requirements(self):
        """Test full suite with dependency scanning."""
        runner = TestRunner()
        code = "import requests"
        requirements = ["requests==2.19.0"]

        with patch.object(
            runner._sandbox,
            "execute",
            new_callable=AsyncMock,
            return_value=SandboxResult(
                success=True, stdout="", stderr="", exit_code=0, execution_time=0.1
            ),
        ):
            with patch.object(
                runner._security, "scan_code", new_callable=AsyncMock, return_value=[]
            ):
                with patch.object(
                    runner._security,
                    "scan_dependencies",
                    new_callable=AsyncMock,
                    return_value=[
                        SecurityIssue(
                            severity="high",
                            category="vulnerable_dependency",
                            message="Vulnerable",
                        )
                    ],
                ):
                    result = await runner.run_full_suite(code, "python", requirements)

        # Should have dependency scan result
        dep_results = [r for r in result.results if r["test"] == "dependency_scan"]
        assert len(dep_results) == 1
        assert dep_results[0]["success"] is False

    @pytest.mark.asyncio
    async def test_run_full_suite_requirements_pass(self):
        """Test full suite with safe dependencies."""
        runner = TestRunner()
        code = "import safe_pkg"
        requirements = ["safe_pkg==1.0.0"]

        with patch.object(
            runner._sandbox,
            "execute",
            new_callable=AsyncMock,
            return_value=SandboxResult(
                success=True, stdout="", stderr="", exit_code=0, execution_time=0.1
            ),
        ):
            with patch.object(
                runner._security, "scan_code", new_callable=AsyncMock, return_value=[]
            ):
                with patch.object(
                    runner._security,
                    "scan_dependencies",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    result = await runner.run_full_suite(code, "python", requirements)

        dep_results = [r for r in result.results if r["test"] == "dependency_scan"]
        assert len(dep_results) == 1
        assert dep_results[0]["success"] is True

    def test_generate_report(self):
        """Test test report generation."""
        from datetime import datetime, timedelta

        runner = TestRunner()
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=5)

        suite_result = TestSuiteResult(
            suite_name="test_suite",
            start_time=start_time,
            end_time=end_time,
            passed=3,
            failed=1,
            skipped=1,
            results=[{"test": "test_1", "success": True}],
        )

        report = runner.generate_report(suite_result)

        assert report["summary"]["suite_name"] == "test_suite"
        assert report["summary"]["total_tests"] == 5
        assert report["summary"]["passed"] == 3
        assert report["summary"]["failed"] == 1
        assert report["summary"]["skipped"] == 1
        assert report["summary"]["success_rate"] == 0.6
        assert report["summary"]["duration_seconds"] == 5.0

    def test_generate_report_zero_tests(self):
        """Test report generation with zero tests."""
        from datetime import datetime

        runner = TestRunner()
        now = datetime.utcnow()

        suite_result = TestSuiteResult(
            suite_name="empty_suite",
            start_time=now,
            end_time=now,
            passed=0,
            failed=0,
            skipped=0,
            results=[],
        )

        report = runner.generate_report(suite_result)

        assert report["summary"]["success_rate"] == 0


# =============================================================================
# Sandbox Tests
# =============================================================================


class TestSandboxExtended:
    """Extended tests for Sandbox - covering lines 77-80, 86-89, 95-98, 108-109, 140-141, 151-181."""

    @pytest.mark.asyncio
    async def test_execute_javascript_success(self, tmp_path):
        """Test JavaScript execution (when Node.js is available)."""
        sandbox = Sandbox()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="Hello JS", stderr=""
            )

            result = await sandbox.execute('console.log("Hello JS")', language="javascript")

            assert result.success is True
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_execute_unsupported_language(self):
        """Test execution with unsupported language."""
        sandbox = Sandbox()

        result = await sandbox.execute("code", language="ruby")

        assert result.success is False
        assert "Unsupported language: ruby" in result.stderr
        assert result.exit_code == -1

    @pytest.mark.asyncio
    async def test_execute_with_additional_files(self):
        """Test execution with additional files."""
        sandbox = Sandbox()

        code = """
with open("data/config.json") as f:
    print(f.read())
"""
        files = {"data/config.json": '{"key": "value"}'}

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout='{"key": "value"}', stderr=""
            )

            await sandbox.execute(code, language="python", files=files)

            # Files should be written before execution
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_execute_exception_handling(self):
        """Test exception handling during execution."""
        sandbox = Sandbox()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("Cannot execute process")

            result = await sandbox.execute("print('test')", language="python")

            assert result.success is False
            assert "Cannot execute process" in result.stderr

    @pytest.mark.asyncio
    async def test_run_python_timeout(self):
        """Test Python execution timeout."""
        sandbox = Sandbox(timeout=1)

        with patch("subprocess.run") as mock_run:
            import subprocess

            mock_run.side_effect = subprocess.TimeoutExpired(cmd="python", timeout=1)

            result = await sandbox.execute("import time; time.sleep(10)", language="python")

            assert result.success is False
            assert "timed out" in result.stderr

    @pytest.mark.asyncio
    async def test_run_javascript_timeout(self):
        """Test JavaScript execution timeout."""
        sandbox = Sandbox(timeout=1)

        with patch("subprocess.run") as mock_run:
            import subprocess

            mock_run.side_effect = subprocess.TimeoutExpired(cmd="node", timeout=1)

            result = await sandbox.execute("while(true){}", language="javascript")

            assert result.success is False
            assert "timed out" in result.stderr

    @pytest.mark.asyncio
    async def test_run_javascript_node_not_found(self):
        """Test JavaScript execution when Node.js is not installed."""
        sandbox = Sandbox()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("node not found")

            result = await sandbox.execute('console.log("test")', language="javascript")

            assert result.success is False
            assert "Node.js not found" in result.stderr


# =============================================================================
# SecurityScanner Extended Tests
# =============================================================================


class TestSecurityScannerExtended:
    """Extended tests for SecurityScanner - covering lines 103-105, 117-123, 189-199."""

    @pytest.mark.asyncio
    async def test_scan_python_ast_dangerous_imports(self):
        """Test AST scanning for dangerous imports."""
        scanner = SecurityScanner()
        code = """
import pickle
import marshal
"""

        issues = await scanner.scan_code(code)

        dangerous_import_issues = [i for i in issues if i.category == "dangerous_import"]
        assert len(dangerous_import_issues) == 2

    @pytest.mark.asyncio
    async def test_scan_python_ast_file_write(self):
        """Test AST scanning for file write operations."""
        scanner = SecurityScanner()
        code = """
f = open("output.txt", "w")
f.write("data")
f.close()
"""

        issues = await scanner.scan_code(code)

        file_write_issues = [i for i in issues if i.category == "file_write"]
        assert len(file_write_issues) == 1

    @pytest.mark.asyncio
    async def test_scan_python_ast_syntax_error(self):
        """Test AST scanning with syntax error."""
        scanner = SecurityScanner()
        code = """
def broken(
    return x
"""

        issues = await scanner.scan_code(code)

        syntax_issues = [i for i in issues if i.category == "syntax_error"]
        assert len(syntax_issues) == 1

    def test_generate_report(self):
        """Test security report generation."""
        scanner = SecurityScanner()
        issues = [
            SecurityIssue(
                severity="critical", category="eval", message="Eval found", line=10
            ),
            SecurityIssue(
                severity="high", category="sql", message="SQL injection", line=20
            ),
            SecurityIssue(
                severity="medium", category="pickle", message="Pickle load", line=30
            ),
            SecurityIssue(
                severity="low", category="info", message="Info disclosure", line=40
            ),
        ]

        report = scanner.generate_report(issues)

        assert report["total_issues"] == 4
        assert report["severity_counts"]["critical"] == 1
        assert report["severity_counts"]["high"] == 1
        assert report["severity_counts"]["medium"] == 1
        assert report["severity_counts"]["low"] == 1
        assert len(report["issues"]) == 4


# =============================================================================
# ValidationEngine Extended Tests
# =============================================================================


class TestValidationEngineExtended:
    """Extended tests for ValidationEngine - covering lines 118-130, 195."""

    @pytest.mark.asyncio
    async def test_validate_with_rule_exception(self):
        """Test validation when a rule raises an exception."""
        engine = ValidationEngine()

        # Add a rule that raises an exception
        async def failing_rule(code, context):
            raise RuntimeError("Rule execution failed")

        engine.add_rule(
            ValidationRule(
                name="failing_rule", check=failing_rule, required=True, weight=1.0
            )
        )

        result = await engine.validate("valid code")

        # Should have the failed rule in results
        failed_results = [
            r for r in result["results"] if r["rule"] == "failing_rule"
        ]
        assert len(failed_results) == 1
        assert failed_results[0]["status"] == "fail"
        assert "Rule execution failed" in failed_results[0]["message"]

    @pytest.mark.asyncio
    async def test_validate_with_vulnerabilities(self):
        """Test validation with critical vulnerabilities."""
        engine = ValidationEngine()

        code = """
result = eval(user_input)
"""

        result = await engine.validate(code)

        assert result["overall_status"] == "fail"
        vuln_results = [
            r for r in result["results"] if r["rule"] == "no_critical_vulnerabilities"
        ]
        assert len(vuln_results) == 1
        assert vuln_results[0]["status"] == "fail"

    @pytest.mark.asyncio
    async def test_add_custom_rule(self):
        """Test adding custom validation rules."""
        engine = ValidationEngine()

        async def custom_rule(code, context):
            has_docstring = '"""' in code or "'''" in code
            if has_docstring:
                return ValidationResult(
                    rule_name="docstring_check",
                    status=ValidationStatus.PASS,
                    message="Has docstring",
                    score=1.0,
                )
            return ValidationResult(
                rule_name="docstring_check",
                status=ValidationStatus.WARNING,
                message="No docstring",
                score=0.5,
            )

        engine.add_rule(
            ValidationRule(
                name="docstring_check", check=custom_rule, required=False, weight=0.5
            )
        )

        code_with_docstring = '''
def hello():
    """Say hello."""
    return "Hello"
'''

        result = await engine.validate(code_with_docstring)

        docstring_results = [
            r for r in result["results"] if r["rule"] == "docstring_check"
        ]
        assert len(docstring_results) == 1
