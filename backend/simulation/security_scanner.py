"""
Security scanner for Simulation module.

This module provides vulnerability scanning for generated code
including dependency checks and static analysis.
"""

import ast
import re
from dataclasses import dataclass
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityIssue:
    """A security issue found in code."""
    severity: str  # critical, high, medium, low
    category: str
    message: str
    line: int | None = None
    code_snippet: str | None = None


class SecurityScanner:
    """
    Security scanner for code analysis.

    Performs static analysis to detect vulnerabilities,
    unsafe patterns, and security risks.
    """

    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = {
        "eval": r"\beval\s*\(",
        "exec": r"\bexec\s*\(",
        "subprocess_shell": r"subprocess\.\w+.*shell\s*=\s*True",
        "sql_injection": r"(execute|cursor\.execute).*\+.*format",
        "hardcoded_password": r"(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
        "pickle_load": r"pickle\.load",
        "yaml_load": r"yaml\.load\s*\(",
    }

    def __init__(self):
        """Initialize the security scanner."""
        self._logger = get_logger(__name__)

    async def scan_code(
        self,
        code: str,
        language: str = "python"
    ) -> list[SecurityIssue]:
        """
        Scan code for security issues.

        Args:
            code: Code to scan
            language: Programming language

        Returns:
            List of security issues
        """
        issues = []

        if language == "python":
            issues.extend(self._scan_python_patterns(code))
            issues.extend(await self._scan_python_ast(code))

        return issues

    def _scan_python_patterns(self, code: str) -> list[SecurityIssue]:
        """Scan Python code using regex patterns."""
        issues = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self.DANGEROUS_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    severity = self._get_severity(pattern_name)
                    issues.append(SecurityIssue(
                        severity=severity,
                        category=pattern_name,
                        message=f"Potentially dangerous pattern: {pattern_name}",
                        line=line_num,
                        code_snippet=line.strip()
                    ))

        return issues

    async def _scan_python_ast(self, code: str) -> list[SecurityIssue]:
        """Scan Python code using AST analysis."""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["pickle", "marshal"]:
                            issues.append(SecurityIssue(
                                severity="medium",
                                category="dangerous_import",
                                message=f"Dangerous import: {alias.name}",
                                line=getattr(node, 'lineno', None)
                            ))

                # Check for unsafe file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["open", "file"]:
                            # Check for write mode
                            if any(
                                isinstance(arg, ast.Constant) and
                                isinstance(arg.value, str) and
                                "w" in arg.value
                                for arg in node.args[1:2]
                            ):
                                issues.append(SecurityIssue(
                                    severity="low",
                                    category="file_write",
                                    message="File write operation detected",
                                    line=getattr(node, 'lineno', None)
                                ))

        except SyntaxError as e:
            issues.append(SecurityIssue(
                severity="high",
                category="syntax_error",
                message=f"Syntax error: {e}"
            ))

        return issues

    async def scan_dependencies(
        self,
        requirements: list[str]
    ) -> list[SecurityIssue]:
        """
        Scan dependencies for known vulnerabilities.

        Args:
            requirements: List of package requirements

        Returns:
            List of security issues
        """
        issues = []

        # Known vulnerable packages (simplified)
        vulnerable_packages = {
            "requests": [("2.0.0", "2.20.0", "CVE-2018-18074")],
            "urllib3": [("1.0", "1.24.2", "CVE-2019-11324")],
            "django": [("1.0", "3.0.7", "CVE-2020-13254")],
        }

        for req in requirements:
            pkg_name = req.split("==")[0].split(">=")[0].strip()

            if pkg_name in vulnerable_packages:
                for _min_ver, _max_ver, cve in vulnerable_packages[pkg_name]:
                    issues.append(SecurityIssue(
                        severity="high",
                        category="vulnerable_dependency",
                        message=f"Package {pkg_name} may have vulnerability {cve}"
                    ))

        return issues

    def _get_severity(self, pattern_name: str) -> str:
        """Get severity level for a pattern."""
        severity_map = {
            "eval": "critical",
            "exec": "critical",
            "subprocess_shell": "high",
            "sql_injection": "critical",
            "hardcoded_password": "high",
            "pickle_load": "medium",
            "yaml_load": "medium",
        }
        return severity_map.get(pattern_name, "low")

    def generate_report(self, issues: list[SecurityIssue]) -> dict[str, Any]:
        """Generate security scan report."""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        return {
            "total_issues": len(issues),
            "severity_counts": severity_counts,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "line": i.line,
                    "code": i.code_snippet
                }
                for i in issues
            ]
        }
