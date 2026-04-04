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


class TestPipelineExtendedCoverage:
    """Tests for Pipeline - line 186 (sync function execution)."""

    @pytest.fixture
    def pipeline(self):
        """Create a Pipeline instance."""
        from backend.workflows.pipeline import Pipeline

        return Pipeline(name="test_pipeline")

    @pytest.mark.asyncio
    async def test_execute_step_sync_function_line_186(self, pipeline):
        """Test line 186: sync function execution in _execute_step."""

        # Define a sync (non-async) function for the step
        def sync_step_action(context):
            return {"result": "sync_result", "value": context.get("input", 0) * 2}

        # Add a sync step
        pipeline.add_step(
            name="sync_step",
            action=sync_step_action,
        )

        # Execute the pipeline
        result = await pipeline.execute(context={"input": 5})

        # Line 186: sync function should be executed correctly
        assert result["steps"]["sync_step"]["result"]["result"] == "sync_result"
        assert result["steps"]["sync_step"]["result"]["value"] == 10

    @pytest.mark.asyncio
    async def test_execute_step_async_function(self, pipeline):
        """Test async function execution in _execute_step."""

        # Define an async function for the step
        async def async_step_action(context):
            return {"result": "async_result"}

        pipeline.add_step(
            name="async_step",
            action=async_step_action,
        )

        result = await pipeline.execute(context={})

        # Line 184: async function should be awaited
        assert result["steps"]["async_step"]["result"]["result"] == "async_result"

    @pytest.mark.asyncio
    async def test_execute_step_mixed_functions(self, pipeline):
        """Test pipeline with both sync and async functions."""

        def sync_action(context):
            return {"type": "sync"}

        async def async_action(context):
            return {"type": "async"}

        pipeline.add_step(name="first", action=sync_action)
        pipeline.add_step(name="second", action=async_action)

        result = await pipeline.execute(context={})

        assert result["steps"]["first"]["result"]["type"] == "sync"
        assert result["steps"]["second"]["result"]["type"] == "async"

    def test_get_status(self, pipeline):
        """Test get_status method."""
        pipeline.add_step(name="step1", action=lambda ctx: {})
        pipeline.add_step(name="step2", action=lambda ctx: {})

        status = pipeline.get_status()

        assert status["pipeline"] == "test_pipeline"
        assert status["total_steps"] == 2
