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

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self):
        """Test deleting a nonexistent project returns False."""
        result = await self.service.delete_project("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_projects_filter_by_status(self, sample_project_data):
        """Test listing projects filtered by status."""
        await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        projects = await self.service.list_projects(status="draft")
        assert len(projects) == 1
        assert projects[0]["status"] == "draft"

        # No projects with different status
        projects = await self.service.list_projects(status="active")
        assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_list_projects_filter_by_created_by(self, sample_project_data):
        """Test listing projects filtered by creator."""
        await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
            created_by="user-001"
        )
        await self.service.create_project(
            name="Project 2",
            description="Another project",
            created_by="user-002"
        )

        projects = await self.service.list_projects(created_by="user-001")
        assert len(projects) == 1
        assert projects[0]["created_by"] == "user-001"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self):
        """Test updating a nonexistent project returns None."""
        result = await self.service.update_project(
            "nonexistent-id",
            {"name": "Updated"}
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_update_progress_success(self, sample_project_data):
        """Test updating project progress."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        result = await self.service.update_progress(created["id"], 50.0)

        assert result is not None
        assert result["progress_percent"] == 50.0

    @pytest.mark.asyncio
    async def test_update_progress_not_found(self):
        """Test updating progress for nonexistent project."""
        result = await self.service.update_progress("nonexistent-id", 50.0)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_progress_clamps_max(self, sample_project_data):
        """Test that progress is clamped to max 100."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        result = await self.service.update_progress(created["id"], 150.0)

        assert result is not None
        assert result["progress_percent"] == 100.0

    @pytest.mark.asyncio
    async def test_update_progress_clamps_min(self, sample_project_data):
        """Test that progress is clamped to min 0."""
        created = await self.service.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"]
        )

        result = await self.service.update_progress(created["id"], -50.0)

        assert result is not None
        assert result["progress_percent"] == 0.0


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
