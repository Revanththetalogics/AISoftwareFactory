"""
Comprehensive tests for workflow service module.

Tests for WorkflowService covering all methods and edge cases.
"""

from unittest.mock import AsyncMock, patch

import pytest
from backend.models.workflow import Workflow, WorkflowStatus
from backend.services.workflow_service import WorkflowService


class TestWorkflowService:
    """Comprehensive tests for WorkflowService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = WorkflowService()

    @pytest.mark.asyncio
    async def test_create_workflow_basic(self):
        """Test basic workflow creation."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        assert workflow is not None
        assert workflow.name == "Test Workflow"
        assert workflow.project_id == "proj-123"
        assert workflow.status == WorkflowStatus.PENDING
        assert workflow.workflow_id is not None

    @pytest.mark.asyncio
    async def test_create_workflow_with_steps(self):
        """Test workflow creation with steps."""
        steps = [
            {"step_id": "s1", "name": "Step 1", "description": "First step"},
            {"step_id": "s2", "name": "Step 2", "description": "Second step"}
        ]

        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123",
            steps=steps
        )

        assert len(workflow.steps) == 2
        assert workflow.steps[0].step_id == "s1"
        assert workflow.steps[1].step_id == "s2"

    @pytest.mark.asyncio
    async def test_create_workflow_with_description(self):
        """Test workflow creation with description."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123",
            description="Test Description"
        )

        assert workflow.description == "Test Description"

    @pytest.mark.asyncio
    async def test_create_workflow_with_created_by(self):
        """Test workflow creation with creator."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123",
            created_by="user-001"
        )

        assert workflow.created_by == "user-001"

    @pytest.mark.asyncio
    async def test_get_workflow_existing(self):
        """Test getting an existing workflow."""
        created = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        retrieved = await self.service.get_workflow(created.workflow_id)

        assert retrieved is not None
        assert retrieved.workflow_id == created.workflow_id

    @pytest.mark.asyncio
    async def test_get_workflow_nonexistent(self):
        """Test getting a nonexistent workflow."""
        result = await self.service.get_workflow("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_workflows_all(self):
        """Test listing all workflows."""
        await self.service.create_workflow(name="WF1", project_id="proj-1")
        await self.service.create_workflow(name="WF2", project_id="proj-2")

        workflows = await self.service.list_workflows()

        assert len(workflows) == 2

    @pytest.mark.asyncio
    async def test_list_workflows_filter_by_project(self):
        """Test listing workflows filtered by project ID."""
        await self.service.create_workflow(name="WF1", project_id="proj-1")
        await self.service.create_workflow(name="WF2", project_id="proj-2")
        await self.service.create_workflow(name="WF3", project_id="proj-1")

        workflows = await self.service.list_workflows(project_id="proj-1")

        assert len(workflows) == 2
        assert all(w.project_id == "proj-1" for w in workflows)

    @pytest.mark.asyncio
    async def test_list_workflows_filter_by_status(self):
        """Test listing workflows filtered by status."""
        wf1 = await self.service.create_workflow(name="WF1", project_id="proj-1")
        await self.service.create_workflow(name="WF2", project_id="proj-2")

        # Update one workflow status
        wf1.status = WorkflowStatus.RUNNING

        workflows = await self.service.list_workflows(status=WorkflowStatus.RUNNING)

        assert len(workflows) == 1
        assert workflows[0].status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_list_workflows_filter_by_both(self):
        """Test listing workflows filtered by both project and status."""
        wf1 = await self.service.create_workflow(name="WF1", project_id="proj-1")
        await self.service.create_workflow(name="WF2", project_id="proj-1")
        wf3 = await self.service.create_workflow(name="WF3", project_id="proj-2")

        wf1.status = WorkflowStatus.RUNNING
        wf3.status = WorkflowStatus.RUNNING

        workflows = await self.service.list_workflows(
            project_id="proj-1",
            status=WorkflowStatus.RUNNING
        )

        assert len(workflows) == 1
        assert workflows[0].project_id == "proj-1"
        assert workflows[0].status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_start_workflow_success(self):
        """Test starting a workflow successfully."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        with patch.object(self.service._engine, 'run', new_callable=AsyncMock) as mock_run:
            result = await self.service.start_workflow(workflow.workflow_id)

            assert result is not None
            assert result.status == WorkflowStatus.RUNNING
            assert result.started_at is not None
            mock_run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_start_workflow_not_found(self):
        """Test starting a nonexistent workflow."""
        result = await self.service.start_workflow("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_start_workflow_cannot_execute(self):
        """Test starting a workflow that cannot be executed."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        # Set status to COMPLETED so it can't be executed
        workflow.status = WorkflowStatus.COMPLETED

        result = await self.service.start_workflow(workflow.workflow_id)

        assert result is not None
        assert result.status == WorkflowStatus.COMPLETED  # Status unchanged

    @pytest.mark.asyncio
    async def test_start_workflow_execution_fails(self):
        """Test workflow execution failure."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        with patch.object(self.service._engine, 'run', new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = Exception("Execution failed")

            result = await self.service.start_workflow(workflow.workflow_id)

            assert result is not None
            assert result.status == WorkflowStatus.FAILED

    @pytest.mark.asyncio
    async def test_update_workflow_status_success(self):
        """Test updating workflow status successfully."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        result = await self.service.update_workflow_status(
            workflow.workflow_id,
            "running"
        )

        assert result is not None
        assert result.status == WorkflowStatus.RUNNING

    @pytest.mark.asyncio
    async def test_update_workflow_status_not_found(self):
        """Test updating status of nonexistent workflow."""
        result = await self.service.update_workflow_status(
            "nonexistent-id",
            "running"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_workflow_status_invalid(self):
        """Test updating workflow with invalid status."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        result = await self.service.update_workflow_status(
            workflow.workflow_id,
            "invalid_status"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_workflow_success(self):
        """Test cancelling a workflow successfully."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        result = await self.service.cancel_workflow(workflow.workflow_id)

        assert result is not None
        assert result.status == WorkflowStatus.CANCELLED
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_cancel_workflow_not_found(self):
        """Test cancelling a nonexistent workflow."""
        result = await self.service.cancel_workflow("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_workflow_already_complete(self):
        """Test cancelling an already completed workflow."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        # Mark as completed
        workflow.status = WorkflowStatus.COMPLETED

        result = await self.service.cancel_workflow(workflow.workflow_id)

        assert result is not None
        assert result.status == WorkflowStatus.COMPLETED  # Unchanged

    @pytest.mark.asyncio
    async def test_cancel_workflow_already_failed(self):
        """Test cancelling an already failed workflow."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        workflow.status = WorkflowStatus.FAILED

        result = await self.service.cancel_workflow(workflow.workflow_id)

        assert result is not None
        assert result.status == WorkflowStatus.FAILED

    @pytest.mark.asyncio
    async def test_cancel_workflow_already_cancelled(self):
        """Test cancelling an already cancelled workflow."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        workflow.status = WorkflowStatus.CANCELLED

        result = await self.service.cancel_workflow(workflow.workflow_id)

        assert result is not None
        assert result.status == WorkflowStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_delete_workflow_success(self):
        """Test deleting a workflow successfully."""
        workflow = await self.service.create_workflow(
            name="Test Workflow",
            project_id="proj-123"
        )

        result = await self.service.delete_workflow(workflow.workflow_id)

        assert result is True

        # Verify deletion
        retrieved = await self.service.get_workflow(workflow.workflow_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self):
        """Test deleting a nonexistent workflow."""
        result = await self.service.delete_workflow("nonexistent-id")
        assert result is False


class TestWorkflowServiceInit:
    """Tests for WorkflowService initialization."""

    def test_init_creates_engine(self):
        """Test that initialization creates workflow engine."""
        service = WorkflowService()

        assert service._engine is not None
        assert service._workflows == {}
        assert service._logger is not None


class TestWorkflowModel:
    """Tests for Workflow model methods used by service."""

    def test_workflow_can_execute_pending(self):
        """Test can_execute returns True for PENDING status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.PENDING
        )

        assert workflow.can_execute() is True

    def test_workflow_can_execute_paused(self):
        """Test can_execute returns True for PAUSED status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.PAUSED
        )

        assert workflow.can_execute() is True

    def test_workflow_can_execute_running(self):
        """Test can_execute returns False for RUNNING status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.RUNNING
        )

        assert workflow.can_execute() is False

    def test_workflow_is_complete_completed(self):
        """Test is_complete returns True for COMPLETED status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.COMPLETED
        )

        assert workflow.is_complete() is True

    def test_workflow_is_complete_failed(self):
        """Test is_complete returns True for FAILED status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.FAILED
        )

        assert workflow.is_complete() is True

    def test_workflow_is_complete_cancelled(self):
        """Test is_complete returns True for CANCELLED status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.CANCELLED
        )

        assert workflow.is_complete() is True

    def test_workflow_is_complete_running(self):
        """Test is_complete returns False for RUNNING status."""
        workflow = Workflow(
            workflow_id="wf-123",
            name="Test",
            project_id="proj-123",
            status=WorkflowStatus.RUNNING
        )

        assert workflow.is_complete() is False
