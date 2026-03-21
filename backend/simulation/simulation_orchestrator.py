"""
Simulation orchestrator for Simulation module.

This module provides unified test orchestration and management
for all simulation components.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.core.logging import get_logger
from backend.simulation.report_generator import ReportGenerator
from backend.simulation.test_runner import TestRunner
from backend.simulation.validation_engine import ValidationEngine

logger = get_logger(__name__)


@dataclass
class SimulationConfig:
    """Simulation configuration."""
    run_security_scan: bool = True
    run_performance_test: bool = True
    run_integration_test: bool = True
    generate_reports: bool = True
    output_formats: list[str] = None

    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ["json", "markdown"]


class SimulationOrchestrator:
    """
    Simulation orchestrator for unified test management.

    Coordinates all simulation components and manages the complete
    testing workflow from execution to reporting.
    """

    def __init__(self):
        """Initialize the simulation orchestrator."""
        self._test_runner = TestRunner()
        self._validator = ValidationEngine()
        self._reporter = ReportGenerator()
        self._logger = get_logger(__name__)

    async def run_simulation(
        self,
        code: str,
        language: str = "python",
        requirements: list[str] | None = None,
        config: SimulationConfig | None = None
    ) -> dict[str, Any]:
        """
        Run complete simulation workflow.

        Args:
            code: Code to simulate
            language: Programming language
            requirements: Package requirements
            config: Simulation configuration

        Returns:
            Complete simulation results
        """
        config = config or SimulationConfig()
        start_time = datetime.utcnow()

        self._logger.info("Starting simulation workflow")

        results = {
            "simulation_id": f"sim_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "start_time": start_time.isoformat(),
            "config": {
                "language": language,
                "security_scan": config.run_security_scan,
                "performance_test": config.run_performance_test,
                "integration_test": config.run_integration_test
            },
            "tests": {},
            "validation": {},
            "reports": []
        }

        # 1. Run test suite
        if config.run_security_scan:
            self._logger.info("Running test suite")
            test_result = await self._test_runner.run_full_suite(
                code, language, requirements
            )
            results["tests"] = self._test_runner.generate_report(test_result)

        # 2. Run validation
        self._logger.info("Running validation")
        validation_result = await self._validator.validate(code)
        results["validation"] = validation_result

        # 3. Generate reports
        if config.generate_reports:
            self._logger.info("Generating reports")
            combined_results = {
                "tests": results["tests"],
                "validation": results["validation"],
                "summary": {
                    "test_success_rate": results["tests"].get("summary", {}).get("success_rate", 0),
                    "validation_score": results["validation"].get("score", 0),
                    "overall_pass": (
                        results["tests"].get("summary", {}).get("failed", 0) == 0 and
                        results["validation"].get("overall_status") == "pass"
                    )
                }
            }

            for fmt in config.output_formats:
                if fmt == "json":
                    path = self._reporter.generate_json(combined_results)
                    results["reports"].append({"format": "json", "path": path})
                elif fmt == "markdown":
                    path = self._reporter.generate_markdown(combined_results)
                    results["reports"].append({"format": "markdown", "path": path})
                elif fmt == "html":
                    path = self._reporter.generate_html(combined_results)
                    results["reports"].append({"format": "html", "path": path})

        results["end_time"] = datetime.utcnow().isoformat()
        results["status"] = "completed"

        self._logger.info(
            "Simulation workflow completed",
            simulation_id=results["simulation_id"]
        )

        return results

    def get_simulation_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """
        Get simulation summary.

        Args:
            results: Simulation results

        Returns:
            Summary information
        """
        return {
            "simulation_id": results.get("simulation_id"),
            "status": results.get("status"),
            "overall_pass": results.get("validation", {}).get("overall_status") == "pass",
            "test_success_rate": results.get("tests", {}).get("summary", {}).get("success_rate", 0),
            "validation_score": results.get("validation", {}).get("score", 0),
            "reports_generated": len(results.get("reports", []))
        }
