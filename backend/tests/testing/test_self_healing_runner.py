"""
Tests for SelfHealingTestRunner - Intelligent test execution with auto-recovery.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from backend.testing.intelligence_engine import TestCase, TestPriority, TestType
from backend.testing.self_healing_runner import (
    FlakyTest,
    SelfHealingTestRunner,
    TestExecutionResult,
    TestResultStatus,
    TestSuiteResult,
)


@pytest.fixture
def test_runner():
    """Fixture for SelfHealingTestRunner."""
    runner = SelfHealingTestRunner(
        max_retries=3,
        retry_delay_ms=100,
        flaky_threshold=0.2,
        enable_healing=True,
        parallel_workers=2,
    )
    return runner


@pytest.fixture
def sample_test_cases():
    """Create sample test cases."""
    return [
        TestCase(
            id="test_1",
            name="test_function_1",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="def test_func(): pass",
            priority=TestPriority.HIGH,
        ),
        TestCase(
            id="test_2",
            name="test_function_2",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="def test_func2(): pass",
            priority=TestPriority.MEDIUM,
        ),
        TestCase(
            id="test_3",
            name="test_function_3",
            test_type=TestType.UNIT,
            target_file="/path/file.py",
            code="def test_func3(): pass",
            priority=TestPriority.LOW,
        ),
    ]


class TestTestResultStatusEnum:
    """Tests for TestResultStatus enum."""

    def test_all_status_values(self):
        """Test all TestResultStatus values."""
        assert TestResultStatus.PASSED.value == "passed"
        assert TestResultStatus.FAILED.value == "failed"
        assert TestResultStatus.FLAKY.value == "flaky"
        assert TestResultStatus.HEALED.value == "healed"
        assert TestResultStatus.SKIPPED.value == "skipped"
        assert TestResultStatus.TIMEOUT.value == "timeout"


class TestTestExecutionResult:
    """Tests for TestExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test TestExecutionResult creation."""
        result = TestExecutionResult(
            test_id="test_123",
            test_name="test_function",
            status=TestResultStatus.PASSED,
            duration_ms=150.0,
            attempt_number=1,
        )

        assert result.test_id == "test_123"
        assert result.status == TestResultStatus.PASSED
        assert result.duration_ms == 150.0

    def test_execution_result_with_error(self):
        """Test TestExecutionResult with error."""
        result = TestExecutionResult(
            test_id="test_456",
            test_name="test_failing",
            status=TestResultStatus.FAILED,
            duration_ms=200.0,
            attempt_number=3,
            error_message="AssertionError",
            stack_trace="Traceback...",
        )

        assert result.status == TestResultStatus.FAILED
        assert result.error_message == "AssertionError"
        assert result.attempt_number == 3

    def test_execution_result_to_dict(self):
        """Test TestExecutionResult serialization."""
        result = TestExecutionResult(
            test_id="test_789",
            test_name="test_healed",
            status=TestResultStatus.HEALED,
            duration_ms=300.0,
            attempt_number=2,
            healing_applied=True,
            healing_description="Fixed selector",
        )

        data = result.to_dict()

        assert data["test_id"] == "test_789"
        assert data["status"] == "healed"
        assert data["healing_applied"] is True
        assert "executed_at" in data


class TestFlakyTest:
    """Tests for FlakyTest dataclass."""

    def test_flaky_test_creation(self):
        """Test FlakyTest creation."""
        flaky = FlakyTest(
            test_id="test_123",
            test_name="test_flaky",
            failure_rate=0.3,
            last_failure=datetime(2024, 1, 15, 10, 0, 0),
        )

        assert flaky.test_id == "test_123"
        assert flaky.failure_rate == 0.3
        assert flaky.quarantined is False

    def test_flaky_test_quarantined(self):
        """Test FlakyTest when quarantined."""
        flaky = FlakyTest(
            test_id="test_456",
            test_name="test_very_flaky",
            failure_rate=0.5,
            last_failure=datetime.utcnow(),
            quarantined=True,
            quarantined_at=datetime(2024, 1, 15, 11, 0, 0),
        )

        assert flaky.quarantined is True
        assert flaky.quarantined_at is not None

    def test_flaky_test_to_dict(self):
        """Test FlakyTest serialization."""
        flaky = FlakyTest(
            test_id="test_789",
            test_name="test_flaky",
            failure_rate=0.25,
            last_failure=datetime(2024, 1, 15, 10, 0, 0),
            failure_patterns=["timeout", "network"],
            quarantined=True,
            quarantined_at=datetime(2024, 1, 15, 12, 0, 0),
        )

        data = flaky.to_dict()

        assert data["test_id"] == "test_789"
        assert data["failure_rate"] == 0.25
        assert data["quarantined"] is True


class TestTestSuiteResult:
    """Tests for TestSuiteResult dataclass."""

    def test_suite_result_creation(self):
        """Test TestSuiteResult creation."""
        result = TestSuiteResult(
            suite_name="auth_tests",
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 10, 5, 0),
            total_tests=10,
            passed=8,
            failed=1,
            flaky=0,
            healed=1,
            skipped=0,
        )

        assert result.suite_name == "auth_tests"
        assert result.total_tests == 10
        assert result.passed == 8

    def test_duration_seconds(self):
        """Test duration_seconds calculation."""
        result = TestSuiteResult(
            suite_name="test",
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 10, 2, 30),
            total_tests=5,
            passed=5,
            failed=0,
            flaky=0,
            healed=0,
            skipped=0,
        )

        assert result.duration_seconds == 150.0

    def test_pass_rate(self):
        """Test pass_rate calculation."""
        result = TestSuiteResult(
            suite_name="test",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            total_tests=10,
            passed=6,
            failed=2,
            flaky=1,
            healed=1,
            skipped=0,
        )

        # pass_rate = (passed + healed) / total_tests = (6 + 1) / 10 = 0.7
        assert result.pass_rate == 0.7

    def test_pass_rate_zero_tests(self):
        """Test pass_rate with zero tests."""
        result = TestSuiteResult(
            suite_name="empty",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            total_tests=0,
            passed=0,
            failed=0,
            flaky=0,
            healed=0,
            skipped=0,
        )

        assert result.pass_rate == 0.0

    def test_suite_result_to_dict(self):
        """Test TestSuiteResult serialization."""
        result = TestSuiteResult(
            suite_name="suite",
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 10, 1, 0),
            total_tests=5,
            passed=3,
            failed=1,
            flaky=0,
            healed=1,
            skipped=0,
        )

        data = result.to_dict()

        assert data["suite_name"] == "suite"
        assert data["duration_seconds"] == 60.0
        assert data["pass_rate"] == 0.8


class TestSelfHealingTestRunner:
    """Tests for SelfHealingTestRunner class."""

    def test_runner_initialization(self, test_runner):
        """Test runner initialization."""
        assert test_runner._max_retries == 3
        assert test_runner._retry_delay_ms == 100
        assert test_runner._flaky_threshold == 0.2
        assert test_runner._enable_healing is True
        assert test_runner._parallel_workers == 2

    def test_default_healing_strategies(self, test_runner):
        """Test default healing strategies are registered."""
        assert len(test_runner._healing_strategies) == 3

    @pytest.mark.asyncio
    async def test_run_suite(self, test_runner, sample_test_cases):
        """Test running a test suite."""
        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="test_suite",
        )

        assert isinstance(result, TestSuiteResult)
        assert result.suite_name == "test_suite"
        assert result.total_tests == len(sample_test_cases)

    @pytest.mark.asyncio
    async def test_run_suite_stop_on_failure(self, test_runner, sample_test_cases):
        """Test run_suite with stop_on_first_failure."""
        # Make first test fail
        with patch.object(test_runner, '_execute_test') as mock_execute:
            mock_execute.return_value = {"success": False, "error": "Test failed"}

            result = await test_runner.run_suite(
                test_cases=sample_test_cases,
                suite_name="test_suite",
                stop_on_first_failure=True,
            )

            # Should stop after first failure (after retries)
            assert result.failed >= 1

    @pytest.mark.asyncio
    async def test_run_suite_quarantined_tests(self, test_runner, sample_test_cases):
        """Test run_suite filters quarantined tests."""
        # Quarantine one test
        test_runner._flaky_tests["test_1"] = FlakyTest(
            test_id="test_1",
            test_name="test_function_1",
            failure_rate=0.5,
            last_failure=datetime.utcnow(),
            quarantined=True,
        )

        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="test_suite",
            run_quarantined=False,
        )

        # Should have one less test
        assert result.total_tests == len(sample_test_cases) - 1

    @pytest.mark.asyncio
    async def test_run_suite_include_quarantined(self, test_runner, sample_test_cases):
        """Test run_suite includes quarantined when requested."""
        # Quarantine one test
        test_runner._flaky_tests["test_1"] = FlakyTest(
            test_id="test_1",
            test_name="test_function_1",
            failure_rate=0.5,
            last_failure=datetime.utcnow(),
            quarantined=True,
        )

        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="test_suite",
            run_quarantined=True,
        )

        # Should run all tests
        assert result.total_tests == len(sample_test_cases)

    @pytest.mark.asyncio
    async def test_run_single_test(self, test_runner, sample_test_cases):
        """Test running a single test."""
        result = await test_runner.run_single_test(
            test_case=sample_test_cases[0],
            enable_retry=True,
        )

        assert isinstance(result, TestExecutionResult)
        assert result.test_id == "test_1"

    def test_get_flaky_tests(self, test_runner):
        """Test getting flaky tests."""
        test_runner._flaky_tests["test_1"] = FlakyTest(
            test_id="test_1",
            test_name="test_flaky",
            failure_rate=0.3,
            last_failure=datetime.utcnow(),
        )

        flaky = test_runner.get_flaky_tests()

        assert len(flaky) == 1
        assert flaky[0].test_id == "test_1"

    def test_quarantine_test(self, test_runner):
        """Test quarantining a test."""
        test_runner._flaky_tests["test_1"] = FlakyTest(
            test_id="test_1",
            test_name="test_flaky",
            failure_rate=0.3,
            last_failure=datetime.utcnow(),
        )

        result = test_runner.quarantine_test("test_1", "Too flaky")

        assert result is True
        assert test_runner._flaky_tests["test_1"].quarantined is True

    def test_quarantine_test_not_found(self, test_runner):
        """Test quarantining non-existent test."""
        result = test_runner.quarantine_test("nonexistent", "reason")

        assert result is False

    def test_unquarantine_test(self, test_runner):
        """Test unquarantining a test."""
        test_runner._flaky_tests["test_1"] = FlakyTest(
            test_id="test_1",
            test_name="test_flaky",
            failure_rate=0.3,
            last_failure=datetime.utcnow(),
            quarantined=True,
            quarantined_at=datetime.utcnow(),
        )

        result = test_runner.unquarantine_test("test_1")

        assert result is True
        assert test_runner._flaky_tests["test_1"].quarantined is False

    def test_unquarantine_test_not_found(self, test_runner):
        """Test unquarantining non-existent test."""
        result = test_runner.unquarantine_test("nonexistent")

        assert result is False

    def test_get_execution_statistics_empty(self, test_runner):
        """Test execution statistics with no history."""
        stats = test_runner.get_execution_statistics()

        assert stats["total_test_executions"] == 0
        assert stats["unique_tests"] == 0

    def test_get_execution_statistics(self, test_runner):
        """Test execution statistics with history."""
        # Add some execution history
        test_runner._execution_history["test_1"] = [
            TestExecutionResult(
                test_id="test_1", test_name="test_1",
                status=TestResultStatus.PASSED, duration_ms=100,
                attempt_number=1, healing_applied=True
            ),
            TestExecutionResult(
                test_id="test_1", test_name="test_1",
                status=TestResultStatus.PASSED, duration_ms=100,
                attempt_number=1
            ),
        ]
        test_runner._execution_history["test_2"] = [
            TestExecutionResult(
                test_id="test_2", test_name="test_2",
                status=TestResultStatus.FAILED, duration_ms=100,
                attempt_number=1
            ),
        ]
        test_runner._flaky_tests["test_3"] = FlakyTest(
            test_id="test_3", test_name="test_3",
            failure_rate=0.3, last_failure=datetime.utcnow(),
            quarantined=True
        )

        stats = test_runner.get_execution_statistics()

        assert stats["total_test_executions"] == 3
        assert stats["unique_tests"] == 2
        assert stats["total_healing_applied"] == 1
        assert stats["flaky_tests_detected"] == 1
        assert stats["quarantined_tests"] == 1

    def test_register_healing_strategy(self, test_runner):
        """Test registering custom healing strategy."""
        async def custom_strategy(test_case, failure_result):
            return True

        initial_count = len(test_runner._healing_strategies)
        test_runner.register_healing_strategy(custom_strategy)

        assert len(test_runner._healing_strategies) == initial_count + 1

    @pytest.mark.asyncio
    async def test_heal_timing_issues(self, test_runner, sample_test_cases):
        """Test _heal_timing_issues method."""
        failure_result = {"error": "timeout waiting for element"}

        healed = await test_runner._heal_timing_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is True

    @pytest.mark.asyncio
    async def test_heal_timing_issues_no_match(self, test_runner, sample_test_cases):
        """Test _heal_timing_issues with non-timing error."""
        failure_result = {"error": "assertion failed"}

        healed = await test_runner._heal_timing_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is False

    @pytest.mark.asyncio
    async def test_heal_selector_issues(self, test_runner, sample_test_cases):
        """Test _heal_selector_issues method."""
        failure_result = {"error": "element not found by selector"}

        healed = await test_runner._heal_selector_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is True

    @pytest.mark.asyncio
    async def test_heal_selector_issues_no_match(self, test_runner, sample_test_cases):
        """Test _heal_selector_issues with non-selector error."""
        failure_result = {"error": "database connection failed"}

        healed = await test_runner._heal_selector_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is False

    @pytest.mark.asyncio
    async def test_heal_network_issues(self, test_runner, sample_test_cases):
        """Test _heal_network_issues method."""
        failure_result = {"error": "network connection refused"}

        healed = await test_runner._heal_network_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is True

    @pytest.mark.asyncio
    async def test_heal_network_issues_no_match(self, test_runner, sample_test_cases):
        """Test _heal_network_issues with non-network error."""
        failure_result = {"error": "index out of range"}

        healed = await test_runner._heal_network_issues(
            sample_test_cases[0], failure_result
        )

        assert healed is False

    def test_sort_tests_by_priority(self, test_runner, sample_test_cases):
        """Test _sort_tests_by_priority method."""
        sorted_tests = test_runner._sort_tests_by_priority(sample_test_cases)

        # HIGH priority should come first
        assert sorted_tests[0].priority == TestPriority.HIGH
        assert sorted_tests[-1].priority == TestPriority.LOW

    def test_sort_tests_with_failure_history(self, test_runner, sample_test_cases):
        """Test sorting considers failure history."""
        # Add failure history for low priority test
        test_runner._execution_history["test_3"] = [
            TestExecutionResult(
                test_id="test_3", test_name="test_3",
                status=TestResultStatus.FAILED, duration_ms=100,
                attempt_number=1
            ) for _ in range(5)
        ]

        test_runner._sort_tests_by_priority(sample_test_cases)

        # Test with failures should be prioritized within priority level
        # but HIGH priority still comes first overall

    def test_store_execution_result(self, test_runner):
        """Test _store_execution_result method."""
        result = TestExecutionResult(
            test_id="test_1", test_name="test_1",
            status=TestResultStatus.PASSED, duration_ms=100,
            attempt_number=1
        )

        test_runner._store_execution_result(result)

        assert "test_1" in test_runner._execution_history
        assert len(test_runner._execution_history["test_1"]) == 1

    def test_store_execution_result_limit(self, test_runner):
        """Test _store_execution_result keeps only last 20."""
        for _i in range(25):
            result = TestExecutionResult(
                test_id="test_1", test_name="test_1",
                status=TestResultStatus.PASSED, duration_ms=100,
                attempt_number=1
            )
            test_runner._store_execution_result(result)

        assert len(test_runner._execution_history["test_1"]) == 20

    def test_update_flaky_test_tracking(self, test_runner):
        """Test _update_flaky_test_tracking method."""
        # Add execution history with failures
        test_runner._execution_history["test_1"] = []
        for i in range(10):
            status = TestResultStatus.FAILED if i < 4 else TestResultStatus.PASSED
            test_runner._execution_history["test_1"].append(
                TestExecutionResult(
                    test_id="test_1", test_name="test_1",
                    status=status, duration_ms=100,
                    attempt_number=1
                )
            )

        results = test_runner._execution_history["test_1"]
        test_runner._update_flaky_test_tracking(results)

        # Should detect as flaky (40% failure rate > 20% threshold)
        assert "test_1" in test_runner._flaky_tests

    def test_update_flaky_test_tracking_insufficient_history(self, test_runner):
        """Test _update_flaky_test_tracking with insufficient history."""
        # Only 3 executions, need at least 5
        test_runner._execution_history["test_1"] = [
            TestExecutionResult(
                test_id="test_1", test_name="test_1",
                status=TestResultStatus.FAILED, duration_ms=100,
                attempt_number=1
            ) for _ in range(3)
        ]

        results = test_runner._execution_history["test_1"]
        test_runner._update_flaky_test_tracking(results)

        # Should not be marked as flaky yet
        assert "test_1" not in test_runner._flaky_tests

    @pytest.mark.asyncio
    async def test_run_test_with_healing_success(self, test_runner, sample_test_cases):
        """Test _run_test_with_healing when test passes."""
        result = await test_runner._run_test_with_healing(
            sample_test_cases[0], enable_retry=True
        )

        assert isinstance(result, TestExecutionResult)

    @pytest.mark.asyncio
    async def test_run_test_with_healing_retry(self, test_runner, sample_test_cases):
        """Test _run_test_with_healing with retry logic."""
        call_count = [0]

        async def mock_execute(test_case):
            call_count[0] += 1
            if call_count[0] < 2:
                return {"success": False, "error": "timeout error"}
            return {"success": True}

        with patch.object(test_runner, '_execute_test', side_effect=mock_execute):
            await test_runner._run_test_with_healing(
                sample_test_cases[0], enable_retry=True
            )

            # Should have retried and eventually passed
            assert call_count[0] >= 2

    @pytest.mark.asyncio
    async def test_attempt_healing(self, test_runner, sample_test_cases):
        """Test _attempt_healing method."""
        failure_result = {"error": "timeout waiting for element"}

        healed = await test_runner._attempt_healing(
            sample_test_cases[0], failure_result
        )

        assert healed is True

    @pytest.mark.asyncio
    async def test_attempt_healing_no_strategy_matches(self, test_runner, sample_test_cases):
        """Test _attempt_healing when no strategy matches."""
        failure_result = {"error": "unknown error type xyz"}

        healed = await test_runner._attempt_healing(
            sample_test_cases[0], failure_result
        )

        assert healed is False

    @pytest.mark.asyncio
    async def test_attempt_healing_strategy_error(self, test_runner, sample_test_cases):
        """Test _attempt_healing when strategy raises error."""
        async def failing_strategy(tc, result):
            raise Exception("Strategy error")

        test_runner._healing_strategies = [failing_strategy]

        healed = await test_runner._attempt_healing(
            sample_test_cases[0], {"error": "any error"}
        )

        assert healed is False

    @pytest.mark.asyncio
    async def test_execute_test(self, test_runner, sample_test_cases):
        """Test _execute_test method."""
        result = await test_runner._execute_test(sample_test_cases[0])

        assert "success" in result

    @pytest.mark.asyncio
    async def test_run_suite_exception_handling(self, test_runner, sample_test_cases):
        """Test run_suite handles exceptions gracefully."""
        async def mock_run_with_healing(tc, enable_retry=True):
            raise Exception("Test execution error")

        with patch.object(test_runner, '_run_test_with_healing', side_effect=mock_run_with_healing):
            result = await test_runner.run_suite(
                test_cases=sample_test_cases,
                suite_name="test_suite",
            )

            # Should handle exceptions and count as failures
            assert result.failed >= len(sample_test_cases)


class TestSelfHealingRunnerExtendedCoverage:
    """Tests for extended coverage - lines 244-249, 458-475, 491, 594."""

    @pytest.fixture
    def test_runner(self):
        """Fixture for SelfHealingTestRunner."""
        from backend.testing.self_healing_runner import SelfHealingTestRunner
        runner = SelfHealingTestRunner(
            max_retries=3,
            retry_delay_ms=10,
            flaky_threshold=0.2,
            enable_healing=True,
            parallel_workers=1,
        )
        return runner

    @pytest.fixture
    def sample_test_cases(self):
        """Create sample test cases."""
        from backend.testing.intelligence_engine import TestCase, TestPriority, TestType
        return [
            TestCase(id="test_status", name="test_function", test_type=TestType.UNIT, target_file="/f.py", code="def test(): pass", priority=TestPriority.HIGH),
        ]

    @pytest.mark.asyncio
    async def test_run_suite_flaky_status_line_244_245(self, test_runner, sample_test_cases):
        """Test lines 244-245: FLAKY status handling."""
        from backend.testing.self_healing_runner import TestExecutionResult, TestResultStatus

        # Mock to return FLAKY status
        async def mock_run_test_with_healing(tc, enable_retry=True):
            return TestExecutionResult(
                test_id=tc.id,
                test_name=tc.name,
                status=TestResultStatus.FLAKY,
                duration_ms=100,
                attempt_number=1,
            )

        test_runner._run_test_with_healing = mock_run_test_with_healing

        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="flaky_suite",
        )

        # Line 244-245: flaky count should be incremented
        assert result.flaky == 1

    @pytest.mark.asyncio
    async def test_run_suite_healed_status_line_246_247(self, test_runner, sample_test_cases):
        """Test lines 246-247: HEALED status handling."""
        from backend.testing.self_healing_runner import TestExecutionResult, TestResultStatus

        # Mock to return HEALED status
        async def mock_run_test_with_healing(tc, enable_retry=True):
            return TestExecutionResult(
                test_id=tc.id,
                test_name=tc.name,
                status=TestResultStatus.HEALED,
                duration_ms=100,
                attempt_number=2,
            )

        test_runner._run_test_with_healing = mock_run_test_with_healing

        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="healed_suite",
        )

        # Line 246-247: healed count should be incremented
        assert result.healed == 1

    @pytest.mark.asyncio
    async def test_run_suite_skipped_status_line_248_249(self, test_runner, sample_test_cases):
        """Test lines 248-249: SKIPPED status handling."""
        from backend.testing.self_healing_runner import TestExecutionResult, TestResultStatus

        # Mock to return SKIPPED status
        async def mock_run_test_with_healing(tc, enable_retry=True):
            return TestExecutionResult(
                test_id=tc.id,
                test_name=tc.name,
                status=TestResultStatus.SKIPPED,
                duration_ms=0,
                attempt_number=1,
            )

        test_runner._run_test_with_healing = mock_run_test_with_healing

        result = await test_runner.run_suite(
            test_cases=sample_test_cases,
            suite_name="skipped_suite",
        )

        # Line 248-249: skipped count should be incremented
        assert result.skipped == 1

    @pytest.mark.asyncio
    async def test_run_test_with_healing_exception_lines_458_475(self, test_runner, sample_test_cases):
        """Test lines 458-475: exception handling in _run_test_with_healing."""
        from unittest.mock import AsyncMock

        from backend.testing.self_healing_runner import TestResultStatus

        # Mock _execute_test to raise an exception
        test_runner._execute_test = AsyncMock(side_effect=Exception("Test crashed"))

        result = await test_runner._run_test_with_healing(
            sample_test_cases[0],
            enable_retry=True,
        )

        # Lines 458-475: should return FAILED status with error message
        assert result.status == TestResultStatus.FAILED
        assert "Test crashed" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_test_failure_branch_line_491(self, test_runner, sample_test_cases):
        """Test line 491: _execute_test failure branch."""
        import random
        from unittest.mock import patch

        # Force the random failure branch (line 490-495)
        with patch.object(random, 'random', return_value=0.05):  # 0.05 < 0.1
            result = await test_runner._execute_test(sample_test_cases[0])

            # Line 491: should return failure result
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_update_flaky_test_tracking_no_history_line_594(self, test_runner):
        """Test line 594: continue when test_id not in execution_history."""
        from backend.testing.self_healing_runner import TestExecutionResult, TestResultStatus

        # Create a result for a test that has no history
        result = TestExecutionResult(
            test_id="unknown_test",
            test_name="test_unknown",
            status=TestResultStatus.PASSED,
            duration_ms=100,
            attempt_number=1,
        )

        # Clear execution history to ensure test_id is not present
        test_runner._execution_history.clear()

        # Line 594: should continue (skip) when test_id not in history
        test_runner._update_flaky_test_tracking([result])

        # No flaky tests should be detected
        assert "unknown_test" not in test_runner._flaky_tests

    @pytest.mark.asyncio
    async def test_flaky_test_detection_with_history(self, test_runner, sample_test_cases):
        """Test flaky test detection when failure rate exceeds threshold."""
        from backend.testing.self_healing_runner import TestExecutionResult, TestResultStatus

        test_id = "flaky_test"
        test_name = "test_flaky"

        # Add enough history to trigger flaky detection (needs >= 5 results)
        test_runner._execution_history[test_id] = []
        for i in range(10):
            # 50% failure rate (above 0.2 threshold)
            status = TestResultStatus.FAILED if i % 2 == 0 else TestResultStatus.PASSED
            test_runner._execution_history[test_id].append(
                TestExecutionResult(
                    test_id=test_id,
                    test_name=test_name,
                    status=status,
                    duration_ms=100,
                    attempt_number=1,
                )
            )

        # Now call _update_flaky_test_tracking
        new_result = TestExecutionResult(
            test_id=test_id,
            test_name=test_name,
            status=TestResultStatus.FAILED,
            duration_ms=100,
            attempt_number=1,
        )

        test_runner._update_flaky_test_tracking([new_result])

        # Flaky test should be detected
        assert test_id in test_runner._flaky_tests
