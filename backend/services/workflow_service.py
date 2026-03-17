"""
Workflow service for AI Software Factory.

This module provides business logic for workflow management operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from backend.core.logging import get_logger
from backend.models.workflow import Workflow, WorkflowStatus, WorkflowStep
from backend.workflows.workflow_engine import WorkflowEngine

logger = get_logger(__name__)


class WorkflowService:
    """
    Service for managing workflows.
    
    This service handles workflow lifecycle, execution, and integration
    with the workflow engine.
    """
    
    def __init__(self):
        """Initialize the workflow service."""
        self._workflows: Dict[str, Workflow] = {}
        self._engine = WorkflowEngine()
        self._logger = get_logger(__name__)
    
    async def create_workflow(
        self,
        name: str,
        project_id: str,
        description: str = "",
        steps: Optional[List[Dict[str, Any]]] = None,
        created_by: Optional[str] = None
    ) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            project_id: Associated project ID
            description: Workflow description
            steps: List of workflow steps
            created_by: User ID of creator
            
        Returns:
            Created workflow
        """
        workflow_id = str(uuid4())
        
        # Convert step dicts to WorkflowStep objects
        workflow_steps = []
        if steps:
            for step_data in steps:
                workflow_steps.append(WorkflowStep(**step_data))
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            project_id=project_id,
            steps=workflow_steps,
            status=WorkflowStatus.PENDING,
            created_by=created_by,
            context={}
        )
        
        self._workflows[workflow_id] = workflow
        self._logger.info("Workflow created", workflow_id=workflow_id, name=name)
        
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow or None if not found
        """
        return self._workflows.get(workflow_id)
    
    async def list_workflows(
        self,
        project_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None
    ) -> List[Workflow]:
        """
        List workflows with optional filtering.
        
        Args:
            project_id: Filter by project ID
            status: Filter by status
            
        Returns:
            List of workflows
        """
        workflows = list(self._workflows.values())
        
        if project_id:
            workflows = [w for w in workflows if w.project_id == project_id]
        if status:
            workflows = [w for w in workflows if w.status == status]
        
        return workflows
    
    async def start_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Start a workflow execution.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Updated workflow or None if not found
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None
        
        if not workflow.can_execute():
            self._logger.warning(
                "Cannot start workflow",
                workflow_id=workflow_id,
                status=workflow.status
            )
            return workflow
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        # Execute via workflow engine
        try:
            result = await self._engine.run(workflow)
            self._logger.info("Workflow execution completed", workflow_id=workflow_id)
        except Exception as e:
            self._logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                error=str(e)
            )
            workflow.status = WorkflowStatus.FAILED
        
        return workflow
    
    async def cancel_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Cancel a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Updated workflow or None if not found
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None
        
        if workflow.is_complete():
            return workflow
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()
        
        self._logger.info("Workflow cancelled", workflow_id=workflow_id)
        return workflow
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if deleted, False if not found
        """
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            self._logger.info("Workflow deleted", workflow_id=workflow_id)
            return True
        return False
