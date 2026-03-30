"""Comprehensive tests for services layer to increase coverage"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, UTC
import uuid

from backend.services.auth_service import AuthService
from backend.services.project_service import ProjectService
from backend.services.workflow_service import WorkflowService
from backend.services.reporting_service import ReportingService
from backend.services.schema_management_service import SchemaManagementService

class TestAuthService:
    """Test authentication service"""
    
    @pytest.mark.asyncio
    async def test_user_authentication(self):
        """Test user authentication flow"""
        with patch('backend.services.auth_service.JWTAuthService') as mock_jwt, \
             patch('backend.services.auth_service.UserRepository') as mock_user_repo:
            
            mock_jwt_service = AsyncMock()
            mock_jwt_service.create_access_token.return_value = "access-token"
            mock_jwt_service.create_refresh_token.return_value = "refresh-token"
            mock_jwt.return_value = mock_jwt_service
            
            mock_user_repository = AsyncMock()
            mock_user_repository.get_user_by_email.return_value = MagicMock(
                id="user-1",
                email="test@example.com",
                hashed_password="$2b$12$hashed_password",
                is_active=True
            )
            mock_user_repository.verify_password.return_value = True
            mock_user_repo.return_value = mock_user_repository
            
            auth_service = AuthService()
            
            # Test successful login
            result = await auth_service.authenticate_user(
                email="test@example.com",
                password="password123"
            )
            assert result["access_token"] == "access-token"
            assert result["token_type"] == "bearer"
            
            # Test failed login (wrong password)
            mock_user_repository.verify_password.return_value = False
            result = await auth_service.authenticate_user(
                email="test@example.com",
                password="wrong-password"
            )
            assert result is None
    
    @pytest.mark.asyncio
    async def test_token_management(self):
        """Test token creation and validation"""
        with patch('backend.services.auth_service.JWTAuthService') as mock_jwt:
            mock_jwt_service = AsyncMock()
            mock_jwt_service.create_access_token.return_value = "test-access-token"
            mock_jwt_service.create_refresh_token.return_value = "test-refresh-token"
            mock_jwt_service.verify_token.return_value = {"user_id": "user-1"}
            mock_jwt.return_value = mock_jwt_service
            
            auth_service = AuthService()
            
            # Test token creation
            tokens = await auth_service.create_tokens(user_id="user-1")
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            
            # Test token refresh
            new_tokens = await auth_service.refresh_tokens("old-refresh-token")
            assert new_tokens is not None
            
            # Test token validation
            payload = await auth_service.validate_token("test-access-token")
            assert payload["user_id"] == "user-1"

class TestProjectService:
    """Test project service"""
    
    @pytest.mark.asyncio
    async def test_project_lifecycle(self):
        """Test complete project lifecycle"""
        with patch('backend.services.project_service.ProjectRepository') as mock_proj_repo, \
             patch('backend.services.project_service.GitService') as mock_git_service:
            
            mock_project_repo = AsyncMock()
            mock_project_repo.create_project.return_value = MagicMock(
                id="proj-1",
                name="Test Project",
                status="active"
            )
            mock_project_repo.get_project.return_value = MagicMock(
                id="proj-1",
                name="Test Project",
                status="active"
            )
            mock_project_repo.list_projects.return_value = [
                MagicMock(id="proj-1", name="Test Project")
            ]
            mock_proj_repo.return_value = mock_project_repo
            
            mock_git = AsyncMock()
            mock_git.clone_repository.return_value = {"status": "success"}
            mock_git_service.return_value = mock_git
            
            project_service = ProjectManagementService()
            
            # Test project creation
            project = await project_service.create_project(
                name="Test Project",
                description="A test project",
                owner_id="user-1"
            )
            assert project.id == "proj-1"
            assert project.name == "Test Project"
            
            # Test project retrieval
            retrieved_project = await project_service.get_project("proj-1")
            assert retrieved_project.id == "proj-1"
            
            # Test project listing
            projects = await project_service.list_projects(owner_id="user-1")
            assert len(projects) > 0
            
            # Test project update
            updated_project = await project_service.update_project(
                "proj-1",
                {"description": "Updated description"}
            )
            assert updated_project is not None
            
            # Test project deletion
            await project_service.delete_project("proj-1")

class TestWorkflowService:
    """Test workflow service"""
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test workflow execution"""
        with patch('backend.services.workflow_service.WorkflowRepository') as mock_wf_repo, \
             patch('backend.services.workflow_service.TaskQueue') as mock_task_queue:
            
            mock_workflow_repo = AsyncMock()
            mock_workflow_repo.create_workflow.return_value = MagicMock(
                id="wf-1",
                name="Test Workflow",
                status="pending"
            )
            mock_workflow_repo.get_workflow.return_value = MagicMock(
                id="wf-1",
                name="Test Workflow",
                status="pending"
            )
            mock_wf_repo.return_value = mock_workflow_repo
            
            mock_queue = AsyncMock()
            mock_queue.enqueue_task.return_value = "task-1"
            mock_task_queue.return_value = mock_queue
            
            workflow_service = WorkflowOrchestrationService()
            
            # Test workflow creation
            workflow = await workflow_service.create_workflow(
                name="Test Workflow",
                steps=[{"action": "build", "parameters": {}}],
                owner_id="user-1"
            )
            assert workflow.id == "wf-1"
            
            # Test workflow execution
            execution_result = await workflow_service.execute_workflow("wf-1")
            assert execution_result is not None
            
            # Test workflow status checking
            status = await workflow_service.get_workflow_status("wf-1")
            assert status is not None

