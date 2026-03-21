"""
Pipeline for Workflow module.

This module provides workflow pipeline management for orchestrating
multi-step processes with dependencies and parallel execution.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


class StepStatus(Enum):
    """Pipeline step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStep:
    """A step in the pipeline."""
    name: str
    action: Callable
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class Pipeline:
    """
    Workflow pipeline for multi-step orchestration.

    Provides dependency management, parallel execution, and
    comprehensive pipeline state tracking.
    """

    def __init__(self, name: str):
        """
        Initialize the pipeline.

        Args:
            name: Pipeline name
        """
        self._name = name
        self._steps: Dict[str, PipelineStep] = {}
        self._logger = get_logger(__name__)

    def add_step(
        self,
        name: str,
        action: Callable,
        dependencies: Optional[List[str]] = None
    ) -> 'Pipeline':
        """
        Add a step to the pipeline.

        Args:
            name: Step name
            action: Step action function
            dependencies: List of step names this step depends on

        Returns:
            Self for chaining
        """
        self._steps[name] = PipelineStep(
            name=name,
            action=action,
            dependencies=dependencies or []
        )

        self._logger.info("Step added", pipeline=self._name, step=name)
        return self

    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the pipeline.

        Args:
            context: Shared context for all steps

        Returns:
            Execution results
        """
        context = context or {}
        completed = set()
        failed = set()

        self._logger.info("Pipeline started", pipeline=self._name)

        while len(completed) + len(failed) < len(self._steps):
            # Find ready steps (all dependencies completed)
            ready_steps = [
                name for name, step in self._steps.items()
                if step.status == StepStatus.PENDING
                and all(dep in completed for dep in step.dependencies)
                and not any(dep in failed for dep in step.dependencies)
            ]

            if not ready_steps:
                # Check if we're stuck due to failed dependencies
                pending_steps = [
                    name for name, step in self._steps.items()
                    if step.status == StepStatus.PENDING
                ]

                if pending_steps:
                    for name in pending_steps:
                        step = self._steps[name]
                        failed_deps = [dep for dep in step.dependencies if dep in failed]
                        if failed_deps:
                            step.status = StepStatus.SKIPPED
                            step.error = f"Dependencies failed: {failed_deps}"
                            self._logger.warning(
                                "Step skipped due to failed dependencies",
                                step=name,
                                failed_deps=failed_deps
                            )
                break

            # Execute ready steps in parallel
            tasks = [
                self._execute_step(name, context)
                for name in ready_steps
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for name, result in zip(ready_steps, results):
                if isinstance(result, Exception):
                    failed.add(name)
                    self._steps[name].status = StepStatus.FAILED
                    self._steps[name].error = str(result)
                else:
                    completed.add(name)

        self._logger.info(
            "Pipeline completed",
            pipeline=self._name,
            completed=len(completed),
            failed=len(failed)
        )

        return {
            "pipeline": self._name,
            "completed": list(completed),
            "failed": list(failed),
            "steps": {
                name: {
                    "status": step.status.value,
                    "result": step.result,
                    "error": step.error
                }
                for name, step in self._steps.items()
            }
        }

    async def _execute_step(
        self,
        name: str,
        context: Dict[str, Any]
    ):
        """Execute a single step."""
        step = self._steps[name]
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()

        try:
            self._logger.info("Executing step", step=name)

            if asyncio.iscoroutinefunction(step.action):
                result = await step.action(context)
            else:
                result = step.action(context)

            step.result = result
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()

            self._logger.info("Step completed", step=name)

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()

            self._logger.error("Step failed", step=name, error=str(e))
            raise

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "pipeline": self._name,
            "total_steps": len(self._steps),
            "completed": sum(1 for s in self._steps.values() if s.status == StepStatus.COMPLETED),
            "failed": sum(1 for s in self._steps.values() if s.status == StepStatus.FAILED),
            "running": sum(1 for s in self._steps.values() if s.status == StepStatus.RUNNING),
            "pending": sum(1 for s in self._steps.values() if s.status == StepStatus.PENDING)
        }
