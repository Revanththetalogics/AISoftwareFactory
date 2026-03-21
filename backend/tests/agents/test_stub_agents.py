"""
Tests for Stub Agent implementations.
"""

import pytest

from backend.agents.base_agent import Task, TaskStatus
from backend.agents.stubs.backend_engineer_agent import BackendEngineerAgent
from backend.agents.stubs.ceo_agent import CEOAgent
from backend.agents.stubs.product_manager_agent import ProductManagerAgent


class TestCEOAgent:
    """Test cases for CEOAgent."""

    @pytest.mark.asyncio
    async def test_strategic_planning_task(self):
        """Test strategic planning task execution."""
        agent = CEOAgent()
        task = Task(
            task_type="strategic_planning",
            description="Define Q1 goals",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "plan" in result.output
        assert "objectives" in result.output

    @pytest.mark.asyncio
    async def test_decision_making_task(self):
        """Test decision making task execution."""
        agent = CEOAgent()
        task = Task(
            task_type="decision_making",
            description="Choose tech stack",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "decision" in result.output
        assert "rationale" in result.output

    @pytest.mark.asyncio
    async def test_resource_allocation_task(self):
        """Test resource allocation task execution."""
        agent = CEOAgent()
        task = Task(
            task_type="resource_allocation",
            description="Allocate team for Project X",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "allocation" in result.output
        assert "team_assignments" in result.output

    @pytest.mark.asyncio
    async def test_risk_assessment_task(self):
        """Test risk assessment task execution."""
        agent = CEOAgent()
        task = Task(
            task_type="risk_assessment",
            description="Assess project risks",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "assessment" in result.output
        assert "risks" in result.output

    def test_capabilities(self):
        """Test agent capabilities."""
        agent = CEOAgent()

        assert agent.has_capability("strategic_planning")
        assert agent.has_capability("decision_making")
        assert agent.has_capability("resource_allocation")
        assert agent.has_capability("risk_assessment")


class TestProductManagerAgent:
    """Test cases for ProductManagerAgent."""

    @pytest.mark.asyncio
    async def test_requirements_task(self):
        """Test requirements gathering task."""
        agent = ProductManagerAgent()
        task = Task(
            task_type="requirements",
            description="Define login requirements",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "requirements" in result.output
        assert "functional" in result.output

    @pytest.mark.asyncio
    async def test_user_stories_task(self):
        """Test user stories creation task."""
        agent = ProductManagerAgent()
        task = Task(
            task_type="user_stories",
            description="Create user stories for auth",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "user_stories" in result.output
        assert len(result.output["user_stories"]) > 0

    @pytest.mark.asyncio
    async def test_feature_prioritization_task(self):
        """Test feature prioritization task."""
        agent = ProductManagerAgent()
        task = Task(
            task_type="feature_prioritization",
            description="Prioritize MVP features",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "must_have" in result.output
        assert "should_have" in result.output

    def test_capabilities(self):
        """Test agent capabilities."""
        agent = ProductManagerAgent()

        assert agent.has_capability("requirements_gathering")
        assert agent.has_capability("user_story_creation")
        assert agent.has_capability("feature_prioritization")


class TestBackendEngineerAgent:
    """Test cases for BackendEngineerAgent."""

    @pytest.mark.asyncio
    async def test_api_design_task(self):
        """Test API design task."""
        agent = BackendEngineerAgent()
        task = Task(
            task_type="api_design",
            description="Design user API",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "endpoints" in result.output
        assert len(result.output["endpoints"]) > 0

    @pytest.mark.asyncio
    async def test_database_design_task(self):
        """Test database design task."""
        agent = BackendEngineerAgent()
        task = Task(
            task_type="database_design",
            description="Design user schema",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "entities" in result.output
        assert "indexes" in result.output

    @pytest.mark.asyncio
    async def test_security_task(self):
        """Test security implementation task."""
        agent = BackendEngineerAgent()
        task = Task(
            task_type="security",
            description="Implement auth security",
        )

        result = await agent.execute_task(task)

        assert result.status == TaskStatus.COMPLETED
        assert "authentication" in result.output
        assert "authorization" in result.output

    def test_capabilities(self):
        """Test agent capabilities."""
        agent = BackendEngineerAgent()

        assert agent.has_capability("api_design")
        assert agent.has_capability("database_design")
        assert agent.has_capability("security_implementation")
