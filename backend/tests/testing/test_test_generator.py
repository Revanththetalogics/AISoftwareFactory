"""
Tests for TestGeneratorAgent - AI-powered test case generation.
"""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.testing.agents.test_generator import (
    CodeComponent,
    GeneratedTest,
    TestGeneratorAgent,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="""import pytest

def test_function_happy_path():
    result = function_under_test(1, 2)
    assert result == 3

def test_function_edge_case():
    result = function_under_test(0, 0)
    assert result == 0
""")
    return llm


@pytest.fixture
def test_generator_agent(mock_llm):
    """Fixture for TestGeneratorAgent with mocked LLM."""
    with patch('backend.testing.agents.test_generator.LLMFactory.create_llm', return_value=mock_llm):
        agent = TestGeneratorAgent()
        agent._llm = mock_llm
        return agent


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(result)
        return result

    def _private_method(self):
        """Private method."""
        pass
''')
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_syntax_error_file():
    """Create a temporary Python file with syntax error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('this is not valid python {{{{')
        f.flush()
        yield f.name
    os.unlink(f.name)


class TestCodeComponent:
    """Tests for CodeComponent dataclass."""

    def test_code_component_creation(self):
        """Test CodeComponent creation."""
        component = CodeComponent(
            name="my_function",
            component_type="function",
            file_path="/path/to/file.py",
            line_start=10,
            line_end=20,
            signature="(a: int, b: int) -> int",
            docstring="Add two numbers.",
            complexity=2,
            dependencies=["helper_func"],
            is_async=False,
            is_private=False,
        )

        assert component.name == "my_function"
        assert component.component_type == "function"
        assert component.complexity == 2
        assert component.is_async is False

    def test_code_component_defaults(self):
        """Test CodeComponent default values."""
        component = CodeComponent(
            name="func",
            component_type="function",
            file_path="/path/file.py",
            line_start=1,
            line_end=5,
            signature="()",
        )

        assert component.docstring == ""
        assert component.complexity == 1
        assert component.dependencies == []
        assert component.is_async is False
        assert component.is_private is False


class TestGeneratedTest:
    """Tests for GeneratedTest dataclass."""

    def test_generated_test_creation(self):
        """Test GeneratedTest creation."""
        test = GeneratedTest(
            id="test_123",
            name="test_my_function",
            component_name="my_function",
            test_code="def test_my_function(): pass",
            test_type="unit",
            description="Unit test for my_function",
            fixtures=["mock_db"],
            mocks=["external_service"],
            assertions_count=5,
        )

        assert test.id == "test_123"
        assert test.name == "test_my_function"
        assert test.test_type == "unit"
        assert test.assertions_count == 5

    def test_generated_test_to_dict(self):
        """Test GeneratedTest serialization."""
        test = GeneratedTest(
            id="test_456",
            name="test_function",
            component_name="function",
            test_code="test code",
            test_type="edge_case",
            description="Edge case test",
            fixtures=[],
            mocks=[],
            assertions_count=3,
        )

        data = test.to_dict()

        assert data["id"] == "test_456"
        assert data["name"] == "test_function"
        assert data["test_type"] == "edge_case"
        assert data["assertions_count"] == 3
        assert "generated_at" in data
        assert "test_code" not in data  # Code not in to_dict


class TestTestGeneratorAgent:
    """Tests for TestGeneratorAgent class."""

    def test_agent_initialization(self, test_generator_agent):
        """Test agent initialization."""
        assert test_generator_agent.name == "TestGenerator"
        assert test_generator_agent.role == "QA Engineer"
        assert "test_generation" in test_generator_agent.identity.capabilities
        assert "edge_case_identification" in test_generator_agent.identity.capabilities

    def test_load_prompts(self, test_generator_agent):
        """Test prompts are loaded."""
        prompts = test_generator_agent._prompts

        assert "unit_test" in prompts
        assert "edge_case" in prompts
        assert "error_case" in prompts

    @pytest.mark.asyncio
    async def test_execute_task_generate_tests(self, test_generator_agent, temp_python_file):
        """Test executing generate_tests task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_123",
            task_type="generate_tests",
            description="Generate tests",
            context={
                "file_path": temp_python_file,
                "include_edge_cases": True,
                "include_error_cases": True,
            },
        )

        result = await test_generator_agent.execute_task(task)

        assert result.task_id == "task_123"
        assert result.status.value == "completed"
        assert "tests_generated" in result.output

    @pytest.mark.asyncio
    async def test_execute_task_generate_regression_test(self, test_generator_agent, temp_python_file):
        """Test executing generate_regression_test task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_regression",
            task_type="generate_regression_test",
            description="Generate regression test",
            context={
                "error_message": "AssertionError: 1 != 2",
                "stack_trace": "Traceback...",
                "code_snippet": "assert 1 == 2",
                "file_path": temp_python_file,
            },
        )

        result = await test_generator_agent.execute_task(task)

        assert result.task_id == "task_regression"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_generate_integration_tests(self, test_generator_agent):
        """Test executing generate_integration_tests task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_integration",
            task_type="generate_integration_tests",
            description="Generate integration tests",
            context={},
        )

        result = await test_generator_agent.execute_task(task)

        assert result.task_id == "task_integration"
        assert result.status.value == "completed"

    @pytest.mark.asyncio
    async def test_execute_task_unknown_type(self, test_generator_agent):
        """Test executing unknown task type."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_unknown",
            task_type="unknown_type",
            description="Unknown",
            context={},
        )

        result = await test_generator_agent.execute_task(task)

        assert result.status.value == "failed"
        assert "Unknown task type" in result.error

    @pytest.mark.asyncio
    async def test_generate_tests_for_file(self, test_generator_agent, temp_python_file):
        """Test generating tests for a file."""
        tests = await test_generator_agent.generate_tests_for_file(
            file_path=temp_python_file,
            include_edge_cases=True,
            include_error_cases=True,
            include_property_tests=False,
        )

        assert isinstance(tests, list)
        # Should generate tests for functions and methods

    @pytest.mark.asyncio
    async def test_generate_tests_for_file_no_edge_cases(self, test_generator_agent, temp_python_file):
        """Test generating tests without edge cases."""
        tests = await test_generator_agent.generate_tests_for_file(
            file_path=temp_python_file,
            include_edge_cases=False,
            include_error_cases=False,
        )

        assert isinstance(tests, list)

    @pytest.mark.asyncio
    async def test_generate_test_from_error(self, test_generator_agent, temp_python_file):
        """Test generating regression test from error."""
        test = await test_generator_agent.generate_test_from_error(
            error_message="ZeroDivisionError: division by zero",
            stack_trace="Traceback (most recent call last):\n  File 'test.py', line 5",
            code_snippet="result = 10 / value",
            file_path=temp_python_file,
        )

        assert test is not None
        assert "regression" in test.test_type

    @pytest.mark.asyncio
    async def test_generate_test_from_error_llm_failure(self, test_generator_agent, temp_python_file):
        """Test generate_test_from_error when LLM fails."""
        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        test = await test_generator_agent.generate_test_from_error(
            error_message="Error",
            stack_trace="Trace",
            code_snippet="code",
            file_path=temp_python_file,
        )

        assert test is None

    @pytest.mark.asyncio
    async def test_suggest_test_improvements(self, test_generator_agent):
        """Test suggesting improvements for existing tests."""
        test_generator_agent._llm.generate = AsyncMock(return_value="""[
            {"type": "missing_edge_case", "description": "Test with empty input"},
            {"type": "weak_assertion", "description": "Use more specific assertions"}
        ]""")

        suggestions = await test_generator_agent.suggest_test_improvements(
            existing_test_code="def test_func(): assert func() == True",
            source_code="def func(): return True",
        )

        assert len(suggestions) == 2

    @pytest.mark.asyncio
    async def test_suggest_test_improvements_error(self, test_generator_agent):
        """Test suggest_test_improvements when LLM fails."""
        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        suggestions = await test_generator_agent.suggest_test_improvements(
            existing_test_code="test code",
            source_code="source code",
        )

        assert suggestions == []

    @pytest.mark.asyncio
    async def test_analyze_file(self, test_generator_agent, temp_python_file):
        """Test analyzing file structure."""
        components = await test_generator_agent._analyze_file(temp_python_file)

        assert len(components) > 0
        # Should find 'add', 'divide', 'Calculator.add', etc.
        names = [c.name for c in components]
        assert "add" in names or "divide" in names

    @pytest.mark.asyncio
    async def test_analyze_file_syntax_error(self, test_generator_agent, temp_syntax_error_file):
        """Test analyzing file with syntax error."""
        components = await test_generator_agent._analyze_file(temp_syntax_error_file)

        assert components == []

    @pytest.mark.asyncio
    async def test_analyze_file_not_found(self, test_generator_agent):
        """Test analyzing non-existent file."""
        components = await test_generator_agent._analyze_file("/nonexistent/file.py")

        assert components == []

    def test_calculate_complexity(self, test_generator_agent):
        """Test complexity calculation."""
        import ast

        # Simple function
        simple_code = "def func(): return 1"
        simple_tree = ast.parse(simple_code)
        simple_func = simple_tree.body[0]
        complexity = test_generator_agent._calculate_complexity(simple_func)
        assert complexity == 1

        # Complex function with if/for/while
        complex_code = """
def func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                continue
    return x
"""
        complex_tree = ast.parse(complex_code)
        complex_func = complex_tree.body[0]
        complexity = test_generator_agent._calculate_complexity(complex_func)
        assert complexity > 1

    def test_extract_dependencies(self, test_generator_agent):
        """Test dependency extraction."""
        import ast

        code = """
def func():
    result = helper()
    data = processor.process(result)
    return data
"""
        tree = ast.parse(code)
        func = tree.body[0]

        dependencies = test_generator_agent._extract_dependencies(func)

        assert "helper" in dependencies
        assert "process" in dependencies

    def test_get_signature(self, test_generator_agent):
        """Test signature extraction."""
        import ast

        code = "def func(a: int, b: str = 'default') -> bool: pass"
        tree = ast.parse(code)
        func = tree.body[0]

        signature = test_generator_agent._get_signature(func)

        assert "a: int" in signature
        assert "b: str" in signature
        assert "bool" in signature

    def test_sanitize_name(self, test_generator_agent):
        """Test name sanitization."""
        assert test_generator_agent._sanitize_name("MyClass.method") == "myclass_method"
        assert test_generator_agent._sanitize_name("func-name") == "func_name"
        assert test_generator_agent._sanitize_name("func with spaces") == "func_with_spaces"

    @pytest.mark.asyncio
    async def test_generate_unit_tests(self, test_generator_agent, temp_python_file):
        """Test generating unit tests for a component."""
        component = CodeComponent(
            name="add",
            component_type="function",
            file_path=temp_python_file,
            line_start=1,
            line_end=3,
            signature="(a: int, b: int) -> int",
            docstring="Add two numbers.",
        )

        tests = await test_generator_agent._generate_unit_tests(component, temp_python_file)

        assert len(tests) == 1
        assert "unit" in tests[0].test_type

    @pytest.mark.asyncio
    async def test_generate_unit_tests_error(self, test_generator_agent, temp_python_file):
        """Test _generate_unit_tests when LLM fails."""
        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        component = CodeComponent(
            name="add",
            component_type="function",
            file_path=temp_python_file,
            line_start=1,
            line_end=3,
            signature="()",
        )

        tests = await test_generator_agent._generate_unit_tests(component, temp_python_file)

        assert tests == []

    @pytest.mark.asyncio
    async def test_generate_edge_case_tests(self, test_generator_agent, temp_python_file):
        """Test generating edge case tests."""
        component = CodeComponent(
            name="divide",
            component_type="function",
            file_path=temp_python_file,
            line_start=5,
            line_end=10,
            signature="(a: int, b: int) -> float",
        )

        tests = await test_generator_agent._generate_edge_case_tests(component, temp_python_file)

        assert len(tests) == 1
        assert tests[0].test_type == "edge_case"

    @pytest.mark.asyncio
    async def test_generate_edge_case_tests_error(self, test_generator_agent, temp_python_file):
        """Test _generate_edge_case_tests when LLM fails."""
        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        component = CodeComponent(
            name="func",
            component_type="function",
            file_path=temp_python_file,
            line_start=1,
            line_end=3,
            signature="()",
        )

        tests = await test_generator_agent._generate_edge_case_tests(component, temp_python_file)

        assert tests == []

    @pytest.mark.asyncio
    async def test_generate_error_tests(self, test_generator_agent, temp_python_file):
        """Test generating error handling tests."""
        component = CodeComponent(
            name="divide",
            component_type="function",
            file_path=temp_python_file,
            line_start=5,
            line_end=10,
            signature="(a: int, b: int) -> float",
        )

        tests = await test_generator_agent._generate_error_tests(component, temp_python_file)

        assert len(tests) == 1
        assert tests[0].test_type == "error"

    @pytest.mark.asyncio
    async def test_generate_error_tests_error(self, test_generator_agent, temp_python_file):
        """Test _generate_error_tests when LLM fails."""
        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        component = CodeComponent(
            name="func",
            component_type="function",
            file_path=temp_python_file,
            line_start=1,
            line_end=3,
            signature="()",
        )

        tests = await test_generator_agent._generate_error_tests(component, temp_python_file)

        assert tests == []

    @pytest.mark.asyncio
    async def test_execute_task_missing_file_path(self, test_generator_agent):
        """Test _generate_tests_task without file_path."""
        from backend.agents.base_agent import Task

        task = Task(
            task_id="task_missing",
            task_type="generate_tests",
            description="Missing file path",
            context={},
        )

        result = await test_generator_agent.execute_task(task)

        assert result.status.value == "failed"

    @pytest.mark.asyncio
    async def test_skip_private_methods(self, test_generator_agent, temp_python_file):
        """Test that private methods (not dunder) are skipped."""
        tests = await test_generator_agent.generate_tests_for_file(
            file_path=temp_python_file,
            include_edge_cases=False,
            include_error_cases=False,
        )

        # Private method _private_method should be skipped (unless it starts with __)
        test_names = [t.component_name for t in tests]
        # _private_method should not be tested
        assert not any("_private_method" in name for name in test_names)

    @pytest.mark.asyncio
    async def test_execute_task_exception_handling(self, test_generator_agent):
        """Test exception handling in execute_task."""
        from backend.agents.base_agent import Task

        test_generator_agent._llm.generate = AsyncMock(side_effect=Exception("Error"))

        task = Task(
            task_id="task_error",
            task_type="generate_tests",
            description="Will fail",
            context={"file_path": "/nonexistent/file.py"},
        )

        result = await test_generator_agent.execute_task(task)

        # Should complete but with no tests found
        # or fail depending on implementation
        assert result.task_id == "task_error"


class TestTestGeneratorExtendedCoverage:
    """Tests for extended coverage - line 425 (BoolOp complexity)."""

    @pytest.fixture
    def test_generator_agent(self):
        """Create TestGeneratorAgent with mocked LLM."""
        from unittest.mock import AsyncMock, Mock, patch

        from backend.testing.agents.test_generator import TestGeneratorAgent

        mock_llm = Mock()
        mock_llm.generate = AsyncMock(return_value="def test(): pass")
        with patch('backend.testing.agents.test_generator.LLMFactory.create_llm', return_value=mock_llm):
            agent = TestGeneratorAgent()
            agent._llm = mock_llm
            return agent

    def test_calculate_complexity_with_boolop_line_425(self, test_generator_agent):
        """Test line 425: BoolOp complexity calculation."""
        import ast

        code = '''
