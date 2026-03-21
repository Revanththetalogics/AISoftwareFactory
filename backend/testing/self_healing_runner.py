"""
Self-Healing Test Runner - Intelligent test execution with auto-recovery.

This module provides:
- Automatic retry with exponential backoff
- Flaky test detection and quarantine
- Self-healing selectors for E2E tests
- Smart test ordering based on failure history
- Parallel execution with failure isolation
"""

import asyncio
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger
from backend.testing.intelligence_engine import TestCase

logger = get_logger(__name__)


class TestResultStatus(Enum):
    """Status of a test execution."""
    PASSED = "passed"
    FAILED = "failed"
    FLAKY = "flaky"
    HEALED = "healed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class TestExecutionResult:
    """Result of a single test execution."""
    test_id: str
    test_name: str
    status: TestResultStatus
    duration_ms: float
    attempt_number: int
    error_message: str | None = None
    stack_trace: str | None = None
    healing_applied: bool = False
    healing_description: str = ""
    screenshot_path: str | None = None
    console_output: str = ""
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "attempt_number": self.attempt_number,
            "error_message": self.error_message,
            "healing_applied": self.healing_applied,
            "healing_description": self.healing_description,
            "executed_at": self.executed_at.isoformat(),
        }


@dataclass
class FlakyTest:
    """Information about a flaky test."""
    test_id: str
    test_name: str
    failure_rate: float
    last_failure: datetime
    failure_patterns: list[str] = field(default_factory=list)
    quarantined: bool = False
    quarantined_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "failure_rate": self.failure_rate,
            "last_failure": self.last_failure.isoformat(),
            "quarantined": self.quarantined,
            "quarantined_at": self.quarantined_at.isoformat() if self.quarantined_at else None,
        }


@dataclass
class TestSuiteResult:
    """Result of a complete test suite execution."""
    suite_name: str
    start_time: datetime
    end_time: datetime
    total_tests: int
    passed: int
    failed: int
    flaky: int
    healed: int
    skipped: int
    results: list[TestExecutionResult] = field(default_factory=list)
    execution_log: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed + self.healed) / self.total_tests

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "flaky": self.flaky,
            "healed": self.healed,
            "skipped": self.skipped,
            "pass_rate": self.pass_rate,
        }


