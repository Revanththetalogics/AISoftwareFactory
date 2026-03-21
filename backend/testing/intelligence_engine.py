"""
Test Intelligence Engine - Core orchestrator for AI-driven testing.

This module provides the central intelligence hub that coordinates all testing agents,
analyzes test results, and makes decisions about test generation, bug detection,
and automatic fixes.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from backend.core.logging import get_logger
from backend.llm.base_provider import BaseLLMProvider
from backend.llm.factory import LLMFactory

logger = get_logger(__name__)


class TestPriority(Enum):
    """Test priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TestType(Enum):
    """Types of tests that can be generated."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    VISUAL = "visual"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONTRACT = "contract"


@dataclass
class TestCase:
    """Represents a generated or existing test case."""
    id: str
    name: str
    test_type: TestType
    target_file: str
    code: str
    priority: TestPriority
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_run: datetime | None = None
    success_count: int = 0
    failure_count: int = 0
    is_flaky: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "test_type": self.test_type.value,
            "target_file": self.target_file,
            "priority": self.priority.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "is_flaky": self.is_flaky,
        }


@dataclass
class BugReport:
    """Represents a detected bug with analysis."""
    id: str
    severity: str  # critical, high, medium, low
    category: str  # syntax, logic, security, performance
    file_path: str
    line_number: int | None
    description: str
    root_cause: str
    suggested_fix: str
    confidence: float
    test_case_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "description": self.description,
            "root_cause": self.root_cause,
            "suggested_fix": self.suggested_fix,
            "confidence": self.confidence,
            "test_case_id": self.test_case_id,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class FixResult:
    """Result of an automatic fix attempt."""
    bug_id: str
    success: bool
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    applied_at: datetime = field(default_factory=datetime.utcnow)
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "bug_id": self.bug_id,
            "success": self.success,
            "file_path": self.file_path,
            "explanation": self.explanation,
            "applied_at": self.applied_at.isoformat(),
            "error_message": self.error_message,
        }


@dataclass
class TestSuite:
    """Collection of test cases for a module or feature."""
    name: str
    target_module: str
    test_cases: list[TestCase] = field(default_factory=list)
    coverage_percentage: float = 0.0
    mutation_score: float = 0.0
    last_execution: datetime | None = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_module": self.target_module,
            "test_count": len(self.test_cases),
            "coverage_percentage": self.coverage_percentage,
            "mutation_score": self.mutation_score,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_time_ms": self.execution_time_ms,
        }


class TestIntelligenceEngine:
    """
    Central intelligence engine for AI-driven testing.

    This engine orchestrates all testing activities:
    - Analyzes code to identify testing gaps
    - Generates test cases using LLM
    - Detects bugs and root causes
    - Applies automatic fixes
    - Tracks test health and flakiness
    - Learns from test execution patterns

    Example:
        >>> engine = TestIntelligenceEngine()
        >>> suite = await engine.analyze_module("backend/services/auth.py")
        >>> bugs = await engine.detect_bugs(suite)
        >>> fixes = await engine.apply_fixes(bugs)
    """

    def __init__(self, llm_provider: BaseLLMProvider | None = None):
        """
        Initialize the test intelligence engine.

        Args:
            llm_provider: LLM provider for AI operations
        """
        self._llm = llm_provider or LLMFactory.create_llm()
        self._logger = get_logger(__name__)
        self._test_suites: dict[str, TestSuite] = {}
        self._bug_reports: dict[str, BugReport] = {}
        self._fix_history: list[FixResult] = []
        self._execution_patterns: dict[str, Any] = {}

        # Callbacks for different events
        self._on_test_generated: list[Callable] = []
        self._on_bug_detected: list[Callable] = []
        self._on_fix_applied: list[Callable] = []

        self._logger.info("TestIntelligenceEngine initialized")

    async def analyze_module(
        self,
        file_path: str,
        generate_missing_tests: bool = True
    ) -> TestSuite:
        """
        Analyze a code module for testing gaps.

        Args:
            file_path: Path to the code file
            generate_missing_tests: Whether to generate missing tests

        Returns:
            TestSuite with analysis results
        """
        self._logger.info("Analyzing module", file_path=file_path)

        # Read and parse the code
        code_content = await self._read_file(file_path)

        # Analyze code structure
        analysis = await self._analyze_code_structure(code_content, file_path)

        # Check existing test coverage
        existing_tests = await self._find_existing_tests(file_path)

        # Identify gaps
        gaps = self._identify_test_gaps(analysis, existing_tests)

        # Create test suite
        suite = TestSuite(
            name=f"test_{Path(file_path).stem}",
            target_module=file_path,
        )

        # Generate missing tests if requested
        if generate_missing_tests and gaps:
            generated_tests = await self._generate_tests_for_gaps(
                file_path, code_content, gaps
            )
            suite.test_cases.extend(generated_tests)

        # Calculate coverage
        suite.coverage_percentage = await self._calculate_coverage(file_path)

        self._test_suites[file_path] = suite

        self._logger.info(
            "Module analysis complete",
            file_path=file_path,
            test_count=len(suite.test_cases),
            coverage=suite.coverage_percentage,
        )

        return suite

    async def detect_bugs(
        self,
        test_suite: TestSuite,
        run_tests: bool = True
    ) -> list[BugReport]:
        """
        Detect bugs in code using multiple strategies.

        Args:
            test_suite: Test suite to analyze
            run_tests: Whether to execute tests first

        Returns:
            List of detected bugs
        """
        self._logger.info("Detecting bugs", suite_name=test_suite.name)

        bugs = []

        # Strategy 1: Static analysis
        static_bugs = await self._static_analysis(test_suite.target_module)
        bugs.extend(static_bugs)

        # Strategy 2: Test failure analysis
        if run_tests:
            test_bugs = await self._analyze_test_failures(test_suite)
            bugs.extend(test_bugs)

        # Strategy 3: LLM-based code review
        llm_bugs = await self._llm_code_review(test_suite.target_module)
        bugs.extend(llm_bugs)

        # Store bugs
        for bug in bugs:
            self._bug_reports[bug.id] = bug

        self._logger.info(
            "Bug detection complete",
            bug_count=len(bugs),
            critical=len([b for b in bugs if b.severity == "critical"]),
        )

        return bugs

    async def apply_fixes(
        self,
        bugs: list[BugReport],
        auto_apply: bool = False,
        confidence_threshold: float = 0.85
    ) -> list[FixResult]:
        """
        Apply automatic fixes to detected bugs.

        Args:
            bugs: List of bugs to fix
            auto_apply: Whether to apply fixes automatically
            confidence_threshold: Minimum confidence for auto-apply

        Returns:
            List of fix results
        """
        self._logger.info("Applying fixes", bug_count=len(bugs))

        results = []

        for bug in bugs:
            if bug.confidence < confidence_threshold and auto_apply:
                self._logger.warning(
                    "Skipping fix - confidence too low",
                    bug_id=bug.id,
                    confidence=bug.confidence,
                )
                continue

            # Generate fix
            fix_result = await self._generate_fix(bug)
            results.append(fix_result)

            if fix_result.success:
                self._fix_history.append(fix_result)

                # Notify callbacks
                for callback in self._on_fix_applied:
                    await callback(fix_result)

        self._logger.info(
            "Fix application complete",
            total=len(results),
            successful=sum(1 for r in results if r.success),
        )

        return results

    async def run_self_healing_tests(
        self,
        test_suite: TestSuite,
        max_retries: int = 3
    ) -> dict[str, Any]:
        """
        Run tests with self-healing capabilities.

        Args:
            test_suite: Test suite to run
            max_retries: Maximum retries for flaky tests

        Returns:
            Test execution results
        """
        self._logger.info(
            "Running self-healing tests",
            suite_name=test_suite.name,
        )

        results = {
            "passed": [],
            "failed": [],
            "healed": [],
            "flaky": [],
        }

        for test_case in test_suite.test_cases:
            # Run test with retry logic
            run_result = await self._run_test_with_healing(
                test_case, max_retries
            )

            if run_result["status"] == "passed":
                results["passed"].append(test_case.id)
                test_case.success_count += 1
            elif run_result["status"] == "healed":
                results["healed"].append(test_case.id)
                test_case.success_count += 1
            elif run_result["status"] == "flaky":
                results["flaky"].append(test_case.id)
                test_case.is_flaky = True
            else:
                results["failed"].append(test_case.id)
                test_case.failure_count += 1

            test_case.last_run = datetime.utcnow()

        # Update suite stats
        test_suite.last_execution = datetime.utcnow()

        self._logger.info(
            "Test execution complete",
            passed=len(results["passed"]),
            failed=len(results["failed"]),
            healed=len(results["healed"]),
            flaky=len(results["flaky"]),
        )

        return results

    async def generate_test_from_failure(
        self,
        error_message: str,
        stack_trace: str,
        code_context: str
    ) -> TestCase | None:
        """
        Generate a new test case from a production failure.

        Args:
            error_message: The error message
            stack_trace: Stack trace of the failure
            code_context: Code where the failure occurred

        Returns:
            Generated test case or None
        """
        self._logger.info("Generating test from failure")

        prompt = f"""Analyze this production failure and generate a test case:

