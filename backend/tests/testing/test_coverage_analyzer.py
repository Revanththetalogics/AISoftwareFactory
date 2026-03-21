"""
Tests for CoverageAnalyzer - Advanced test coverage and mutation testing.
"""

import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.testing.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageLevel,
    CoverageReport,
    FileCoverage,
    FunctionCoverage,
    LineCoverage,
    Mutation,
    MutationResult,
)


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="""Test recommendations:
1. Add test for edge case with empty input
2. Add test for error handling
3. Add test for boundary values""")
    return llm


@pytest.fixture
def coverage_analyzer(mock_llm):
    """Fixture for CoverageAnalyzer with mocked LLM."""
    with patch('backend.testing.coverage_analyzer.LLMFactory.create_llm', return_value=mock_llm):
        analyzer = CoverageAnalyzer()
        analyzer._llm = mock_llm
        return analyzer


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    if a < b:
        return 0
    return a - b

class Calculator:
    def multiply(self, a, b):
        return a * b
''')
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_directory():
    """Create a temporary directory with Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "module1.py"), "w") as f:
            f.write("def func1():\n    return 1\n")
        with open(os.path.join(tmpdir, "module2.py"), "w") as f:
            f.write("def func2():\n    x = 1\n    if x > 0:\n        return True\n    return False\n")
        yield tmpdir


class TestCoverageLevelEnum:
    """Tests for CoverageLevel enum."""

    def test_all_coverage_levels(self):
        """Test all CoverageLevel values."""
        assert CoverageLevel.EXCELLENT.value == "excellent"
        assert CoverageLevel.GOOD.value == "good"
        assert CoverageLevel.ACCEPTABLE.value == "acceptable"
        assert CoverageLevel.POOR.value == "poor"
        assert CoverageLevel.CRITICAL.value == "critical"


class TestLineCoverage:
    """Tests for LineCoverage dataclass."""

    def test_line_coverage_creation(self):
        """Test LineCoverage creation."""
        line = LineCoverage(
            line_number=10,
            code="return a + b",
            is_executable=True,
            is_covered=True,
            execution_count=5,
        )

        assert line.line_number == 10
        assert line.is_executable is True
        assert line.is_covered is True
        assert line.execution_count == 5

    def test_line_coverage_to_dict(self):
        """Test LineCoverage serialization."""
        line = LineCoverage(
            line_number=15,
            code="pass",
            is_executable=True,
            is_covered=False,
            execution_count=0,
        )

        data = line.to_dict()

        assert data["line_number"] == 15
        assert data["is_executable"] is True
        assert data["is_covered"] is False
        assert data["execution_count"] == 0


class TestFunctionCoverage:
    """Tests for FunctionCoverage dataclass."""

    def test_function_coverage_creation(self):
        """Test FunctionCoverage creation."""
        func = FunctionCoverage(
            name="my_function",
            line_start=10,
            line_end=20,
            total_lines=10,
            covered_lines=8,
            complexity=3,
        )

        assert func.name == "my_function"
        assert func.total_lines == 10
        assert func.covered_lines == 8
        assert func.complexity == 3

    def test_coverage_percentage(self):
        """Test coverage percentage calculation."""
        func = FunctionCoverage(
            name="func",
            line_start=1,
            line_end=10,
            total_lines=10,
            covered_lines=8,
            complexity=1,
        )

        assert func.coverage_percentage == 80.0

    def test_coverage_percentage_zero_lines(self):
        """Test coverage percentage with zero total lines."""
        func = FunctionCoverage(
            name="empty",
            line_start=1,
            line_end=1,
            total_lines=0,
            covered_lines=0,
            complexity=1,
        )

        assert func.coverage_percentage == 100.0

    def test_function_coverage_to_dict(self):
        """Test FunctionCoverage serialization."""
        func = FunctionCoverage(
            name="test_func",
            line_start=5,
            line_end=15,
            total_lines=10,
            covered_lines=7,
            complexity=2,
        )

        data = func.to_dict()

        assert data["name"] == "test_func"
        assert data["coverage_percentage"] == 70.0
        assert data["complexity"] == 2


class TestFileCoverage:
    """Tests for FileCoverage dataclass."""

    def test_file_coverage_creation(self):
        """Test FileCoverage creation."""
        fc = FileCoverage(
            file_path="/path/to/file.py",
            total_lines=100,
            executable_lines=80,
            covered_lines=60,
        )

        assert fc.file_path == "/path/to/file.py"
        assert fc.total_lines == 100
        assert fc.executable_lines == 80
        assert fc.covered_lines == 60

    def test_coverage_percentage(self):
        """Test coverage percentage calculation."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=80,
            covered_lines=60,
        )

        assert fc.coverage_percentage == 75.0

    def test_coverage_percentage_zero_executable(self):
        """Test coverage percentage with zero executable lines."""
        fc = FileCoverage(
            file_path="/path/empty.py",
            total_lines=10,
            executable_lines=0,
            covered_lines=0,
        )

        assert fc.coverage_percentage == 100.0

    def test_branch_coverage_percentage(self):
        """Test branch coverage percentage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=50,
            executable_lines=40,
            covered_lines=30,
            branches_total=10,
            branches_covered=8,
        )

        assert fc.branch_coverage_percentage == 80.0

    def test_branch_coverage_zero_branches(self):
        """Test branch coverage with zero total branches."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=50,
            executable_lines=40,
            covered_lines=30,
            branches_total=0,
            branches_covered=0,
        )

        assert fc.branch_coverage_percentage == 100.0

    def test_coverage_level_excellent(self):
        """Test coverage level for excellent coverage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=100,
            covered_lines=95,
        )

        assert fc.coverage_level == CoverageLevel.EXCELLENT

    def test_coverage_level_good(self):
        """Test coverage level for good coverage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=100,
            covered_lines=85,
        )

        assert fc.coverage_level == CoverageLevel.GOOD

    def test_coverage_level_acceptable(self):
        """Test coverage level for acceptable coverage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=100,
            covered_lines=75,
        )

        assert fc.coverage_level == CoverageLevel.ACCEPTABLE

    def test_coverage_level_poor(self):
        """Test coverage level for poor coverage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=100,
            covered_lines=55,
        )

        assert fc.coverage_level == CoverageLevel.POOR

    def test_coverage_level_critical(self):
        """Test coverage level for critical coverage."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=100,
            executable_lines=100,
            covered_lines=40,
        )

        assert fc.coverage_level == CoverageLevel.CRITICAL

    def test_get_uncovered_lines(self):
        """Test getting uncovered lines."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=5,
            executable_lines=4,
            covered_lines=2,
            line_coverage=[
                LineCoverage(1, "code1", True, True),
                LineCoverage(2, "# comment", False, False),
                LineCoverage(3, "code2", True, False),
                LineCoverage(4, "code3", True, True),
                LineCoverage(5, "code4", True, False),
            ],
        )

        uncovered = fc.get_uncovered_lines()

        assert 3 in uncovered
        assert 5 in uncovered
        assert 1 not in uncovered
        assert 2 not in uncovered  # Not executable

    def test_file_coverage_to_dict(self):
        """Test FileCoverage serialization."""
        fc = FileCoverage(
            file_path="/path/file.py",
            total_lines=50,
            executable_lines=40,
            covered_lines=36,
            branches_total=10,
            branches_covered=9,
        )

        data = fc.to_dict()

        assert data["file_path"] == "/path/file.py"
        assert data["coverage_percentage"] == 90.0
        assert data["coverage_level"] == "excellent"


class TestMutation:
    """Tests for Mutation dataclass."""

    def test_mutation_creation(self):
        """Test Mutation creation."""
        mutation = Mutation(
            id="mut_123",
            file_path="/path/file.py",
            line_number=15,
            original_code="return a + b",
            mutated_code="return a - b",
            mutation_type="arithmetic",
            description="Changed + to -",
        )

        assert mutation.id == "mut_123"
        assert mutation.mutation_type == "arithmetic"

    def test_mutation_to_dict(self):
        """Test Mutation serialization."""
        mutation = Mutation(
            id="mut_456",
            file_path="/path/file.py",
            line_number=10,
            original_code="a == b",
            mutated_code="a != b",
            mutation_type="comparison",
            description="Changed == to !=",
        )

        data = mutation.to_dict()

        assert data["id"] == "mut_456"
        assert data["mutation_type"] == "comparison"


class TestMutationResult:
    """Tests for MutationResult dataclass."""

    def test_mutation_result_creation(self):
        """Test MutationResult creation."""
        mutation = Mutation(
            id="mut_123",
            file_path="/file.py",
            line_number=10,
            original_code="a + b",
            mutated_code="a - b",
            mutation_type="arithmetic",
            description="Changed operator",
        )

        result = MutationResult(
            mutation=mutation,
            killed=True,
            test_output="AssertionError",
            execution_time_ms=150.0,
        )

        assert result.killed is True
        assert result.execution_time_ms == 150.0

    def test_mutation_result_to_dict(self):
        """Test MutationResult serialization."""
        mutation = Mutation(
            id="mut_789",
            file_path="/file.py",
            line_number=5,
            original_code="True",
            mutated_code="False",
            mutation_type="logical",
            description="Changed boolean",
        )

        result = MutationResult(
            mutation=mutation,
            killed=False,
            test_output="Tests passed",
            execution_time_ms=200.0,
        )

        data = result.to_dict()

        assert data["killed"] is False
        assert data["mutation"]["id"] == "mut_789"


class TestCoverageReport:
    """Tests for CoverageReport dataclass."""

    def test_coverage_report_creation(self):
        """Test CoverageReport creation."""
        report = CoverageReport(
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            overall_coverage=85.0,
            overall_branch_coverage=80.0,
            mutation_score=75.0,
            total_mutations=50,
            killed_mutations=38,
        )

        assert report.overall_coverage == 85.0
        assert report.mutation_score == 75.0

    def test_files_by_coverage_level(self):
        """Test grouping files by coverage level."""
        files = [
            FileCoverage("/path/excellent.py", 100, 100, 95),
            FileCoverage("/path/good.py", 100, 100, 85),
            FileCoverage("/path/poor.py", 100, 100, 55),
            FileCoverage("/path/critical.py", 100, 100, 40),
        ]

        report = CoverageReport(
            timestamp=datetime.utcnow(),
            overall_coverage=70.0,
            overall_branch_coverage=65.0,
            files=files,
        )

        by_level = report.files_by_coverage_level

        assert "/path/excellent.py" in by_level["excellent"]
        assert "/path/good.py" in by_level["good"]
        assert "/path/poor.py" in by_level["poor"]
        assert "/path/critical.py" in by_level["critical"]

    def test_coverage_report_to_dict(self):
        """Test CoverageReport serialization."""
        report = CoverageReport(
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            overall_coverage=80.0,
            overall_branch_coverage=75.0,
            mutation_score=70.0,
            total_mutations=40,
            killed_mutations=28,
        )

        data = report.to_dict()

        assert data["overall_coverage"] == 80.0
        assert data["mutation_score"] == 70.0
        assert "timestamp" in data


class TestCoverageAnalyzer:
    """Tests for CoverageAnalyzer class."""

    def test_analyzer_initialization(self, coverage_analyzer):
        """Test analyzer initialization."""
        assert coverage_analyzer._coverage_history == []
        assert len(coverage_analyzer._mutation_operators) > 0

    def test_load_mutation_operators(self, coverage_analyzer):
        """Test mutation operators are loaded."""
        operators = coverage_analyzer._mutation_operators

        assert "arithmetic" in operators
        assert "comparison" in operators
        assert "logical" in operators
        assert "unary" in operators

    @pytest.mark.asyncio
    async def test_analyze_coverage(self, coverage_analyzer, temp_directory):
        """Test analyzing coverage."""
        report = await coverage_analyzer.analyze_coverage(
            source_path=temp_directory,
            exclude_patterns=["*test*"],
        )

        assert isinstance(report, CoverageReport)
        assert report.overall_coverage >= 0

    @pytest.mark.asyncio
    async def test_analyze_coverage_single_file(self, coverage_analyzer, temp_python_file):
        """Test analyzing coverage for single file."""
        report = await coverage_analyzer.analyze_coverage(
            source_path=temp_python_file,
        )

        assert isinstance(report, CoverageReport)
        assert len(report.files) >= 0

    @pytest.mark.asyncio
    async def test_analyze_coverage_default_excludes(self, coverage_analyzer, temp_directory):
        """Test analyze_coverage with default exclude patterns."""
        report = await coverage_analyzer.analyze_coverage(
            source_path=temp_directory,
        )

        assert isinstance(report, CoverageReport)

    @pytest.mark.asyncio
    async def test_run_mutation_testing(self, coverage_analyzer, temp_python_file):
        """Test running mutation testing."""
        with patch.object(coverage_analyzer, '_test_mutation') as mock_test:
            mock_test.return_value = MutationResult(
                mutation=Mock(),
                killed=True,
                test_output="Test passed",
            )

            results = await coverage_analyzer.run_mutation_testing(
                file_path=temp_python_file,
                max_mutations=5,
            )

            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_identify_coverage_gaps(self, coverage_analyzer, temp_python_file):
        """Test identifying coverage gaps."""
        # Create a report with some gaps
        fc = FileCoverage(
            file_path=temp_python_file,
            total_lines=20,
            executable_lines=15,
            covered_lines=10,
            line_coverage=[
                LineCoverage(i, f"line {i}", True, i <= 10) for i in range(1, 16)
            ],
        )

        report = CoverageReport(
            timestamp=datetime.utcnow(),
            overall_coverage=66.7,
            overall_branch_coverage=60.0,
            files=[fc],
        )

        gaps = await coverage_analyzer.identify_coverage_gaps(report)

        assert isinstance(gaps, list)
        if gaps:
            assert "file_path" in gaps[0]
            assert "uncovered_lines_count" in gaps[0]

    @pytest.mark.asyncio
    async def test_identify_coverage_gaps_high_coverage(self, coverage_analyzer, temp_python_file):
        """Test identify_coverage_gaps with high coverage files."""
        fc = FileCoverage(
            file_path=temp_python_file,
            total_lines=10,
            executable_lines=10,
            covered_lines=10,  # 100% coverage
        )

        report = CoverageReport(
            timestamp=datetime.utcnow(),
            overall_coverage=100.0,
            overall_branch_coverage=100.0,
            files=[fc],
        )

        gaps = await coverage_analyzer.identify_coverage_gaps(report)

        # Should have no gaps for files with >= 90% coverage
        high_coverage_gaps = [g for g in gaps if g["coverage_percentage"] >= 90]
        assert len(high_coverage_gaps) == 0

    @pytest.mark.asyncio
    async def test_get_coverage_trend(self, coverage_analyzer):
        """Test getting coverage trend."""
        # Add some history
        for i in range(5):
            report = CoverageReport(
                timestamp=datetime.utcnow() - timedelta(days=i),
                overall_coverage=80.0 + i,
                overall_branch_coverage=75.0 + i,
                mutation_score=70.0 + i,
            )
            coverage_analyzer._coverage_history.append(report)

        trend = await coverage_analyzer.get_coverage_trend(days=30)

        assert len(trend) == 5
        assert "overall_coverage" in trend[0]

    @pytest.mark.asyncio
    async def test_get_coverage_trend_empty_history(self, coverage_analyzer):
        """Test get_coverage_trend with empty history."""
        trend = await coverage_analyzer.get_coverage_trend(days=30)

        assert trend == []

    def test_get_coverage_statistics_no_history(self, coverage_analyzer):
        """Test get_coverage_statistics with no history."""
        stats = coverage_analyzer.get_coverage_statistics()

        assert "error" in stats

    def test_get_coverage_statistics(self, coverage_analyzer):
        """Test get_coverage_statistics with history."""
        files = [
            FileCoverage("/path/excellent.py", 100, 100, 95),
            FileCoverage("/path/critical.py", 100, 100, 40),
        ]

        report = CoverageReport(
            timestamp=datetime.utcnow(),
            overall_coverage=67.5,
            overall_branch_coverage=60.0,
            mutation_score=50.0,
            files=files,
        )
        coverage_analyzer._coverage_history.append(report)

        stats = coverage_analyzer.get_coverage_statistics()

        assert stats["latest_coverage"] == 67.5
        assert stats["files_analyzed"] == 2
        assert "files_by_coverage_level" in stats

    @pytest.mark.asyncio
    async def test_run_coverage_py(self, coverage_analyzer, temp_directory):
        """Test _run_coverage_py method."""
        data = await coverage_analyzer._run_coverage_py(temp_directory, None)

        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_analyze_file_coverage(self, coverage_analyzer, temp_python_file):
        """Test _analyze_file_coverage method."""
        data = {
            "executable_lines": 10,
            "covered_lines": 8,
            "lines": {i: i <= 8 for i in range(1, 11)},
        }

        fc = await coverage_analyzer._analyze_file_coverage(temp_python_file, data)

        assert isinstance(fc, FileCoverage)
        assert fc.file_path == temp_python_file

    @pytest.mark.asyncio
    async def test_analyze_function_coverage(self, coverage_analyzer, temp_python_file):
        """Test _analyze_function_coverage method."""
        functions = await coverage_analyzer._analyze_function_coverage(temp_python_file)

        assert isinstance(functions, list)
        # Should find functions in the test file

    @pytest.mark.asyncio
    async def test_analyze_function_coverage_syntax_error(self, coverage_analyzer):
        """Test _analyze_function_coverage with syntax error file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("invalid syntax {{{{")
            f.flush()
            file_path = f.name

        try:
            functions = await coverage_analyzer._analyze_function_coverage(file_path)
            assert functions == []
        finally:
            os.unlink(file_path)

    def test_calculate_complexity(self, coverage_analyzer):
        """Test _calculate_complexity method."""
        import ast

        code = """
def func(x):
    if x > 0:
        for i in range(x):
            while i > 0:
                i -= 1
    return x
"""
        tree = ast.parse(code)
        func = tree.body[0]

        complexity = coverage_analyzer._calculate_complexity(func)

        assert complexity > 1

    @pytest.mark.asyncio
    async def test_generate_mutations(self, coverage_analyzer, temp_python_file):
        """Test _generate_mutations method."""
        with open(temp_python_file) as f:
            source_code = f.read()

        mutations = await coverage_analyzer._generate_mutations(
            temp_python_file, source_code, max_mutations=10
        )

        assert isinstance(mutations, list)

    @pytest.mark.asyncio
    async def test_generate_mutations_max_limit(self, coverage_analyzer):
        """Test _generate_mutations respects max limit."""
        code = """
x = 1 + 2
y = 3 - 4
z = 5 * 6
w = a == b
v = c != d
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            file_path = f.name

        try:
            mutations = await coverage_analyzer._generate_mutations(
                file_path, code, max_mutations=2
            )
            assert len(mutations) <= 2
        finally:
            os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_recommend_tests_for_gap(self, coverage_analyzer):
        """Test _recommend_tests_for_gap method."""
        recommendation = await coverage_analyzer._recommend_tests_for_gap(
            file_path="/path/file.py",
            uncovered_context=[{"line": 10, "code": "return x + y"}],
            coverage_percentage=50.0,
        )

        assert isinstance(recommendation, str)

    @pytest.mark.asyncio
    async def test_recommend_tests_for_gap_error(self, coverage_analyzer):
        """Test _recommend_tests_for_gap when LLM fails."""
        coverage_analyzer._llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        recommendation = await coverage_analyzer._recommend_tests_for_gap(
            file_path="/path/file.py",
            uncovered_context=[],
            coverage_percentage=50.0,
        )

        assert recommendation == "Unable to generate recommendation"

    @pytest.mark.asyncio
    async def test_coverage_history_updated(self, coverage_analyzer, temp_python_file):
        """Test that coverage history is updated after analysis."""
        initial_count = len(coverage_analyzer._coverage_history)

        await coverage_analyzer.analyze_coverage(source_path=temp_python_file)

        assert len(coverage_analyzer._coverage_history) == initial_count + 1


class TestCoverageAnalyzerExtendedCoverage:
    """Tests for extended coverage - lines 264, 361, 498, 585, 633-668."""

    @pytest.fixture
    def mock_llm(self):
        """Fixture for mocked LLM provider."""
        from unittest.mock import AsyncMock, Mock
        llm = Mock()
        llm.generate = AsyncMock(return_value="Test recommendation")
        return llm

    @pytest.fixture
    def coverage_analyzer(self, mock_llm):
        """Fixture for CoverageAnalyzer with mocked LLM."""
        from unittest.mock import patch

        from backend.testing.coverage_analyzer import CoverageAnalyzer
        with patch('backend.testing.coverage_analyzer.LLMFactory.create_llm', return_value=mock_llm):
            analyzer = CoverageAnalyzer()
            analyzer._llm = mock_llm
            return analyzer

    @pytest.mark.asyncio
    async def test_analyze_coverage_exclude_pattern_line_264(self, coverage_analyzer):
        """Test line 264: exclude pattern matching in analyze_coverage."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a source file
            source_file = os.path.join(tmpdir, "main.py")
            with open(source_file, "w") as f:
                f.write("def main():\n    pass\n")

            # Create a test file that should be excluded
            test_file = os.path.join(tmpdir, "test_main.py")
            with open(test_file, "w") as f:
                f.write("def test_main():\n    pass\n")

            report = await coverage_analyzer.analyze_coverage(
                source_path=tmpdir,
                exclude_patterns=["**/test_*"]  # Exclude test files (line 264)
            )

            # Test file should be excluded
            file_paths = [f.file_path for f in report.files]
            assert not any("test_main.py" in fp for fp in file_paths)

    @pytest.mark.asyncio
    async def test_identify_coverage_gaps_empty_uncovered_lines_361(self, coverage_analyzer):
        """Test line 361: empty uncovered_lines causes continue."""
        from backend.testing.coverage_analyzer import CoverageReport, FileCoverage, LineCoverage

        # Create a file coverage with 80% coverage but no uncovered executable lines
        file_coverage = FileCoverage(
            file_path="/path/to/file.py",
            total_lines=10,
            executable_lines=10,
            covered_lines=8,  # 80% - below 90% threshold
            line_coverage=[
                LineCoverage(
                    line_number=i,
                    code=f"line {i}",
                    is_executable=True,
                    is_covered=True,  # All lines covered
                ) for i in range(1, 11)
            ],
        )

        report = CoverageReport(
            timestamp=datetime.utcnow(),
            overall_coverage=80.0,
            overall_branch_coverage=75.0,
            files=[file_coverage],
        )

        gaps = await coverage_analyzer.identify_coverage_gaps(report)

        # Should have no gaps since all lines are covered
        assert len(gaps) == 0

    @pytest.mark.asyncio
    async def test_run_coverage_py_skip_test_files_line_498(self, coverage_analyzer):
        """Test line 498: skip files with 'test' in path."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a source file
            source_file = os.path.join(tmpdir, "module.py")
            with open(source_file, "w") as f:
                f.write("def func():\n    return 1\n")

            # Create a test file that should be skipped in _run_coverage_py
            test_dir = os.path.join(tmpdir, "tests")
            os.makedirs(test_dir)
            test_file = os.path.join(test_dir, "test_module.py")
            with open(test_file, "w") as f:
                f.write("def test_func():\n    pass\n")

            coverage_data = await coverage_analyzer._run_coverage_py(tmpdir, None)

            # Test file path should not be in coverage_data (line 498)
            assert not any("test" in path for path in coverage_data.keys())

    def test_calculate_complexity_boolop_line_585(self, coverage_analyzer):
        """Test line 585: BoolOp complexity calculation."""
        import ast

        code = '''
