"""
Comprehensive tests for database models to increase coverage.
"""

from datetime import UTC, datetime

import pytest
from backend.db.base import Base
from backend.models.database import DBAgent, DBAuditLog, DBDeployment, DBProject, DBTask, DBUser, DBWorkflow
from backend.models.task import TaskPriority, TaskStatus
from backend.models.workflow import WorkflowStatus, WorkflowTrigger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Create in-memory SQLite database for testing
@pytest.fixture
def test_engine():
    """Create test database engine."""
    return create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestDBUser:
    """Tests for DBUser model."""

    def test_create_user(self, test_session):
        """Test creating a user."""
        user = DBUser(
            id="user_123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pwd_123",
            first_name="Test",
            last_name="User"
        )

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        assert user.id == "user_123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.permissions == []
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_superuser(self, test_session):
        """Test creating a superuser."""
        user = DBUser(
            id="admin_001",
            username="admin",
            email="admin@example.com",
            hashed_password="hashed_admin_pwd",
            is_superuser=True,
            permissions=["admin", "read", "write", "delete"]
        )

        test_session.add(user)
        test_session.commit()

        assert user.is_superuser is True
        assert len(user.permissions) == 4
        assert "admin" in user.permissions

    def test_user_inactive(self, test_session):
        """Test creating an inactive user."""
        user = DBUser(
            id="user_inactive",
            username="inactive_user",
            email="inactive@example.com",
            hashed_password="hashed_pwd",
            is_active=False
        )

        test_session.add(user)
        test_session.commit()

        assert user.is_active is False

    def test_user_last_login(self, test_session):
        """Test updating user last login."""
        user = DBUser(
            id="user_login",
            username="login_user",
            email="login@example.com",
            hashed_password="hashed_pwd"
        )

        test_session.add(user)
        test_session.commit()

        # Update last login
        user.last_login = datetime.now(UTC)
        test_session.commit()

        assert user.last_login is not None


