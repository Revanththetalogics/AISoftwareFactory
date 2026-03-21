"""
Integration tester for Simulation module.

This module provides end-to-end testing for generated applications
including API testing and workflow validation.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestCase:
    """Integration test case."""
    name: str
    setup: Callable | None = None
    execute: Callable = None
    validate: Callable = None
    teardown: Callable | None = None


@dataclass
class TestResult:
    """Test execution result."""
    name: str
    success: bool
    duration: float
    error: str | None = None
    details: dict[str, Any] | None = None


class IntegrationTester:
    """
    Integration tester for end-to-end validation.

    Provides test case execution with setup, validation, and teardown.
    """

    def __init__(self):
        """Initialize the integration tester."""
        self._test_cases: dict[str, TestCase] = {}
        self._logger = get_logger(__name__)

    def register_test(self, test_case: TestCase):
        """
        Register a test case.

        Args:
            test_case: Test case to register
        """
        self._test_cases[test_case.name] = test_case
        self._logger.info("Test registered", test_name=test_case.name)

    async def run_test(self, test_name: str) -> TestResult:
        """
        Run a single test case.

        Args:
            test_name: Name of test to run

        Returns:
            Test result
        """
        import time

        if test_name not in self._test_cases:
            return TestResult(
                name=test_name,
                success=False,
                duration=0,
                error="Test not found"
            )

        test = self._test_cases[test_name]
        start_time = time.time()

        try:
            # Setup
            if test.setup:
                await test.setup()

            # Execute
            result = await test.execute()

            # Validate
            validation = await test.validate(result)
            success = validation.get("success", True)

            # Teardown
            if test.teardown:
                await test.teardown()

            duration = time.time() - start_time

            return TestResult(
                name=test_name,
                success=success,
                duration=duration,
                details=validation
            )

        except Exception as e:
            duration = time.time() - start_time

            # Ensure teardown runs even on failure
            if test.teardown:
                try:
                    await test.teardown()
                except Exception as teardown_error:
                    self._logger.error(
                        "Teardown failed",
                        test_name=test_name,
                        error=str(teardown_error)
                    )

            return TestResult(
                name=test_name,
                success=False,
                duration=duration,
                error=str(e)
            )

    async def run_all_tests(self) -> list[TestResult]:
        """
        Run all registered tests.

        Returns:
            List of test results
        """
        results = []

        for test_name in self._test_cases:
            result = await self.run_test(test_name)
            results.append(result)

        return results

    async def test_api_workflow(
        self,
        base_url: str,
        workflow: list[dict[str, Any]]
    ) -> TestResult:
        """
        Test an API workflow.

        Args:
            base_url: Base URL for API
            workflow: List of API calls to make

        Returns:
            Test result
        """
        import time

        import aiohttp

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                for step in workflow:
                    method = step.get("method", "GET")
                    path = step["path"]
                    expected_status = step.get("expected_status", 200)

                    url = f"{base_url}{path}"

                    async with session.request(method, url) as resp:
                        if resp.status != expected_status:
                            return TestResult(
                                name="api_workflow",
                                success=False,
                                duration=time.time() - start_time,
                                error=f"Expected {expected_status}, got {resp.status}"
                            )

            return TestResult(
                name="api_workflow",
                success=True,
                duration=time.time() - start_time
            )

        except Exception as e:
            return TestResult(
                name="api_workflow",
                success=False,
                duration=time.time() - start_time,
                error=str(e)
            )
