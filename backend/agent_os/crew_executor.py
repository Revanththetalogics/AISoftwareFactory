"""
Crew executor for AgentOS.

This module provides execution of CrewAI crews with integration
into the AgentOS runtime environment.
"""

from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CrewExecutor:
    """
    Executor for CrewAI crews.

    Provides integration between CrewAI and AgentOS for
    crew-based task execution.
    """

    def __init__(self):
        """Initialize the crew executor."""
        self._active_crews: Dict[str, Any] = {}
        self._logger = get_logger(__name__)

    async def execute_crew(
        self,
        crew_name: str,
        crew_factory: Callable,
        inputs: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a CrewAI crew.

        Args:
            crew_name: Name of the crew
            crew_factory: Function that creates the crew
            inputs: Inputs for the crew
            task_id: Associated task ID

        Returns:
            Execution results
        """
        execution_id = str(uuid4())
        task_id = task_id or execution_id

        self._logger.info(
            "Starting crew execution",
            crew_name=crew_name,
            execution_id=execution_id,
            task_id=task_id
        )

        try:
            # Create the crew
            crew = crew_factory()
            self._active_crews[execution_id] = crew

            # Execute the crew
            result = crew.kickoff(inputs=inputs or {})

            self._logger.info(
                "Crew execution completed",
                crew_name=crew_name,
                execution_id=execution_id
            )

            return {
                "success": True,
                "execution_id": execution_id,
                "result": result,
                "crew_name": crew_name
            }

        except Exception as e:
            self._logger.error(
                "Crew execution failed",
                crew_name=crew_name,
                execution_id=execution_id,
                error=str(e)
            )

            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "crew_name": crew_name
            }

        finally:
            # Cleanup
            if execution_id in self._active_crews:
                del self._active_crews[execution_id]

    def get_active_crews(self) -> List[Dict[str, Any]]:
        """
        Get list of active crew executions.

        Returns:
            List of active crew information
        """
        return [
            {
                "execution_id": exec_id,
                "crew_type": type(crew).__name__
            }
            for exec_id, crew in self._active_crews.items()
        ]

    async def stop_crew(self, execution_id: str) -> bool:
        """
        Stop an active crew execution.

        Args:
            execution_id: Execution ID to stop

        Returns:
            True if stopped, False if not found
        """
        if execution_id in self._active_crews:
            del self._active_crews[execution_id]
            self._logger.info("Crew stopped", execution_id=execution_id)
            return True
        return False
