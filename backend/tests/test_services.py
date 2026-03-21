"""
Tests for service layer.
"""


import pytest

from backend.services.project_service import ProjectService
from backend.services.workflow_service import WorkflowService


class TestProjectService:
    """Tests for ProjectService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = ProjectService()

    @pytest.mark.asyncio
    async def test_create_project(self, sample_project_data):
        """Test project creation."""
        project = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        assert project["name"] == sample_project_data["name"]
        assert project["description"] == sample_project_data["description"]
        assert project["status"] == "draft"
        assert project["id"] is not None

    @pytest.mark.asyncio
    async def test_get_project(self, sample_project_data):
        """Test getting a project by ID."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )
        retrieved = await self.service.get_project(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["name"] == sample_project_data["name"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self):
        """Test getting a project that doesn't exist."""
        result = await self.service.get_project("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_projects(self, sample_project_data):
        """Test listing all projects."""
        await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )
        await self.service.create_project(
            name="Project 2",
            description="Another project"
        )

        projects = await self.service.list_projects()
        assert len(projects) == 2

    @pytest.mark.asyncio
    async def test_update_project(self, sample_project_data):
        """Test updating a project."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        updated = await self.service.update_project(
            created["id"],
            {"name": "Updated Name"}
        )

        assert updated is not None
        assert updated["name"] == "Updated Name"
        assert updated["description"] == sample_project_data["description"]

    @pytest.mark.asyncio
    async def test_delete_project(self, sample_project_data):
        """Test deleting a project."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        result = await self.service.delete_project(created["id"])
        assert result is True

        # Verify deletion
        retrieved = await self.service.get_project(created["id"])
        assert retrieved is None


class TestWorkflowService:
    """Tests for WorkflowService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = WorkflowService()

    @pytest.mark.asyncio
    async def test_create_workflow(self, sample_workflow_data):
        """Test workflow creation."""
        workflow = await self.service.create_workflow(
            name=sample_workflow_data["name"],
            project_id="proj-123"
        )

        assert workflow.name == sample_workflow_data["name"]
        assert workflow.workflow_id is not None

    @pytest.mark.asyncio
    async def test_get_workflow(self, sample_workflow_data):
        """Test getting a workflow by ID."""
        created = await self.service.create_workflow(
            name=sample_workflow_data["name"],
            project_id="proj-123"
        )
        retrieved = await self.service.get_workflow(created.workflow_id)

        assert retrieved is not None
        assert retrieved.workflow_id == created.workflow_id

    @pytest.mark.asyncio
    async def test_update_workflow_status(self, sample_workflow_data):
        """Test updating workflow status."""
        created = await self.service.create_workflow(
            name=sample_workflow_data["name"],
            project_id="proj-123"
        )

        updated = await self.service.update_workflow_status(
            created.workflow_id,
            "running"
        )

        assert updated is not None
        assert updated.status.value == "running"