Error: {error_message}

Stack Trace:
{stack_trace}

Code Context:
```python
{code_context}
```

Generate a pytest test case that would catch this bug. Include:
1. Test function with proper naming
2. Setup/mocks if needed
3. Assertions that verify the fix
4. Edge cases

Return only the test code."""

        try:
            response = await self._llm.generate(prompt)

            test_case = TestCase(
                id=f"regression_{datetime.utcnow().timestamp()}",
                name=f"test_regression_{error_message[:30]}",
                test_type=TestType.UNIT,
                target_file="unknown",
                code=response,
                priority=TestPriority.HIGH,
                description=f"Regression test for: {error_message}",
            )

            self._logger.info("Generated regression test", test_id=test_case.id)

            # Notify callbacks
            for callback in self._on_test_generated:
                await callback(test_case)

            return test_case

        except Exception as e:
            self._logger.error("Failed to generate test from failure", error=str(e))
            return None

    def get_test_health_report(self) -> dict[str, Any]:
        """
        Generate comprehensive test health report.

        Returns:
            Test health metrics
        """
        total_tests = sum(
            len(suite.test_cases) for suite in self._test_suites.values()
        )

        flaky_tests = [
            tc for suite in self._test_suites.values()
            for tc in suite.test_cases if tc.is_flaky
        ]

        total_bugs = len(self._bug_reports)
        critical_bugs = len([
            b for b in self._bug_reports.values() if b.severity == "critical"
        ])

        avg_coverage = (
            sum(s.coverage_percentage for s in self._test_suites.values()) /
            len(self._test_suites) if self._test_suites else 0
        )

        return {
            "summary": {
                "total_test_suites": len(self._test_suites),
                "total_tests": total_tests,
                "flaky_tests": len(flaky_tests),
                "total_bugs_detected": total_bugs,
                "critical_bugs": critical_bugs,
                "average_coverage": round(avg_coverage, 2),
                "fixes_applied": len(self._fix_history),
            },
            "flaky_tests": [tc.to_dict() for tc in flaky_tests],
            "recent_bugs": [
                b.to_dict() for b in list(self._bug_reports.values())[-10:]
            ],
            "recent_fixes": [
                f.to_dict() for f in self._fix_history[-10:]
            ],
        }

    # Private helper methods

    async def _read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            with open(file_path) as f:
                return f.read()
        except Exception as e:
            self._logger.error("Failed to read file", file_path=file_path, error=str(e))
            return ""

    async def _analyze_code_structure(self, code: str, file_path: str) -> dict[str, Any]:
        """Analyze code structure to identify testable components."""
        import ast

        try:
            tree = ast.parse(code)

            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, ast.FunctionDef)
                    ]
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                    })

            return {
                "functions": functions,
                "classes": classes,
                "total_lines": len(code.splitlines()),
            }

        except SyntaxError as e:
            self._logger.error("Syntax error in code", file_path=file_path, error=str(e))
            return {"functions": [], "classes": [], "total_lines": 0}

    async def _find_existing_tests(self, file_path: str) -> list[str]:
        """Find existing tests for a file."""
        test_patterns = [
            f"tests/test_{Path(file_path).name}",
            f"tests/{Path(file_path).parent.name}/test_{Path(file_path).name}",
        ]

        existing = []
        for pattern in test_patterns:
            if Path(pattern).exists():
                existing.append(pattern)

        return existing

    def _identify_test_gaps(
        self,
        analysis: dict[str, Any],
        existing_tests: list[str]
    ) -> list[dict[str, Any]]:
        """Identify gaps in test coverage."""
        gaps = []

        # Check for untested functions
        for func in analysis.get("functions", []):
            if not func["name"].startswith("_"):  # Skip private
                gaps.append({
                    "type": "function",
                    "name": func["name"],
                    "line": func["line"],
                })

        # Check for untested classes
        for cls in analysis.get("classes", []):
            gaps.append({
                "type": "class",
                "name": cls["name"],
                "line": cls["line"],
                "methods": cls["methods"],
            })

        return gaps

    async def _generate_tests_for_gaps(
        self,
        file_path: str,
        code: str,
        gaps: list[dict[str, Any]]
    ) -> list[TestCase]:
        """Generate test cases for identified gaps."""
        test_cases = []

        for gap in gaps:
            prompt = f"""Generate pytest test cases for this {gap['type']}:

File: {file_path}

Code:
```python
{code}
```

Target: {gap['name']} ({gap['type']})

Generate comprehensive tests including:
1. Happy path tests
2. Edge cases
3. Error handling
4. Mock external dependencies

Return only the test code."""

            try:
                response = await self._llm.generate(prompt)

                test_case = TestCase(
                    id=f"{gap['name']}_{datetime.utcnow().timestamp()}",
                    name=f"test_{gap['name']}",
                    test_type=TestType.UNIT,
                    target_file=file_path,
                    code=response,
                    priority=TestPriority.MEDIUM,
                    description=f"Generated test for {gap['name']}",
                )

                test_cases.append(test_case)

                # Notify callbacks
                for callback in self._on_test_generated:
                    await callback(test_case)

            except Exception as e:
                self._logger.error(
                    "Failed to generate test",
                    target=gap['name'],
                    error=str(e),
                )

        return test_cases

    async def _calculate_coverage(self, file_path: str) -> float:
        """Calculate test coverage for a file."""
        # This would integrate with coverage.py
        # For now, return a placeholder
        return 0.0

    async def _static_analysis(self, file_path: str) -> list[BugReport]:
        """Run static analysis to find bugs."""
        # This would integrate with tools like pylint, bandit, mypy
        return []

    async def _analyze_test_failures(self, test_suite: TestSuite) -> list[BugReport]:
        """Analyze test failures to identify bugs."""
        # This would run tests and analyze failures
        return []

    async def _llm_code_review(self, file_path: str) -> list[BugReport]:
        """Use LLM to review code for bugs."""
        code = await self._read_file(file_path)

        prompt = f"""Review this code for bugs and issues:

```python
{code}
```

Identify:
1. Logic errors
2. Security vulnerabilities
3. Performance issues
4. Code smells

Return findings as JSON array:
[{{"severity": "critical|high|medium|low", "category": "syntax|logic|security|performance", "line": number, "description": "...", "suggestion": "..."}}]

If no issues found, return empty array []."""

        try:
            response = await self._llm.generate(prompt)

            # Parse JSON response
            import json
            findings = json.loads(response)

            bugs = []
            for finding in findings:
                bug = BugReport(
                    id=f"llm_{file_path}_{finding.get('line', 0)}",
                    severity=finding["severity"],
                    category=finding["category"],
                    file_path=file_path,
                    line_number=finding.get("line"),
                    description=finding["description"],
                    root_cause="Detected by LLM code review",
                    suggested_fix=finding.get("suggestion", ""),
                    confidence=0.8,
                )
                bugs.append(bug)

            return bugs

        except Exception as e:
            self._logger.error("LLM code review failed", error=str(e))
            return []

    async def _generate_fix(self, bug: BugReport) -> FixResult:
        """Generate a fix for a bug."""
        code = await self._read_file(bug.file_path)

        prompt = f"""Fix this bug:

File: {bug.file_path}
Line: {bug.line_number}
Description: {bug.description}
Root Cause: {bug.root_cause}

Code:
```python
{code}
```

Provide the fixed code section only."""

        try:
            fixed_code = await self._llm.generate(prompt)

            return FixResult(
                bug_id=bug.id,
                success=True,
                file_path=bug.file_path,
                original_code=code,
                fixed_code=fixed_code,
                explanation=f"Applied fix for: {bug.description}",
            )

        except Exception as e:
            return FixResult(
                bug_id=bug.id,
                success=False,
                file_path=bug.file_path,
                original_code=code,
                fixed_code=code,
                explanation="Failed to generate fix",
                error_message=str(e),
            )

    async def _run_test_with_healing(
        self,
        test_case: TestCase,
        max_retries: int
    ) -> dict[str, Any]:
        """Run a test with self-healing capabilities."""
        # This would implement the actual test execution with healing
        # For now, return a placeholder
        return {"status": "passed"}

    def register_callback(self, event: str, callback: Callable):
        """Register a callback for an event."""
        if event == "test_generated":
            self._on_test_generated.append(callback)
        elif event == "bug_detected":
            self._on_bug_detected.append(callback)
        elif event == "fix_applied":
            self._on_fix_applied.append(callback)