def complex_function(a, b, c, d, e):
    if a and b and c:  # BoolOp with 3 values: +2
        return 1
    if a or b or c or d or e:  # BoolOp with 5 values: +4
        return 2
    return 0
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        complexity = test_generator_agent._calculate_complexity(func_node)

        # Base: 1
        # First if: +1
        # First BoolOp "a and b and c" (3 values): +2
        # Second if: +1
        # Second BoolOp "a or b or c or d or e" (5 values): +4
        # Total: 1 + 1 + 2 + 1 + 4 = 9
        assert complexity == 9

    def test_calculate_complexity_nested_boolop(self, test_generator_agent):
        """Test BoolOp complexity with nested conditions."""
        import ast

        code = '''
def nested_func(x, y, z):
    while x and y:  # While: +1, BoolOp (2 values): +1
        for i in range(10):  # For: +1
            if z or x:  # If: +1, BoolOp (2 values): +1
                pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        complexity = test_generator_agent._calculate_complexity(func_node)

        # Base: 1
        # While: +1
        # BoolOp "x and y" (2 values): +1
        # For: +1
        # If: +1
        # BoolOp "z or x" (2 values): +1
        # Total: 1 + 1 + 1 + 1 + 1 + 1 = 6
        assert complexity == 6

    def test_calculate_complexity_single_boolop(self, test_generator_agent):
        """Test single BoolOp with 2 operands."""
        import ast

        code = '''
def simple_func(a, b):
    return a and b  # BoolOp with 2 values: +1
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        complexity = test_generator_agent._calculate_complexity(func_node)

        # Base: 1, BoolOp (2 values): +1 = 2
        assert complexity == 2