class TestDBProject:
    """Tests for DBProject model."""

    def test_create_project(self, test_session):
        """Test creating a project."""
        owner = DBUser(id="owner_123", username="owner", email="owner@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(
            id="proj_001",
            name="Test Project",
            description="A test project",
            requirements="Python, FastAPI",
            status="active",
            tech_stack=["Python", "FastAPI", "React"],
            current_phase="development",
            progress_percent=25,
            extra_metadata={"priority": "high"},
            owner_id=owner.id
        )

        test_session.add(project)
        test_session.commit()
        test_session.refresh(project)

        assert project.id == "proj_001"
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.status == "active"
        assert len(project.tech_stack) == 3
        assert project.current_phase == "development"
        assert project.progress_percent == 25
        assert project.extra_metadata["priority"] == "high"
        assert project.owner_id == owner.id

    def test_project_default_values(self, test_session):
        """Test project default values."""
        owner = DBUser(id="owner_456", username="owner2", email="owner2@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(
            id="proj_default",
            name="Default Project",
            owner_id=owner.id
        )

        test_session.add(project)
        test_session.commit()

        assert project.status == "draft"
        assert project.progress_percent == 0
        assert project.extra_metadata == {}
        assert project.deleted_at is None

    def test_project_soft_delete(self, test_session):
        """Test soft deleting a project."""
        owner = DBUser(id="owner_789", username="owner3", email="owner3@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_delete", name="To Delete", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        # Soft delete
        project.deleted_at = datetime.now(UTC)
        test_session.commit()

        assert project.deleted_at is not None


class TestDBWorkflow:
    """Tests for DBWorkflow model."""

    def test_create_workflow(self, test_session):
        """Test creating a workflow."""
        owner = DBUser(id="wf_owner", username="wf_owner", email="wf@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_wf", name="WF Project", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        workflow = DBWorkflow(
            id="wf_001",
            name="CI/CD Pipeline",
            description="Automated deployment workflow",
            version="2.0.0",
            status=WorkflowStatus.RUNNING,
            trigger=WorkflowTrigger.WEBHOOK,
            project_id=project.id,
            steps=[{"id": "step1", "name": "Build"}, {"id": "step2", "name": "Deploy"}],
            created_by=owner.id
        )

        test_session.add(workflow)
        test_session.commit()
        test_session.refresh(workflow)

        assert workflow.id == "wf_001"
        assert workflow.name == "CI/CD Pipeline"
        assert workflow.version == "2.0.0"
        assert workflow.status == WorkflowStatus.RUNNING
        assert workflow.trigger == WorkflowTrigger.WEBHOOK
        assert len(workflow.steps) == 2
        assert workflow.context == {}
        assert workflow.extra_metadata == {}

    def test_workflow_progress_tracking(self, test_session):
        """Test workflow progress tracking."""
        owner = DBUser(id="wf_owner2", username="wf_owner2", email="wf2@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_wf2", name="WF Project 2", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        workflow = DBWorkflow(
            id="wf_002",
            name="Test Workflow",
            project_id=project.id,
            steps=[{"id": "s1"}, {"id": "s2"}, {"id": "s3"}],
            current_step_id="s2",
            completed_steps=["s1"],
            failed_steps=[]
        )

        test_session.add(workflow)
        test_session.commit()

        assert workflow.current_step_id == "s2"
        assert len(workflow.completed_steps) == 1
        assert workflow.failed_steps == []

    def test_workflow_timestamps(self, test_session):
        """Test workflow timestamps."""
        owner = DBUser(id="wf_owner3", username="wf_owner3", email="wf3@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_wf3", name="WF Project 3", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        workflow = DBWorkflow(
            id="wf_003",
            name="Timed Workflow",
            project_id=project.id,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC)
        )

        test_session.add(workflow)
        test_session.commit()

        assert workflow.started_at is not None
        assert workflow.completed_at is not None


class TestDBTask:
    """Tests for DBTask model."""

    def test_create_task(self, test_session):
        """Test creating a task."""
        owner = DBUser(id="task_owner", username="task_owner", email="task@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_task", name="Task Project", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        task = DBTask(
            id="task_001",
            name="Implement Feature",
            description="Add new authentication feature",
            status=TaskStatus.RUNNING,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            agent_id="agent_001",
            crew_type="development",
            input_data={"feature": "auth"},
            retry_count=0,
            max_retries=3,
            timeout_seconds=600,
            created_by=owner.id
        )

        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        assert task.id == "task_001"
        assert task.name == "Implement Feature"
        assert task.status == TaskStatus.RUNNING
        assert task.priority == TaskPriority.HIGH
        assert task.agent_id == "agent_001"
        assert task.crew_type == "development"
        assert task.input_data == {"feature": "auth"}
        assert task.retry_count == 0
        assert task.max_retries == 3

    def test_task_dependencies(self, test_session):
        """Test task with dependencies."""
        owner = DBUser(id="task_owner2", username="task_owner2", email="task2@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_task2", name="Task Project 2", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        task = DBTask(
            id="task_002",
            name="Dependent Task",
            project_id=project.id,
            dependencies=["task_001", "task_003"],
            result={"output": "completed"}
        )

        test_session.add(task)
        test_session.commit()

        assert len(task.dependencies) == 2
        assert "task_001" in task.dependencies
        assert task.result == {"output": "completed"}

    def test_task_scheduling(self, test_session):
        """Test task scheduling."""
        owner = DBUser(id="task_owner3", username="task_owner3", email="task3@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_task3", name="Task Project 3", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        scheduled_time = datetime.now(UTC)
        task = DBTask(
            id="task_003",
            name="Scheduled Task",
            project_id=project.id,
            scheduled_at=scheduled_time,
            started_at=scheduled_time,
            completed_at=datetime.now(UTC)
        )

        test_session.add(task)
        test_session.commit()

        assert task.scheduled_at is not None
        assert task.started_at is not None
        assert task.completed_at is not None


class TestDBAgent:
    """Tests for DBAgent model."""

    def test_create_agent(self, test_session):
        """Test creating an agent."""
        agent = DBAgent(
            id="agent_001",
            name="Code Reviewer",
            role="reviewer",
            description="AI agent for code review",
            capabilities=["code_review", "testing", "documentation"],
            status="busy",
            config={"model": "gpt-4", "temperature": 0.7}
        )

        test_session.add(agent)
        test_session.commit()
        test_session.refresh(agent)

        assert agent.id == "agent_001"
        assert agent.name == "Code Reviewer"
        assert agent.role == "reviewer"
        assert len(agent.capabilities) == 3
        assert agent.status == "busy"
        assert agent.config["model"] == "gpt-4"

    def test_agent_idle_status(self, test_session):
        """Test agent default idle status."""
        agent = DBAgent(
            id="agent_002",
            name="Developer Bot",
            role="developer"
        )

        test_session.add(agent)
        test_session.commit()

        assert agent.status == "idle"
        assert agent.current_task_id is None

    def test_agent_active_task(self, test_session):
        """Test agent with active task."""
        agent = DBAgent(
            id="agent_003",
            name="Active Agent",
            role="worker",
            status="active",
            current_task_id="task_123",
            last_active=datetime.now(UTC)
        )

        test_session.add(agent)
        test_session.commit()

        assert agent.status == "active"
        assert agent.current_task_id == "task_123"
        assert agent.last_active is not None


class TestDBDeployment:
    """Tests for DBDeployment model."""

    def test_create_deployment(self, test_session):
        """Test creating a deployment."""
        owner = DBUser(id="deploy_owner", username="deploy_owner", email="deploy@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_deploy", name="Deploy Project", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        deployment = DBDeployment(
            id="deploy_001",
            project_id=project.id,
            environment="production",
            version="1.0.0",
            status="success",
            config={"replicas": 3, "cpu": "500m", "memory": "512Mi"},
            url="https://app.example.com",
            created_by=owner.id
        )

        test_session.add(deployment)
        test_session.commit()
        test_session.refresh(deployment)

        assert deployment.id == "deploy_001"
        assert deployment.environment == "production"
        assert deployment.version == "1.0.0"
        assert deployment.status == "success"
        assert deployment.url == "https://app.example.com"
        assert deployment.config["replicas"] == 3

    def test_deployment_failure(self, test_session):
        """Test failed deployment."""
        owner = DBUser(id="deploy_owner2", username="deploy_owner2", email="deploy2@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_deploy2", name="Deploy Project 2", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        deployment = DBDeployment(
            id="deploy_002",
            project_id=project.id,
            environment="staging",
            version="1.0.1",
            status="failed",
            error_message="Container failed to start: OOMKilled",
            steps=[{"name": "build", "status": "success"}, {"name": "deploy", "status": "failed"}]
        )

        test_session.add(deployment)
        test_session.commit()

        assert deployment.status == "failed"
        assert "OOMKilled" in deployment.error_message
        assert len(deployment.steps) == 2

    def test_deployment_unique_constraint(self, test_session):
        """Test deployment unique constraint."""
        owner = DBUser(id="deploy_owner3", username="deploy_owner3", email="deploy3@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="proj_deploy3", name="Deploy Project 3", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        deployment1 = DBDeployment(
            id="deploy_003",
            project_id=project.id,
            environment="production",
            version="1.0.0",
            status="success"
        )

        test_session.add(deployment1)
        test_session.commit()

        # Try to add duplicate (should fail at DB level due to unique constraint)
        deployment2 = DBDeployment(
            id="deploy_004",
            project_id=project.id,
            environment="production",
            version="1.0.0",
            status="pending"
        )

        test_session.add(deployment2)
        with pytest.raises(Exception):  # IntegrityError or similar
            test_session.commit()


class TestDBAuditLog:
    """Tests for DBAuditLog model."""

    def test_create_audit_log(self, test_session):
        """Test creating an audit log entry."""
        owner = DBUser(id="audit_owner", username="audit_owner", email="audit@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        audit_log = DBAuditLog(
            id="audit_001",
            user_id=owner.id,
            action="CREATE",
            resource_type="project",
            resource_id="proj_001",
            details={"name": "New Project", "action": "created"},
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        test_session.add(audit_log)
        test_session.commit()
        test_session.refresh(audit_log)

        assert audit_log.id == "audit_001"
        assert audit_log.user_id == owner.id
        assert audit_log.action == "CREATE"
        assert audit_log.resource_type == "project"
        assert audit_log.ip_address == "192.168.1.100"
        assert audit_log.user_agent is not None

    def test_audit_log_login_action(self, test_session):
        """Test audit log for login action."""
        audit_log = DBAuditLog(
            id="audit_002",
            action="LOGIN",
            resource_type="user",
            resource_id="user_123",
            ip_address="10.0.0.1"
        )

        test_session.add(audit_log)
        test_session.commit()

        assert audit_log.action == "LOGIN"
        assert audit_log.user_id is None  # Login before authentication

    def test_audit_log_details_json(self, test_session):
        """Test audit log with complex JSON details."""
        audit_log = DBAuditLog(
            id="audit_003",
            action="UPDATE",
            resource_type="workflow",
            resource_id="wf_001",
            details={
                "changes": {
                    "status": {"old": "pending", "new": "running"},
                    "current_step": {"old": None, "new": "step_2"}
                },
                "timestamp": datetime.now(UTC).isoformat()
            }
        )

        test_session.add(audit_log)
        test_session.commit()

        assert audit_log.details["changes"]["status"]["old"] == "pending"
        assert audit_log.details["changes"]["status"]["new"] == "running"


class TestModelRelationships:
    """Tests for model relationships."""

    def test_user_projects_relationship(self, test_session):
        """Test user-projects relationship."""
        owner = DBUser(id="rel_owner", username="rel_owner", email="rel@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="rel_proj", name="Relationship Project", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        assert len(owner.projects) == 1
        assert owner.projects[0].id == project.id
        assert project.owner.id == owner.id

    def test_project_workflows_relationship(self, test_session):
        """Test project-workflows relationship."""
        owner = DBUser(id="rel_owner2", username="rel_owner2", email="rel2@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="rel_proj2", name="Relationship Project 2", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        workflow = DBWorkflow(
            id="rel_wf",
            name="Relationship Workflow",
            project_id=project.id,
            created_by=owner.id
        )
        test_session.add(workflow)
        test_session.commit()

        assert len(project.workflows) == 1
        assert project.workflows[0].id == workflow.id
        assert workflow.project.id == project.id

    def test_workflow_tasks_relationship(self, test_session):
        """Test workflow-tasks relationship."""
        owner = DBUser(id="rel_owner3", username="rel_owner3", email="rel3@example.com", hashed_password="pwd")
        test_session.add(owner)
        test_session.commit()

        project = DBProject(id="rel_proj3", name="Relationship Project 3", owner_id=owner.id)
        test_session.add(project)
        test_session.commit()

        workflow = DBWorkflow(
            id="rel_wf2",
            name="Relationship Workflow 2",
            project_id=project.id,
            created_by=owner.id
        )
        test_session.add(workflow)
        test_session.commit()

        task = DBTask(
            id="rel_task",
            name="Relationship Task",
            project_id=project.id,
            workflow_id=workflow.id,
            created_by=owner.id
        )
        test_session.add(task)
        test_session.commit()

        assert len(workflow.tasks) == 1
        assert workflow.tasks[0].id == task.id
        assert task.workflow.id == workflow.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