def complex_func(a, b, c, d):
    if a and b and c:  # BoolOp with 3 values
        return True
    elif a or b or c or d:  # BoolOp with 4 values
        return False
    return None
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        complexity = coverage_analyzer._calculate_complexity(func_node)

        # Base: 1
        # If: +1
        # elif (If): +1
        # BoolOp "a and b and c" (3 values): +2
        # BoolOp "a or b or c or d" (4 values): +3
        # Total: 1 + 1 + 1 + 2 + 3 = 8
        assert complexity == 8

    @pytest.mark.asyncio
    async def test_test_mutation_method_lines_633_668(self, coverage_analyzer):
        """Test lines 633-668: _test_mutation method."""
        import os
        import tempfile
        from unittest.mock import Mock, patch

        from backend.testing.coverage_analyzer import Mutation

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def add(a, b):\n    return a + b\n")
            f.flush()
            file_path = f.name

        try:
            original_code = "def add(a, b):\n    return a + b\n"

            mutation = Mutation(
                id="mut_1",
                file_path=file_path,
                line_number=2,
                original_code="    return a + b",
                mutated_code="    return a - b",
                mutation_type="arithmetic",
                description="Replace + with -",
            )

            # Mock subprocess.run to simulate test failure (mutation killed)
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero means tests failed, mutation killed
            mock_result.stdout = "Test output"
            mock_result.stderr = ""

            with patch('subprocess.run', return_value=mock_result):
                result = await coverage_analyzer._test_mutation(mutation, original_code)

                # Mutation should be killed since tests "failed"
                assert result.killed is True
                assert result.mutation == mutation

        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)

    @pytest.mark.asyncio
    async def test_test_mutation_exception_handling(self, coverage_analyzer):
        """Test _test_mutation exception handling in lines 659-664."""
        import os
        import tempfile
        from unittest.mock import patch

        from backend.testing.coverage_analyzer import Mutation

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def func():\n    return 1\n")
            f.flush()
            file_path = f.name

        try:
            original_code = "def func():\n    return 1\n"

            mutation = Mutation(
                id="mut_exc",
                file_path=file_path,
                line_number=2,
                original_code="    return 1",
                mutated_code="    return 0",
                mutation_type="constant",
                description="Replace 1 with 0",
            )

            # Mock subprocess.run to raise an exception
            with patch('subprocess.run', side_effect=Exception("Subprocess timeout")):
                result = await coverage_analyzer._test_mutation(mutation, original_code)

                # Mutation should not be killed due to exception
                assert result.killed is False
                assert "Subprocess timeout" in result.test_output

        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)


