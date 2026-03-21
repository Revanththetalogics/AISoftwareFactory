"""
Report generator for Simulation module.

This module provides comprehensive test report generation in multiple formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Report generator for simulation results.

    Generates reports in JSON, HTML, and Markdown formats.
    """

    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for report output
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger(__name__)

    def generate_json(
        self,
        results: dict[str, Any],
        filename: str | None = None
    ) -> str:
        """
        Generate JSON report.

        Args:
            results: Test results
            filename: Output filename

        Returns:
            Path to generated report
        """
        filename = filename or f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self._output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        self._logger.info("JSON report generated", path=str(filepath))
        return str(filepath)

    def generate_markdown(
        self,
        results: dict[str, Any],
        filename: str | None = None
    ) -> str:
        """
        Generate Markdown report.

        Args:
            results: Test results
            filename: Output filename

        Returns:
            Path to generated report
        """
        filename = filename or f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self._output_dir / filename

        lines = [
            "# Simulation Test Report",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}",
            "",
            "## Summary",
            ""
        ]

        if "summary" in results:
            summary = results["summary"]
            lines.extend([
                f"- **Total Tests:** {summary.get('total_tests', 'N/A')}",
                f"- **Passed:** {summary.get('passed', 'N/A')}",
                f"- **Failed:** {summary.get('failed', 'N/A')}",
                f"- **Success Rate:** {summary.get('success_rate', 0) * 100:.1f}%",
                f"- **Duration:** {summary.get('duration_seconds', 0):.2f}s",
                ""
            ])

        if "results" in results:
            lines.extend(["## Detailed Results", ""])
            for result in results["results"]:
                status = "✅" if result.get("success") else "❌"
                lines.append(f"### {status} {result.get('test', 'Unknown')}")
                lines.append("")
                if "details" in result:
                    for key, value in result["details"].items():
                        lines.append(f"- **{key}:** {value}")
                    lines.append("")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self._logger.info("Markdown report generated", path=str(filepath))
        return str(filepath)

    def generate_html(
        self,
        results: dict[str, Any],
        filename: str | None = None
    ) -> str:
        """
        Generate HTML report.

        Args:
            results: Test results
            filename: Output filename

        Returns:
            Path to generated report
        """
        filename = filename or f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self._output_dir / filename

        summary = results.get("summary", {})
        success_rate = summary.get("success_rate", 0) * 100

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Simulation Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>Simulation Test Report</h1>
    <p><strong>Generated:</strong> {datetime.utcnow().isoformat()}</p>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {summary.get('total_tests', 'N/A')}</p>
        <p class="passed">Passed: {summary.get('passed', 'N/A')}</p>
        <p class="failed">Failed: {summary.get('failed', 'N/A')}</p>
        <p>Success Rate: {success_rate:.1f}%</p>
        <p>Duration: {summary.get('duration_seconds', 0):.2f}s</p>
    </div>

    <h2>Detailed Results</h2>
"""

        for result in results.get("results", []):
            status_class = "passed" if result.get("success") else "failed"
            html += f"""
    <div class="test-result">
        <h3 class="{status_class}">{result.get('test', 'Unknown')}</h3>
        <p>Status: {'PASS' if result.get('success') else 'FAIL'}</p>
    </div>
"""

        html += """
</body>
</html>
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        self._logger.info("HTML report generated", path=str(filepath))
        return str(filepath)
