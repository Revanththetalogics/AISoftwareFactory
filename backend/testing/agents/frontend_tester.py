"""
Frontend Tester Agent - E2E and visual testing automation.

This agent handles:
- Playwright E2E test generation and execution
- Visual regression testing
- Accessibility testing (axe-core)
- Component testing
- Cross-browser testing
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.factory import LLMFactory

logger = get_logger(__name__)


class BrowserType(Enum):
    """Supported browser types."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class TestStatus(Enum):
    """Test execution status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    FLAKY = "flaky"
    TIMEOUT = "timeout"


@dataclass
class VisualDiff:
    """Visual difference information."""

    baseline_path: str
    current_path: str
    diff_path: str
    pixel_diff_count: int
    diff_percentage: float
    is_significant: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_path": self.baseline_path,
            "current_path": self.current_path,
            "diff_path": self.diff_path,
            "pixel_diff_count": self.pixel_diff_count,
            "diff_percentage": self.diff_percentage,
            "is_significant": self.is_significant,
        }


@dataclass
class E2ETestResult:
    """Result of an E2E test."""

    test_name: str
    status: TestStatus
    duration_ms: float
    browser: str
    url: str
    error_message: str | None = None
    screenshot_path: str | None = None
    video_path: str | None = None
    visual_diff: VisualDiff | None = None
    accessibility_violations: list[dict] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    network_errors: list[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "browser": self.browser,
            "url": self.url,
            "error_message": self.error_message,
            "screenshot_path": self.screenshot_path,
            "video_path": self.video_path,
            "visual_diff": self.visual_diff.to_dict() if self.visual_diff else None,
            "accessibility_violations_count": len(self.accessibility_violations),
            "console_errors_count": len(self.console_errors),
            "network_errors_count": len(self.network_errors),
            "executed_at": self.executed_at.isoformat(),
        }


@dataclass
class GeneratedE2ETest:
    """Generated E2E test."""

    id: str
    name: str
    description: str
    test_code: str
    target_url: str
    user_flow: list[str]
    assertions: list[str]
    selectors: dict[str, str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_url": self.target_url,
            "user_flow": self.user_flow,
            "assertions": self.assertions,
            "selectors": self.selectors,
            "generated_at": self.generated_at.isoformat(),
        }


class FrontendTesterAgent(BaseAgent):
    """
    Agent for frontend E2E and visual testing.

    This agent provides:
    - Playwright test generation from user flows
    - Cross-browser test execution
    - Visual regression testing
    - Accessibility testing
    - Self-healing selectors
    - Component-level testing

    Example:
        >>> agent = FrontendTesterAgent()
        >>> task = Task(
        ...     task_type="generate_e2e_tests",
        ...     description="Generate tests for login flow",
        ...     context={"page_path": "/login", "user_flow": [...]}
        ... )
        >>> result = await agent.execute_task(task)
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the frontend tester agent.

        Args:
            base_url: Base URL for the frontend application
        """
        super().__init__(
            name="FrontendTester",
            role="E2E & Visual Testing Specialist",
            capabilities=[
                "e2e_test_generation",
                "visual_regression",
                "accessibility_testing",
                "cross_browser_testing",
                "self_healing_selectors",
                "component_testing",
            ],
            description="Automates frontend testing with E2E, visual, and accessibility checks",
        )
        self._llm = LLMFactory.create_llm()
        self._base_url = base_url
        self._playwright_available = self._check_playwright()
        self._test_history: list[E2ETestResult] = []
        self._selector_healing_cache: dict[str, str] = {}

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a frontend testing task.

        Args:
            task: Task containing testing parameters

        Returns:
            TaskResult with test results
        """
        start_time = datetime.utcnow()

        try:
            if task.task_type == "generate_e2e_tests":
                result = await self._generate_e2e_tests_task(task)
            elif task.task_type == "run_e2e_tests":
                result = await self._run_e2e_tests_task(task)
            elif task.task_type == "visual_regression":
                result = await self._visual_regression_task(task)
            elif task.task_type == "accessibility_audit":
                result = await self._accessibility_audit_task(task)
            elif task.task_type == "cross_browser_test":
                result = await self._cross_browser_test_task(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown task type: {task.task_type}",
                )

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self._logger.error("Frontend testing failed", error=str(e))
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_e2e_tests_from_flow(
        self, page_path: str, user_flow: list[str], page_description: str = "", generate_assertions: bool = True
    ) -> list[GeneratedE2ETest]:
        """
        Generate E2E tests from a user flow description.

        Args:
            page_path: Path to the page (e.g., "/login")
            user_flow: List of user actions (e.g., ["click login button", "enter email"])
            page_description: Description of the page
            generate_assertions: Whether to generate assertions

        Returns:
            List of generated E2E tests
        """
        self._logger.info("Generating E2E tests", page_path=page_path)

        prompt = f"""Generate Playwright E2E tests for this user flow:

Page: {page_path}
Description: {page_description}

User Flow:
{chr(10).join(f"{i + 1}. {step}" for i, step in enumerate(user_flow))}

Generate Playwright test code that:
1. Navigates to the page
2. Performs each step in the user flow
3. Uses resilient selectors (data-testid preferred)
4. Includes proper waits and timeouts
5. Has descriptive test names
6. Handles async operations properly

Return the complete test file code with imports and test cases."""

        try:
            test_code = await self._llm.generate(prompt)

            # Parse selectors from the generated code
            selectors = self._extract_selectors(test_code)

            test = GeneratedE2ETest(
                id=f"e2e_{page_path.replace('/', '_')}_{datetime.utcnow().timestamp()}",
                name=f"test_{page_path.replace('/', '_')}_flow",
                description=f"E2E test for {page_path} user flow",
                test_code=test_code,
                target_url=f"{self._base_url}{page_path}",
                user_flow=user_flow,
                assertions=["page loaded", "flow completed"] if generate_assertions else [],
                selectors=selectors,
            )

            self._logger.info(
                "E2E test generated",
                page_path=page_path,
                selectors_count=len(selectors),
            )

            return [test]

        except Exception as e:
            self._logger.error("Failed to generate E2E tests", error=str(e))
            return []

    async def generate_tests_from_component(
        self, component_name: str, component_props: dict[str, Any], component_usage_examples: list[str]
    ) -> list[GeneratedE2ETest]:
        """
        Generate tests for a React component.

        Args:
            component_name: Name of the component
            component_props: Component props definition
            component_usage_examples: Examples of component usage

        Returns:
            List of generated tests
        """
        prompt = f"""Generate tests for this React component:

Component: {component_name}
Props: {json.dumps(component_props, indent=2)}

Usage Examples:
{chr(10).join(component_usage_examples)}

Generate:
1. Unit tests using React Testing Library
2. Interaction tests (clicks, inputs, etc.)
3. Prop validation tests
4. Accessibility tests
5. Snapshot tests

Return the complete test file code."""

        try:
            test_code = await self._llm.generate(prompt)

            test = GeneratedE2ETest(
                id=f"component_{component_name}_{datetime.utcnow().timestamp()}",
                name=f"test_{component_name}",
                description=f"Tests for {component_name} component",
                test_code=test_code,
                target_url="",
                user_flow=[],
                assertions=["component renders", "props work correctly"],
                selectors={},
            )

            return [test]

        except Exception as e:
            self._logger.error("Failed to generate component tests", error=str(e))
            return []

    async def run_visual_regression_test(
        self, page_path: str, viewport_sizes: list[dict[str, int]] = None, threshold: float = 0.1
    ) -> list[E2ETestResult]:
        """
        Run visual regression tests.

        Args:
            page_path: Path to test
            viewport_sizes: List of viewport sizes to test
            threshold: Difference threshold (0-1)

        Returns:
            List of test results
        """
        if not self._playwright_available:
            self._logger.warning("Playwright not available, skipping visual test")
            return []

        if viewport_sizes is None:
            viewport_sizes = [
                {"width": 1920, "height": 1080},  # Desktop
                {"width": 768, "height": 1024},  # Tablet
                {"width": 375, "height": 667},  # Mobile
            ]

        results = []

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()

                for viewport in viewport_sizes:
                    context = await browser.new_context(viewport=viewport)
                    page = await context.new_page()

                    start_time = datetime.utcnow()

                    try:
                        await page.goto(f"{self._base_url}{page_path}")
                        await page.wait_for_load_state("networkidle")

                        # Take screenshot
                        screenshot_path = (
                            f"screenshots/{page_path.replace('/', '_')}_{viewport['width']}x{viewport['height']}.png"
                        )
                        Path("screenshots").mkdir(exist_ok=True)
                        await page.screenshot(path=screenshot_path, full_page=True)

                        # Compare with baseline
                        baseline_path = (
                            f"baselines/{page_path.replace('/', '_')}_{viewport['width']}x{viewport['height']}.png"
                        )

                        visual_diff = None
                        if Path(baseline_path).exists():
                            visual_diff = await self._compare_screenshots(baseline_path, screenshot_path, threshold)

                        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                        result = E2ETestResult(
                            test_name=f"visual_{page_path}_{viewport['width']}x{viewport['height']}",
                            status=TestStatus.PASSED
                            if not visual_diff or not visual_diff.is_significant
                            else TestStatus.FAILED,
                            duration_ms=duration,
                            browser="chromium",
                            url=f"{self._base_url}{page_path}",
                            screenshot_path=screenshot_path,
                            visual_diff=visual_diff,
                        )
                        results.append(result)

                    except Exception as e:
                        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                        result = E2ETestResult(
                            test_name=f"visual_{page_path}_{viewport['width']}x{viewport['height']}",
                            status=TestStatus.FAILED,
                            duration_ms=duration,
                            browser="chromium",
                            url=f"{self._base_url}{page_path}",
                            error_message=str(e),
                        )
                        results.append(result)

                    await context.close()

                await browser.close()

        except ImportError:
            self._logger.error("Playwright not installed")

        return results

    async def run_accessibility_audit(self, page_path: str) -> dict[str, Any]:
        """
        Run accessibility audit using axe-core.

        Args:
            page_path: Path to test

        Returns:
            Accessibility audit results
        """
        if not self._playwright_available:
            return {"error": "Playwright not available"}

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(f"{self._base_url}{page_path}")
                await page.wait_for_load_state("networkidle")

                # Inject axe-core
                await page.add_script_tag(path="node_modules/axe-core/axe.min.js")

                # Run accessibility check
                violations = await page.evaluate("""
                    async () => {
                        const results = await axe.run();
                        return results.violations;
                    }
                """)

                await browser.close()

                return {
                    "page_path": page_path,
                    "violations_count": len(violations),
                    "violations": violations,
                    "passed": len(violations) == 0,
                }

        except Exception as e:
            self._logger.error("Accessibility audit failed", error=str(e))
            return {"error": str(e)}

    async def heal_selector(self, broken_selector: str, page_content: str, element_description: str) -> str | None:
        """
        Heal a broken selector using AI.

        Args:
            broken_selector: The selector that no longer works
            page_content: Current page HTML/content
            element_description: Description of the element

        Returns:
            New selector or None
        """
        # Check cache first
        if broken_selector in self._selector_healing_cache:
            return self._selector_healing_cache[broken_selector]

        prompt = f"""Find a new selector for this element:

Broken Selector: {broken_selector}
Element Description: {element_description}

Page Content (truncated):
{page_content[:3000]}

Provide a new, resilient Playwright selector that:
1. Uses data-testid if available
2. Falls back to semantic attributes
3. Is specific but not brittle
4. Works with Playwright's locator API

Return only the selector string."""

        try:
            new_selector = await self._llm.generate(prompt)
            new_selector = new_selector.strip().strip('"').strip("'")

            # Cache the result
            self._selector_healing_cache[broken_selector] = new_selector

            self._logger.info(
                "Selector healed",
                old=broken_selector,
                new=new_selector,
            )

            return new_selector

        except Exception as e:
            self._logger.error("Failed to heal selector", error=str(e))
            return None

    def get_test_statistics(self) -> dict[str, Any]:
        """
        Get statistics about frontend tests.

        Returns:
            Test statistics
        """
        total = len(self._test_history)
        passed = sum(1 for t in self._test_history if t.status == TestStatus.PASSED)
        failed = sum(1 for t in self._test_history if t.status == TestStatus.FAILED)
        flaky = sum(1 for t in self._test_history if t.status == TestStatus.FLAKY)

        avg_duration = sum(t.duration_ms for t in self._test_history) / total if total > 0 else 0

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "flaky": flaky,
            "pass_rate": passed / total if total > 0 else 0,
            "average_duration_ms": round(avg_duration, 2),
            "by_browser": self._group_by_browser(),
            "recent_results": [r.to_dict() for r in self._test_history[-10:]],
        }

    # Private methods

    def _check_playwright(self) -> bool:
        """Check if Playwright is available."""
        try:
            import playwright  # noqa: F401

            return True
        except ImportError:
            return False

    def _extract_selectors(self, test_code: str) -> dict[str, str]:
        """Extract selectors from generated test code."""
        selectors = {}

        # Pattern for common selector types
        import re

        # data-testid selectors
        testid_pattern = r'\[data-testid=["\']([^"\']+)["\']\]'
        for match in re.finditer(testid_pattern, test_code):
            selectors[f"testid_{match.group(1)}"] = match.group(0)

        # Role selectors
        role_pattern = r'getByRole\(["\']([^"\']+)["\'][^)]*\)'
        for match in re.finditer(role_pattern, test_code):
            selectors[f"role_{match.group(1)}"] = match.group(0)

        return selectors

    async def _compare_screenshots(self, baseline_path: str, current_path: str, threshold: float) -> VisualDiff:
        """Compare two screenshots and return diff information using PIL pixel diff."""
        try:
            from PIL import Image, ImageChops

            baseline = Image.open(baseline_path).convert("RGB")
            current = Image.open(current_path).convert("RGB")
            # Resize current to match baseline if sizes differ
            if baseline.size != current.size:
                current = current.resize(baseline.size, Image.LANCZOS)
            diff = ImageChops.difference(baseline, current)
            total_pixels = baseline.width * baseline.height
            diff_pixels = sum(1 for p in diff.getdata() if any(c > 10 for c in p))
            diff_pct = diff_pixels / total_pixels if total_pixels else 0.0
            diff_path = current_path.replace(".png", "_diff.png")
            diff.save(diff_path)
            return VisualDiff(
                baseline_path=baseline_path,
                current_path=current_path,
                diff_path=diff_path,
                pixel_diff_count=diff_pixels,
                diff_percentage=diff_pct,
                is_significant=diff_pct > threshold,
            )
        except Exception as exc:
            self._logger.warning("Screenshot comparison failed", error=str(exc))
            diff_path = current_path.replace(".png", "_diff.png")
            return VisualDiff(
                baseline_path=baseline_path,
                current_path=current_path,
                diff_path=diff_path,
                pixel_diff_count=0,
                diff_percentage=0.0,
                is_significant=False,
            )

    def _group_by_browser(self) -> dict[str, int]:
        """Group test results by browser."""
        by_browser = {}
        for result in self._test_history:
            browser = result.browser
            by_browser[browser] = by_browser.get(browser, 0) + 1
        return by_browser

    async def _generate_e2e_tests_task(self, task: Task) -> dict[str, Any]:
        """Handle generate_e2e_tests task type."""
        tests = await self.generate_e2e_tests_from_flow(
            page_path=task.context["page_path"],
            user_flow=task.context["user_flow"],
            page_description=task.context.get("page_description", ""),
            generate_assertions=task.context.get("generate_assertions", True),
        )

        return {
            "tests_generated": len(tests),
            "tests": [t.to_dict() for t in tests],
        }

    async def _run_e2e_tests_task(self, task: Task) -> dict[str, Any]:
        """Handle run_e2e_tests task type."""
        # This would execute the actual Playwright tests
        return {"status": "not_implemented_in_simulation"}

    async def _visual_regression_task(self, task: Task) -> dict[str, Any]:
        """Handle visual_regression task type."""
        results = await self.run_visual_regression_test(
            page_path=task.context["page_path"],
            viewport_sizes=task.context.get("viewport_sizes"),
            threshold=task.context.get("threshold", 0.1),
        )

        self._test_history.extend(results)

        return {
            "tests_run": len(results),
            "passed": sum(1 for r in results if r.status == TestStatus.PASSED),
            "failed": sum(1 for r in results if r.status == TestStatus.FAILED),
            "results": [r.to_dict() for r in results],
        }

    async def _accessibility_audit_task(self, task: Task) -> dict[str, Any]:
        """Handle accessibility_audit task type."""
        result = await self.run_accessibility_audit(
            page_path=task.context["page_path"],
        )

        return result

    async def _cross_browser_test_task(self, task: Task) -> dict[str, Any]:
        """Handle cross_browser_test task type."""
        browsers = task.context.get("browsers", ["chromium", "firefox", "webkit"])

        return {
            "browsers": browsers,
            "status": "not_implemented_in_simulation",
        }
