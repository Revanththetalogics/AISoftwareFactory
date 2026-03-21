"""
Workflow Engine using LangGraph for AI Software Factory.

This module provides the core workflow orchestration using LangGraph's StateGraph
for managing the software development lifecycle.
"""


from langgraph.graph import END, StateGraph

from backend.core.logging import get_logger
from backend.workflows.crew_integration import CrewIntegration
from backend.workflows.state_machine import (
    PhaseStatus,
    ProjectPhase,
    WorkflowState,
)

logger = get_logger(__name__)


class WorkflowEngine:
    """
    Workflow engine for orchestrating the software development lifecycle.

    This engine uses LangGraph's StateGraph to manage workflow states and
    transitions, integrating with CrewAI for agent collaboration within phases.

    Attributes:
        crew_integration: Integration layer for CrewAI
        graph: Compiled LangGraph StateGraph

    Example:
        >>> engine = WorkflowEngine()
        >>> state = WorkflowState(project_id="proj-123")
        >>> final_state = await engine.run(state)
    """

    def __init__(self):
        """Initialize the workflow engine."""
        self.crew_integration = CrewIntegration()
        self._graph = self._build_graph()
        self._logger = get_logger(__name__)
        self._logger.info("Workflow engine initialized")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph for the workflow.

        Returns:
            Compiled StateGraph
        """
        # Create state graph
        workflow = StateGraph(WorkflowState)

        # Add nodes for each phase
        workflow.add_node("idea", self._execute_idea_phase)
        workflow.add_node("requirements", self._execute_requirements_phase)
        workflow.add_node("architecture", self._execute_architecture_phase)
        workflow.add_node("implementation", self._execute_implementation_phase)
        workflow.add_node("testing", self._execute_testing_phase)
        workflow.add_node("deployment", self._execute_deployment_phase)
        workflow.add_node("complete", self._execute_complete_phase)
        workflow.add_node("failed", self._execute_failed_phase)

        # Add edges with conditional routing
        workflow.add_conditional_edges(
            "idea",
            self._route_from_idea,
            {
                "requirements": "requirements",
                "failed": "failed",
            }
        )

        workflow.add_conditional_edges(
            "requirements",
            self._route_from_requirements,
            {
                "architecture": "architecture",
                "failed": "failed",
            }
        )

        workflow.add_conditional_edges(
            "architecture",
            self._route_from_architecture,
            {
                "implementation": "implementation",
                "failed": "failed",
            }
        )

        workflow.add_conditional_edges(
            "implementation",
            self._route_from_implementation,
            {
                "testing": "testing",
                "failed": "failed",
            }
        )

        workflow.add_conditional_edges(
            "testing",
            self._route_from_testing,
            {
                "deployment": "deployment",
                "failed": "failed",
            }
        )

        workflow.add_conditional_edges(
            "deployment",
            self._route_from_deployment,
            {
                "complete": "complete",
                "failed": "failed",
            }
        )

        # Terminal states
        workflow.add_edge("complete", END)
        workflow.add_edge("failed", END)

        # Set entry point
        workflow.set_entry_point("idea")

        return workflow.compile()

    async def run(
        self,
        state: WorkflowState,
        max_iterations: int = 100,
    ) -> WorkflowState:
        """
        Run the workflow from the current state.

        Args:
            state: Initial workflow state
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            Final workflow state

        Example:
            >>> engine = WorkflowEngine()
            >>> initial_state = WorkflowState(project_id="proj-123")
            >>> final_state = await engine.run(initial_state)
            >>> print(final_state.current_phase)
        """
        self._logger.info(
            "Starting workflow execution",
            project_id=state.project_id,
            current_phase=state.current_phase.value,
        )

        try:
            # Execute the graph using LangGraph's standard invoke pattern
            # LangGraph 0.0.40 uses sync invoke() method
            import asyncio

            # Run sync invoke() in async executor since we're in async context
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._graph.invoke(
                    state,
                    {"recursion_limit": max_iterations}
                )
            )

            self._logger.info(
                "Workflow execution completed",
                project_id=result.project_id,
                final_phase=result.current_phase.value,
            )

            return result

        except Exception as exc:
            self._logger.error(
                "Workflow execution failed",
                project_id=state.project_id,
                error=str(exc),
            )
            # Mark as failed
            state.set_current_phase(ProjectPhase.FAILED)
            state.update_phase_status(
                ProjectPhase.FAILED,
                PhaseStatus.FAILED,
                error=str(exc),
            )
            return state

    async def run_phase(
        self,
        state: WorkflowState,
        phase: ProjectPhase,
    ) -> WorkflowState:
        """
        Run a single workflow phase.

        Args:
            state: Current workflow state
            phase: Phase to execute

        Returns:
            Updated workflow state
        """
        self._logger.info(
            "Executing single phase",
            project_id=state.project_id,
            phase=phase.value,
        )

        # Map phase to node function
        phase_handlers = {
            ProjectPhase.IDEA: self._execute_idea_phase,
            ProjectPhase.REQUIREMENTS: self._execute_requirements_phase,
            ProjectPhase.ARCHITECTURE: self._execute_architecture_phase,
            ProjectPhase.IMPLEMENTATION: self._execute_implementation_phase,
            ProjectPhase.TESTING: self._execute_testing_phase,
            ProjectPhase.DEPLOYMENT: self._execute_deployment_phase,
        }

        handler = phase_handlers.get(phase)
        if handler:
            return await handler(state)

        return state

    # Phase execution handlers

    async def _execute_idea_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the idea phase."""
        self._logger.info("Executing idea phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.IDEA,
            PhaseStatus.IN_PROGRESS,
        )

        # Idea phase is typically just initialization
        # In a real implementation, this might validate the idea

        state.update_phase_status(
            ProjectPhase.IDEA,
            PhaseStatus.COMPLETED,
            output={"message": "Idea phase completed"},
        )

        state.set_current_phase(ProjectPhase.IDEA)
        return state

    async def _execute_requirements_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the requirements phase with CrewAI."""
        self._logger.info("Executing requirements phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.REQUIREMENTS,
            PhaseStatus.IN_PROGRESS,
        )

        # Execute with CrewAI
        result = await self.crew_integration.execute_phase(
            ProjectPhase.REQUIREMENTS,
            state.context,
        )

        if result["success"]:
            # Map output to state context
            context_updates = self.crew_integration.map_crew_output_to_state(
                ProjectPhase.REQUIREMENTS,
                result["output"],
            )
            for key, value in context_updates.items():
                state.add_to_context(key, value)

            state.update_phase_status(
                ProjectPhase.REQUIREMENTS,
                PhaseStatus.COMPLETED,
                output=result["output"],
            )
        else:
            state.update_phase_status(
                ProjectPhase.REQUIREMENTS,
                PhaseStatus.FAILED,
                error=result.get("error", "Unknown error"),
            )

        state.set_current_phase(ProjectPhase.REQUIREMENTS)
        return state

    async def _execute_architecture_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the architecture phase with CrewAI."""
        self._logger.info("Executing architecture phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.ARCHITECTURE,
            PhaseStatus.IN_PROGRESS,
        )

        # Execute with CrewAI
        result = await self.crew_integration.execute_phase(
            ProjectPhase.ARCHITECTURE,
            state.context,
        )

        if result["success"]:
            context_updates = self.crew_integration.map_crew_output_to_state(
                ProjectPhase.ARCHITECTURE,
                result["output"],
            )
            for key, value in context_updates.items():
                state.add_to_context(key, value)

            state.update_phase_status(
                ProjectPhase.ARCHITECTURE,
                PhaseStatus.COMPLETED,
                output=result["output"],
            )
        else:
            state.update_phase_status(
                ProjectPhase.ARCHITECTURE,
                PhaseStatus.FAILED,
                error=result.get("error", "Unknown error"),
            )

        state.set_current_phase(ProjectPhase.ARCHITECTURE)
        return state

    async def _execute_implementation_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the implementation phase with CrewAI."""
        self._logger.info("Executing implementation phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.IMPLEMENTATION,
            PhaseStatus.IN_PROGRESS,
        )

        # Execute with CrewAI
        result = await self.crew_integration.execute_phase(
            ProjectPhase.IMPLEMENTATION,
            state.context,
        )

        if result["success"]:
            context_updates = self.crew_integration.map_crew_output_to_state(
                ProjectPhase.IMPLEMENTATION,
                result["output"],
            )
            for key, value in context_updates.items():
                state.add_to_context(key, value)

            state.update_phase_status(
                ProjectPhase.IMPLEMENTATION,
                PhaseStatus.COMPLETED,
                output=result["output"],
            )
        else:
            state.update_phase_status(
                ProjectPhase.IMPLEMENTATION,
                PhaseStatus.FAILED,
                error=result.get("error", "Unknown error"),
            )

        state.set_current_phase(ProjectPhase.IMPLEMENTATION)
        return state

    async def _execute_testing_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the testing phase."""
        self._logger.info("Executing testing phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.TESTING,
            PhaseStatus.IN_PROGRESS,
        )

        # Testing phase - stub for now
        # In Phase 6, this will integrate with Simulation Layer

        state.update_phase_status(
            ProjectPhase.TESTING,
            PhaseStatus.COMPLETED,
            output={"message": "Testing phase completed (stub)"},
        )

        state.set_current_phase(ProjectPhase.TESTING)
        return state

    async def _execute_deployment_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the deployment phase with CrewAI."""
        self._logger.info("Executing deployment phase", project_id=state.project_id)

        state.update_phase_status(
            ProjectPhase.DEPLOYMENT,
            PhaseStatus.IN_PROGRESS,
        )

        # Execute with CrewAI
        result = await self.crew_integration.execute_phase(
            ProjectPhase.DEPLOYMENT,
            state.context,
        )

        if result["success"]:
            context_updates = self.crew_integration.map_crew_output_to_state(
                ProjectPhase.DEPLOYMENT,
                result["output"],
            )
            for key, value in context_updates.items():
                state.add_to_context(key, value)

            state.update_phase_status(
                ProjectPhase.DEPLOYMENT,
                PhaseStatus.COMPLETED,
                output=result["output"],
            )
        else:
            state.update_phase_status(
                ProjectPhase.DEPLOYMENT,
                PhaseStatus.FAILED,
                error=result.get("error", "Unknown error"),
            )

        state.set_current_phase(ProjectPhase.DEPLOYMENT)
        return state

    async def _execute_complete_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the complete phase."""
        self._logger.info(
            "Project completed successfully",
            project_id=state.project_id,
        )

        state.set_current_phase(ProjectPhase.COMPLETE)
        state.update_phase_status(
            ProjectPhase.COMPLETE,
            PhaseStatus.COMPLETED,
            output={"message": "Project completed successfully"},
        )

        return state

    async def _execute_failed_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute the failed phase."""
        self._logger.error(
            "Project failed",
            project_id=state.project_id,
            failed_phase=state.current_phase.value,
        )

        state.set_current_phase(ProjectPhase.FAILED)

        return state

    # Routing functions

    def _route_from_idea(self, state: WorkflowState) -> str:
        """Determine next step from idea phase."""
        if state.phases[ProjectPhase.IDEA].status == PhaseStatus.FAILED:
            return "failed"
        return "requirements"

    def _route_from_requirements(self, state: WorkflowState) -> str:
        """Determine next step from requirements phase."""
        if state.phases[ProjectPhase.REQUIREMENTS].status == PhaseStatus.FAILED:
            return "failed"
        return "architecture"

    def _route_from_architecture(self, state: WorkflowState) -> str:
        """Determine next step from architecture phase."""
        if state.phases[ProjectPhase.ARCHITECTURE].status == PhaseStatus.FAILED:
            return "failed"
        return "implementation"

    def _route_from_implementation(self, state: WorkflowState) -> str:
        """Determine next step from implementation phase."""
        if state.phases[ProjectPhase.IMPLEMENTATION].status == PhaseStatus.FAILED:
            return "failed"
        return "testing"

    def _route_from_testing(self, state: WorkflowState) -> str:
        """Determine next step from testing phase."""
        if state.phases[ProjectPhase.TESTING].status == PhaseStatus.FAILED:
            return "failed"
        return "deployment"

    def _route_from_deployment(self, state: WorkflowState) -> str:
        """Determine next step from deployment phase."""
        if state.phases[ProjectPhase.DEPLOYMENT].status == PhaseStatus.FAILED:
            return "failed"
        return "complete"
