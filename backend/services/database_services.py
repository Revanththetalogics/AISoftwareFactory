"""
Database Services for AI Software Factory.

This module provides database-backed service implementations for:
- DBProject management
- DBWorkflow execution
- DBAgent management
- Deployment tracking
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.models.database import DBProject, DBWorkflow, DBTask, DBAgent, DBDeployment, DBUser
from backend.models.task import TaskStatus, TaskPriority
from backend.models.workflow import WorkflowStatus, WorkflowTrigger
from backend.db.session import get_db_context
from backend.utils.validation import sanitize_input
from backend.utils.enhanced_logging import PerformanceTimer, business_events

logger = get_logger(__name__)


class DatabaseProjectService:
    """Database-backed project service implementation."""
    
    async def create_project(
        self,
        name: str,
        description: str,
        requirements: Optional[str] = None,
        tech_stack: Optional[Dict[str, Any]] = None,
        owner_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> DBProject:
        """Create a new project in the database."""
        with PerformanceTimer("create_project", project_name=name, owner_id=owner_id) as timer:
            if db is None:
                async with get_db_context() as db:
                    project = await self._create_project(db, name, description, requirements, tech_stack, owner_id)
            else:
                project = await self._create_project(db, name, description, requirements, tech_stack, owner_id)
            
            timer.set_result_metadata(project_id=project.id)
            business_events.project_created(project.id, project.name, owner_id or "anonymous")
            return project
    
    async def _create_project(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        requirements: Optional[str] = None,
        tech_stack: Optional[Dict[str, Any]] = None,
        owner_id: Optional[str] = None
    ) -> DBProject:
        """Internal method to create project."""
        # Sanitize inputs
        clean_name = sanitize_input(name, max_length=100)
        clean_description = sanitize_input(description, max_length=2000)
        clean_requirements = sanitize_input(requirements, max_length=5000) if requirements else None
        
        project = DBProject(
            id=f"proj-{uuid4().hex[:12]}",
            name=clean_name,
            description=clean_description,
            requirements=clean_requirements,
            status="draft",
            tech_stack=tech_stack or {},
            current_phase=None,
            progress_percent=0,
            owner_id=owner_id or "anonymous",
            metadata={}
        )
        
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        logger.info("Project created in database", project_id=project.id, name=project.name)
        return project
    
    async def get_project(self, project_id: str, db: AsyncSession = None) -> Optional[DBProject]:
        """Get project by ID."""
        with PerformanceTimer("get_project", project_id=project_id):
            if db is None:
                async with get_db_context() as db:
                    return await self._get_project(db, project_id)
            
            return await self._get_project(db, project_id)
    
    async def _get_project(self, db: AsyncSession, project_id: str) -> Optional[DBProject]:
        """Internal method to get project."""
        stmt = select(DBProject).where(DBProject.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if project:
            logger.debug("Project retrieved", project_id=project_id)
        else:
            logger.warning("Project not found", project_id=project_id)
            
        return project
    
    async def list_projects(
        self,
        owner_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = None
    ) -> List[DBProject]:
        """List projects with optional filtering."""
        with PerformanceTimer("list_projects", owner_id=owner_id, status=status, limit=limit) as timer:
            if db is None:
                async with get_db_context() as db:
                    projects = await self._list_projects(db, owner_id, status, skip, limit)
            else:
                projects = await self._list_projects(db, owner_id, status, skip, limit)
            
            timer.set_result_metadata(count=len(projects))
            return projects
    
    async def _list_projects(
        self,
        db: AsyncSession,
        owner_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DBProject]:
        """Internal method to list projects."""
        stmt = select(DBProject)
        
        if owner_id:
            stmt = stmt.where(DBProject.owner_id == owner_id)
        if status:
            stmt = stmt.where(DBProject.status == status)
            
        stmt = stmt.order_by(DBProject.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        projects = list(result.scalars().all())
        
        logger.info("Projects listed", count=len(projects), owner_id=owner_id, status=status)
        return projects
    
    async def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any],
        db: AsyncSession = None
    ) -> Optional[DBProject]:
        """Update project fields."""
        with PerformanceTimer("update_project", project_id=project_id) as timer:
            if db is None:
                async with get_db_context() as db:
                    project = await self._update_project(db, project_id, updates)
            else:
                project = await self._update_project(db, project_id, updates)
            
            if project:
                timer.set_result_metadata(updated_fields=list(updates.keys()))
                business_events.project_updated(project_id, "system", updates)
            
            return project
    
    async def _update_project(
        self,
        db: AsyncSession,
        project_id: str,
        updates: Dict[str, Any]
    ) -> Optional[DBProject]:
        """Internal method to update project."""
        # Sanitize text fields
        if "name" in updates:
            updates["name"] = sanitize_input(updates["name"], max_length=100)
        if "description" in updates:
            updates["description"] = sanitize_input(updates["description"], max_length=2000)
        if "requirements" in updates and updates["requirements"]:
            updates["requirements"] = sanitize_input(updates["requirements"], max_length=5000)
        
        stmt = update(DBProject).where(DBProject.id == project_id).values(
            **updates,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(stmt)
        await db.commit()
        
        return await self._get_project(db, project_id)
    
    async def delete_project(self, project_id: str, db: AsyncSession = None) -> bool:
        """Delete project."""
        with PerformanceTimer("delete_project", project_id=project_id):
            if db is None:
                async with get_db_context() as db:
                    return await self._delete_project(db, project_id)
            
            return await self._delete_project(db, project_id)
    
    async def _delete_project(self, db: AsyncSession, project_id: str) -> bool:
        """Internal method to delete project."""
        stmt = delete(DBProject).where(DBProject.id == project_id)
        result = await db.execute(stmt)
        await db.commit()
        
        success = result.rowcount > 0
        if success:
            logger.info("Project deleted", project_id=project_id)
        else:
            logger.warning("Project not found for deletion", project_id=project_id)
            
        return success


class DatabaseWorkflowService:
    """Database-backed workflow service implementation."""
    
    async def create_workflow(
        self,
        name: str,
        project_id: str,
        steps: List[Dict[str, Any]],
        created_by: Optional[str] = None,
        db: AsyncSession = None
    ) -> DBWorkflow:
        """Create a new workflow in the database."""
        if db is None:
            async with get_db_context() as db:
                return await self._create_workflow(db, name, project_id, steps, created_by)
        
        return await self._create_workflow(db, name, project_id, steps, created_by)
    
    async def _create_workflow(
        self,
        db: AsyncSession,
        name: str,
        project_id: str,
        steps: List[Dict[str, Any]],
        created_by: Optional[str] = None
    ) -> DBWorkflow:
        """Internal method to create workflow."""
        workflow = DBWorkflow(
            id=f"wf-{uuid4().hex[:12]}",
            name=sanitize_input(name, max_length=100),
            project_id=project_id,
            steps=steps,
            status=WorkflowStatus.PENDING,
            trigger=WorkflowTrigger.MANUAL,
            completed_steps=[],
            failed_steps=[],
            context={},
            created_by=created_by
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        logger.info("Workflow created in database", workflow_id=workflow.id, name=workflow.name)
        return workflow
    
    async def get_workflow(self, workflow_id: str, db: AsyncSession = None) -> Optional[DBWorkflow]:
        """Get workflow by ID."""
        if db is None:
            async with get_db_context() as db:
                return await self._get_workflow(db, workflow_id)
        
        return await self._get_workflow(db, workflow_id)
    
    async def _get_workflow(self, db: AsyncSession, workflow_id: str) -> Optional[DBWorkflow]:
        """Internal method to get workflow."""
        stmt = select(DBWorkflow).where(DBWorkflow.id == workflow_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_workflow_status(
        self,
        workflow_id: str,
        status: WorkflowStatus,
        current_step_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[DBWorkflow]:
        """Update workflow status."""
        if db is None:
            async with get_db_context() as db:
                return await self._update_workflow_status(db, workflow_id, status, current_step_id)
        
        return await self._update_workflow_status(db, workflow_id, status, current_step_id)
    
    async def _update_workflow_status(
        self,
        db: AsyncSession,
        workflow_id: str,
        status: WorkflowStatus,
        current_step_id: Optional[str] = None
    ) -> Optional[DBWorkflow]:
        """Internal method to update workflow status."""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if current_step_id:
            updates["current_step_id"] = current_step_id
            
        if status in [WorkflowStatus.RUNNING]:
            updates["started_at"] = datetime.utcnow()
        elif status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            updates["completed_at"] = datetime.utcnow()
        
        stmt = update(DBWorkflow).where(DBWorkflow.id == workflow_id).values(**updates)
        await db.execute(stmt)
        await db.commit()
        
        return await self._get_workflow(db, workflow_id)


class DatabaseAgentService:
    """Database-backed agent service implementation."""
    
    async def register_agent(
        self,
        name: str,
        role: str,
        capabilities: List[str],
        db: AsyncSession = None
    ) -> DBAgent:
        """Register a new agent in the database."""
        if db is None:
            async with get_db_context() as db:
                return await self._register_agent(db, name, role, capabilities)
        
        return await self._register_agent(db, name, role, capabilities)
    
    async def _register_agent(
        self,
        db: AsyncSession,
        name: str,
        role: str,
        capabilities: List[str]
    ) -> DBAgent:
        """Internal method to register agent."""
        agent = DBAgent(
            id=f"agent-{uuid4().hex[:12]}",
            name=sanitize_input(name, max_length=100),
            role=sanitize_input(role, max_length=50),
            capabilities=capabilities,
            status="idle",
            config={}
        )
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        logger.info("Agent registered in database", agent_id=agent.id, name=agent.name)
        return agent
    
    async def get_agent(self, agent_id: str, db: AsyncSession = None) -> Optional[DBAgent]:
        """Get agent by ID."""
        if db is None:
            async with get_db_context() as db:
                return await self._get_agent(db, agent_id)
        
        return await self._get_agent(db, agent_id)
    
    async def _get_agent(self, db: AsyncSession, agent_id: str) -> Optional[DBAgent]:
        """Internal method to get agent."""
        stmt = select(DBAgent).where(DBAgent.id == agent_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_agents(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        db: AsyncSession = None
    ) -> List[DBAgent]:
        """List agents with optional filtering."""
        if db is None:
            async with get_db_context() as db:
                return await self._list_agents(db, role, status)
        
        return await self._list_agents(db, role, status)
    
    async def _list_agents(
        self,
        db: AsyncSession,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[DBAgent]:
        """Internal method to list agents."""
        stmt = select(DBAgent)
        
        if role:
            stmt = stmt.where(DBAgent.role == role)
        if status:
            stmt = stmt.where(DBAgent.status == status)
            
        stmt = stmt.order_by(DBAgent.created_at.desc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Global service instances
project_service = DatabaseProjectService()
workflow_service = DatabaseWorkflowService()
agent_service = DatabaseAgentService()


def get_project_service() -> DatabaseProjectService:
    """Get project service instance."""
    return project_service


def get_workflow_service() -> DatabaseWorkflowService:
    """Get workflow service instance."""
    return workflow_service


def get_agent_service() -> DatabaseAgentService:
    """Get agent service instance."""
    return agent_service