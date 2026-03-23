"""
Product Manager Agent Implementation.

This agent handles product requirements, user stories, and feature definitions
for the AI Software Factory.
"""

import time
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

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
        """Process Product Manager-specific tasks using the enterprise LLM router."""
        llm = get_llm_router().get_agent_llm(task_type="chat")
        task_handlers = {
            "requirements": self._handle_requirements,
            "user_stories": self._handle_user_stories,
            "feature_prioritization": self._handle_feature_prioritization,
            "product_spec": self._handle_product_spec,
            "ux_design": self._handle_ux_design,
        }
        handler = task_handlers.get(task.task_type, self._handle_generic_task)
        return await handler(task, llm=llm)

    async def _handle_requirements(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle requirements gathering tasks."""
        prompt = (
            f"You are an experienced Product Manager. Gather and document requirements for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: requirements (string summary), "
            f"functional (list of functional requirements), "
            f"non_functional (list of non-functional requirements), "
            f"constraints (list of constraints), "
            f"assumptions (list of assumptions), "
            f"acceptance_criteria (list of strings)."
        )
        raw = llm(prompt) if llm else f"Requirements for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "requirements": raw,
            "functional": [],
            "non_functional": [],
            "constraints": [],
            "assumptions": [],
            "acceptance_criteria": [],
        }

    async def _handle_user_stories(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle user story creation tasks."""
        prompt = (
            f"You are an experienced Product Manager. Write detailed user stories for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: user_stories (list of objects, each with "
            f"id, story, acceptance_criteria list, priority, and estimated_points)."
        )
        raw = llm(prompt) if llm else f"User stories for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {"user_stories": [{"id": "US-001", "story": raw, "acceptance_criteria": ["Task completed"], "priority": "medium", "estimated_points": 3}], "raw_output": raw}

    async def _handle_feature_prioritization(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle feature prioritization tasks."""
        prompt = (
            f"You are an experienced Product Manager. Prioritize features using MoSCoW for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: prioritization (string summary), "
            f"must_have (list of strings), should_have (list of strings), "
            f"could_have (list of strings), wont_have (list of strings), "
            f"moscow (object with m, s, c, w keys as lists), "
            f"rationale (string)."
        )
        raw = llm(prompt) if llm else f"Feature priorities for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "prioritization": raw,
            "must_have": [],
            "should_have": [],
            "could_have": [],
            "wont_have": [],
            "moscow": {"m": [], "s": [], "c": [], "w": []},
            "rationale": "",
        }

    async def _handle_product_spec(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle product specification tasks."""
        prompt = (
            f"You are an experienced Product Manager. Write a detailed product specification for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: specification (string full spec), "
            f"overview (string), target_users (list of strings), "
            f"key_features (list of strings), "
            f"success_metrics (list of strings), "
            f"out_of_scope (list of strings), "
            f"timeline_estimate (string)."
        )
        raw = llm(prompt) if llm else f"Product spec for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "specification": raw,
            "overview": "",
            "target_users": [],
            "key_features": [],
            "success_metrics": [],
            "out_of_scope": [],
            "timeline_estimate": "TBD",
        }

    async def _handle_ux_design(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle UX design tasks."""
        prompt = (
            f"You are an experienced Product Manager with UX expertise. Design the UX for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: ux_design (string description), "
            f"user_flows (list of strings), wireframes (list of strings), "
            f"design_principles (list of strings), "
            f"accessibility_requirements (list of strings), "
            f"key_screens (list of objects with name, purpose, key_elements)."
        )
        raw = llm(prompt) if llm else f"UX design for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "ux_design": raw,
            "user_flows": [],
            "wireframes": [],
            "design_principles": [],
            "accessibility_requirements": [],
            "key_screens": [],
        }

    async def _handle_generic_task(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle generic tasks."""
        prompt = (
            f"You are an experienced Product Manager. Complete the following task:\n"
            f"Task type: {task.task_type}\n"
            f"Description: {task.description}\n\n"
            f"Provide a thorough, product-focused response."
        )
        result = llm(prompt) if llm else f"Processed: {task.description}"
        return {"result": result, "task_type": task.task_type}

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
