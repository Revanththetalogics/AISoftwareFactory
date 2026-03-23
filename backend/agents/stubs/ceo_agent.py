"""
CEO Agent Implementation.

This agent provides strategic leadership and high-level decision making
for the AI Software Factory.
"""

import time
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)


class CEOAgent(BaseAgent):
    """
    CEO Agent for strategic leadership and decision making.

    This agent is responsible for:
    - Strategic planning and vision
    - High-level decision making
    - Resource allocation
    - Team coordination
    - Risk assessment

    Example:
        >>> agent = CEOAgent()
        >>> task = Task(task_type="strategic_planning", description="Define Q1 goals")
        >>> result = await agent.execute_task(task)
    """

    def __init__(
        self,
        agent_id: str = None,
        name: str = "CEO Agent",
        **kwargs: Any,
    ):
        """
        Initialize the CEO Agent.

        Args:
            agent_id: Unique identifier
            name: Agent name
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="CEO",
            capabilities=[
                "strategic_planning",
                "decision_making",
                "resource_allocation",
                "risk_assessment",
                "team_coordination",
            ],
            description="Strategic leader responsible for overall project direction and decision making",
            **kwargs,
        )

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a CEO-level task.

        Args:
            task: Task to execute

        Returns:
            TaskResult: Result of task execution

        Example:
            >>> task = Task(
            ...     task_type="strategic_planning",
            ...     description="Define project roadmap"
            ... )
            >>> result = await agent.execute_task(task)
        """
        start_time = time.time()

        self._logger.info(
            "CEO Agent executing task",
            task_id=task.task_id,
            task_type=task.task_type,
        )

        try:
            output = await self._process_ceo_task(task)

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
                "CEO Agent task failed",
                task_id=task.task_id,
                error=str(exc),
            )

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(exc),
                execution_time_ms=execution_time,
            )

    async def _process_ceo_task(self, task: Task) -> dict[str, Any]:
        """
        Process CEO-specific tasks using the enterprise LLM router.

        Args:
            task: Task to process

        Returns:
            Dictionary with task output
        """
        llm = get_llm_router().get_agent_llm(task_type="reasoning")
        task_handlers = {
            "strategic_planning": self._handle_strategic_planning,
            "decision_making": self._handle_decision_making,
            "resource_allocation": self._handle_resource_allocation,
            "risk_assessment": self._handle_risk_assessment,
        }
        handler = task_handlers.get(task.task_type, self._handle_generic_task)
        return await handler(task, llm=llm)

    async def _handle_strategic_planning(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle strategic planning tasks."""
        prompt = (
            f"You are a strategic CEO. Create a detailed strategic plan for the following:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: plan (string), objectives (list of strings), "
            f"timeline (string), resources_needed (list of strings), key_risks (list of strings)."
        )
        raw = llm(prompt) if llm else f"Strategic plan for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                return parsed
        except Exception:  # noqa: S110
            pass
        return {
            "plan": raw,
            "objectives": [],
            "timeline": "TBD",
            "resources_needed": [],
            "key_risks": [],
        }

    async def _handle_decision_making(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle decision making tasks."""
        prompt = (
            f"You are a strategic CEO. Analyse and make a clear decision on:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: decision (string), rationale (string), "
            f"alternatives_considered (list of strings), risk_level (low|medium|high), "
            f"recommended_action (string)."
        )
        raw = llm(prompt) if llm else f"Decision on: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "decision": raw,
            "rationale": "",
            "alternatives_considered": [],
            "risk_level": "unknown",
            "recommended_action": raw,
        }

    async def _handle_resource_allocation(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle resource allocation tasks."""
        prompt = (
            f"You are a strategic CEO. Propose a resource allocation plan for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: allocation (string description), budget (string), "
            f"team_assignments (dict of role->headcount), timeline (string), "
            f"priority_areas (list of strings)."
        )
        raw = llm(prompt) if llm else f"Resource plan for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "allocation": raw,
            "budget": "TBD",
            "team_assignments": {},
            "timeline": "TBD",
            "priority_areas": [],
        }

    async def _handle_risk_assessment(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle risk assessment tasks."""
        prompt = (
            f"You are a strategic CEO. Perform a thorough risk assessment for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: assessment (string summary), "
            f"risks (list of objects with type, level, description, mitigation), "
            f"overall_risk_level (low|medium|high|critical), "
            f"recommended_mitigations (list of strings)."
        )
        raw = llm(prompt) if llm else f"Risk analysis for: {task.description}"
        try:
            import json
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "assessment": raw,
            "risks": [],
            "overall_risk_level": "unknown",
            "recommended_mitigations": [],
        }

    async def _handle_generic_task(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle generic tasks."""
        prompt = (
            f"You are a strategic CEO. Respond to the following task:\n"
            f"Task type: {task.task_type}\n"
            f"Description: {task.description}\n\n"
            f"Provide a thorough, actionable response."
        )
        result = llm(prompt) if llm else f"Processed: {task.description}"
        return {"result": result, "task_type": task.task_type}

    def _get_relevant_capabilities(self, task: Task) -> list:
        """Get capabilities relevant to the task."""
        capability_map = {
            "strategic_planning": ["strategic_planning"],
            "decision_making": ["decision_making"],
            "resource_allocation": ["resource_allocation"],
            "risk_assessment": ["risk_assessment"],
        }
        return capability_map.get(task.task_type, ["team_coordination"])
