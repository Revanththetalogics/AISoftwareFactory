"""
Workflow Engine for AI Software Factory.

This module provides the workflow orchestration system using LangGraph
for state management and CrewAI for agent collaboration within phases.
"""

from backend.workflows.state_machine import WorkflowState, ProjectPhase
from backend.workflows.workflow_engine import WorkflowEngine
from backend.workflows.crew_integration import CrewIntegration

__all__ = [
    "WorkflowState",
    "ProjectPhase",
    "WorkflowEngine",
    "CrewIntegration",
]
