"""
Tests for Quality Checker.
"""

from backend.codegen.quality_checker import (
    CodeIssue,
    IssueCategory,
    IssueSeverity,
    QualityChecker,
    QualityReport,
)


class TestCodeIssue:
    """Test cases for CodeIssue."""

    def test_issue_creation(self):
        """Test creating an issue."""
        issue = CodeIssue(
            rule_id="TEST001",
            message="Test issue",
            severity=IssueSeverity.HIGH,
            category=IssueCategory.STYLE,
            line=10,
        )

        assert issue.rule_id == "TEST001"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.line == 10

    def test_issue_to_dict(self):
        """Test converting issue to dict."""
        issue = CodeIssue(
            rule_id="TEST001",
            message="Test",
            severity=IssueSeverity.LOW,
            category=IssueCategory.MAINTAINABILITY,
        )

        data = issue.to_dict()

        assert data["rule_id"] == "TEST001"
        assert data["severity"] == "low"


class TestQualityReport:
    """Test cases for QualityReport."""

    def test_report_properties(self):
        """Test report properties."""
        report = QualityReport(
            file_path="test.py",
            issues=[
                CodeIssue(
                    rule_id="1", message="Critical", severity=IssueSeverity.CRITICAL, category=IssueCategory.SECURITY
                ),
                CodeIssue(rule_id="2", message="High", severity=IssueSeverity.HIGH, category=IssueCategory.STYLE),
                CodeIssue(rule_id="3", message="Low", severity=IssueSeverity.LOW, category=IssueCategory.STYLE),
            ],
            score=75.0,
        )

        assert report.issue_count == 3
        assert report.critical_issues == 1
        assert report.high_issues == 1

    def test_report_to_dict(self):
        """Test converting report to dict."""
        report = QualityReport(
            file_path="test.py",
            score=90.0,
            language="python",
        )

        data = report.to_dict()

        assert data["file_path"] == "test.py"
        assert data["score"] == 90.0
        assert data["language"] == "python"


class TestQualityChecker:
    """Test cases for QualityChecker."""

    def setup_method(self):
        """Create fresh checker."""
        self.checker = QualityChecker()

    def test_check_python_clean_code(self):
        """Test checking clean Python code."""
        code = '''
def hello():
    """Say hello."""
    return "Hello"
'''

        report = self.checker.check_code(code, "python", "test.py")

        assert report.score >= 90
        assert report.issue_count <= 1  # May have docstring suggestion

    def test_check_python_with_print(self):
        """Test detecting print statements."""
        code = '''
def hello():
    """Say hello."""
    print("Hello")
'''

        report = self.checker.check_code(code, "python", "test.py")

        # Should have at least one issue about print
        print_issues = [i for i in report.issues if "print" in i.message.lower()]
        assert len(print_issues) > 0

    def test_check_python_bare_except(self):
        """Test detecting bare except."""
        code = """
try:
    something()
except:
    pass
"""

        report = self.checker.check_code(code, "python", "test.py")

        bare_except_issues = [i for i in report.issues if "bare" in i.message.lower()]
        assert len(bare_except_issues) > 0
        assert bare_except_issues[0].severity == IssueSeverity.HIGH

    def test_check_python_long_line(self):
        """Test detecting long lines."""
        code = 'x = "' + "a" * 150 + '"\n'

        report = self.checker.check_code(code, "python", "test.py")

        long_line_issues = [i for i in report.issues if "long" in i.message.lower()]
        assert len(long_line_issues) > 0

    def test_check_python_hardcoded_secret(self):
        """Test detecting hardcoded secrets."""
        code = 'password = "secret123"\n'

        report = self.checker.check_code(code, "python", "test.py")

        secret_issues = [i for i in report.issues if "secret" in i.message.lower()]
        assert len(secret_issues) > 0
        assert secret_issues[0].severity == IssueSeverity.CRITICAL

    def test_check_python_todo(self):
        """Test detecting TODO comments."""
        code = "# TODO: Fix this later\n"

        report = self.checker.check_code(code, "python", "test.py")

        todo_issues = [i for i in report.issues if "TODO" in i.message]
        assert len(todo_issues) > 0
        assert todo_issues[0].severity == IssueSeverity.INFO

    def test_detect_language(self):
        """Test language detection."""
        assert self.checker._detect_language("test.py") == "python"
        assert self.checker._detect_language("test.js") == "javascript"
        assert self.checker._detect_language("test.ts") == "typescript"
        assert self.checker._detect_language("test.json") == "json"
        assert self.checker._detect_language("test.yaml") == "yaml"

    def test_check_project(self):
        """Test checking multiple files."""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
        }

        reports = self.checker.check_project(files)

        assert len(reports) == 2
        assert "main.py" in reports
        assert "utils.py" in reports

    def test_calculate_score(self):
        """Test score calculation."""
        issues = [
            CodeIssue(
                rule_id="1", message="Critical", severity=IssueSeverity.CRITICAL, category=IssueCategory.SECURITY
            ),
            CodeIssue(rule_id="2", message="High", severity=IssueSeverity.HIGH, category=IssueCategory.STYLE),
        ]

        score = self.checker._calculate_score(issues)

        assert score < 100
        assert score >= 0

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        code = """
# Comment

def foo():
    pass

class Bar:
    pass
"""

        metrics = self.checker._calculate_metrics(code, "python")

        assert metrics["total_lines"] > 0
        assert metrics["function_count"] == 1
        assert metrics["class_count"] == 1
