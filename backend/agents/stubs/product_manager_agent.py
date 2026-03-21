"""
Product Manager Agent Implementation.

This agent handles product requirements, user stories, and feature definitions
for the AI Software Factory.
"""

import time
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger

logger = get_logger(__name__)


class ProductManagerAgent(BaseAgent):
    """
    Product Manager Agent for requirements and product definition.

    This agent is responsible for:
    - Requirements gathering and documentation
    - User story creation
    - Feature prioritization
    - Product specification
    - User experience design

    Example:
        >>> agent = ProductManagerAgent()
        >>> task = Task(task_type="requirements", description="Define user login flow")
        >>> result = await agent.execute_task(task)
    """

    def __init__(
        self,
        agent_id: str = None,
        name: str = "Product Manager Agent",
        **kwargs: Any,
    ):
        """
        Initialize the Product Manager Agent.

        Args:
            agent_id: Unique identifier
            name: Agent name
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="Product Manager",
            capabilities=[
                "requirements_gathering",
                "user_story_creation",
                "feature_prioritization",
                "product_specification",
                "ux_design",
                "market_research",
            ],
            description="Product expert responsible for translating ideas into actionable requirements",
            **kwargs,
        )

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a Product Manager-level task.

        Args:
            task: Task to execute

        Returns:
            TaskResult: Result of task execution
        """
        start_time = time.time()

        self._logger.info(
            "Product Manager Agent executing task",
            task_id=task.task_id,
            task_type=task.task_type,
        )

        try:
            output = await self._process_pm_task(task)

            execution_time = (time.time() - start_time) * 1000

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output=output,
                execution_time_ms=execution_time,
                metadata={
                    "agent_role": self.role,
                    "capabilities_used": self._get_relevant_capabilities(task),
                },
            )

        except Exception as exc:
            execution_time = (time.time() - start_time) * 1000
            self._logger.error(
                "Product Manager Agent task failed",
                task_id=task.task_id,
                error=str(exc),
            )

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(exc),
                execution_time_ms=execution_time,
            )

    async def _process_pm_task(self, task: Task) -> dict[str, Any]:
        """Process Product Manager-specific tasks."""
        task_handlers = {
            "requirements": self._handle_requirements,
            "user_stories": self._handle_user_stories,
            "feature_prioritization": self._handle_feature_prioritization,
            "product_spec": self._handle_product_spec,
            "ux_design": self._handle_ux_design,
        }

        handler = task_handlers.get(task.task_type, self._handle_generic_task)
        return await handler(task)

    async def _handle_requirements(self, task: Task) -> dict[str, Any]:
        """Handle requirements gathering tasks."""
        return {
            "requirements": f"Requirements for: {task.description}",
            "functional": [
                "User can create account",
                "User can log in",
                "User can reset password",
            ],
            "non_functional": [
                "Response time < 200ms",
                "99.9% uptime",
                "WCAG 2.1 AA compliance",
            ],
            "constraints": [
                "Must use existing auth provider",
                "GDPR compliant",
            ],
        }

    async def _handle_user_stories(self, task: Task) -> dict[str, Any]:
        """Handle user story creation tasks."""
        return {
            "user_stories": [
                {
                    "id": "US-001",
                    "story": "As a user, I want to create an account so that I can access the platform",
                    "acceptance_criteria": [
                        "User can enter email and password",
                        "System validates email format",
                        "System sends confirmation email",
                    ],
                    "priority": "high",
                },
                {
                    "id": "US-002",
                    "story": "As a user, I want to log in so that I can access my account",
                    "acceptance_criteria": [
                        "User can enter credentials",
                        "System validates credentials",
                        "User is redirected to dashboard",
                    ],
                    "priority": "high",
                },
            ],
        }

    async def _handle_feature_prioritization(self, task: Task) -> dict[str, Any]:
        """Handle feature prioritization tasks."""
        return {
            "prioritization": f"Feature priorities for: {task.description}",
            "must_have": ["User authentication", "Dashboard", "Profile management"],
            "should_have": ["Notifications", "Search", "Filters"],
            "nice_to_have": ["Dark mode", "Export data", "API access"],
            "moscow": {
                "m": ["Auth", "Core features"],
                "s": ["Enhanced features"],
                "c": ["Nice-to-haves"],
                "w": ["Future enhancements"],
            },
        }

    async def _handle_product_spec(self, task: Task) -> dict[str, Any]:
        """Handle product specification tasks."""
        return {
            "specification": f"Product spec for: {task.description}",
            "overview": "Product overview and value proposition",
            "target_users": ["Small businesses", "Enterprise teams", "Individual users"],
            "key_features": ["Feature A", "Feature B", "Feature C"],
            "success_metrics": ["User adoption", "Retention rate", "NPS score"],
        }

    async def _handle_ux_design(self, task: Task) -> dict[str, Any]:
        """Handle UX design tasks."""
        return {
            "ux_design": f"UX design for: {task.description}",
            "user_flows": ["Registration flow", "Login flow", "Onboarding"],
            "wireframes": ["Homepage", "Dashboard", "Settings"],
            "design_principles": ["Simplicity", "Consistency", "Accessibility"],
        }

    async def _handle_generic_task(self, task: Task) -> dict[str, Any]:
        """Handle generic tasks."""
        return {
            "result": f"Processed: {task.description}",
            "task_type": task.task_type,
        }

    def _get_relevant_capabilities(self, task: Task) -> list:
        """Get capabilities relevant to the task."""
        capability_map = {
            "requirements": ["requirements_gathering"],
            "user_stories": ["user_story_creation"],
            "feature_prioritization": ["feature_prioritization"],
            "product_spec": ["product_specification"],
            "ux_design": ["ux_design"],
        }
        return capability_map.get(task.task_type, ["requirements_gathering"])
