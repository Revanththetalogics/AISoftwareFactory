"""
Tests for Workflow Engine.
"""

import pytest

from backend.workflows.state_machine import PhaseStatus, ProjectPhase, WorkflowState
from backend.workflows.workflow_engine import WorkflowEngine


class TestWorkflowEngine:
    """Test cases for WorkflowEngine."""

    def setup_method(self):
        """Create fresh engine for each test."""
        self.engine = WorkflowEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine.crew_integration is not None
        assert self.engine._graph is not None

    @pytest.mark.asyncio
    async def test_run_workflow(self):
        """Test running complete workflow."""
        state = WorkflowState(project_id="test-proj-123")

        # Note: This will run through the workflow
        # In a real test with mocked CrewAI, we'd verify all phases
        # For now, we just verify the engine runs without errors
        final_state = await self.engine.run(state)

        assert final_state is not None
        assert final_state.project_id == "test-proj-123"

    @pytest.mark.asyncio
    async def test_run_single_phase_idea(self):
        """Test running single phase (idea)."""
        state = WorkflowState(project_id="test-proj-123")

        result = await self.engine.run_phase(state, ProjectPhase.IDEA)

        assert result.current_phase == ProjectPhase.IDEA
        assert result.is_phase_completed(ProjectPhase.IDEA)

    def test_phase_routing(self):
        """Test phase routing logic."""
        # Test routing from idea
        state = WorkflowState(project_id="test-proj-123")
        state.update_phase_status(ProjectPhase.IDEA, PhaseStatus.COMPLETED)

        next_step = self.engine._route_from_idea(state)
        assert next_step == "requirements"

        # Test routing to failed
        state2 = WorkflowState(project_id="test-proj-456")
        state2.update_phase_status(ProjectPhase.IDEA, PhaseStatus.FAILED)

        next_step = self.engine._route_from_idea(state2)
        assert next_step == "failed"


class TestWorkflowEnginePhases:
    """Test cases for individual phase execution."""

    def setup_method(self):
        """Create fresh engine for each test."""
        self.engine = WorkflowEngine()

    @pytest.mark.asyncio
    async def test_execute_idea_phase(self):
        """Test executing idea phase."""
        state = WorkflowState(project_id="test-proj")

        result = await self.engine._execute_idea_phase(state)

        assert result.is_phase_completed(ProjectPhase.IDEA)
        assert result.current_phase == ProjectPhase.IDEA

    @pytest.mark.asyncio
    async def test_execute_complete_phase(self):
        """Test executing complete phase."""
        state = WorkflowState(project_id="test-proj")

        result = await self.engine._execute_complete_phase(state)

        assert result.current_phase == ProjectPhase.COMPLETE

    @pytest.mark.asyncio
    async def test_execute_failed_phase(self):
        """Test executing failed phase."""
        state = WorkflowState(project_id="test-proj")
        state.set_current_phase(ProjectPhase.IMPLEMENTATION)

        result = await self.engine._execute_failed_phase(state)

        assert result.current_phase == ProjectPhase.FAILED
