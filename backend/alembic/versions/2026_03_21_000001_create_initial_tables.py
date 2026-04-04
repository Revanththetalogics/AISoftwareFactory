"""create initial tables

Revision ID: 2026_03_21_000001
Revises:
Create Date: 2026-03-21

This migration creates all initial tables for the AI Software Factory:
- users: User authentication and authorization
- projects: Software development projects
- workflows: Automated workflow processes
- tasks: Unit of work items
- agents: AI agent configurations
- deployments: Application deployments
- audit_logs: System audit trail
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2026_03_21_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables with proper indexes and constraints."""

    # Enable required PostgreSQL extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ========== Users Table ==========
    op.create_table(
        "users",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(50), nullable=True),
        sa.Column("last_name", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("permissions", sa.JSON, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )

    # Users indexes
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_active", "users", ["is_active"])

    # ========== Projects Table ==========
    op.create_table(
        "projects",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("requirements", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("tech_stack", sa.JSON, nullable=True),
        sa.Column("current_phase", sa.String(50), nullable=True),
        sa.Column("progress_percent", sa.Integer, server_default="0"),
        sa.Column("extra_metadata", sa.JSON, server_default="{}"),
        sa.Column("owner_id", sa.String(50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Projects indexes
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("idx_projects_owner", "projects", ["owner_id"])
    op.create_index("idx_projects_status", "projects", ["status"])
    op.create_index("idx_projects_created", "projects", ["created_at"])
    # GIN index for text search on project names (requires pg_trgm extension)
    op.execute("CREATE INDEX idx_projects_name_trgm ON projects USING gin (name gin_trgm_ops)")

    # ========== Workflows Table ==========
    op.create_table(
        "workflows",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(20), server_default="1.0.0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("trigger", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("project_id", sa.String(50), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("steps", sa.JSON, server_default="[]"),
        sa.Column("current_step_id", sa.String(50), nullable=True),
        sa.Column("completed_steps", sa.JSON, server_default="[]"),
        sa.Column("failed_steps", sa.JSON, server_default="[]"),
        sa.Column("context", sa.JSON, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(50), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("extra_metadata", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Workflows indexes
    op.create_index("ix_workflows_id", "workflows", ["id"])
    op.create_index("idx_workflows_project", "workflows", ["project_id"])
    op.create_index("idx_workflows_status", "workflows", ["status"])
    op.create_index("idx_workflows_created_by", "workflows", ["created_by"])
    op.create_index("idx_workflows_created", "workflows", ["created_at"])

    # ========== Tasks Table ==========
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="3"),
        sa.Column("project_id", sa.String(50), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("workflow_id", sa.String(50), sa.ForeignKey("workflows.id"), nullable=True),
        sa.Column("step_id", sa.String(50), nullable=True),
        sa.Column("agent_id", sa.String(50), nullable=True),
        sa.Column("crew_type", sa.String(50), nullable=True),
        sa.Column("input_data", sa.JSON, server_default="{}"),
        sa.Column("result", sa.JSON, nullable=True),
        sa.Column("dependencies", sa.JSON, server_default="[]"),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        sa.Column("max_retries", sa.Integer, server_default="3"),
        sa.Column("timeout_seconds", sa.Integer, server_default="300"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(50), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("extra_metadata", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Tasks indexes
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("idx_tasks_project", "tasks", ["project_id"])
    op.create_index("idx_tasks_workflow", "tasks", ["workflow_id"])
    op.create_index("idx_tasks_status", "tasks", ["status"])
    op.create_index("idx_tasks_priority", "tasks", ["priority"])
    op.create_index("idx_tasks_created_by", "tasks", ["created_by"])
    op.create_index("idx_tasks_scheduled", "tasks", ["scheduled_at"])
    op.create_index("idx_tasks_created", "tasks", ["created_at"])

    # ========== Agents Table ==========
    op.create_table(
        "agents",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("capabilities", sa.JSON, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="idle"),
        sa.Column("current_task_id", sa.String(50), nullable=True),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config", sa.JSON, server_default="{}"),
        sa.Column("extra_metadata", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Agents indexes
    op.create_index("ix_agents_id", "agents", ["id"])
    op.create_index("idx_agents_role", "agents", ["role"])
    op.create_index("idx_agents_status", "agents", ["status"])
    op.create_index("idx_agents_current_task", "agents", ["current_task_id"])

    # ========== Deployments Table ==========
    op.create_table(
        "deployments",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("project_id", sa.String(50), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("environment", sa.String(20), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("config", sa.JSON, server_default="{}"),
        sa.Column("steps", sa.JSON, server_default="[]"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("url", sa.String(255), nullable=True),
        sa.Column("created_by", sa.String(50), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Deployments indexes and constraints
    op.create_index("ix_deployments_id", "deployments", ["id"])
    op.create_index("idx_deployments_project", "deployments", ["project_id"])
    op.create_index("idx_deployments_environment", "deployments", ["environment"])
    op.create_index("idx_deployments_status", "deployments", ["status"])
    op.create_index("idx_deployments_created", "deployments", ["created_at"])
    op.create_unique_constraint("uq_project_env_version", "deployments", ["project_id", "environment", "version"])

    # ========== Audit Logs Table ==========
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.String(50), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(50), nullable=False),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Audit logs indexes
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("idx_auditlogs_user", "audit_logs", ["user_id"])
    op.create_index("idx_auditlogs_resource", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("idx_auditlogs_action", "audit_logs", ["action"])
    op.create_index("idx_auditlogs_created", "audit_logs", ["created_at"])


def downgrade() -> None:
    """Drop all tables in reverse order of creation."""

    # Drop audit_logs
    op.drop_index("idx_auditlogs_created", table_name="audit_logs")
    op.drop_index("idx_auditlogs_action", table_name="audit_logs")
    op.drop_index("idx_auditlogs_resource", table_name="audit_logs")
    op.drop_index("idx_auditlogs_user", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    # Drop deployments
    op.drop_constraint("uq_project_env_version", "deployments", type_="unique")
    op.drop_index("idx_deployments_created", table_name="deployments")
    op.drop_index("idx_deployments_status", table_name="deployments")
    op.drop_index("idx_deployments_environment", table_name="deployments")
    op.drop_index("idx_deployments_project", table_name="deployments")
    op.drop_index("ix_deployments_id", table_name="deployments")
    op.drop_table("deployments")

    # Drop agents
    op.drop_index("idx_agents_current_task", table_name="agents")
    op.drop_index("idx_agents_status", table_name="agents")
    op.drop_index("idx_agents_role", table_name="agents")
    op.drop_index("ix_agents_id", table_name="agents")
    op.drop_table("agents")

    # Drop tasks
    op.drop_index("idx_tasks_created", table_name="tasks")
    op.drop_index("idx_tasks_scheduled", table_name="tasks")
    op.drop_index("idx_tasks_created_by", table_name="tasks")
    op.drop_index("idx_tasks_priority", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_workflow", table_name="tasks")
    op.drop_index("idx_tasks_project", table_name="tasks")
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")

    # Drop workflows
    op.drop_index("idx_workflows_created", table_name="workflows")
    op.drop_index("idx_workflows_created_by", table_name="workflows")
    op.drop_index("idx_workflows_status", table_name="workflows")
    op.drop_index("idx_workflows_project", table_name="workflows")
    op.drop_index("ix_workflows_id", table_name="workflows")
    op.drop_table("workflows")

    # Drop projects
    op.execute("DROP INDEX IF EXISTS idx_projects_name_trgm")
    op.drop_index("idx_projects_created", table_name="projects")
    op.drop_index("idx_projects_status", table_name="projects")
    op.drop_index("idx_projects_owner", table_name="projects")
    op.drop_index("ix_projects_id", table_name="projects")
    op.drop_table("projects")

    # Drop users
    op.drop_index("idx_users_active", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_index("idx_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    # Drop extension (optional - usually kept)
    # op.execute("DROP EXTENSION IF EXISTS pg_trgm")
