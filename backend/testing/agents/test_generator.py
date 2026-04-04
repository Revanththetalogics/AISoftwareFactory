"""
Test Generator Agent - AI-powered test case generation.

This agent uses LLM and code analysis to generate comprehensive test cases
for Python backend code and TypeScript/React frontend code.
"""

import ast
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.factory import LLMFactory

logger = get_logger(__name__)


@dataclass
class CodeComponent:
    """Represents a testable code component."""

    name: str
    component_type: str  # function, class, method
    file_path: str
    line_start: int
    line_end: int
    signature: str
    docstring: str = ""
    complexity: int = 1
    dependencies: list[str] = field(default_factory=list)
    is_async: bool = False
    is_private: bool = False


@dataclass
class GeneratedTest:
    """Represents a generated test case."""

    id: str
    name: str
    component_name: str
    test_code: str
    test_type: str  # unit, integration, edge_case, error
    description: str
    fixtures: list[str] = field(default_factory=list)
    mocks: list[str] = field(default_factory=list)
    assertions_count: int = 0
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "component_name": self.component_name,
            "test_type": self.test_type,
            "description": self.description,
            "fixtures": self.fixtures,
            "mocks": self.mocks,
            "assertions_count": self.assertions_count,
            "generated_at": self.generated_at.isoformat(),
        }


class TestGeneratorAgent(BaseAgent):
    """
    Agent for generating test cases using AI.

    This agent analyzes code structure and generates comprehensive tests:
    - Unit tests for functions and methods
    - Edge case tests
    - Error handling tests
    - Integration test scenarios
    - Property-based tests (Hypothesis)

    Example:
        >>> agent = TestGeneratorAgent()
        >>> task = Task(
        ...     task_type="generate_tests",
        ...     description="Generate tests for auth service",
        ...     context={"file_path": "backend/services/auth.py"}
        ... )
        >>> result = await agent.execute_task(task)
    """

    def __init__(self):
        """Initialize the test generator agent."""
        super().__init__(
            name="TestGenerator",
            role="QA Engineer",
            capabilities=[
                "test_generation",
                "code_analysis",
                "edge_case_identification",
                "mock_creation",
                "fixture_generation",
            ],
            description="Generates comprehensive test cases using AI analysis",
        )
        self._llm = LLMFactory.create_llm()
        self._prompts = self._load_prompts()

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a test generation task.

        Args:
            task: Task containing generation parameters

        Returns:
            TaskResult with generated tests
        """
        start_time = datetime.now(UTC)

        try:
            if task.task_type == "generate_tests":
                result = await self._generate_tests_task(task)
            elif task.task_type == "generate_regression_test":
                result = await self._generate_regression_test_task(task)
            elif task.task_type == "generate_integration_tests":
                result = await self._generate_integration_tests_task(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown task type: {task.task_type}",
                )

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            self._logger.error("Test generation failed", error=str(e))
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def generate_tests_for_file(
        self,
        file_path: str,
        include_edge_cases: bool = True,
        include_error_cases: bool = True,
        include_property_tests: bool = False,
    ) -> list[GeneratedTest]:
        """
        Generate comprehensive tests for a file.

        Args:
            file_path: Path to the source file
            include_edge_cases: Include edge case tests
            include_error_cases: Include error handling tests
            include_property_tests: Include property-based tests

        Returns:
            List of generated tests
        """
        self._logger.info("Generating tests", file_path=file_path)

        # Parse code to find components
        components = await self._analyze_file(file_path)

        all_tests = []

        for component in components:
            # Skip private methods (usually)
            if component.is_private and not component.name.startswith("__"):
                continue

            # Generate unit tests
            unit_tests = await self._generate_unit_tests(component, file_path)
            all_tests.extend(unit_tests)

            # Generate edge case tests
            if include_edge_cases:
                edge_tests = await self._generate_edge_case_tests(component, file_path)
                all_tests.extend(edge_tests)

            # Generate error case tests
            if include_error_cases:
                error_tests = await self._generate_error_tests(component, file_path)
                all_tests.extend(error_tests)

        self._logger.info(
            "Test generation complete",
            file_path=file_path,
            test_count=len(all_tests),
        )

        return all_tests

    async def generate_test_from_error(
        self, error_message: str, stack_trace: str, code_snippet: str, file_path: str
    ) -> GeneratedTest | None:
        """
        Generate a regression test from an error.

        Args:
            error_message: The error that occurred
            stack_trace: Stack trace
            code_snippet: Code where error occurred
            file_path: File path

        Returns:
            Generated regression test
        """
        prompt = f"""Generate a regression test for this error:

Error Message:
{error_message}

Stack Trace:
{stack_trace}

Code:
```python
{code_snippet}
```

Create a pytest test that:
1. Reproduces this exact error
2. Verifies the expected behavior
3. Includes proper setup and teardown

Return only the test code."""

        try:
            test_code = await self._llm.generate(prompt)

            return GeneratedTest(
                id=f"regression_{datetime.now(UTC).timestamp()}",
                name=f"test_regression_{self._sanitize_name(error_message[:30])}",
                component_name=file_path,
                test_code=test_code,
                test_type="regression",
                description=f"Regression test for: {error_message[:100]}",
            )

        except Exception as e:
            self._logger.error("Failed to generate regression test", error=str(e))
            return None

    async def suggest_test_improvements(self, existing_test_code: str, source_code: str) -> list[dict[str, Any]]:
        """
        Suggest improvements for existing tests.

        Args:
            existing_test_code: Current test code
            source_code: Source code being tested

        Returns:
            List of improvement suggestions
        """
        prompt = f"""Analyze these tests and suggest improvements:

Source Code:
```python
{source_code}
```

Existing Tests:
```python
{existing_test_code}
```

Identify:
1. Missing test cases
2. Weak assertions
3. Missing edge cases
4. Opportunities for parameterized tests
5. Missing error handling tests

Return as JSON array of suggestions."""

        try:
            response = await self._llm.generate(prompt)
            import json

            suggestions = json.loads(response)
            return suggestions
        except Exception as e:
            self._logger.error("Failed to analyze tests", error=str(e))
            return []

    # Private methods

    def _load_prompts(self) -> dict[str, str]:
        """Load prompt templates."""
        return {
            "unit_test": """Generate pytest unit tests for this {component_type}:

Name: {name}
Signature: {signature}
File: {file_path}

Code:
```python
{code}
```

Requirements:
1. Use pytest fixtures for dependencies
2. Mock external calls
3. Test happy path and common scenarios
4. Use descriptive test names
5. Include type hints in tests

Generate the complete test code:""",
            "edge_case": """Generate edge case tests for this {component_type}:

Name: {name}
Signature: {signature}

Consider:
- Empty inputs
- Null/None values
- Boundary values
- Maximum/minimum values
- Unicode/special characters
- Very large inputs

Generate pytest tests for these edge cases:""",
            "error_case": """Generate error handling tests for this {component_type}:

Name: {name}
Signature: {signature}
Code:
```python
{code}
```

Identify potential exceptions and error conditions:
1. Invalid input types
2. Missing required parameters
3. Resource not found scenarios
4. Permission/authentication errors
5. External service failures

