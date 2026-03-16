"""
Tests for State Machine.
"""

import pytest
from datetime import datetime

from backend.workflows.state_machine import (
    ProjectPhase,
    PhaseStatus,
    PhaseState,
    WorkflowState,
    can_transition,
    get_next_phases,
)


class TestProjectPhase:
    """Test cases for ProjectPhase enum."""
    
    def test_phase_values(self):
        """Test phase enum values."""
        assert ProjectPhase.IDEA.value == "idea"
        assert ProjectPhase.REQUIREMENTS.value == "requirements"
        assert ProjectPhase.ARCHITECTURE.value == "architecture"
        assert ProjectPhase.IMPLEMENTATION.value == "implementation"
        assert ProjectPhase.TESTING.value == "testing"
        assert ProjectPhase.DEPLOYMENT.value == "deployment"
        assert ProjectPhase.COMPLETE.value == "complete"
        assert ProjectPhase.FAILED.value == "failed"


class TestPhaseState:
    """Test cases for PhaseState."""
    
    def test_phase_state_creation(self):
        """Test creating phase state."""
        state = PhaseState(phase=ProjectPhase.IDEA)
        
        assert state.phase == ProjectPhase.IDEA
        assert state.status == PhaseStatus.PENDING
        assert state.output == {}
    
    def test_phase_state_to_dict(self):
        """Test converting phase state to dict."""
        state = PhaseState(
            phase=ProjectPhase.IDEA,
            status=PhaseStatus.COMPLETED,
            output={"result": "success"},
        )
        
        result = state.to_dict()
        
        assert result["phase"] == "idea"
        assert result["status"] == "completed"
        assert result["output"] == {"result": "success"}


class TestWorkflowState:
    """Test cases for WorkflowState."""
    
    def test_workflow_state_creation(self):
        """Test creating workflow state."""
        state = WorkflowState(project_id="proj-123")
        
        assert state.project_id == "proj-123"
        assert state.current_phase == ProjectPhase.IDEA
        assert len(state.phases) > 0
    
    def test_get_phase_state(self):
        """Test getting phase state."""
        state = WorkflowState(project_id="proj-123")
        
        phase_state = state.get_phase_state(ProjectPhase.IDEA)
        
        assert phase_state is not None
        assert phase_state.phase == ProjectPhase.IDEA
    
    def test_update_phase_status(self):
        """Test updating phase status."""
        state = WorkflowState(project_id="proj-123")
        
        state.update_phase_status(
            ProjectPhase.IDEA,
            PhaseStatus.COMPLETED,
            output={"result": "success"},
        )
        
        phase_state = state.get_phase_state(ProjectPhase.IDEA)
        assert phase_state.status == PhaseStatus.COMPLETED
        assert phase_state.output == {"result": "success"}
        assert phase_state.completed_at is not None
    
    def test_set_current_phase(self):
        """Test setting current phase."""
        state = WorkflowState(project_id="proj-123")
        
        state.set_current_phase(ProjectPhase.REQUIREMENTS)
        
        assert state.current_phase == ProjectPhase.REQUIREMENTS
    
    def test_add_to_context(self):
        """Test adding to context."""
        state = WorkflowState(project_id="proj-123")
        
        state.add_to_context("key", "value")
        
        assert state.context["key"] == "value"
    
    def test_get_from_context(self):
        """Test getting from context."""
        state = WorkflowState(project_id="proj-123")
        state.add_to_context("key", "value")
        
        result = state.get_from_context("key")
        
        assert result == "value"
    
    def test_get_from_context_default(self):
        """Test getting from context with default."""
        state = WorkflowState(project_id="proj-123")
        
        result = state.get_from_context("missing", "default")
        
        assert result == "default"
    
    def test_is_phase_completed(self):
        """Test checking if phase is completed."""
        state = WorkflowState(project_id="proj-123")
        state.update_phase_status(ProjectPhase.IDEA, PhaseStatus.COMPLETED)
        
        assert state.is_phase_completed(ProjectPhase.IDEA) is True
        assert state.is_phase_completed(ProjectPhase.REQUIREMENTS) is False
    
    def test_get_completed_phases(self):
        """Test getting completed phases."""
        state = WorkflowState(project_id="proj-123")
        state.update_phase_status(ProjectPhase.IDEA, PhaseStatus.COMPLETED)
        state.update_phase_status(ProjectPhase.REQUIREMENTS, PhaseStatus.COMPLETED)
        
        completed = state.get_completed_phases()
        
        assert ProjectPhase.IDEA in completed
        assert ProjectPhase.REQUIREMENTS in completed
        assert ProjectPhase.ARCHITECTURE not in completed
    
    def test_to_dict(self):
        """Test converting to dict."""
        state = WorkflowState(project_id="proj-123")
        
        result = state.to_dict()
        
        assert result["project_id"] == "proj-123"
        assert result["current_phase"] == "idea"
        assert "phases" in result
        assert "context" in result


class TestTransitions:
    """Test cases for phase transitions."""
    
    def test_valid_transitions(self):
        """Test valid phase transitions."""
        assert can_transition(ProjectPhase.IDEA, ProjectPhase.REQUIREMENTS) is True
        assert can_transition(ProjectPhase.REQUIREMENTS, ProjectPhase.ARCHITECTURE) is True
        assert can_transition(ProjectPhase.ARCHITECTURE, ProjectPhase.IMPLEMENTATION) is True
        assert can_transition(ProjectPhase.IMPLEMENTATION, ProjectPhase.TESTING) is True
        assert can_transition(ProjectPhase.TESTING, ProjectPhase.DEPLOYMENT) is True
        assert can_transition(ProjectPhase.DEPLOYMENT, ProjectPhase.COMPLETE) is True
    
    def test_invalid_transitions(self):
        """Test invalid phase transitions."""
        assert can_transition(ProjectPhase.IDEA, ProjectPhase.COMPLETE) is False
        assert can_transition(ProjectPhase.COMPLETE, ProjectPhase.IDEA) is False
        assert can_transition(ProjectPhase.FAILED, ProjectPhase.IDEA) is False
    
    def test_get_next_phases(self):
        """Test getting next phases."""
        next_phases = get_next_phases(ProjectPhase.IDEA)
        
        assert ProjectPhase.REQUIREMENTS in next_phases
        assert ProjectPhase.FAILED in next_phases
