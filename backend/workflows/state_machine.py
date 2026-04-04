"""
State Machine for AI Software Factory Workflow Engine.

This module defines the workflow states, phases, and state transitions
for the project lifecycle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ProjectPhase(StrEnum):
    """
    Project lifecycle phases.

    These phases represent the complete software development lifecycle
    from idea to deployment.
    """

    IDEA = "idea"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"
    FAILED = "failed"


class PhaseStatus(StrEnum):
    """Status of a workflow phase."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseState:
    """
    State of a single phase in the workflow.

    Attributes:
        phase: The phase identifier
        status: Current status of the phase
        started_at: When the phase started
        completed_at: When the phase completed
        output: Phase output data
        error: Error message if phase failed
        metadata: Additional phase metadata
    """

    phase: ProjectPhase
    status: PhaseStatus = PhaseStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert phase state to dictionary."""
        return {
            "phase": self.phase.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class WorkflowState:
    """
    Complete state of a workflow execution.

    This class tracks the entire state of a project as it moves through
    the software development lifecycle.

    Attributes:
        project_id: Unique project identifier
        current_phase: Currently active phase
        phases: State of all phases
        context: Shared context across phases
        created_at: When the workflow was created
        updated_at: When the workflow was last updated
    """

    project_id: str
    current_phase: ProjectPhase = ProjectPhase.IDEA
    phases: dict[ProjectPhase, PhaseState] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize phase states if not provided."""
        if not self.phases:
            for phase in ProjectPhase:
                if phase not in (ProjectPhase.COMPLETE, ProjectPhase.FAILED):
                    self.phases[phase] = PhaseState(phase=phase)

    def get_phase_state(self, phase: ProjectPhase) -> PhaseState | None:
        """Get the state of a specific phase."""
        return self.phases.get(phase)

    def update_phase_status(
        self,
        phase: ProjectPhase,
        status: PhaseStatus,
        output: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """Update the status of a phase."""
        if phase not in self.phases:
            self.phases[phase] = PhaseState(phase=phase)

        phase_state = self.phases[phase]
        phase_state.status = status

        if status == PhaseStatus.IN_PROGRESS and not phase_state.started_at:
            phase_state.started_at = datetime.now()

        if status in (PhaseStatus.COMPLETED, PhaseStatus.FAILED, PhaseStatus.SKIPPED):
            phase_state.completed_at = datetime.now()

        if output:
            phase_state.output.update(output)

        if error:
            phase_state.error = error

        self.updated_at = datetime.now()

    def set_current_phase(self, phase: ProjectPhase) -> None:
        """Set the current active phase."""
        self.current_phase = phase
        self.updated_at = datetime.now()

    def add_to_context(self, key: str, value: Any) -> None:
        """Add data to the shared context."""
        self.context[key] = value
        self.updated_at = datetime.now()

    def get_from_context(self, key: str, default: Any = None) -> Any:
        """Get data from the shared context."""
        return self.context.get(key, default)

    def is_phase_completed(self, phase: ProjectPhase) -> bool:
        """Check if a phase is completed."""
        phase_state = self.phases.get(phase)
        return phase_state is not None and phase_state.status == PhaseStatus.COMPLETED

    def get_completed_phases(self) -> list[ProjectPhase]:
        """Get list of completed phases."""
        return [phase for phase, state in self.phases.items() if state.status == PhaseStatus.COMPLETED]

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow state to dictionary."""
        return {
            "project_id": self.project_id,
            "current_phase": self.current_phase.value,
            "phases": {phase.value: state.to_dict() for phase, state in self.phases.items()},
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Define valid phase transitions
VALID_TRANSITIONS: dict[ProjectPhase, list[ProjectPhase]] = {
    ProjectPhase.IDEA: [ProjectPhase.REQUIREMENTS, ProjectPhase.FAILED],
    ProjectPhase.REQUIREMENTS: [ProjectPhase.ARCHITECTURE, ProjectPhase.FAILED],
    ProjectPhase.ARCHITECTURE: [ProjectPhase.IMPLEMENTATION, ProjectPhase.FAILED],
    ProjectPhase.IMPLEMENTATION: [ProjectPhase.TESTING, ProjectPhase.FAILED],
    ProjectPhase.TESTING: [ProjectPhase.DEPLOYMENT, ProjectPhase.FAILED],
    ProjectPhase.DEPLOYMENT: [ProjectPhase.COMPLETE, ProjectPhase.FAILED],
    ProjectPhase.COMPLETE: [],
    ProjectPhase.FAILED: [],
}


def can_transition(from_phase: ProjectPhase, to_phase: ProjectPhase) -> bool:
    """
    Check if a phase transition is valid.

    Args:
        from_phase: Current phase
        to_phase: Target phase

    Returns:
        True if the transition is valid
    """
    return to_phase in VALID_TRANSITIONS.get(from_phase, [])


def get_next_phases(phase: ProjectPhase) -> list[ProjectPhase]:
    """
    Get valid next phases from the current phase.

    Args:
        phase: Current phase

    Returns:
        List of valid next phases
    """
    return VALID_TRANSITIONS.get(phase, [])
