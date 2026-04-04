"""
Comprehensive tests for GraphBuilder module.

Covers all uncovered lines in graph_builder.py:
- Lines 77-81, 93, 111, 120-124, 129-130, 138-145, 150-154, 162
"""

import pytest

from backend.workflows.graph_builder import GraphBuilder, Node


class TestGraphBuilderComprehensive:
    """Comprehensive tests for GraphBuilder class."""

    def test_node_dataclass(self):
        """Test Node dataclass creation."""

        async def action(state):
            return state

        node = Node(
            name="test_node",
            action=action,
            transitions={"default": "next_node"},
        )

        assert node.name == "test_node"
        assert node.action == action
        assert node.transitions["default"] == "next_node"

    def test_init(self):
        """Test GraphBuilder initialization."""
        builder = GraphBuilder()

        assert builder._nodes == {}
        assert builder._entry_point is None
        assert builder._logger is not None

    def test_add_node_first_node_sets_entry_point(self):
        """Test that first node becomes entry point."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("first_node", action)

        assert builder._entry_point == "first_node"

    def test_add_node_with_transitions(self):
        """Test adding node with transitions."""
        builder = GraphBuilder()

        async def action(state):
            return state

        transitions = {"success": "node_b", "failure": "node_c"}
        builder.add_node("node_a", action, transitions=transitions)

        assert builder._nodes["node_a"].transitions == transitions

    def test_add_node_returns_self_for_chaining(self):
        """Test that add_node returns self for chaining."""
        builder = GraphBuilder()

        async def action(state):
            return state

        result = builder.add_node("node", action)

        assert result is builder

    def test_set_entry_point_success(self):
        """Test setting entry point to existing node."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("node_a", action)
        builder.add_node("node_b", action)

        result = builder.set_entry_point("node_b")

        assert builder._entry_point == "node_b"
        assert result is builder

    def test_set_entry_point_not_found(self):
        """Test setting entry point to non-existent node raises error."""
        builder = GraphBuilder()

        with pytest.raises(ValueError, match="Node 'unknown' not found"):
            builder.set_entry_point("unknown")

    def test_add_edge_success(self):
        """Test adding edge between nodes."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("node_a", action)
        builder.add_node("node_b", action)
        builder.add_edge("node_a", "node_b", condition="default")

        assert builder._nodes["node_a"].transitions["default"] == "node_b"

    def test_add_edge_from_node_not_found(self):
        """Test adding edge from non-existent node raises error."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("node_b", action)

        with pytest.raises(ValueError, match="Node 'unknown' not found"):
            builder.add_edge("unknown", "node_b")

    def test_add_edge_custom_condition(self):
        """Test adding edge with custom condition."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("node_a", action)
        builder.add_node("node_b", action)
        builder.add_edge("node_a", "node_b", condition="on_success")

        assert builder._nodes["node_a"].transitions["on_success"] == "node_b"

    @pytest.mark.asyncio
    async def test_execute_no_entry_point(self):
        """Test execute without entry point raises error."""
        builder = GraphBuilder()

        with pytest.raises(ValueError, match="No entry point set"):
            await builder.execute({"input": "test"})

    @pytest.mark.asyncio
    async def test_execute_single_node(self):
        """Test executing single node graph."""
        builder = GraphBuilder()

        async def action(state):
            state["processed"] = True
            return state

        builder.add_node("only_node", action)

        result = await builder.execute({"input": "test"})

        assert result["processed"] is True
        assert result["input"] == "test"

    @pytest.mark.asyncio
    async def test_execute_linear_graph(self):
        """Test executing linear graph with multiple nodes."""
        builder = GraphBuilder()
        execution_order = []

        async def action_a(state):
            execution_order.append("a")
            return {"step": "a"}

        async def action_b(state):
            execution_order.append("b")
            return {"step": "b"}

        async def action_c(state):
            execution_order.append("c")
            return {"step": "c"}

        builder.add_node("a", action_a)
        builder.add_node("b", action_b)
        builder.add_node("c", action_c)
        builder.add_edge("a", "b")
        builder.add_edge("b", "c")

        result = await builder.execute({})

        assert execution_order == ["a", "b", "c"]
        assert result["step"] == "c"

    @pytest.mark.asyncio
    async def test_execute_with_condition_routing(self):
        """Test conditional routing based on state."""
        builder = GraphBuilder()

        async def start_action(state):
            return {"should_branch": True}

        async def branch_a_action(state):
            return {"branch": "a"}

        async def branch_b_action(state):
            return {"branch": "b"}

        builder.add_node("start", start_action, transitions={"should_branch": "branch_a", "default": "branch_b"})
        builder.add_node("branch_a", branch_a_action)
        builder.add_node("branch_b", branch_b_action)

        result = await builder.execute({})

        assert result["branch"] == "a"

    @pytest.mark.asyncio
    async def test_execute_default_transition(self):
        """Test default transition when no condition matches."""
        builder = GraphBuilder()

        async def start_action(state):
            return {"other_flag": True}

        async def next_action(state):
            return {"reached": "default"}

        builder.add_node("start", start_action, transitions={"nonexistent": "nowhere", "default": "next"})
        builder.add_node("next", next_action)

        result = await builder.execute({})

        assert result["reached"] == "default"

    @pytest.mark.asyncio
    async def test_execute_loop_detection(self):
        """Test that loop detection prevents infinite loops."""
        builder = GraphBuilder()
        call_count = [0]

        async def loop_action(state):
            call_count[0] += 1
            return {"count": call_count[0]}

        builder.add_node("loop_node", loop_action, transitions={"default": "loop_node"})

        await builder.execute({})

        # Should only execute once due to loop detection
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_execute_node_not_found_during_execution(self):
        """Test handling of missing node during execution."""
        builder = GraphBuilder()

        async def action(state):
            return {"done": True}

        builder.add_node("start", action, transitions={"default": "missing_node"})

        result = await builder.execute({})

        # Should stop when node is not found
        assert result["done"] is True

    @pytest.mark.asyncio
    async def test_execute_node_exception(self):
        """Test handling of exception during node execution."""
        builder = GraphBuilder()

        async def failing_action(state):
            raise RuntimeError("Node failed")

        builder.add_node("failing", failing_action)

        result = await builder.execute({})

        assert "error" in result
        assert "Node failed" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_preserves_initial_state(self):
        """Test that initial state is copied, not modified."""
        builder = GraphBuilder()

        async def action(state):
            state["modified"] = True
            return state

        builder.add_node("modifier", action)

        initial_state = {"original": "value"}
        result = await builder.execute(initial_state)

        # Original state should not be modified
        assert "modified" not in initial_state
        assert result["modified"] is True

    @pytest.mark.asyncio
    async def test_execute_complex_routing(self):
        """Test complex routing with multiple conditions."""
        builder = GraphBuilder()

        async def start(state):
            return {"flag_a": False, "flag_b": True}

        async def action_a(state):
            return {"path": "a"}

        async def action_b(state):
            return {"path": "b"}

        async def action_default(state):
            return {"path": "default"}

        builder.add_node(
            "start",
            start,
            transitions={
                "flag_a": "action_a",
                "flag_b": "action_b",
                "default": "action_default",
            },
        )
        builder.add_node("action_a", action_a)
        builder.add_node("action_b", action_b)
        builder.add_node("action_default", action_default)

        result = await builder.execute({})

        # flag_b is True, should take that path
        assert result["path"] == "b"

    def test_get_graph_structure(self):
        """Test getting graph structure for visualization."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("start", action, transitions={"default": "end"})
        builder.add_node("end", action)

        structure = builder.get_graph_structure()

        assert structure["entry_point"] == "start"
        assert len(structure["nodes"]) == 2

        node_names = [n["name"] for n in structure["nodes"]]
        assert "start" in node_names
        assert "end" in node_names

        start_node = next(n for n in structure["nodes"] if n["name"] == "start")
        assert start_node["transitions"]["default"] == "end"

    def test_get_graph_structure_empty(self):
        """Test getting structure of empty graph."""
        builder = GraphBuilder()

        structure = builder.get_graph_structure()

        assert structure["entry_point"] is None
        assert structure["nodes"] == []

    def test_add_multiple_transitions(self):
        """Test adding multiple transitions to same node."""
        builder = GraphBuilder()

        async def action(state):
            return state

        builder.add_node("hub", action)
        builder.add_node("branch_1", action)
        builder.add_node("branch_2", action)
        builder.add_node("branch_3", action)

        builder.add_edge("hub", "branch_1", condition="condition_1")
        builder.add_edge("hub", "branch_2", condition="condition_2")
        builder.add_edge("hub", "branch_3", condition="default")

        transitions = builder._nodes["hub"].transitions
        assert transitions["condition_1"] == "branch_1"
        assert transitions["condition_2"] == "branch_2"
        assert transitions["default"] == "branch_3"

    @pytest.mark.asyncio
    async def test_execute_state_accumulation(self):
        """Test that state accumulates across nodes."""
        builder = GraphBuilder()

        async def add_a(state):
            return {"a": "value_a"}

        async def add_b(state):
            return {"b": "value_b"}

        async def add_c(state):
            return {"c": "value_c"}

        builder.add_node("node_a", add_a, transitions={"default": "node_b"})
        builder.add_node("node_b", add_b, transitions={"default": "node_c"})
        builder.add_node("node_c", add_c)

        result = await builder.execute({"initial": "data"})

        assert result["initial"] == "data"
        assert result["a"] == "value_a"
        assert result["b"] == "value_b"
        assert result["c"] == "value_c"

    def test_chaining_operations(self):
        """Test method chaining for building graphs."""
        builder = GraphBuilder()

        async def action(state):
            return state

        result = (
            builder.add_node("start", action)
            .add_node("middle", action)
            .add_node("end", action)
            .set_entry_point("start")
        )

        assert result is builder
        assert len(builder._nodes) == 3
        assert builder._entry_point == "start"
