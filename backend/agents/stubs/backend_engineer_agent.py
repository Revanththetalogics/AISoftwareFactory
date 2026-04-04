"""
Backend Engineer Agent Implementation.

This agent handles backend development, API design, and database schema
for the AI Software Factory.
"""

import time
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)


class BackendEngineerAgent(BaseAgent):
    """
    Backend Engineer Agent for server-side development.

    This agent is responsible for:
    - API design and implementation
    - Database schema design
    - Business logic implementation
    - Security implementation
    - Performance optimization
    - Testing and documentation

    Example:
        >>> agent = BackendEngineerAgent()
        >>> task = Task(task_type="api_design", description="Design user API")
        >>> result = await agent.execute_task(task)
    """

    def __init__(
        self,
        agent_id: str = None,
        name: str = "Backend Engineer Agent",
        **kwargs: Any,
    ):
        """
        Initialize the Backend Engineer Agent.

        Args:
            agent_id: Unique identifier
            name: Agent name
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="Backend Engineer",
            capabilities=[
                "api_design",
                "database_design",
                "business_logic",
                "security_implementation",
                "performance_optimization",
                "testing",
                "documentation",
            ],
            description="Backend expert responsible for server-side development and APIs",
            **kwargs,
        )

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a Backend Engineer-level task.

        Args:
            task: Task to execute

        Returns:
            TaskResult: Result of task execution
        """
        start_time = time.time()

        self._logger.info(
            "Backend Engineer Agent executing task",
            task_id=task.task_id,
            task_type=task.task_type,
        )

        try:
            output = await self._process_backend_task(task)

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
                "Backend Engineer Agent task failed",
                task_id=task.task_id,
                error=str(exc),
            )

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(exc),
                execution_time_ms=execution_time,
            )

    async def _process_backend_task(self, task: Task) -> dict[str, Any]:
        """Process Backend Engineer-specific tasks using the enterprise LLM router."""
        llm = get_llm_router().get_agent_llm(task_type="coding")
        task_handlers = {
            "api_design": self._handle_api_design,
            "database_design": self._handle_database_design,
            "business_logic": self._handle_business_logic,
            "security": self._handle_security,
            "performance": self._handle_performance,
            "testing": self._handle_testing,
        }

        handler = task_handlers.get(task.task_type, self._handle_generic_task)
        return await handler(task, llm=llm)

    async def _handle_api_design(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle API design tasks."""
        prompt = (
            f"You are a senior backend engineer. Design a complete REST API for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: api_design (string description), "
            f"endpoints (list of objects with path, method, description, auth_required), "
            f"authentication (string), rate_limiting (string), versioning (string), "
            f"error_handling (string)."
        )
        raw = llm(prompt) if llm else f"API design for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "api_design": raw,
            "endpoints": [{"path": "/api/v1/resource", "method": "GET", "description": raw, "auth_required": True}],
            "authentication": "JWT Bearer",
            "rate_limiting": "TBD",
            "versioning": "URL path versioning",
            "error_handling": "Standard HTTP error codes",
        }

    async def _handle_database_design(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle database design tasks."""
        prompt = (
            f"You are a senior backend engineer. Design a PostgreSQL database schema for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: database_design (string description), "
            f"entities (list of objects with name, fields list), "
            f"indexes (list of strings), constraints (list of strings), "
            f"migrations (list of strings describing migrations needed)."
        )
        raw = llm(prompt) if llm else f"Database design for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "database_design": raw,
            "entities": [],
            "indexes": [],
            "constraints": [],
            "migrations": [],
        }

    async def _handle_business_logic(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle business logic implementation tasks."""
        prompt = (
            f"You are a senior backend engineer. Design the business logic layer for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: business_logic (string description), "
            f"services (list of objects with name, methods list, responsibilities), "
            f"validation_rules (list of strings), "
            f"error_cases (list of strings), "
            f"code_outline (string with key class/function signatures)."
        )
        raw = llm(prompt) if llm else f"Business logic for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "business_logic": raw,
            "services": [],
            "validation_rules": [],
            "error_cases": [],
            "code_outline": "",
        }

    async def _handle_security(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle security implementation tasks."""
        prompt = (
            f"You are a senior backend security engineer. Design the security implementation for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: security (string description), "
            f"authentication (object with type, algorithm, expiration), "
            f"authorization (object with type, roles list), "
            f"data_protection (list of strings), "
            f"vulnerabilities_addressed (list of strings), "
            f"security_headers (list of strings)."
        )
        raw = llm(prompt) if llm else f"Security implementation for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "security": raw,
            "authentication": {},
            "authorization": {},
            "data_protection": [],
            "vulnerabilities_addressed": [],
            "security_headers": [],
        }

    async def _handle_performance(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle performance optimization tasks."""
        prompt = (
            f"You are a senior backend performance engineer. Design optimizations for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: performance (string description), "
            f"optimizations (list of strings), "
            f"caching_strategy (object mapping cache_type->strategy), "
            f"target_metrics (object mapping metric_name->target), "
            f"bottlenecks (list of strings), "
            f"profiling_approach (string)."
        )
        raw = llm(prompt) if llm else f"Performance optimization for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "performance": raw,
            "optimizations": [],
            "caching_strategy": {},
            "target_metrics": {},
            "bottlenecks": [],
            "profiling_approach": "",
        }

    async def _handle_testing(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle testing tasks."""
        prompt = (
            f"You are a senior backend engineer. Design a comprehensive test strategy for:\n"
            f"{task.description}\n\n"
            f"Respond as JSON with keys: testing (string description), "
            f"unit_tests (object with coverage_target, framework, test_files list), "
            f"integration_tests (object with coverage_target, scope list), "
            f"e2e_tests (object with scope list), "
            f"test_data_strategy (string), "
            f"ci_pipeline (string)."
        )
        raw = llm(prompt) if llm else f"Test suite for: {task.description}"
        try:
            import json
            import re

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:  # noqa: S110
            pass
        return {
            "testing": raw,
            "unit_tests": {},
            "integration_tests": {},
            "e2e_tests": {},
            "test_data_strategy": "",
            "ci_pipeline": "",
        }

    async def _handle_generic_task(self, task: Task, llm: Any = None) -> dict[str, Any]:
        """Handle generic tasks."""
        prompt = (
            f"You are a senior backend engineer. Complete the following task:\n"
            f"Task type: {task.task_type}\n"
            f"Description: {task.description}\n\n"
            f"Provide a detailed, technical response."
        )
        result = llm(prompt) if llm else f"Processed: {task.description}"
        return {
            "result": result,
            "task_type": task.task_type,
        }

    def _get_relevant_capabilities(self, task: Task) -> list:
        """Get capabilities relevant to the task."""
        capability_map = {
            "api_design": ["api_design"],
            "database_design": ["database_design"],
            "business_logic": ["business_logic"],
            "security": ["security_implementation"],
            "performance": ["performance_optimization"],
            "testing": ["testing"],
        }
        return capability_map.get(task.task_type, ["business_logic"])
