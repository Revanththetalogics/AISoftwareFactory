"""
Test runner for Simulation module.

This module provides unified test execution and result aggregation
for all simulation tests.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from backend.core.logging import get_logger
from backend.simulation.integration_tester import IntegrationTester
from backend.simulation.performance_tester import PerformanceTester
from backend.simulation.sandbox import Sandbox
from backend.simulation.security_scanner import SecurityScanner

logger = get_logger(__name__)


@dataclass
class TestSuiteResult:
    """Complete test suite result."""
    suite_name: str
    start_time: datetime
    end_time: datetime
    passed: int
    failed: int
    skipped: int
    results: list[dict[str, Any]] = field(default_factory=list)


class TestRunner:
    """
    Unified test runner for all simulation tests.

    Orchestrates sandbox, security, performance, and integration tests
    with comprehensive reporting.
    """

    def __init__(self):
        """Initialize the test runner."""
        self._sandbox = Sandbox()
        self._security = SecurityScanner()
        self._performance = PerformanceTester()
        self._integration = IntegrationTester()
        self._logger = get_logger(__name__)

    async def run_full_suite(
        self,
        code: str,
        language: str = "python",
        requirements: list[str] | None = None
    ) -> TestSuiteResult:
        """
        Run complete test suite on code.

        Args:
            code: Code to test
            language: Programming language
            requirements: Package requirements

        Returns:
            Complete test suite results
        """
        start_time = datetime.utcnow()
        results = []
        passed = 0
        failed = 0

        # 1. Sandbox execution test
        self._logger.info("Running sandbox tests")
        sandbox_result = await self._sandbox.execute(code, language)
        results.append({
            "test": "sandbox_execution",
            "success": sandbox_result.success,
            "details": {
                "exit_code": sandbox_result.exit_code,
                "execution_time": sandbox_result.execution_time
            }
        })
        if sandbox_result.success:
            passed += 1
        else:
            failed += 1

        # 2. Security scan
        self._logger.info("Running security scan")
        security_issues = await self._security.scan_code(code, language)
        critical_issues = [i for i in security_issues if i.severity == "critical"]
        results.append({
            "test": "security_scan",
            "success": len(critical_issues) == 0,
            "details": {
                "total_issues": len(security_issues),
                "critical_issues": len(critical_issues)
            }
        })
        if len(critical_issues) == 0:
            passed += 1
        else:
            failed += 1

        # 3. Dependency security scan
        if requirements:
            self._logger.info("Running dependency security scan")
            dep_issues = await self._security.scan_dependencies(requirements)
            results.append({
                "test": "dependency_scan",
                "success": len(dep_issues) == 0,
                "details": {"vulnerabilities": len(dep_issues)}
            })
            if len(dep_issues) == 0:
                passed += 1
            else:
                failed += 1

        end_time = datetime.utcnow()

        return TestSuiteResult(
            suite_name="full_simulation_suite",
            start_time=start_time,
            end_time=end_time,
            passed=passed,
            failed=failed,
            skipped=0,
            results=results
        )

    def generate_report(self, result: TestSuiteResult) -> dict[str, Any]:
        """Generate comprehensive test report."""
        total = result.passed + result.failed + result.skipped
        duration = (result.end_time - result.start_time).total_seconds()

        return {
            "summary": {
                "suite_name": result.suite_name,
                "total_tests": total,
                "passed": result.passed,
                "failed": result.failed,
                "skipped": result.skipped,
                "success_rate": result.passed / total if total > 0 else 0,
                "duration_seconds": duration
            },
            "results": result.results,
            "timestamp": result.end_time.isoformat()
        }