Generate pytest tests using pytest.raises():""",
        }

    async def _analyze_file(self, file_path: str) -> list[CodeComponent]:
        """Analyze a file to extract testable components."""
        try:
            with open(file_path) as f:
                code = f.read()

            tree = ast.parse(code)
            components = []
            code.splitlines()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Calculate complexity
                    complexity = self._calculate_complexity(node)

                    # Get dependencies
                    dependencies = self._extract_dependencies(node)

                    component = CodeComponent(
                        name=node.name,
                        component_type="function",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        signature=self._get_signature(node),
                        docstring=ast.get_docstring(node) or "",
                        complexity=complexity,
                        dependencies=dependencies,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                        is_private=node.name.startswith("_"),
                    )
                    components.append(component)

                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            complexity = self._calculate_complexity(item)
                            dependencies = self._extract_dependencies(item)

                            component = CodeComponent(
                                name=f"{node.name}.{item.name}",
                                component_type="method",
                                file_path=file_path,
                                line_start=item.lineno,
                                line_end=item.end_lineno,
                                signature=self._get_signature(item),
                                docstring=ast.get_docstring(item) or "",
                                complexity=complexity,
                                dependencies=dependencies,
                                is_async=isinstance(item, ast.AsyncFunctionDef),
                                is_private=item.name.startswith("_"),
                            )
                            components.append(component)

            return components

        except Exception as e:
            self._logger.error("Failed to analyze file", file_path=file_path, error=str(e))
            return []

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _extract_dependencies(self, node: ast.AST) -> list[str]:
        """Extract external dependencies from a function."""
        dependencies = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(child.func.attr)
        return dependencies

    def _get_signature(self, node: ast.FunctionDef) -> str:
        """Get function signature as string."""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        returns = ""
        if node.returns:
            returns = f" -> {ast.unparse(node.returns)}"

        return f"({', '.join(args)}){returns}"

    async def _generate_unit_tests(self, component: CodeComponent, file_path: str) -> list[GeneratedTest]:
        """Generate unit tests for a component."""
        # Read the full code
        with open(file_path) as f:
            code = f.read()

        prompt = self._prompts["unit_test"].format(
            component_type=component.component_type,
            name=component.name,
            signature=component.signature,
            file_path=file_path,
            code=code,
        )

        try:
            test_code = await self._llm.generate(prompt)

            test = GeneratedTest(
                id=f"unit_{component.name}_{datetime.now(UTC).timestamp()}",
                name=f"test_{self._sanitize_name(component.name)}",
                component_name=component.name,
                test_code=test_code,
                test_type="unit",
                description=f"Unit tests for {component.name}",
                assertions_count=test_code.count("assert"),
            )

            return [test]

        except Exception as e:
            self._logger.error(
                "Failed to generate unit tests",
                component=component.name,
                error=str(e),
            )
            return []

    async def _generate_edge_case_tests(self, component: CodeComponent, file_path: str) -> list[GeneratedTest]:
        """Generate edge case tests."""
        prompt = self._prompts["edge_case"].format(
            component_type=component.component_type,
            name=component.name,
            signature=component.signature,
        )

        try:
            test_code = await self._llm.generate(prompt)

            test = GeneratedTest(
                id=f"edge_{component.name}_{datetime.now(UTC).timestamp()}",
                name=f"test_{self._sanitize_name(component.name)}_edge_cases",
                component_name=component.name,
                test_code=test_code,
                test_type="edge_case",
                description=f"Edge case tests for {component.name}",
            )

            return [test]

        except Exception as e:
            self._logger.error(
                "Failed to generate edge case tests",
                component=component.name,
                error=str(e),
            )
            return []

    async def _generate_error_tests(self, component: CodeComponent, file_path: str) -> list[GeneratedTest]:
        """Generate error handling tests."""
        with open(file_path) as f:
            code = f.read()

        prompt = self._prompts["error_case"].format(
            component_type=component.component_type,
            name=component.name,
            signature=component.signature,
            code=code,
        )

        try:
            test_code = await self._llm.generate(prompt)

            test = GeneratedTest(
                id=f"error_{component.name}_{datetime.now(UTC).timestamp()}",
                name=f"test_{self._sanitize_name(component.name)}_errors",
                component_name=component.name,
                test_code=test_code,
                test_type="error",
                description=f"Error handling tests for {component.name}",
            )

            return [test]

        except Exception as e:
            self._logger.error(
                "Failed to generate error tests",
                component=component.name,
                error=str(e),
            )
            return []

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use in test function names."""
        return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    async def _generate_tests_task(self, task: Task) -> dict[str, Any]:
        """Handle generate_tests task type."""
        file_path = task.context.get("file_path")
        if not file_path:
            raise ValueError("file_path required in context")

        tests = await self.generate_tests_for_file(
            file_path,
            include_edge_cases=task.context.get("include_edge_cases", True),
            include_error_cases=task.context.get("include_error_cases", True),
        )

        return {
            "file_path": file_path,
            "tests_generated": len(tests),
            "tests": [t.to_dict() for t in tests],
        }

    async def _generate_regression_test_task(self, task: Task) -> dict[str, Any]:
        """Handle generate_regression_test task type."""
        test = await self.generate_test_from_error(
            error_message=task.context["error_message"],
            stack_trace=task.context["stack_trace"],
            code_snippet=task.context["code_snippet"],
            file_path=task.context["file_path"],
        )

        return {
            "test": test.to_dict() if test else None,
        }

    async def _generate_integration_tests_task(self, task: Task) -> dict[str, Any]:
        """Handle generate_integration_tests task type."""
        # Integration test generation logic
        return {"status": "not_implemented"}
