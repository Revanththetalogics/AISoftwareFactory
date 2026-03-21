"""
Tests for FrontendTesterAgent - E2E and visual testing automation.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.testing.agents.frontend_tester import (
    BrowserType,
    E2ETestResult,
    FrontendTesterAgent,
    GeneratedE2ETest,
    TestStatus,
    VisualDiff,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="""import { test, expect } from '@playwright/test';

test('user login flow', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'user@test.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="submit"]');
    await expect(page).toHaveURL('/dashboard');
});
""")
    return llm


@pytest.fixture
def frontend_tester_agent(mock_llm):
    """Fixture for FrontendTesterAgent with mocked LLM."""
    with patch('backend.testing.agents.frontend_tester.LLMFactory.create_llm', return_value=mock_llm):
        agent = FrontendTesterAgent(base_url="http://localhost:3000")
        agent._llm = mock_llm
        agent._playwright_available = False  # Mock playwright not available
        return agent


class TestBrowserTypeEnum:
    """Tests for BrowserType enum."""

    def test_all_browser_values(self):
        """Test all BrowserType values."""
        assert BrowserType.CHROMIUM.value == "chromium"
        assert BrowserType.FIREFOX.value == "firefox"
        assert BrowserType.WEBKIT.value == "webkit"


class TestTestStatusEnum:
    """Tests for TestStatus enum."""

    def test_all_status_values(self):
        """Test all TestStatus values."""
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.SKIPPED.value == "skipped"
        assert TestStatus.FLAKY.value == "flaky"
        assert TestStatus.TIMEOUT.value == "timeout"


class TestVisualDiff:
    """Tests for VisualDiff dataclass."""

    def test_visual_diff_creation(self):
        """Test VisualDiff creation."""
        diff = VisualDiff(
            baseline_path="/baselines/page.png",
            current_path="/screenshots/page.png",
            diff_path="/diffs/page_diff.png",
            pixel_diff_count=150,
            diff_percentage=0.5,
            is_significant=False,
        )

        assert diff.baseline_path == "/baselines/page.png"
        assert diff.pixel_diff_count == 150
        assert diff.diff_percentage == 0.5
        assert diff.is_significant is False

    def test_visual_diff_to_dict(self):
        """Test VisualDiff serialization."""
        diff = VisualDiff(
            baseline_path="/baselines/page.png",
            current_path="/screenshots/page.png",
            diff_path="/diffs/page_diff.png",
            pixel_diff_count=1000,
            diff_percentage=5.5,
            is_significant=True,
        )

        data = diff.to_dict()

        assert data["baseline_path"] == "/baselines/page.png"
        assert data["pixel_diff_count"] == 1000
        assert data["diff_percentage"] == 5.5
        assert data["is_significant"] is True


class TestE2ETestResult:
    """Tests for E2ETestResult dataclass."""

    def test_e2e_result_creation(self):
        """Test E2ETestResult creation."""
        result = E2ETestResult(
            test_name="test_login",
            status=TestStatus.PASSED,
            duration_ms=1500.0,
            browser="chromium",
            url="http://localhost:3000/login",
        )

        assert result.test_name == "test_login"
        assert result.status == TestStatus.PASSED
        assert result.duration_ms == 1500.0
        assert result.browser == "chromium"

    def test_e2e_result_with_visual_diff(self):
        """Test E2ETestResult with visual diff."""
        visual_diff = VisualDiff(
            baseline_path="/baseline.png",
            current_path="/current.png",
            diff_path="/diff.png",
            pixel_diff_count=100,
            diff_percentage=2.0,
            is_significant=True,
        )

        result = E2ETestResult(
            test_name="test_visual",
            status=TestStatus.FAILED,
            duration_ms=2000.0,
            browser="chromium",
            url="http://localhost:3000/page",
            visual_diff=visual_diff,
        )

        data = result.to_dict()

        assert data["visual_diff"] is not None
        assert data["visual_diff"]["is_significant"] is True

    def test_e2e_result_to_dict(self):
        """Test E2ETestResult serialization."""
        result = E2ETestResult(
            test_name="test_navigation",
            status=TestStatus.PASSED,
            duration_ms=500.0,
            browser="firefox",
            url="http://localhost:3000",
            error_message=None,
            screenshot_path="/screenshots/nav.png",
            accessibility_violations=[{"id": "color-contrast"}],
            console_errors=["Error: undefined"],
            network_errors=["404 /api/missing"],
        )

        data = result.to_dict()

        assert data["test_name"] == "test_navigation"
        assert data["status"] == "passed"
        assert data["accessibility_violations_count"] == 1
        assert data["console_errors_count"] == 1
        assert data["network_errors_count"] == 1
        assert "executed_at" in data


class TestGeneratedE2ETest:
    """Tests for GeneratedE2ETest dataclass."""

    def test_generated_test_creation(self):
        """Test GeneratedE2ETest creation."""
        test = GeneratedE2ETest(
            id="e2e_login_123",
            name="test_login_flow",
            description="Test user login flow",
            test_code="test code here",
            target_url="http://localhost:3000/login",
            user_flow=["click login", "enter email", "submit"],
            assertions=["user redirected to dashboard"],
            selectors={"email": "[data-testid='email']"},
        )

        assert test.id == "e2e_login_123"
        assert test.name == "test_login_flow"
        assert len(test.user_flow) == 3

    def test_generated_test_to_dict(self):
        """Test GeneratedE2ETest serialization."""
        test = GeneratedE2ETest(
            id="e2e_test",
            name="test_flow",
            description="Description",
            test_code="code",
            target_url="http://localhost:3000",
            user_flow=["step1", "step2"],
            assertions=["assert1"],
            selectors={"btn": "#button"},
        )

        data = test.to_dict()

        assert data["id"] == "e2e_test"
        assert data["name"] == "test_flow"
        assert "generated_at" in data
        assert "test_code" not in data  # Code not in to_dict


class TestFrontendTesterAgent:
    """Tests for FrontendTesterAgent class."""

    def test_agent_initialization(self, frontend_tester_agent):
        """Test agent initialization."""
        assert frontend_tester_agent.name == "FrontendTester"
        assert frontend_tester_agent.role == "E2E & Visual Testing Specialist"
        assert "e2e_test_generation" in frontend_tester_agent.identity.capabilities
        assert frontend_tester_agent._base_url == "http://localhost:3000"

    @pytest.mark.asyncio
    async def test_execute_task_generate_e2e_tests(self, frontend_tester_agent):
        """Test executing generate_e2e_tests task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_123",
            task_type="generate_e2e_tests",
            description="Generate E2E tests",
            context={
                "page_path": "/login",
                "user_flow": ["enter email", "enter password", "click submit"],
                "page_description": "Login page",
                "generate_assertions": True,
            },
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.task_id == "task_123"
        assert result.status.value == "completed"
        assert "tests_generated" in result.output

    @pytest.mark.asyncio
    async def test_execute_task_run_e2e_tests(self, frontend_tester_agent):
        """Test executing run_e2e_tests task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_run",
            task_type="run_e2e_tests",
            description="Run E2E tests",
            context={},
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.task_id == "task_run"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_visual_regression(self, frontend_tester_agent):
        """Test executing visual_regression task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_visual",
            task_type="visual_regression",
            description="Visual regression test",
            context={
                "page_path": "/home",
                "threshold": 0.1,
            },
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.task_id == "task_visual"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_accessibility_audit(self, frontend_tester_agent):
        """Test executing accessibility_audit task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_a11y",
            task_type="accessibility_audit",
            description="Accessibility audit",
            context={
                "page_path": "/dashboard",
            },
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.task_id == "task_a11y"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_cross_browser_test(self, frontend_tester_agent):
        """Test executing cross_browser_test task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_cross",
            task_type="cross_browser_test",
            description="Cross browser test",
            context={
                "browsers": ["chromium", "firefox"],
            },
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.task_id == "task_cross"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_unknown_type(self, frontend_tester_agent):
        """Test executing unknown task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_unknown",
            task_type="unknown_type",
            description="Unknown",
            context={},
        )

        result = await frontend_tester_agent.execute_task(task)

        assert result.status.value == "failed"
        assert "Unknown task type" in result.error

    @pytest.mark.asyncio
    async def test_generate_e2e_tests_from_flow(self, frontend_tester_agent):
        """Test generating E2E tests from user flow."""
        tests = await frontend_tester_agent.generate_e2e_tests_from_flow(
            page_path="/login",
            user_flow=["click login button", "enter credentials", "submit form"],
            page_description="User login page",
            generate_assertions=True,
        )

        assert len(tests) == 1
        assert tests[0].target_url == "http://localhost:3000/login"
        assert len(tests[0].user_flow) == 3

    @pytest.mark.asyncio
    async def test_generate_e2e_tests_llm_error(self, frontend_tester_agent):
        """Test generate_e2e_tests when LLM fails."""
        frontend_tester_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        tests = await frontend_tester_agent.generate_e2e_tests_from_flow(
            page_path="/test",
            user_flow=["step1"],
        )

        assert tests == []

    @pytest.mark.asyncio
    async def test_generate_tests_from_component(self, frontend_tester_agent):
        """Test generating tests from React component."""
        tests = await frontend_tester_agent.generate_tests_from_component(
            component_name="Button",
            component_props={"label": "string", "onClick": "function"},
            component_usage_examples=["<Button label='Click me' />"],
        )

        assert len(tests) == 1
        assert tests[0].name == "test_Button"

    @pytest.mark.asyncio
    async def test_generate_tests_from_component_error(self, frontend_tester_agent):
        """Test generate_tests_from_component when LLM fails."""
        frontend_tester_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        tests = await frontend_tester_agent.generate_tests_from_component(
            component_name="Button",
            component_props={},
            component_usage_examples=[],
        )

        assert tests == []

    @pytest.mark.asyncio
    async def test_run_visual_regression_no_playwright(self, frontend_tester_agent):
        """Test visual regression when Playwright not available."""
        frontend_tester_agent._playwright_available = False

        results = await frontend_tester_agent.run_visual_regression_test(
            page_path="/home",
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_run_accessibility_audit_no_playwright(self, frontend_tester_agent):
        """Test accessibility audit when Playwright not available."""
        frontend_tester_agent._playwright_available = False

        result = await frontend_tester_agent.run_accessibility_audit(
            page_path="/home",
        )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_heal_selector(self, frontend_tester_agent):
        """Test healing a broken selector."""
        frontend_tester_agent._llm.generate = AsyncMock(
            return_value='[data-testid="new-selector"]'
        )

        new_selector = await frontend_tester_agent.heal_selector(
            broken_selector="#old-id",
            page_content="<div data-testid='new-selector'>Content</div>",
            element_description="Submit button",
        )

        assert new_selector is not None
        assert "new-selector" in new_selector

    @pytest.mark.asyncio
    async def test_heal_selector_from_cache(self, frontend_tester_agent):
        """Test healing selector returns cached result."""
        frontend_tester_agent._selector_healing_cache["#cached"] = "[data-testid='cached']"

        new_selector = await frontend_tester_agent.heal_selector(
            broken_selector="#cached",
            page_content="<div>content</div>",
            element_description="Element",
        )

        assert new_selector == "[data-testid='cached']"

    @pytest.mark.asyncio
    async def test_heal_selector_error(self, frontend_tester_agent):
        """Test heal_selector when LLM fails."""
        frontend_tester_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        new_selector = await frontend_tester_agent.heal_selector(
            broken_selector="#broken",
            page_content="<div>content</div>",
            element_description="Element",
        )

        assert new_selector is None

    def test_get_test_statistics_empty(self, frontend_tester_agent):
        """Test getting statistics with no test history."""
        stats = frontend_tester_agent.get_test_statistics()

        assert stats["total_tests"] == 0
        assert stats["passed"] == 0
        assert stats["pass_rate"] == 0

    def test_get_test_statistics_with_history(self, frontend_tester_agent):
        """Test getting statistics with test history."""
        frontend_tester_agent._test_history = [
            E2ETestResult(
                test_name="test1",
                status=TestStatus.PASSED,
                duration_ms=100,
                browser="chromium",
                url="/test1",
            ),
            E2ETestResult(
                test_name="test2",
                status=TestStatus.PASSED,
                duration_ms=200,
                browser="chromium",
                url="/test2",
            ),
            E2ETestResult(
                test_name="test3",
                status=TestStatus.FAILED,
                duration_ms=300,
                browser="firefox",
                url="/test3",
            ),
            E2ETestResult(
                test_name="test4",
                status=TestStatus.FLAKY,
                duration_ms=400,
                browser="webkit",
                url="/test4",
            ),
        ]

        stats = frontend_tester_agent.get_test_statistics()

        assert stats["total_tests"] == 4
        assert stats["passed"] == 2
        assert stats["failed"] == 1
        assert stats["flaky"] == 1
        assert stats["pass_rate"] == 0.5
        assert stats["average_duration_ms"] == 250.0
        assert "chromium" in stats["by_browser"]

    def test_check_playwright_not_installed(self, frontend_tester_agent):
        """Test _check_playwright when not installed."""
        with patch.dict('sys.modules', {'playwright': None}):
            # Create a new agent to trigger the check
            with patch('backend.testing.agents.frontend_tester.LLMFactory.create_llm'):
                FrontendTesterAgent()
                # The check happens during init

    def test_extract_selectors(self, frontend_tester_agent):
        """Test extracting selectors from test code."""
        test_code = """
        await page.locator('[data-testid="submit-btn"]').click();
        await page.getByRole('button', { name: 'Login' }).click();
        await page.locator('[data-testid="email-input"]').fill('test@test.com');
        """

        selectors = frontend_tester_agent._extract_selectors(test_code)

        assert "testid_submit-btn" in selectors
        assert "testid_email-input" in selectors

    @pytest.mark.asyncio
    async def test_compare_screenshots(self, frontend_tester_agent):
        """Test screenshot comparison."""
        diff = await frontend_tester_agent._compare_screenshots(
            baseline_path="/baseline.png",
            current_path="/current.png",
            threshold=0.1,
        )

        assert isinstance(diff, VisualDiff)
        assert diff.baseline_path == "/baseline.png"
        assert diff.current_path == "/current.png"

    def test_group_by_browser(self, frontend_tester_agent):
        """Test grouping results by browser."""
        frontend_tester_agent._test_history = [
            E2ETestResult(
                test_name="test1", status=TestStatus.PASSED,
                duration_ms=100, browser="chromium", url="/t1"
            ),
            E2ETestResult(
                test_name="test2", status=TestStatus.PASSED,
                duration_ms=100, browser="chromium", url="/t2"
            ),
            E2ETestResult(
                test_name="test3", status=TestStatus.PASSED,
                duration_ms=100, browser="firefox", url="/t3"
            ),
        ]

        by_browser = frontend_tester_agent._group_by_browser()

        assert by_browser["chromium"] == 2
        assert by_browser["firefox"] == 1

    @pytest.mark.asyncio
    async def test_execute_task_exception_handling(self, frontend_tester_agent):
        """Test exception handling in execute_task.

        Note: The generate_e2e_tests_from_flow method catches exceptions internally
        and returns an empty list, so the task completes with empty results
        rather than failing.
        """
        from backend.agents.base_agent import Task

        frontend_tester_agent._llm.generate = AsyncMock(side_effect=Exception("Error"))

        task = Task(
            task_id="task_error",
            task_type="generate_e2e_tests",
            description="Will complete with empty results due to internal error handling",
            context={
                "page_path": "/test",
                "user_flow": ["step"],
            },
        )

        result = await frontend_tester_agent.execute_task(task)

        # The exception is caught internally, so task completes with empty results
        assert result.status.value == "completed"
        assert result.output["tests_generated"] == 0
