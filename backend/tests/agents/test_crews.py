"""
Tests for crew modules - CEO Crew and Engineering Crew.

Achieves 100% coverage for:
- backend/agents/crews/ceo_crew.py
- backend/agents/crews/engineering_crew.py
"""

from unittest.mock import Mock, patch

import pytest


# We need to patch before importing to handle abstract class
@pytest.fixture(autouse=True)
def patch_abstract():
    """Patch abstract method to allow instantiation."""
    with patch.object(
        __import__('backend.agents.base_agent', fromlist=['BaseAgent']).BaseAgent,
        '__abstractmethods__',
        frozenset()
    ):
        yield


class TestCEOCrew:
    """Tests for CEOCrew."""

    def test_ceo_crew_init(self):
        """Test CEOCrew initialization."""
        from backend.agents.crews.ceo_crew import CEOCrew

        with patch.object(CEOCrew, '__abstractmethods__', frozenset()):
            crew = object.__new__(CEOCrew)
            crew.__init__()
            assert crew.name == "CEO Crew"

    @patch('backend.agents.crews.ceo_crew.Agent')
    @patch('backend.agents.crews.ceo_crew.Crew')
    def test_create_crew(self, mock_crew_class, mock_agent_class):
        """Test creating CEO crew with agents."""
        from backend.agents.crews.ceo_crew import CEOCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        # Create instance by bypassing __init__
        ceo_crew = object.__new__(CEOCrew)
        ceo_crew._logger = Mock()

        crew = ceo_crew.create_crew()

        assert crew == mock_crew_instance
        # Should create 3 agents: CEO, PM, Tech Lead
        assert mock_agent_class.call_count == 3
        mock_crew_class.assert_called_once()

    @patch('backend.agents.crews.ceo_crew.Agent')
    @patch('backend.agents.crews.ceo_crew.Crew')
    @patch('backend.agents.crews.ceo_crew.Task')
    @pytest.mark.asyncio
    async def test_make_strategic_decision(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test making strategic decision."""
        from backend.agents.crews.ceo_crew import CEOCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Strategic decision result")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        # Create instance by bypassing __init__
        ceo_crew = object.__new__(CEOCrew)
        ceo_crew._logger = Mock()

        context = {
            "project_state": "In Progress",
            "options": ["Option A", "Option B"],
            "constraints": ["Budget limit"]
        }

        result = await ceo_crew.make_strategic_decision(context)

        assert result["decision"] == "Strategic decision result"
        assert result["crew"] == "CEO Crew"
        assert result["context"] == context

    @patch('backend.agents.crews.ceo_crew.Agent')
    @patch('backend.agents.crews.ceo_crew.Crew')
    @patch('backend.agents.crews.ceo_crew.Task')
    @pytest.mark.asyncio
    async def test_make_strategic_decision_empty_context(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test making strategic decision with empty context."""
        from backend.agents.crews.ceo_crew import CEOCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Decision")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        ceo_crew = object.__new__(CEOCrew)
        ceo_crew._logger = Mock()

        result = await ceo_crew.make_strategic_decision({})

        assert result["decision"] == "Decision"
        assert result["context"] == {}

    @patch('backend.agents.crews.ceo_crew.Agent')
    @patch('backend.agents.crews.ceo_crew.Crew')
    @patch('backend.agents.crews.ceo_crew.Task')
    @pytest.mark.asyncio
    async def test_review_project_status(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test reviewing project status."""
        from backend.agents.crews.ceo_crew import CEOCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Project review")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        ceo_crew = object.__new__(CEOCrew)
        ceo_crew._logger = Mock()

        project_data = {
            "name": "Test Project",
            "status": "Active",
            "progress": 75,
            "issues": ["Issue 1", "Issue 2"]
        }

        result = await ceo_crew.review_project_status(project_data)

        assert result["review"] == "Project review"
        assert result["crew"] == "CEO Crew"
        assert result["project"] == "Test Project"

    @patch('backend.agents.crews.ceo_crew.Agent')
    @patch('backend.agents.crews.ceo_crew.Crew')
    @patch('backend.agents.crews.ceo_crew.Task')
    @pytest.mark.asyncio
    async def test_review_project_status_empty_data(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test reviewing project status with empty data."""
        from backend.agents.crews.ceo_crew import CEOCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Review result")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        ceo_crew = object.__new__(CEOCrew)
        ceo_crew._logger = Mock()

        result = await ceo_crew.review_project_status({})

        assert result["review"] == "Review result"
        assert result["project"] is None


class TestEngineeringCrew:
    """Tests for EngineeringCrew."""

    def test_engineering_crew_init(self):
        """Test EngineeringCrew initialization."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        crew = object.__new__(EngineeringCrew)
        crew.__init__()
        assert crew.name == "Engineering Crew"

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    def test_create_crew(self, mock_crew_class, mock_agent_class):
        """Test creating engineering crew with agents."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        crew = eng_crew.create_crew()

        assert crew == mock_crew_instance
        # Should create 3 agents: Senior Dev, Reviewer, QA
        assert mock_agent_class.call_count == 3

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_implement_feature(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test implementing a feature."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Feature implemented")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        feature_spec = {
            "name": "User Authentication",
            "description": "Implement OAuth login",
            "requirements": ["Req 1", "Req 2"],
            "acceptance_criteria": ["Criteria 1", "Criteria 2"]
        }

        result = await eng_crew.implement_feature(feature_spec)

        assert result["implementation"] == "Feature implemented"
        assert result["crew"] == "Engineering Crew"
        assert result["feature"] == "User Authentication"

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_implement_feature_empty_spec(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test implementing feature with empty spec."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Result")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        result = await eng_crew.implement_feature({})

        assert result["feature"] is None

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_review_code(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test reviewing code."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Code review result")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        code = "def hello_world():\n    print('Hello, World!')\n"
        context = {"language": "python"}

        result = await eng_crew.review_code(code, context)

        assert result["review"] == "Code review result"
        assert result["crew"] == "Engineering Crew"
        assert result["lines_reviewed"] == 2

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_review_code_without_context(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test reviewing code without context."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Review")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        result = await eng_crew.review_code("print('hi')")

        assert result["review"] == "Review"

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_review_code_long_code(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test reviewing long code (truncation)."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Review")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        long_code = "x = 1\n" * 5000  # Long code
        result = await eng_crew.review_code(long_code)

        assert result["lines_reviewed"] == 5000

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_create_tests_unit(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test creating unit tests."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Test suite")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        code = "def add(a, b): return a + b"

        result = await eng_crew.create_tests(code, test_type="unit")

        assert result["tests"] == "Test suite"
        assert result["crew"] == "Engineering Crew"
        assert result["test_type"] == "unit"

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_create_tests_integration(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test creating integration tests."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Integration tests")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        result = await eng_crew.create_tests("code", test_type="integration")

        assert result["test_type"] == "integration"

    @patch('backend.agents.crews.engineering_crew.Agent')
    @patch('backend.agents.crews.engineering_crew.Crew')
    @patch('backend.agents.crews.engineering_crew.Task')
    @pytest.mark.asyncio
    async def test_create_tests_default_type(
        self,
        mock_task_class,
        mock_crew_class,
        mock_agent_class
    ):
        """Test creating tests with default type."""
        from backend.agents.crews.engineering_crew import EngineeringCrew

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_instance.agents = [mock_agent, mock_agent, mock_agent]
        mock_crew_instance.kickoff = Mock(return_value="Tests")
        mock_crew_class.return_value = mock_crew_instance

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        eng_crew = object.__new__(EngineeringCrew)
        eng_crew._logger = Mock()

        result = await eng_crew.create_tests("code")

        assert result["test_type"] == "unit"


class TestPlanningCrew:
    """Tests for planning_crew module."""

    @patch('backend.agents.crews.planning_crew.get_llm_router')
    @patch('backend.agents.crews.planning_crew.get_ceo_role')
    @patch('backend.agents.crews.planning_crew.get_product_manager_role')
    @patch('backend.agents.crews.planning_crew.Crew')
    def test_create_planning_crew(
        self,
        mock_crew_class,
        mock_pm_role,
        mock_ceo_role,
        mock_get_router
    ):
        """Test creating planning crew - LLM is auto-wired from router."""
        from backend.agents.crews.planning_crew import create_planning_crew

        mock_llm = Mock()
        mock_get_router.return_value.get_agent_llm.return_value = mock_llm

        mock_agent = Mock()
        mock_ceo_role.return_value = mock_agent
        mock_pm_role.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        crew = create_planning_crew()

        assert crew == mock_crew_instance
        mock_get_router.return_value.get_agent_llm.assert_called_once_with(task_type="reasoning")
        mock_ceo_role.assert_called_once_with(llm=mock_llm)
        mock_pm_role.assert_called_once_with(llm=mock_llm)
        mock_crew_class.assert_called_once()

    @patch('backend.agents.crews.planning_crew.Task')
    def test_create_requirements_task(self, mock_task_class):
        """Test creating requirements task."""
        from backend.agents.crews.planning_crew import create_requirements_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_requirements_task("Build a web app")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Build a web app" in call_args.kwargs['description']

    @patch('backend.agents.crews.planning_crew.Task')
    def test_create_product_strategy_task(self, mock_task_class):
        """Test creating product strategy task."""
        from backend.agents.crews.planning_crew import create_product_strategy_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_product_strategy_task("Requirements doc")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Requirements doc" in call_args.kwargs['description']


class TestDesignCrew:
    """Tests for design_crew module."""

    @patch('backend.agents.crews.design_crew.get_llm_router')
    @patch('backend.agents.crews.design_crew.get_ceo_role')
    @patch('backend.agents.crews.design_crew.get_architect_role')
    @patch('backend.agents.crews.design_crew.get_product_manager_role')
    @patch('backend.agents.crews.design_crew.Crew')
    def test_create_design_crew(
        self,
        mock_crew_class,
        mock_pm_role,
        mock_architect_role,
        mock_ceo_role,
        mock_get_router
    ):
        """Test creating design crew - LLM is auto-wired from router."""
        from backend.agents.crews.design_crew import create_design_crew

        mock_llm = Mock()
        mock_get_router.return_value.get_agent_llm.return_value = mock_llm

        mock_agent = Mock()
        mock_ceo_role.return_value = mock_agent
        mock_architect_role.return_value = mock_agent
        mock_pm_role.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        crew = create_design_crew()

        assert crew == mock_crew_instance
        mock_get_router.return_value.get_agent_llm.assert_called_once_with(task_type="reasoning")
        mock_ceo_role.assert_called_once_with(llm=mock_llm)
        mock_architect_role.assert_called_once_with(llm=mock_llm)
        mock_pm_role.assert_called_once_with(llm=mock_llm)

    @patch('backend.agents.crews.design_crew.Task')
    def test_create_architecture_task(self, mock_task_class):
        """Test creating architecture task."""
        from backend.agents.crews.design_crew import create_architecture_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_architecture_task("Requirements document")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Requirements document" in call_args.kwargs['description']

    @patch('backend.agents.crews.design_crew.Task')
    def test_create_technology_selection_task(self, mock_task_class):
        """Test creating technology selection task."""
        from backend.agents.crews.design_crew import create_technology_selection_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_technology_selection_task("Architecture doc")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Architecture doc" in call_args.kwargs['description']


class TestImplementationCrew:
    """Tests for implementation_crew module."""

    @patch('backend.agents.crews.implementation_crew.get_llm_router')
    @patch('backend.agents.crews.implementation_crew.get_architect_role')
    @patch('backend.agents.crews.implementation_crew.get_backend_engineer_role')
    @patch('backend.agents.crews.implementation_crew.get_frontend_engineer_role')
    @patch('backend.agents.crews.implementation_crew.get_product_manager_role')
    @patch('backend.agents.crews.implementation_crew.Crew')
    def test_create_implementation_crew(
        self,
        mock_crew_class,
        mock_pm_role,
        mock_frontend_role,
        mock_backend_role,
        mock_architect_role,
        mock_get_router
    ):
        """Test creating implementation crew - LLM is auto-wired from router."""
        from backend.agents.crews.implementation_crew import create_implementation_crew

        mock_llm = Mock()
        mock_get_router.return_value.get_agent_llm.return_value = mock_llm

        mock_agent = Mock()
        mock_architect_role.return_value = mock_agent
        mock_backend_role.return_value = mock_agent
        mock_frontend_role.return_value = mock_agent
        mock_pm_role.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        crew = create_implementation_crew()

        assert crew == mock_crew_instance
        mock_get_router.return_value.get_agent_llm.assert_called_once_with(task_type="coding")
        mock_architect_role.assert_called_once_with(llm=mock_llm)
        mock_backend_role.assert_called_once_with(llm=mock_llm)
        mock_frontend_role.assert_called_once_with(llm=mock_llm)
        mock_pm_role.assert_called_once_with(llm=mock_llm)

    @patch('backend.agents.crews.implementation_crew.Task')
    def test_create_backend_implementation_task(self, mock_task_class):
        """Test creating backend implementation task."""
        from backend.agents.crews.implementation_crew import create_backend_implementation_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_backend_implementation_task("Architecture", "Requirements")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Architecture" in call_args.kwargs['description']
        assert "Requirements" in call_args.kwargs['description']

    @patch('backend.agents.crews.implementation_crew.Task')
    def test_create_frontend_implementation_task(self, mock_task_class):
        """Test creating frontend implementation task."""
        from backend.agents.crews.implementation_crew import create_frontend_implementation_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_frontend_implementation_task("Architecture doc", "Requirements doc")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Architecture doc" in call_args.kwargs['description']
        assert "Requirements doc" in call_args.kwargs['description']


class TestDeploymentCrew:
    """Tests for deployment_crew module."""

    @patch('backend.agents.crews.deployment_crew.get_llm_router')
    @patch('backend.agents.crews.deployment_crew.get_devops_engineer_role')
    @patch('backend.agents.crews.deployment_crew.get_architect_role')
    @patch('backend.agents.crews.deployment_crew.get_backend_engineer_role')
    @patch('backend.agents.crews.deployment_crew.Crew')
    def test_create_deployment_crew(
        self,
        mock_crew_class,
        mock_backend_role,
        mock_architect_role,
        mock_devops_role,
        mock_get_router
    ):
        """Test creating deployment crew - LLM is auto-wired from router."""
        from backend.agents.crews.deployment_crew import create_deployment_crew

        mock_llm = Mock()
        mock_get_router.return_value.get_agent_llm.return_value = mock_llm

        mock_agent = Mock()
        mock_devops_role.return_value = mock_agent
        mock_architect_role.return_value = mock_agent
        mock_backend_role.return_value = mock_agent

        mock_crew_instance = Mock()
        mock_crew_class.return_value = mock_crew_instance

        crew = create_deployment_crew()

        assert crew == mock_crew_instance
        mock_get_router.return_value.get_agent_llm.assert_called_once_with(task_type="coding")
        mock_devops_role.assert_called_once_with(llm=mock_llm)
        mock_architect_role.assert_called_once_with(llm=mock_llm)
        mock_backend_role.assert_called_once_with(llm=mock_llm)

    @patch('backend.agents.crews.deployment_crew.Task')
    def test_create_infrastructure_task(self, mock_task_class):
        """Test creating infrastructure task."""
        from backend.agents.crews.deployment_crew import create_infrastructure_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_infrastructure_task("Architecture document")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Architecture document" in call_args.kwargs['description']

    @patch('backend.agents.crews.deployment_crew.Task')
    def test_create_cicd_task(self, mock_task_class):
        """Test creating CI/CD task."""
        from backend.agents.crews.deployment_crew import create_cicd_task

        mock_task = Mock()
        mock_task_class.return_value = mock_task

        task = create_cicd_task("Infrastructure doc")

        assert task == mock_task
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args
        assert "Infrastructure doc" in call_args.kwargs['description']


class TestAgentRoles:
    """Tests for all agent role functions."""

    @patch('backend.agents.roles.architect_role.Agent')
    def test_get_architect_role(self, mock_agent_class):
        """Test get_architect_role creates correct agent."""
        from backend.agents.roles.architect_role import get_architect_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_architect_role()

        assert agent == mock_agent
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "System Architect"
        assert call_kwargs['verbose'] is True
        assert call_kwargs['allow_delegation'] is True
        assert call_kwargs['llm'] is None

    @patch('backend.agents.roles.architect_role.Agent')
    def test_get_architect_role_with_llm(self, mock_agent_class):
        """Test get_architect_role with custom LLM."""
        from backend.agents.roles.architect_role import get_architect_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_architect_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm

    @patch('backend.agents.roles.backend_engineer_role.Agent')
    def test_get_backend_engineer_role(self, mock_agent_class):
        """Test get_backend_engineer_role creates correct agent."""
        from backend.agents.roles.backend_engineer_role import get_backend_engineer_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_backend_engineer_role()

        assert agent == mock_agent
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "Backend Engineer"
        assert call_kwargs['allow_delegation'] is False

    @patch('backend.agents.roles.backend_engineer_role.Agent')
    def test_get_backend_engineer_role_with_llm(self, mock_agent_class):
        """Test get_backend_engineer_role with custom LLM."""
        from backend.agents.roles.backend_engineer_role import get_backend_engineer_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_backend_engineer_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm

    @patch('backend.agents.roles.devops_engineer_role.Agent')
    def test_get_devops_engineer_role(self, mock_agent_class):
        """Test get_devops_engineer_role creates correct agent."""
        from backend.agents.roles.devops_engineer_role import get_devops_engineer_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_devops_engineer_role()

        assert agent == mock_agent
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "DevOps Engineer"

    @patch('backend.agents.roles.devops_engineer_role.Agent')
    def test_get_devops_engineer_role_with_llm(self, mock_agent_class):
        """Test get_devops_engineer_role with custom LLM."""
        from backend.agents.roles.devops_engineer_role import get_devops_engineer_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_devops_engineer_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm

    @patch('backend.agents.roles.frontend_engineer_role.Agent')
    def test_get_frontend_engineer_role(self, mock_agent_class):
        """Test get_frontend_engineer_role creates correct agent."""
        from backend.agents.roles.frontend_engineer_role import get_frontend_engineer_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_frontend_engineer_role()

        assert agent == mock_agent
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "Frontend Engineer"

    @patch('backend.agents.roles.frontend_engineer_role.Agent')
    def test_get_frontend_engineer_role_with_llm(self, mock_agent_class):
        """Test get_frontend_engineer_role with custom LLM."""
        from backend.agents.roles.frontend_engineer_role import get_frontend_engineer_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_frontend_engineer_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm

    @patch('backend.agents.roles.product_manager_role.Agent')
    def test_get_product_manager_role(self, mock_agent_class):
        """Test get_product_manager_role creates correct agent."""
        from backend.agents.roles.product_manager_role import get_product_manager_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_product_manager_role()

        assert agent == mock_agent
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "Product Manager"
        assert call_kwargs['allow_delegation'] is True

    @patch('backend.agents.roles.product_manager_role.Agent')
    def test_get_product_manager_role_with_llm(self, mock_agent_class):
        """Test get_product_manager_role with custom LLM."""
        from backend.agents.roles.product_manager_role import get_product_manager_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_product_manager_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm

    @patch('backend.agents.roles.ceo_role.Agent')
    def test_get_ceo_role(self, mock_agent_class):
        """Test get_ceo_role creates correct agent."""
        from backend.agents.roles.ceo_role import get_ceo_role

        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        agent = get_ceo_role()

        assert agent == mock_agent
        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['role'] == "Chief Executive Officer"
        assert call_kwargs['allow_delegation'] is True

    @patch('backend.agents.roles.ceo_role.Agent')
    def test_get_ceo_role_with_llm(self, mock_agent_class):
        """Test get_ceo_role with custom LLM."""
        from backend.agents.roles.ceo_role import get_ceo_role

        mock_llm = Mock()
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        get_ceo_role(llm=mock_llm)

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs['llm'] == mock_llm
