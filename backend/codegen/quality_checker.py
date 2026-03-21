"""
Code Quality Checker for AI Software Factory.

This module provides code quality analysis and checking capabilities.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


class IssueSeverity(str, Enum):
    """Severity levels for code issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories of code issues."""
    STYLE = "style"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    DOCUMENTATION = "documentation"


@dataclass
class CodeIssue:
    """
    Represents a code quality issue.

    Attributes:
        rule_id: Rule identifier
        message: Issue description
        severity: Issue severity
        category: Issue category
        line: Line number (if applicable)
        column: Column number (if applicable)
        file_path: File path (if applicable)
        suggestion: Suggested fix
    """
    rule_id: str
    message: str
    severity: IssueSeverity
    category: IssueCategory
    line: Optional[int] = None
    column: Optional[int] = None
    file_path: Optional[str] = None
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "line": self.line,
            "column": self.column,
            "file_path": self.file_path,
            "suggestion": self.suggestion,
        }


@dataclass
class QualityReport:
    """
    Code quality report.

    Attributes:
        file_path: File path analyzed
        issues: List of issues found
        score: Quality score (0-100)
        language: Programming language
        metrics: Additional metrics
    """
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    score: float = 100.0
    language: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def issue_count(self) -> int:
        """Get total number of issues."""
        return len(self.issues)

    @property
    def critical_issues(self) -> int:
        """Get number of critical issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)

    @property
    def high_issues(self) -> int:
        """Get number of high severity issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "score": self.score,
            "language": self.language,
            "issue_count": self.issue_count,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "metrics": self.metrics,
            "issues": [i.to_dict() for i in self.issues],
        }


class QualityChecker:
    """
    Code quality checker.

    This class provides:
    - Static code analysis
    - Style checking
    - Security scanning
    - Complexity analysis

    Example:
        >>> checker = QualityChecker()
        >>> report = checker.check_code(code, "python", "main.py")
        >>> print(f"Quality score: {report.score}")
    """

    def __init__(self):
        """Initialize the quality checker."""
        self._logger = get_logger(__name__)

    def check_code(
        self,
        code: str,
        language: str,
        file_path: str = "",
    ) -> QualityReport:
        """
        Check code quality.

        Args:
            code: Code to check
            language: Programming language
            file_path: File path (for context)

        Returns:
            QualityReport with issues and score
        """
        report = QualityReport(
            file_path=file_path,
            language=language,
        )

        if language == "python":
            report.issues.extend(self._check_python_code(code, file_path))

        # Calculate score based on issues
        report.score = self._calculate_score(report.issues)

        # Add basic metrics
        report.metrics = self._calculate_metrics(code, language)

        self._logger.info(
            "Code quality check completed",
            file=file_path,
            score=report.score,
            issues=report.issue_count,
        )

        return report

    def _check_python_code(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check Python code for issues."""
        issues = []
        lines = code.split("\n")

        # Check for common issues
        for line_num, line in enumerate(lines, 1):
            # Check for print statements (should use logging)
            if re.search(r"^\s*print\(", line):
                issues.append(CodeIssue(
                    rule_id="PY001",
                    message="Use logging instead of print statements",
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.MAINTAINABILITY,
                    line=line_num,
                    file_path=file_path,
                    suggestion="Replace print() with logger.info() or appropriate log level",
                ))

            # Check for bare except
            if re.search(r"^\s*except\s*:", line):
                issues.append(CodeIssue(
                    rule_id="PY002",
                    message="Bare except clause - should catch specific exceptions",
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.SECURITY,
                    line=line_num,
                    file_path=file_path,
                    suggestion="Use 'except SpecificException:' instead of 'except:'",
                ))

            # Check for TODO comments
            if "TODO" in line.upper():
                issues.append(CodeIssue(
                    rule_id="PY003",
                    message="TODO comment found",
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.MAINTAINABILITY,
                    line=line_num,
                    file_path=file_path,
                    suggestion="Address TODO or create a ticket to track it",
                ))

            # Check line length
            if len(line) > 120:
                issues.append(CodeIssue(
                    rule_id="PY004",
                    message=f"Line too long ({len(line)} > 120 characters)",
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.STYLE,
                    line=line_num,
                    file_path=file_path,
                    suggestion="Break line into multiple lines",
                ))

            # Check for hardcoded secrets (basic pattern)
            if re.search(r"(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]", line, re.IGNORECASE):
                if "os.environ" not in line and "getenv" not in line:
                    issues.append(CodeIssue(
                        rule_id="PY005",
                        message="Potential hardcoded secret detected",
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        line=line_num,
                        file_path=file_path,
                        suggestion="Use environment variables for secrets",
                    ))

        # Check for missing docstring
        if not re.search(r'"""|\'\'\'', code):
            issues.append(CodeIssue(
                rule_id="PY006",
                message="Missing module docstring",
                severity=IssueSeverity.LOW,
                category=IssueCategory.DOCUMENTATION,
                file_path=file_path,
                suggestion="Add a module-level docstring",
            ))

        return issues

    def _calculate_score(self, issues: List[CodeIssue]) -> float:
        """
        Calculate quality score based on issues.

        Args:
            issues: List of issues

        Returns:
            Score from 0-100
        """
        if not issues:
            return 100.0

        # Deduct points based on severity
        deductions = {
            IssueSeverity.CRITICAL: 25,
            IssueSeverity.HIGH: 15,
            IssueSeverity.MEDIUM: 8,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 0,
        }

        total_deduction = sum(
            deductions.get(issue.severity, 0) for issue in issues
        )

        return max(0.0, 100.0 - total_deduction)

    def _calculate_metrics(self, code: str, language: str) -> Dict[str, Any]:
        """
        Calculate code metrics.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Dictionary of metrics
        """
        lines = code.split("\n")

        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith("#")]),
            "comment_lines": len([line for line in lines if line.strip().startswith("#")]),
            "blank_lines": len([line for line in lines if not line.strip()]),
        }

        if language == "python":
            # Count functions and classes
            metrics["function_count"] = len(re.findall(r"^\s*def\s+\w+", code, re.MULTILINE))
            metrics["class_count"] = len(re.findall(r"^\s*class\s+\w+", code, re.MULTILINE))

        return metrics

    def check_project(self, files: Dict[str, str]) -> Dict[str, QualityReport]:
        """
        Check quality of multiple files.

        Args:
            files: Dictionary mapping file paths to code content

        Returns:
            Dictionary mapping file paths to quality reports
        """
        reports = {}

        for file_path, code in files.items():
            # Detect language from extension
            language = self._detect_language(file_path)
            reports[file_path] = self.check_code(code, language, file_path)

        return reports

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sql": "sql",
            ".dockerfile": "dockerfile",
        }

        ext = file_path.lower()
        if "." in file_path:
            ext = file_path[file_path.rfind("."):].lower()

        return extension_map.get(ext, "unknown")
