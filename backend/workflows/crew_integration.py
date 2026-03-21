"""
CrewAI Integration for Workflow Engine.

This module provides the bridge between LangGraph workflows and CrewAI crews,
enabling agent collaboration within workflow phases.
"""

from typing import Any

from crewai import Crew
from crewai import Task as CrewTask

from backend.agents.crews import (
    create_deployment_crew,
    create_design_crew,
    create_implementation_crew,
    create_planning_crew,
)
from backend.agents.crews.deployment_crew import (
    create_infrastructure_task,
)
from backend.agents.crews.design_crew import (
    create_architecture_task,
)
from backend.agents.crews.implementation_crew import (
    create_backend_implementation_task,
    create_frontend_implementation_task,
)
from backend.agents.crews.planning_crew import (
    create_requirements_task,
)
from backend.core.logging import get_logger
from backend.workflows.state_machine import ProjectPhase

logger = get_logger(__name__)


class CrewIntegration:
    """
    Integration layer between LangGraph workflows and CrewAI crews.

    This class is responsible for:
    - Assembling appropriate crews for each workflow phase
    - Executing crew tasks within workflow phases
    - Mapping crew outputs to workflow state
    - Managing crew lifecycle

    Example:
        >>> integration = CrewIntegration()
        >>> result = await integration.execute_phase(
        ...     phase=ProjectPhase.REQUIREMENTS,
        ...     context={"idea": "Build a SaaS app"}
        ... )
    """

    def __init__(self):
        """Initialize the crew integration."""
        self._crews: dict[ProjectPhase, Crew] = {}
        self._logger = get_logger(__name__)

    def assemble_crew_for_phase(self, phase: ProjectPhase) -> Crew | None:
        """
        Assemble the appropriate crew for a workflow phase.

        Args:
            phase: Workflow phase

        Returns:
            Configured Crew instance or None if phase doesn't use crews

        Example:
            >>> crew = integration.assemble_crew_for_phase(ProjectPhase.REQUIREMENTS)
            >>> print(crew)
        """
        if phase in self._crews:
            return self._crews[phase]

        crew = None

        if phase == ProjectPhase.REQUIREMENTS:
            crew = create_planning_crew()
        elif phase == ProjectPhase.ARCHITECTURE:
            crew = create_design_crew()
        elif phase == ProjectPhase.IMPLEMENTATION:
            crew = create_implementation_crew()
        elif phase == ProjectPhase.DEPLOYMENT:
            crew = create_deployment_crew()

        if crew:
            self._crews[phase] = crew
            self._logger.info("Crew assembled for phase", phase=phase.value)

        return crew

    async def execute_phase(
        self,
        phase: ProjectPhase,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a workflow phase using the appropriate crew.

        Args:
            phase: Workflow phase to execute
            context: Shared context from workflow state

        Returns:
            Dictionary containing crew execution results

        Example:
            >>> result = await integration.execute_phase(
            ...     phase=ProjectPhase.REQUIREMENTS,
            ...     context={"idea": "Build a SaaS app"}
            ... )
            >>> print(result["output"])
        """
        self._logger.info(
            "Executing phase with crew",
            phase=phase.value,
            context_keys=list(context.keys()),
        )

        # Get or create crew for phase
        crew = self.assemble_crew_for_phase(phase)

        if not crew:
            self._logger.warning("No crew available for phase", phase=phase.value)
            return {
                "success": True,
                "output": {},
                "message": f"Phase {phase.value} completed without crew execution",
            }

        try:
            # Create tasks for the crew based on phase and context
            tasks = self._create_tasks_for_phase(phase, context)

            if tasks:
                crew.tasks = tasks

                # Execute crew (kickoff)
                # Note: CrewAI kickoff is synchronous, run in thread pool for async
                import asyncio
                result = await asyncio.to_thread(crew.kickoff)

                self._logger.info(
                    "Phase execution completed",
                    phase=phase.value,
                    result_type=type(result).__name__,
                )

                return {
                    "success": True,
                    "output": self._parse_crew_result(result),
                    "raw_result": str(result),
                }
            else:
                return {
                    "success": True,
                    "output": {},
                    "message": "No tasks created for phase",
                }

        except Exception as exc:
            self._logger.error(
                "Phase execution failed",
                phase=phase.value,
                error=str(exc),
            )
            return {
                "success": False,
                "error": str(exc),
                "output": {},
            }

    def _create_tasks_for_phase(
        self,
        phase: ProjectPhase,
        context: dict[str, Any],
    ) -> list[CrewTask]:
        """
        Create CrewAI tasks for a workflow phase.

        Args:
            phase: Workflow phase
            context: Shared context

        Returns:
            List of CrewAI tasks
        """
        tasks = []

        if phase == ProjectPhase.REQUIREMENTS:
            idea = context.get("idea", "")
            if idea:
                tasks.append(create_requirements_task(idea))

        elif phase == ProjectPhase.ARCHITECTURE:
            requirements = context.get("requirements", "")
            if requirements:
                tasks.append(create_architecture_task(requirements))

        elif phase == ProjectPhase.IMPLEMENTATION:
            architecture = context.get("architecture", "")
            requirements = context.get("requirements", "")
            if architecture and requirements:
                tasks.append(create_backend_implementation_task(architecture, requirements))
                tasks.append(create_frontend_implementation_task(architecture, requirements))

        elif phase == ProjectPhase.DEPLOYMENT:
            architecture = context.get("architecture", "")
            if architecture:
                tasks.append(create_infrastructure_task(architecture))

        return tasks

    def _parse_crew_result(self, result: Any) -> dict[str, Any]:
        """
        Parse CrewAI result into a dictionary.

        Args:
            result: CrewAI execution result

        Returns:
            Parsed result dictionary
        """
        # CrewAI returns different types depending on execution
        if hasattr(result, 'to_dict'):
            return result.to_dict()
        elif isinstance(result, str):
            return {"result": result}
        elif isinstance(result, dict):
            return result
        else:
            return {"result": str(result)}

    def map_crew_output_to_state(
        self,
        phase: ProjectPhase,
        crew_output: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Map crew output to workflow state context.

        Args:
            phase: Workflow phase
            crew_output: Output from crew execution

        Returns:
            Dictionary of context updates

        Example:
            >>> updates = integration.map_crew_output_to_state(
            ...     phase=ProjectPhase.REQUIREMENTS,
            ...     crew_output={"requirements": "..."}
            ... )
            >>> print(updates)
        """
        context_updates = {}

        if phase == ProjectPhase.REQUIREMENTS:
            if "requirements" in crew_output:
                context_updates["requirements"] = crew_output["requirements"]
            if "product_strategy" in crew_output:
                context_updates["product_strategy"] = crew_output["product_strategy"]

        elif phase == ProjectPhase.ARCHITECTURE:
            if "architecture" in crew_output:
                context_updates["architecture"] = crew_output["architecture"]
            if "technology_stack" in crew_output:
                context_updates["technology_stack"] = crew_output["technology_stack"]

        elif phase == ProjectPhase.IMPLEMENTATION:
            if "backend_code" in crew_output:
                context_updates["backend_code"] = crew_output["backend_code"]
            if "frontend_code" in crew_output:
                context_updates["frontend_code"] = crew_output["frontend_code"]

        elif phase == ProjectPhase.DEPLOYMENT:
            if "infrastructure" in crew_output:
                context_updates["infrastructure"] = crew_output["infrastructure"]
            if "cicd_config" in crew_output:
                context_updates["cicd_config"] = crew_output["cicd_config"]

        return context_updates
