"""
Project service for AI Software Factory.

This module provides business logic for project management operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from backend.core.logging import get_logger
from backend.models.task import Task, TaskStatus, TaskPriority

logger = get_logger(__name__)


class ProjectService:
    """
    Service for managing projects.
    
    This service handles project CRUD operations, lifecycle management,
    and integration with workflows and agents.
    """
    
    def __init__(self):
        """Initialize the project service."""
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._logger = get_logger(__name__)
    
    async def create_project(
        self,
        name: str,
        description: str,
        requirements: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            requirements: Project requirements
            created_by: User ID of creator
            
        Returns:
            Created project data
        """
        project_id = str(uuid4())
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "requirements": requirements,
            "status": "draft",
            "current_phase": "idea",
            "progress_percent": 0.0,
            "tech_stack": {},
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        self._projects[project_id] = project
        self._logger.info("Project created", project_id=project_id, name=name)
        
        return project
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data or None if not found
        """
        return self._projects.get(project_id)
    
    async def list_projects(
        self,
        status: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List projects with optional filtering.
        
        Args:
            status: Filter by status
            created_by: Filter by creator
            
        Returns:
            List of project data
        """
        projects = list(self._projects.values())
        
        if status:
            projects = [p for p in projects if p["status"] == status]
        if created_by:
            projects = [p for p in projects if p["created_by"] == created_by]
        
        return sorted(projects, key=lambda p: p["created_at"], reverse=True)
    
    async def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a project.
        
        Args:
            project_id: Project ID
            updates: Fields to update
            
        Returns:
            Updated project data or None if not found
        """
        project = self._projects.get(project_id)
        if not project:
            return None
        
        # Update allowed fields
        allowed_fields = ["name", "description", "requirements", "status", 
                         "current_phase", "tech_stack", "metadata"]
        for field in allowed_fields:
            if field in updates:
                project[field] = updates[field]
        
        project["updated_at"] = datetime.utcnow().isoformat()
        
        self._logger.info("Project updated", project_id=project_id)
        return project
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        if project_id in self._projects:
            del self._projects[project_id]
            self._logger.info("Project deleted", project_id=project_id)
            return True
        return False
    
    async def update_progress(
        self,
        project_id: str,
        progress_percent: float
    ) -> Optional[Dict[str, Any]]:
        """
        Update project progress.
        
        Args:
            project_id: Project ID
            progress_percent: Progress percentage (0-100)
            
        Returns:
            Updated project data or None if not found
        """
        project = self._projects.get(project_id)
        if not project:
            return None
        
        project["progress_percent"] = min(100.0, max(0.0, progress_percent))
        project["updated_at"] = datetime.utcnow().isoformat()
        
        return project
