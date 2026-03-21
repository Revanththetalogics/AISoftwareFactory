"""
Comprehensive tests for WorkflowEngine module.

Covers all uncovered lines in workflow_engine.py:
- Lines 164-170, 222, 262-284, 288-322, 326-360, 364-381, 385-419, 459-461, 465-467, 471-473, 477-479, 483-485
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.workflows.state_machine import PhaseStatus, ProjectPhase, WorkflowState
from backend.workflows.workflow_engine import WorkflowEngine


class TestWorkflowEngine:
    """Comprehensive tests for WorkflowEngine."""

    def test_init(self):
        """Test WorkflowEngine initialization."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            assert engine.crew_integration is not None
            assert engine._graph is not None

    @pytest.mark.asyncio
    async def test_run_workflow_success(self):
        """Test successful workflow run."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            # Mock the crew integration methods that the graph nodes call
            # This is more reliable than mocking the graph itself
            with patch.object(engine.crew_integration, 'execute_crew', return_value=state):
                result = await engine.run(state)

            assert result.project_id == "test-123"

    @pytest.mark.asyncio
    async def test_run_workflow_exception(self):
        """Test workflow run with exception."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            # Mock the crew integration to raise exception
            with patch.object(engine.crew_integration, 'execute_crew', side_effect=RuntimeError("Workflow failed")):
                result = await engine.run(state)

            assert result.current_phase == ProjectPhase.FAILED
            assert (
                result.phases[ProjectPhase.FAILED].status == PhaseStatus.FAILED
            )

    @pytest.mark.asyncio
    async def test_run_phase_idea(self):
        """Test running a single idea phase."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine.run_phase(state, ProjectPhase.IDEA)

            assert result is not None

    @pytest.mark.asyncio
    async def test_run_phase_unknown(self):
        """Test running with unknown phase returns state unchanged."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            # COMPLETE phase is not in handlers
            result = await engine.run_phase(state, ProjectPhase.COMPLETE)

            assert result == state

    @pytest.mark.asyncio
    async def test_execute_idea_phase(self):
        """Test idea phase execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_idea_phase(state)

            assert result.phases[ProjectPhase.IDEA].status == PhaseStatus.COMPLETED
            assert result.current_phase == ProjectPhase.IDEA

    @pytest.mark.asyncio
    async def test_execute_requirements_phase_success(self):
        """Test requirements phase with successful crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": True,
                    "output": {"requirements": "User requirements doc"},
                }
            )
            mock_crew.map_crew_output_to_state = MagicMock(
                return_value={"requirements": "User requirements doc"}
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.add_to_context("idea", "Build a todo app")

            result = await engine._execute_requirements_phase(state)

            assert result.phases[ProjectPhase.REQUIREMENTS].status == PhaseStatus.COMPLETED
            assert result.context.get("requirements") == "User requirements doc"

    @pytest.mark.asyncio
    async def test_execute_requirements_phase_failure(self):
        """Test requirements phase with failed crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": False,
                    "error": "Crew execution failed",
                }
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_requirements_phase(state)

            assert result.phases[ProjectPhase.REQUIREMENTS].status == PhaseStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_architecture_phase_success(self):
        """Test architecture phase with successful crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": True,
                    "output": {"architecture": "System architecture"},
                }
            )
            mock_crew.map_crew_output_to_state = MagicMock(
                return_value={"architecture": "System architecture"}
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_architecture_phase(state)

            assert result.phases[ProjectPhase.ARCHITECTURE].status == PhaseStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_architecture_phase_failure(self):
        """Test architecture phase with failed crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": False,
                    "error": "Architecture design failed",
                }
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_architecture_phase(state)

            assert result.phases[ProjectPhase.ARCHITECTURE].status == PhaseStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_implementation_phase_success(self):
        """Test implementation phase with successful crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": True,
                    "output": {"backend_code": "code"},
                }
            )
            mock_crew.map_crew_output_to_state = MagicMock(
                return_value={"backend_code": "code"}
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_implementation_phase(state)

            assert result.phases[ProjectPhase.IMPLEMENTATION].status == PhaseStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_implementation_phase_failure(self):
        """Test implementation phase with failed crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": False,
                    "error": "Implementation failed",
                }
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_implementation_phase(state)

            assert result.phases[ProjectPhase.IMPLEMENTATION].status == PhaseStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_testing_phase(self):
        """Test testing phase execution (stub)."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_testing_phase(state)

            assert result.phases[ProjectPhase.TESTING].status == PhaseStatus.COMPLETED
            assert result.current_phase == ProjectPhase.TESTING

    @pytest.mark.asyncio
    async def test_execute_deployment_phase_success(self):
        """Test deployment phase with successful crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": True,
                    "output": {"infrastructure": "terraform configs"},
                }
            )
            mock_crew.map_crew_output_to_state = MagicMock(
                return_value={"infrastructure": "terraform configs"}
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_deployment_phase(state)

            assert result.phases[ProjectPhase.DEPLOYMENT].status == PhaseStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_deployment_phase_failure(self):
        """Test deployment phase with failed crew execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={
                    "success": False,
                    "error": "Deployment failed",
                }
            )
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_deployment_phase(state)

            assert result.phases[ProjectPhase.DEPLOYMENT].status == PhaseStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_complete_phase(self):
        """Test complete phase execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_complete_phase(state)

            assert result.current_phase == ProjectPhase.COMPLETE
            assert result.phases[ProjectPhase.COMPLETE].status == PhaseStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_failed_phase(self):
        """Test failed phase execution."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")

            result = await engine._execute_failed_phase(state)

            assert result.current_phase == ProjectPhase.FAILED

    def test_route_from_idea_success(self):
        """Test routing from idea phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.IDEA, PhaseStatus.COMPLETED)

            route = engine._route_from_idea(state)

            assert route == "requirements"

    def test_route_from_idea_failed(self):
        """Test routing from idea phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.IDEA, PhaseStatus.FAILED)

            route = engine._route_from_idea(state)

            assert route == "failed"

    def test_route_from_requirements_success(self):
        """Test routing from requirements phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.REQUIREMENTS, PhaseStatus.COMPLETED)

            route = engine._route_from_requirements(state)

            assert route == "architecture"

    def test_route_from_requirements_failed(self):
        """Test routing from requirements phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.REQUIREMENTS, PhaseStatus.FAILED)

            route = engine._route_from_requirements(state)

            assert route == "failed"

    def test_route_from_architecture_success(self):
        """Test routing from architecture phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.ARCHITECTURE, PhaseStatus.COMPLETED)

            route = engine._route_from_architecture(state)

            assert route == "implementation"

    def test_route_from_architecture_failed(self):
        """Test routing from architecture phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.ARCHITECTURE, PhaseStatus.FAILED)

            route = engine._route_from_architecture(state)

            assert route == "failed"

    def test_route_from_implementation_success(self):
        """Test routing from implementation phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(
                ProjectPhase.IMPLEMENTATION, PhaseStatus.COMPLETED
            )

            route = engine._route_from_implementation(state)

            assert route == "testing"

    def test_route_from_implementation_failed(self):
        """Test routing from implementation phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.IMPLEMENTATION, PhaseStatus.FAILED)

            route = engine._route_from_implementation(state)

            assert route == "failed"

    def test_route_from_testing_success(self):
        """Test routing from testing phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.TESTING, PhaseStatus.COMPLETED)

            route = engine._route_from_testing(state)

            assert route == "deployment"

    def test_route_from_testing_failed(self):
        """Test routing from testing phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.TESTING, PhaseStatus.FAILED)

            route = engine._route_from_testing(state)

            assert route == "failed"

    def test_route_from_deployment_success(self):
        """Test routing from deployment phase on success."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.DEPLOYMENT, PhaseStatus.COMPLETED)

            route = engine._route_from_deployment(state)

            assert route == "complete"

    def test_route_from_deployment_failed(self):
        """Test routing from deployment phase on failure."""
        with patch("backend.workflows.workflow_engine.CrewIntegration"):
            engine = WorkflowEngine()
            state = WorkflowState(project_id="test-123")
            state.update_phase_status(ProjectPhase.DEPLOYMENT, PhaseStatus.FAILED)

            route = engine._route_from_deployment(state)

            assert route == "failed"

    @pytest.mark.asyncio
    async def test_run_phase_all_phases(self):
        """Test running all phase types through run_phase."""
        with patch("backend.workflows.workflow_engine.CrewIntegration") as mock_crew_cls:
            mock_crew = MagicMock()
            mock_crew.execute_phase = AsyncMock(
                return_value={"success": True, "output": {}}
            )
            mock_crew.map_crew_output_to_state = MagicMock(return_value={})
            mock_crew_cls.return_value = mock_crew

            engine = WorkflowEngine()

            phases_to_test = [
                ProjectPhase.IDEA,
                ProjectPhase.REQUIREMENTS,
                ProjectPhase.ARCHITECTURE,
                ProjectPhase.IMPLEMENTATION,
                ProjectPhase.TESTING,
                ProjectPhase.DEPLOYMENT,
            ]

            for phase in phases_to_test:
                state = WorkflowState(project_id="test-123")
                result = await engine.run_phase(state, phase)
                assert result is not None
