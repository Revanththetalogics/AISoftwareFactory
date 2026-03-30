"""
Comprehensive tests for ProjectService to increase coverage.
"""

from datetime import datetime

import pytest
from backend.services.project_service import ProjectService


class TestProjectService:
    """Comprehensive tests for ProjectService."""

    @pytest.fixture
    def project_service(self):
        """Create ProjectService instance."""
        return ProjectService()

    def test_init(self, project_service):
        """Test ProjectService initialization."""
        assert project_service is not None
        assert hasattr(project_service, '_projects')
        assert isinstance(project_service._projects, dict)
        assert len(project_service._projects) == 0
        assert hasattr(project_service, '_logger')

    @pytest.mark.asyncio
    async def test_create_project_basic(self, project_service):
        """Test creating a basic project."""
        name = "Test Project"
        description = "A test project description"

        result = await project_service.create_project(name, description)

        assert result is not None
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == name
        assert result["description"] == description
        assert result["status"] == "draft"
        assert result["current_phase"] == "idea"
        assert result["progress_percent"] == 0.0
        assert "created_at" in result
        assert "updated_at" in result
        assert "tech_stack" in result
        assert "metadata" in result

        # Verify project was stored
        assert len(project_service._projects) == 1
        assert result["id"] in project_service._projects

    @pytest.mark.asyncio
    async def test_create_project_with_requirements(self, project_service):
        """Test creating project with requirements."""
        result = await project_service.create_project(
            name="Project with Requirements",
            description="Description here",
            requirements="These are the requirements"
        )

        assert result["requirements"] == "These are the requirements"

    @pytest.mark.asyncio
    async def test_create_project_with_creator(self, project_service):
        """Test creating project with creator info."""
        creator_id = "user123"
        result = await project_service.create_project(
            name="Project",
            description="Desc",
            created_by=creator_id
        )

        assert result["created_by"] == creator_id

    @pytest.mark.asyncio
    async def test_get_project_success(self, project_service):
        """Test getting existing project."""
        # First create a project
        created_project = await project_service.create_project("Test", "Desc")
        project_id = created_project["id"]

        # Then get it
        result = await project_service.get_project(project_id)

        assert result is not None
        assert result["id"] == project_id
        assert result["name"] == "Test"

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, project_service):
        """Test getting non-existent project."""
        result = await project_service.get_project("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, project_service):
        """Test listing projects when none exist."""
        result = await project_service.list_projects()
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_projects_multiple(self, project_service):
        """Test listing multiple projects."""
        # Create multiple projects
        await project_service.create_project("Project 1", "Desc 1")
        await project_service.create_project("Project 2", "Desc 2")
        await project_service.create_project("Project 3", "Desc 3")

        result = await project_service.list_projects()

        assert isinstance(result, list)
        assert len(result) == 3

        # Should be sorted by created_at descending
        assert result[0]["name"] == "Project 3"
        assert result[1]["name"] == "Project 2"
        assert result[2]["name"] == "Project 1"

    @pytest.mark.asyncio
    async def test_list_projects_filter_by_status(self, project_service):
        """Test filtering projects by status."""
        # Create projects with different statuses
        proj1 = await project_service.create_project("Draft Project", "Desc")
        proj2 = await project_service.create_project("Active Project", "Desc")

        # Update second project status
        await project_service.update_project(proj2["id"], {"status": "active"})

        # Filter by draft status
        drafts = await project_service.list_projects(status="draft")
        assert len(drafts) == 1
        assert drafts[0]["id"] == proj1["id"]

        # Filter by active status
        actives = await project_service.list_projects(status="active")
        assert len(actives) == 1
        assert actives[0]["id"] == proj2["id"]

    @pytest.mark.asyncio
    async def test_list_projects_filter_by_creator(self, project_service):
        """Test filtering projects by creator."""
        # Create projects by different users
        proj1 = await project_service.create_project("User1 Project", "Desc", created_by="user1")
        proj2 = await project_service.create_project("User2 Project", "Desc", created_by="user2")

        # Filter by user1
        user1_projects = await project_service.list_projects(created_by="user1")
        assert len(user1_projects) == 1
        assert user1_projects[0]["id"] == proj1["id"]

        # Filter by user2
        user2_projects = await project_service.list_projects(created_by="user2")
        assert len(user2_projects) == 1
        assert user2_projects[0]["id"] == proj2["id"]

    @pytest.mark.asyncio
    async def test_list_projects_combined_filters(self, project_service):
        """Test combining multiple filters."""
        # Create projects with various combinations
        proj1 = await project_service.create_project("Draft by User1", "Desc", created_by="user1")
        proj2 = await project_service.create_project("Active by User1", "Desc", created_by="user1")
        await project_service.create_project("Draft by User2", "Desc", created_by="user2")

        # Update statuses
        await project_service.update_project(proj2["id"], {"status": "active"})

        # Filter by both status and creator
        result = await project_service.list_projects(status="draft", created_by="user1")
        assert len(result) == 1
        assert result[0]["id"] == proj1["id"]

    @pytest.mark.asyncio
    async def test_update_project_success(self, project_service):
        """Test successful project update."""
        # Create project first
        original = await project_service.create_project("Original Name", "Original Desc")
        project_id = original["id"]

        # Update it
        updates = {
            "name": "Updated Name",
            "description": "Updated Description",
            "status": "active",
            "current_phase": "development"
        }

        result = await project_service.update_project(project_id, updates)

        assert result is not None
        assert result["id"] == project_id
        assert result["name"] == "Updated Name"
        assert result["description"] == "Updated Description"
        assert result["status"] == "active"
        assert result["current_phase"] == "development"
        assert result["updated_at"] != result["created_at"]  # Timestamp should be updated

    @pytest.mark.asyncio
    async def test_update_project_partial_updates(self, project_service):
        """Test partial project updates."""
        original = await project_service.create_project("Test", "Desc")
        project_id = original["id"]

        # Update only name
        result = await project_service.update_project(project_id, {"name": "New Name"})

        assert result["name"] == "New Name"
        # Other fields should remain unchanged
        assert result["description"] == "Desc"
        assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_update_project_allowed_fields_only(self, project_service):
        """Test that only allowed fields can be updated."""
        original = await project_service.create_project("Test", "Desc")
        project_id = original["id"]

        # Try to update disallowed fields
        updates = {
            "name": "Allowed Update",
            "disallowed_field": "Should be ignored",
            "another_disallowed": "Also ignored"
        }

        result = await project_service.update_project(project_id, updates)

        assert result["name"] == "Allowed Update"
        # Disallowed fields should not be in the project
        assert "disallowed_field" not in result
        assert "another_disallowed" not in result

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, project_service):
        """Test updating non-existent project."""
        result = await project_service.update_project("nonexistent", {"name": "New Name"})
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_project_success(self, project_service):
        """Test successful project deletion."""
        # Create project first
        project = await project_service.create_project("To Delete", "Desc")
        project_id = project["id"]

        # Verify it exists
        assert len(project_service._projects) == 1
        assert project_id in project_service._projects

        # Delete it
        result = await project_service.delete_project(project_id)

        assert result is True
        assert len(project_service._projects) == 0
        assert project_id not in project_service._projects

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, project_service):
        """Test deleting non-existent project."""
        result = await project_service.delete_project("nonexistent-id")
        assert result is False
        # Should not affect existing projects
        assert len(project_service._projects) == 0

    @pytest.mark.asyncio
    async def test_delete_project_leaves_others(self, project_service):
        """Test that deleting one project doesn't affect others."""
        # Create multiple projects
        proj1 = await project_service.create_project("Project 1", "Desc")
        proj2 = await project_service.create_project("Project 2", "Desc")
        proj3 = await project_service.create_project("Project 3", "Desc")

        assert len(project_service._projects) == 3

        # Delete middle project
        result = await project_service.delete_project(proj2["id"])
        assert result is True

        # Should have 2 projects left
        assert len(project_service._projects) == 2
        assert proj1["id"] in project_service._projects
        assert proj3["id"] in project_service._projects
        assert proj2["id"] not in project_service._projects

    @pytest.mark.asyncio
    async def test_update_progress_success(self, project_service):
        """Test successful progress update."""
        project = await project_service.create_project("Progress Test", "Desc")
        project_id = project["id"]

        # Update progress to 50%
        result = await project_service.update_progress(project_id, 50.0)

        assert result is not None
        assert result["id"] == project_id
        assert result["progress_percent"] == 50.0
        assert result["updated_at"] != result["created_at"]

    @pytest.mark.asyncio
    async def test_update_progress_clamping(self, project_service):
        """Test that progress is clamped between 0 and 100."""
        project = await project_service.create_project("Clamping Test", "Desc")
        project_id = project["id"]

        # Test values above 100
        result = await project_service.update_progress(project_id, 150.0)
        assert result["progress_percent"] == 100.0

        # Test values below 0
        result = await project_service.update_progress(project_id, -25.0)
        assert result["progress_percent"] == 0.0

    @pytest.mark.asyncio
    async def test_update_progress_decimal_values(self, project_service):
        """Test progress updates with decimal values."""
        project = await project_service.create_project("Decimal Test", "Desc")
        project_id = project["id"]

        result = await project_service.update_progress(project_id, 75.5)
        assert result["progress_percent"] == 75.5

    @pytest.mark.asyncio
    async def test_update_progress_not_found(self, project_service):
        """Test progress update for non-existent project."""
        result = await project_service.update_progress("nonexistent", 50.0)
        assert result is None

    @pytest.mark.asyncio
    async def test_project_timestamps(self, project_service):
        """Test that timestamps are properly set."""
        # Create project
        project = await project_service.create_project("Timestamp Test", "Desc")

        assert "created_at" in project
        assert "updated_at" in project

        created_time = datetime.fromisoformat(project["created_at"].replace('Z', '+00:00'))
        updated_time = datetime.fromisoformat(project["updated_at"].replace('Z', '+00:00'))

        # Times should be very close (within a few seconds)
        time_diff = abs((updated_time - created_time).total_seconds())
        assert time_diff < 5

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, project_service):
        """Test sequence of operations on the same project."""
        # 1. Create project
        project = await project_service.create_project("Sequential Test", "Initial desc")
        project_id = project["id"]

        # 2. Update it
        await project_service.update_project(project_id, {
            "description": "Updated desc",
            "status": "active"
        })

        # 3. Update progress
        await project_service.update_progress(project_id, 25.0)

        # 4. Get final state
        final_project = await project_service.get_project(project_id)

        assert final_project["description"] == "Updated desc"
        assert final_project["status"] == "active"
        assert final_project["progress_percent"] == 25.0
        # Updated timestamp should be different (allow small time differences)
        assert final_project["updated_at"] != project["created_at"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
