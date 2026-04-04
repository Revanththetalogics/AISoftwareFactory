"""
Tests for Workflow components.
"""

import pytest

from backend.workflows.graph_builder import GraphBuilder
from backend.workflows.pipeline import Pipeline


class TestGraphBuilder:
    """Tests for GraphBuilder."""

    def test_add_node(self):
        """Test adding a node."""
        builder = GraphBuilder()

        async def action(state):
            return {"result": "done"}

        builder.add_node("node1", action)

        assert "node1" in builder._nodes
        assert builder._entry_point == "node1"

    def test_add_edge(self):
        """Test adding an edge."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("node1", action)
        builder.add_node("node2", action)
        builder.add_edge("node1", "node2")

        assert builder._nodes["node1"].transitions["default"] == "node2"

    @pytest.mark.asyncio
    async def test_execute_simple_graph(self):
        """Test executing a simple graph."""
        builder = GraphBuilder()

        async def action(state):
            state["executed"] = True
            return state

        builder.add_node("start", action)

        result = await builder.execute({"input": "test"})

        assert result["executed"] is True
        assert result["input"] == "test"


class TestPipeline:
    """Tests for Pipeline."""

    def test_add_step(self):
        """Test adding a step."""
        pipeline = Pipeline("test_pipeline")

        async def action(context):
            return {"result": "step1"}

        pipeline.add_step("step1", action)

        assert "step1" in pipeline._steps

    @pytest.mark.asyncio
    async def test_execute_pipeline(self):
        """Test executing a pipeline."""
        pipeline = Pipeline("test_pipeline")
        results = []

        async def step1_action(context):
            results.append("step1")
            return {"step1": "done"}

        async def step2_action(context):
            results.append("step2")
            return {"step2": "done"}

        pipeline.add_step("step1", step1_action)
        pipeline.add_step("step2", step2_action, dependencies=["step1"])

        result = await pipeline.execute()

        assert "step1" in results
        assert "step2" in results
        assert set(result["completed"]) == {"step1", "step2"}

    @pytest.mark.asyncio
    async def test_pipeline_with_failed_step(self):
        """Test pipeline execution with a failed step."""
        pipeline = Pipeline("test_pipeline")

        async def failing_action(context):
            raise ValueError("Step failed")

        async def dependent_action(context):
            return {"result": "should not run"}

        pipeline.add_step("failing", failing_action)
        pipeline.add_step("dependent", dependent_action, dependencies=["failing"])

        result = await pipeline.execute()

        assert "failing" in result["failed"]
        # Dependent step should be skipped
        step_status = result["steps"]["dependent"]["status"]
        assert step_status == "skipped"

    def test_get_status(self):
        """Test getting pipeline status."""
        pipeline = Pipeline("test_pipeline")

        async def action(context):
            return {}

        pipeline.add_step("step1", action)
        pipeline.add_step("step2", action)

        status = pipeline.get_status()

        assert status["pipeline"] == "test_pipeline"
        assert status["total_steps"] == 2
        assert status["pending"] == 2