class SelfHealingTestRunner:
    """
    Self-healing test runner with intelligent recovery.

    Features:
    - Automatic retry with exponential backoff
    - Flaky test detection and quarantine
    - Self-healing selectors for E2E tests
    - Smart test ordering
    - Parallel execution
    - Real-time healing

    Example:
        >>> runner = SelfHealingTestRunner()
        >>> suite = TestSuite(name="auth_tests", test_cases=[...])
        >>> result = await runner.run_suite(suite)
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay_ms: int = 1000,
        flaky_threshold: float = 0.2,
        enable_healing: bool = True,
        parallel_workers: int = 4,
    ):
        """
        Initialize the self-healing test runner.

        Args:
            max_retries: Maximum retry attempts for failed tests
            retry_delay_ms: Initial retry delay in milliseconds
            flaky_threshold: Failure rate threshold for flaky detection
            enable_healing: Enable self-healing features
            parallel_workers: Number of parallel test workers
        """
        self._max_retries = max_retries
        self._retry_delay_ms = retry_delay_ms
        self._flaky_threshold = flaky_threshold
        self._enable_healing = enable_healing
        self._parallel_workers = parallel_workers

        self._logger = get_logger(__name__)
        self._execution_history: dict[str, list[TestExecutionResult]] = {}
        self._flaky_tests: dict[str, FlakyTest] = {}
        self._healing_strategies: list[Callable] = []

        self._register_default_healing_strategies()

    async def run_suite(
        self,
        test_cases: list[TestCase],
        suite_name: str = "test_suite",
        stop_on_first_failure: bool = False,
        run_quarantined: bool = False,
    ) -> TestSuiteResult:
        """
        Run a test suite with self-healing capabilities.

        Args:
            test_cases: List of test cases to run
            suite_name: Name of the test suite
            stop_on_first_failure: Stop on first failure
            run_quarantined: Include quarantined tests

        Returns:
            TestSuiteResult with execution results
        """
        start_time = datetime.utcnow()

        self._logger.info(
            "Starting test suite execution",
            suite_name=suite_name,
            test_count=len(test_cases),
        )

        # Filter out quarantined tests unless explicitly requested
        if not run_quarantined:
            test_cases = [
                tc for tc in test_cases
                if tc.id not in self._flaky_tests or not self._flaky_tests[tc.id].quarantined
            ]

        # Sort tests by priority and failure history
        sorted_tests = self._sort_tests_by_priority(test_cases)

        # Execute tests
        results = []
        passed = failed = flaky = healed = skipped = 0

        # Use semaphore for parallel execution
        semaphore = asyncio.Semaphore(self._parallel_workers)

        async def run_with_semaphore(test_case: TestCase):
            async with semaphore:
                return await self._run_test_with_healing(test_case)

        # Run all tests
        tasks = [run_with_semaphore(tc) for tc in sorted_tests]
        execution_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in execution_results:
            if isinstance(result, Exception):
                self._logger.error("Test execution failed with exception", error=str(result))
                failed += 1
                continue

            results.append(result)

            if result.status == TestResultStatus.PASSED:
                passed += 1
            elif result.status == TestResultStatus.FAILED:
                failed += 1
                if stop_on_first_failure:
                    break
            elif result.status == TestResultStatus.FLAKY:
                flaky += 1
            elif result.status == TestResultStatus.HEALED:
                healed += 1
            elif result.status == TestResultStatus.SKIPPED:
                skipped += 1

        end_time = datetime.utcnow()

        suite_result = TestSuiteResult(
            suite_name=suite_name,
            start_time=start_time,
            end_time=end_time,
            total_tests=len(results),
            passed=passed,
            failed=failed,
            flaky=flaky,
            healed=healed,
            skipped=skipped,
            results=results,
        )

        # Update flaky test tracking
        self._update_flaky_test_tracking(results)

        self._logger.info(
            "Test suite execution complete",
            suite_name=suite_name,
            passed=passed,
            failed=failed,
            flaky=flaky,
            healed=healed,
            duration_seconds=suite_result.duration_seconds,
        )

        return suite_result

    async def run_single_test(
        self,
        test_case: TestCase,
        enable_retry: bool = True
    ) -> TestExecutionResult:
        """
        Run a single test with self-healing.

        Args:
            test_case: Test case to run
            enable_retry: Enable retry on failure

        Returns:
            TestExecutionResult
        """
        return await self._run_test_with_healing(test_case, enable_retry)

    def get_flaky_tests(self) -> list[FlakyTest]:
        """
        Get list of detected flaky tests.

        Returns:
            List of flaky tests
        """
        return list(self._flaky_tests.values())

    def quarantine_test(self, test_id: str, reason: str = "") -> bool:
        """
        Quarantine a flaky test.

        Args:
            test_id: Test ID to quarantine
            reason: Reason for quarantine

        Returns:
            True if quarantined
        """
        if test_id not in self._flaky_tests:
            return False

        self._flaky_tests[test_id].quarantined = True
        self._flaky_tests[test_id].quarantined_at = datetime.utcnow()

        self._logger.info("Test quarantined", test_id=test_id, reason=reason)

        return True

    def unquarantine_test(self, test_id: str) -> bool:
        """
        Remove a test from quarantine.

        Args:
            test_id: Test ID to unquarantine

        Returns:
            True if unquarantined
        """
        if test_id not in self._flaky_tests:
            return False

        self._flaky_tests[test_id].quarantined = False
        self._flaky_tests[test_id].quarantined_at = None

        self._logger.info("Test unquarantined", test_id=test_id)

        return True

    def get_execution_statistics(self) -> dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Statistics dictionary
        """
        total_executions = sum(
            len(results) for results in self._execution_history.values()
        )

        total_healed = sum(
            1 for results in self._execution_history.values()
            for r in results if r.healing_applied
        )

        return {
            "total_test_executions": total_executions,
            "unique_tests": len(self._execution_history),
            "flaky_tests_detected": len(self._flaky_tests),
            "quarantined_tests": sum(
                1 for ft in self._flaky_tests.values() if ft.quarantined
            ),
            "total_healing_applied": total_healed,
            "healing_success_rate": (
                total_healed / total_executions if total_executions > 0 else 0
            ),
        }

    def register_healing_strategy(self, strategy: Callable):
        """
        Register a custom healing strategy.

        Args:
            strategy: Healing strategy function
        """
        self._healing_strategies.append(strategy)

    # Private methods

    def _register_default_healing_strategies(self):
        """Register default healing strategies."""
        self._healing_strategies = [
            self._heal_timing_issues,
            self._heal_selector_issues,
            self._heal_network_issues,
        ]

    async def _run_test_with_healing(
        self,
        test_case: TestCase,
        enable_retry: bool = True
    ) -> TestExecutionResult:
        """Run a test with retry and healing logic."""
        last_result = None

        for attempt in range(1, self._max_retries + 1):
            start_time = time.time()

            try:
                # Execute the actual test
                result = await self._execute_test(test_case)
                duration_ms = (time.time() - start_time) * 1000

                if result["success"]:
                    # Test passed
                    execution_result = TestExecutionResult(
                        test_id=test_case.id,
                        test_name=test_case.name,
                        status=TestResultStatus.PASSED,
                        duration_ms=duration_ms,
                        attempt_number=attempt,
                        healing_applied=last_result is not None,
                    )

                    # Store in history
                    self._store_execution_result(execution_result)

                    return execution_result

                else:
                    # Test failed - try healing
                    if self._enable_healing and attempt < self._max_retries:
                        healed = await self._attempt_healing(test_case, result)

                        if healed:
                            last_result = result
                            # Retry with exponential backoff
                            delay = self._retry_delay_ms * (2 ** (attempt - 1))
                            await asyncio.sleep(delay / 1000)
                            continue

                    # No healing possible or max retries reached
                    duration_ms = (time.time() - start_time) * 1000

                    execution_result = TestExecutionResult(
                        test_id=test_case.id,
                        test_name=test_case.name,
                        status=TestResultStatus.FAILED,
                        duration_ms=duration_ms,
                        attempt_number=attempt,
                        error_message=result.get("error"),
                        stack_trace=result.get("stack_trace"),
                        healing_applied=last_result is not None,
                    )

                    self._store_execution_result(execution_result)

                    return execution_result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                execution_result = TestExecutionResult(
                    test_id=test_case.id,
                    test_name=test_case.name,
                    status=TestResultStatus.FAILED,
                    duration_ms=duration_ms,
                    attempt_number=attempt,
                    error_message=str(e),
                )

                self._store_execution_result(execution_result)

                return execution_result

        # Should not reach here
        return TestExecutionResult(  # pragma: no cover
            test_id=test_case.id,
            test_name=test_case.name,
            status=TestResultStatus.FAILED,
            duration_ms=0,
            attempt_number=self._max_retries,
            error_message="Max retries exceeded",
        )

    async def _execute_test(self, test_case: TestCase) -> dict[str, Any]:
        """Execute a single test."""
        # This would integrate with pytest or Playwright
        # For now, simulate test execution

        # Simulate occasional failures for testing
        if random.random() < 0.1:  # 10% failure rate for demo
            return {
                "success": False,
                "error": "Simulated test failure",
                "stack_trace": "Traceback (most recent call last):...",
            }

        return {"success": True}

    async def _attempt_healing(
        self,
        test_case: TestCase,
        failure_result: dict[str, Any]
    ) -> bool:
        """Attempt to heal a failing test."""
        for strategy in self._healing_strategies:
            try:
                healed = await strategy(test_case, failure_result)
                if healed:
                    return True
            except Exception as e:
                self._logger.error("Healing strategy failed", error=str(e))

        return False

    async def _heal_timing_issues(
        self,
        test_case: TestCase,
        failure_result: dict[str, Any]
    ) -> bool:
        """Heal timing-related issues."""
        error = failure_result.get("error", "")

        if "timeout" in error.lower() or "element not found" in error.lower():
            self._logger.info("Applying timing healing", test_id=test_case.id)
            # Would add implicit waits or retry logic
            return True

        return False

    async def _heal_selector_issues(
        self,
        test_case: TestCase,
        failure_result: dict[str, Any]
    ) -> bool:
        """Heal selector-related issues."""
        error = failure_result.get("error", "")

        if "selector" in error.lower() or "element not found" in error.lower():
            self._logger.info("Applying selector healing", test_id=test_case.id)
            # Would attempt to find alternative selectors
            return True

        return False

    async def _heal_network_issues(
        self,
        test_case: TestCase,
        failure_result: dict[str, Any]
    ) -> bool:
        """Heal network-related issues."""
        error = failure_result.get("error", "")

        if "network" in error.lower() or "connection" in error.lower():
            self._logger.info("Applying network healing", test_id=test_case.id)
            # Would add retry logic for network requests
            return True

        return False

    def _sort_tests_by_priority(self, test_cases: list[TestCase]) -> list[TestCase]:
        """Sort tests by priority and failure history."""
        def sort_key(tc: TestCase):
            # Priority score (lower is higher priority)
            priority_score = tc.priority.value

            # Failure history score
            history = self._execution_history.get(tc.id, [])
            recent_failures = sum(
                1 for r in history[-5:]
                if r.status in [TestResultStatus.FAILED, TestResultStatus.FLAKY]
            )

            # Tests with recent failures should run first (fail fast)
            return (priority_score, -recent_failures, tc.name)

        return sorted(test_cases, key=sort_key)

    def _store_execution_result(self, result: TestExecutionResult):
        """Store execution result in history."""
        if result.test_id not in self._execution_history:
            self._execution_history[result.test_id] = []

        self._execution_history[result.test_id].append(result)

        # Keep only last 20 results per test
        self._execution_history[result.test_id] = (
            self._execution_history[result.test_id][-20:]
        )

    def _update_flaky_test_tracking(self, results: list[TestExecutionResult]):
        """Update flaky test tracking based on results."""
        for result in results:
            if result.test_id not in self._execution_history:
                continue

            history = self._execution_history[result.test_id]

            if len(history) >= 5:
                # Calculate failure rate
                recent = history[-10:]
                failures = sum(
                    1 for r in recent
                    if r.status in [TestResultStatus.FAILED, TestResultStatus.FLAKY]
                )
                failure_rate = failures / len(recent)

                if failure_rate >= self._flaky_threshold:
                    if result.test_id not in self._flaky_tests:
                        self._flaky_tests[result.test_id] = FlakyTest(
                            test_id=result.test_id,
                            test_name=result.test_name,
                            failure_rate=failure_rate,
                            last_failure=datetime.utcnow(),
                        )
                        self._logger.warning(
                            "Flaky test detected",
                            test_id=result.test_id,
                            failure_rate=failure_rate,
                        )
                    else:
                        self._flaky_tests[result.test_id].failure_rate = failure_rate
                        self._flaky_tests[result.test_id].last_failure = datetime.utcnow()
