"""
Graph builder for Workflow module.

This module provides LangGraph workflow construction for complex
agent orchestration and state management.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Node:
    """A node in the workflow graph."""
    name: str
    action: Callable
    transitions: dict[str, str]  # condition -> next_node


class GraphBuilder:
    """
    Graph builder for LangGraph workflows.

    Provides construction of stateful agent workflows with
    conditional transitions and state management.
    """

    def __init__(self):
        """Initialize the graph builder."""
        self._nodes: dict[str, Node] = {}
        self._entry_point: str | None = None
        self._logger = get_logger(__name__)

    def add_node(
        self,
        name: str,
        action: Callable,
        transitions: dict[str, str] | None = None
    ) -> 'GraphBuilder':
        """
        Add a node to the graph.

        Args:
            name: Node name
            action: Node action function
            transitions: Transition rules (condition -> next_node)

        Returns:
            Self for chaining
        """
        self._nodes[name] = Node(
            name=name,
            action=action,
            transitions=transitions or {}
        )

        if self._entry_point is None:
            self._entry_point = name

        self._logger.info("Node added", node_name=name)
        return self

    def set_entry_point(self, name: str) -> 'GraphBuilder':
        """
        Set the entry point node.

        Args:
            name: Entry node name

        Returns:
            Self for chaining
        """
        if name not in self._nodes:
            raise ValueError(f"Node '{name}' not found")

        self._entry_point = name
        return self

    def add_edge(self, from_node: str, to_node: str, condition: str = "default"):
        """
        Add an edge between nodes.

        Args:
            from_node: Source node
            to_node: Target node
            condition: Transition condition
        """
        if from_node not in self._nodes:
            raise ValueError(f"Node '{from_node}' not found")

        self._nodes[from_node].transitions[condition] = to_node

    async def execute(
        self,
        initial_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute the workflow graph.

        Args:
            initial_state: Initial workflow state

        Returns:
            Final workflow state
        """
        if not self._entry_point:
            raise ValueError("No entry point set")

        state = initial_state.copy()
        current_node_name = self._entry_point
        visited = set()

        while current_node_name:
            # Prevent infinite loops
            if current_node_name in visited:
                self._logger.warning(
                    "Loop detected in workflow",
                    node=current_node_name
                )
                break
            visited.add(current_node_name)

            node = self._nodes.get(current_node_name)
            if not node:
                self._logger.error("Node not found", node=current_node_name)
                break

            self._logger.info("Executing node", node_name=node.name)

            # Execute node action
            try:
                result = await node.action(state)
                state.update(result)
            except Exception as e:
                self._logger.error(
                    "Node execution failed",
                    node=node.name,
                    error=str(e)
                )
                state["error"] = str(e)
                break

            # Determine next node
            next_node = None
            for condition, target in node.transitions.items():
                if condition == "default":
                    next_node = target
                elif condition in state and state[condition]:
                    next_node = target
                    break

            current_node_name = next_node

        return state

    def get_graph_structure(self) -> dict[str, Any]:
        """Get the graph structure for visualization."""
        return {
            "entry_point": self._entry_point,
            "nodes": [
                {
                    "name": n.name,
                    "transitions": n.transitions
                }
                for n in self._nodes.values()
            ]
        }