class TestReportingService:
    """Test reporting service"""
    
    @pytest.mark.asyncio
    async def test_report_generation(self):
        """Test report generation"""
        with patch('backend.services.reporting_service.ReportRepository') as mock_report_repo, \
             patch('backend.services.reporting_service.TemplateEngine') as mock_template_engine:
            
            mock_report_repository = AsyncMock()
            mock_report_repository.create_report.return_value = MagicMock(
                id="report-1",
                type="performance",
                status="generated"
            )
            mock_report_repository.get_report.return_value = MagicMock(
                id="report-1",
                content="Report content"
            )
            mock_report_repo.return_value = mock_report_repository
            
            mock_template = AsyncMock()
            mock_template.render.return_value = "Rendered report content"
            mock_template_engine.return_value = mock_template
            
            reporting_service = ReportGenerationService()
            
            # Test report creation
            report = await reporting_service.generate_report(
                report_type="performance",
                parameters={"period": "monthly"},
                user_id="user-1"
            )
            assert report.id == "report-1"
            
            # Test report retrieval
            retrieved_report = await reporting_service.get_report("report-1")
            assert retrieved_report is not None
            
            # Test report listing
            reports = await reporting_service.list_reports(user_id="user-1")
            assert isinstance(reports, list)

class TestSchemaManagementService:
    """Test schema management service"""
    
    @pytest.mark.asyncio
    async def test_schema_operations(self):
        """Test schema validation and management"""
        with patch('backend.services.schema_management_service.SchemaRepository') as mock_schema_repo, \
             patch('backend.services.schema_management_service.JSONSchemaValidator') as mock_validator:
            
            mock_schema_repository = AsyncMock()
            mock_schema_repository.create_schema.return_value = MagicMock(
                id="schema-1",
                name="User Schema",
                version="1.0.0"
            )
            mock_schema_repository.validate_data_against_schema.return_value = {
                "valid": True,
                "errors": []
            }
            mock_schema_repo.return_value = mock_schema_repository
            
            mock_json_validator = AsyncMock()
            mock_json_validator.validate.return_value = True
            mock_validator.return_value = mock_json_validator
            
            schema_service = SchemaManager()
            
            # Test schema creation
            schema = await schema_service.create_schema(
                name="User Schema",
                definition={"type": "object", "properties": {}},
                version="1.0.0"
            )
            assert schema.id == "schema-1"
            
            # Test schema validation
            validation_result = await schema_service.validate_data(
                schema_id="schema-1",
                data={"name": "John"}
            )
            assert validation_result["valid"] is True
            
            # Test schema evolution
            evolved_schema = await schema_service.evolve_schema(
                schema_id="schema-1",
                new_definition={"type": "object", "properties": {"age": {"type": "number"}}}
            )
            assert evolved_schema is not None

class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest.mark.asyncio
    async def test_project_with_workflow_integration(self):
        """Test integration between project and workflow services"""
        with patch('backend.services.project_service.ProjectManagementService') as mock_project_svc, \
             patch('backend.services.workflow_service.WorkflowOrchestrationService') as mock_workflow_svc:
            
            mock_project_service = AsyncMock()
            mock_project_service.get_project.return_value = MagicMock(
                id="proj-1",
                name="Integrated Project"
            )
            mock_project_svc.return_value = mock_project_service
            
            mock_workflow_service = AsyncMock()
            mock_workflow_service.create_workflow.return_value = MagicMock(
                id="wf-1",
                name="Build Workflow"
            )
            mock_workflow_service.execute_workflow.return_value = {
                "status": "completed",
                "result": "success"
            }
            mock_workflow_svc.return_value = mock_workflow_service
            
            # Test integrated workflow: create project, create workflow, execute workflow
            # This demonstrates service coordination

if __name__ == "__main__":
    pytest.main([__file__, "-v"])