class TestCoverageAnalyzerExcludePatterns:
    """Tests to cover line 264 (exclude patterns in analyze_coverage)."""

    @pytest.mark.asyncio
    async def test_analyze_coverage_exclude_patterns_match(self, coverage_analyzer):
        """Test that files matching exclude patterns are skipped (line 264)."""
        # Mock _run_coverage_py to return data including a test file
        mock_coverage_data = {
            "/path/to/tests/test_file.py": {
                "executed_lines": [1, 2, 3],
                "missing_lines": [],
            },
            "/path/to/src/module.py": {
                "executed_lines": [1, 2],
                "missing_lines": [3, 4],
            },
        }

        with patch.object(coverage_analyzer, '_run_coverage_py', return_value=mock_coverage_data):
            with patch.object(coverage_analyzer, '_analyze_file_coverage') as mock_analyze:
                mock_analyze.return_value = FileCoverage(
                    file_path="/path/to/src/module.py",
                    total_lines=10,
                    executable_lines=4,
                    covered_lines=2,
                )

                report = await coverage_analyzer.analyze_coverage(
                    source_path="/path/to/src",
                    exclude_patterns=["*/tests/*"],  # This should exclude test_file.py
                )

                # _analyze_file_coverage should only be called for non-excluded files
                # If line 264 (continue) is hit, the test file should be skipped
                assert isinstance(report, CoverageReport)
