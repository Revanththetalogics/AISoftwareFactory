"""
Comprehensive tests for CrewIntegration module.

Covers all uncovered lines in crew_integration.py:
- Lines 76, 82-93, 126-170, 191-215, 228-235, 259-285
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.workflows.crew_integration import CrewIntegration
from backend.workflows.state_machine import ProjectPhase


class TestCrewIntegration:
    """Tests for CrewIntegration class."""

    def test_init(self):
        """Test CrewIntegration initialization."""
        integration = CrewIntegration()
        assert integration._crews == {}
        assert integration._logger is not None

    def test_assemble_crew_for_phase_requirements(self):
        """Test assembling crew for requirements phase."""
        integration = CrewIntegration()

        with patch("backend.workflows.crew_integration.create_planning_crew") as mock_create:
            mock_crew = MagicMock()
            mock_create.return_value = mock_crew

            crew = integration.assemble_crew_for_phase(ProjectPhase.REQUIREMENTS)

            assert crew == mock_crew
            mock_create.assert_called_once()
            assert ProjectPhase.REQUIREMENTS in integration._crews

    def test_assemble_crew_for_phase_architecture(self):
        """Test assembling crew for architecture phase."""
        integration = CrewIntegration()

        with patch("backend.workflows.crew_integration.create_design_crew") as mock_create:
            mock_crew = MagicMock()
            mock_create.return_value = mock_crew

            crew = integration.assemble_crew_for_phase(ProjectPhase.ARCHITECTURE)

            assert crew == mock_crew
            mock_create.assert_called_once()

    def test_assemble_crew_for_phase_implementation(self):
        """Test assembling crew for implementation phase."""
        integration = CrewIntegration()

        with patch("backend.workflows.crew_integration.create_implementation_crew") as mock_create:
            mock_crew = MagicMock()
            mock_create.return_value = mock_crew

            crew = integration.assemble_crew_for_phase(ProjectPhase.IMPLEMENTATION)

            assert crew == mock_crew
            mock_create.assert_called_once()

    def test_assemble_crew_for_phase_deployment(self):
        """Test assembling crew for deployment phase."""
        integration = CrewIntegration()

        with patch("backend.workflows.crew_integration.create_deployment_crew") as mock_create:
            mock_crew = MagicMock()
            mock_create.return_value = mock_crew

            crew = integration.assemble_crew_for_phase(ProjectPhase.DEPLOYMENT)

            assert crew == mock_crew
            mock_create.assert_called_once()

    def test_assemble_crew_for_phase_cached(self):
        """Test that assembled crews are cached."""
        integration = CrewIntegration()

        with patch("backend.workflows.crew_integration.create_planning_crew") as mock_create:
            mock_crew = MagicMock()
            mock_create.return_value = mock_crew

            crew1 = integration.assemble_crew_for_phase(ProjectPhase.REQUIREMENTS)
            crew2 = integration.assemble_crew_for_phase(ProjectPhase.REQUIREMENTS)

            assert crew1 == crew2
            mock_create.assert_called_once()  # Only called once

    def test_assemble_crew_for_phase_no_crew(self):
        """Test assembling crew for phase that doesn't use crews."""
        integration = CrewIntegration()

        # TESTING phase doesn't have a crew
        crew = integration.assemble_crew_for_phase(ProjectPhase.TESTING)

        assert crew is None

    @pytest.mark.asyncio
    async def test_execute_phase_no_crew(self):
        """Test executing phase when no crew is available."""
        integration = CrewIntegration()

        with patch.object(
            integration, "assemble_crew_for_phase", return_value=None
        ):
            result = await integration.execute_phase(
                ProjectPhase.TESTING,
                context={"idea": "test"},
            )

        assert result["success"] is True
        assert "without crew execution" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_phase_with_crew_success(self):
        """Test successful phase execution with crew."""
        integration = CrewIntegration()

        mock_crew = MagicMock()
        mock_crew.kickoff = MagicMock(return_value="Crew result")

        with patch.object(
            integration, "assemble_crew_for_phase", return_value=mock_crew
        ):
            with patch.object(
                integration, "_create_tasks_for_phase", return_value=[MagicMock()]
            ):
                result = await integration.execute_phase(
                    ProjectPhase.REQUIREMENTS,
                    context={"idea": "Build a SaaS app"},
                )

        assert result["success"] is True
        assert "output" in result
        assert "raw_result" in result

    @pytest.mark.asyncio
    async def test_execute_phase_with_crew_no_tasks(self):
        """Test phase execution when no tasks are created."""
        integration = CrewIntegration()

        mock_crew = MagicMock()

        with patch.object(
            integration, "assemble_crew_for_phase", return_value=mock_crew
        ):
            with patch.object(
                integration, "_create_tasks_for_phase", return_value=[]
            ):
                result = await integration.execute_phase(
                    ProjectPhase.REQUIREMENTS,
                    context={},
                )

        assert result["success"] is True
        assert "No tasks created" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_phase_with_crew_exception(self):
        """Test phase execution when crew raises an exception."""
        integration = CrewIntegration()

        mock_crew = MagicMock()
        mock_crew.kickoff = MagicMock(side_effect=RuntimeError("Crew failed"))

        with patch.object(
            integration, "assemble_crew_for_phase", return_value=mock_crew
        ):
            with patch.object(
                integration, "_create_tasks_for_phase", return_value=[MagicMock()]
            ):
                result = await integration.execute_phase(
                    ProjectPhase.REQUIREMENTS,
                    context={"idea": "test"},
                )

        assert result["success"] is False
        assert "Crew failed" in result["error"]

    def test_create_tasks_for_phase_requirements(self):
        """Test creating tasks for requirements phase."""
        integration = CrewIntegration()

        with patch(
            "backend.workflows.crew_integration.create_requirements_task"
        ) as mock_create:
            mock_task = MagicMock()
            mock_create.return_value = mock_task

            tasks = integration._create_tasks_for_phase(
                ProjectPhase.REQUIREMENTS,
                context={"idea": "Build a todo app"},
            )

            assert len(tasks) == 1
            mock_create.assert_called_once_with("Build a todo app")

    def test_create_tasks_for_phase_requirements_no_idea(self):
        """Test creating tasks for requirements without idea."""
        integration = CrewIntegration()

        tasks = integration._create_tasks_for_phase(
            ProjectPhase.REQUIREMENTS,
            context={},
        )

        assert len(tasks) == 0

    def test_create_tasks_for_phase_architecture(self):
        """Test creating tasks for architecture phase."""
        integration = CrewIntegration()

        with patch(
            "backend.workflows.crew_integration.create_architecture_task"
        ) as mock_create:
            mock_task = MagicMock()
            mock_create.return_value = mock_task

            tasks = integration._create_tasks_for_phase(
                ProjectPhase.ARCHITECTURE,
                context={"requirements": "User requirements"},
            )

            assert len(tasks) == 1
            mock_create.assert_called_once_with("User requirements")

    def test_create_tasks_for_phase_architecture_no_requirements(self):
        """Test creating tasks for architecture without requirements."""
        integration = CrewIntegration()

        tasks = integration._create_tasks_for_phase(
            ProjectPhase.ARCHITECTURE,
            context={},
        )

        assert len(tasks) == 0

    def test_create_tasks_for_phase_implementation(self):
        """Test creating tasks for implementation phase."""
        integration = CrewIntegration()

        with patch(
            "backend.workflows.crew_integration.create_backend_implementation_task"
        ) as mock_backend:
            with patch(
                "backend.workflows.crew_integration.create_frontend_implementation_task"
            ) as mock_frontend:
                mock_backend.return_value = MagicMock()
                mock_frontend.return_value = MagicMock()

                tasks = integration._create_tasks_for_phase(
                    ProjectPhase.IMPLEMENTATION,
                    context={
                        "architecture": "System arch",
                        "requirements": "User reqs",
                    },
                )

                assert len(tasks) == 2
                mock_backend.assert_called_once()
                mock_frontend.assert_called_once()

    def test_create_tasks_for_phase_implementation_missing_context(self):
        """Test creating tasks for implementation with missing context."""
        integration = CrewIntegration()

        tasks = integration._create_tasks_for_phase(
            ProjectPhase.IMPLEMENTATION,
            context={"architecture": "arch"},  # Missing requirements
        )

        assert len(tasks) == 0

    def test_create_tasks_for_phase_deployment(self):
        """Test creating tasks for deployment phase."""
        integration = CrewIntegration()

        with patch(
            "backend.workflows.crew_integration.create_infrastructure_task"
        ) as mock_create:
            mock_task = MagicMock()
            mock_create.return_value = mock_task

            tasks = integration._create_tasks_for_phase(
                ProjectPhase.DEPLOYMENT,
                context={"architecture": "System architecture"},
            )

            assert len(tasks) == 1
            mock_create.assert_called_once_with("System architecture")

    def test_create_tasks_for_phase_deployment_no_architecture(self):
        """Test creating tasks for deployment without architecture."""
        integration = CrewIntegration()

        tasks = integration._create_tasks_for_phase(
            ProjectPhase.DEPLOYMENT,
            context={},
        )

        assert len(tasks) == 0

    def test_parse_crew_result_with_to_dict(self):
        """Test parsing result with to_dict method."""
        integration = CrewIntegration()

        mock_result = MagicMock()
        mock_result.to_dict = MagicMock(return_value={"key": "value"})

        parsed = integration._parse_crew_result(mock_result)

        assert parsed == {"key": "value"}

    def test_parse_crew_result_string(self):
        """Test parsing string result."""
        integration = CrewIntegration()

        parsed = integration._parse_crew_result("String result")

        assert parsed == {"result": "String result"}

    def test_parse_crew_result_dict(self):
        """Test parsing dict result."""
        integration = CrewIntegration()

        parsed = integration._parse_crew_result({"existing": "dict"})

        assert parsed == {"existing": "dict"}

    def test_parse_crew_result_other(self):
        """Test parsing other types of results."""
        integration = CrewIntegration()

        parsed = integration._parse_crew_result(12345)

        assert parsed == {"result": "12345"}

    def test_map_crew_output_to_state_requirements(self):
        """Test mapping requirements phase output to state."""
        integration = CrewIntegration()

        crew_output = {
            "requirements": "User requirements document",
            "product_strategy": "Go-to-market strategy",
        }

        updates = integration.map_crew_output_to_state(
            ProjectPhase.REQUIREMENTS, crew_output
        )

        assert updates["requirements"] == "User requirements document"
        assert updates["product_strategy"] == "Go-to-market strategy"

    def test_map_crew_output_to_state_requirements_partial(self):
        """Test mapping partial requirements output."""
        integration = CrewIntegration()

        crew_output = {"requirements": "User requirements"}

        updates = integration.map_crew_output_to_state(
            ProjectPhase.REQUIREMENTS, crew_output
        )

        assert updates["requirements"] == "User requirements"
        assert "product_strategy" not in updates

    def test_map_crew_output_to_state_architecture(self):
        """Test mapping architecture phase output to state."""
        integration = CrewIntegration()

        crew_output = {
            "architecture": "System architecture doc",
            "technology_stack": {"backend": "Python", "frontend": "React"},
        }

        updates = integration.map_crew_output_to_state(
            ProjectPhase.ARCHITECTURE, crew_output
        )

        assert updates["architecture"] == "System architecture doc"
        assert updates["technology_stack"]["backend"] == "Python"

    def test_map_crew_output_to_state_implementation(self):
        """Test mapping implementation phase output to state."""
        integration = CrewIntegration()

        crew_output = {
            "backend_code": "Python backend code",
            "frontend_code": "React frontend code",
        }

        updates = integration.map_crew_output_to_state(
            ProjectPhase.IMPLEMENTATION, crew_output
        )

        assert updates["backend_code"] == "Python backend code"
        assert updates["frontend_code"] == "React frontend code"

    def test_map_crew_output_to_state_deployment(self):
        """Test mapping deployment phase output to state."""
        integration = CrewIntegration()

        crew_output = {
            "infrastructure": "Terraform configs",
            "cicd_config": "GitHub Actions workflow",
        }

        updates = integration.map_crew_output_to_state(
            ProjectPhase.DEPLOYMENT, crew_output
        )

        assert updates["infrastructure"] == "Terraform configs"
        assert updates["cicd_config"] == "GitHub Actions workflow"

    def test_map_crew_output_to_state_empty(self):
        """Test mapping empty output to state."""
        integration = CrewIntegration()

        updates = integration.map_crew_output_to_state(
            ProjectPhase.REQUIREMENTS, {}
        )

        assert updates == {}

    def test_map_crew_output_to_state_unknown_phase(self):
        """Test mapping output for unknown/unsupported phase."""
        integration = CrewIntegration()

        updates = integration.map_crew_output_to_state(
            ProjectPhase.TESTING,
            {"test_results": "All passed"},
        )

        # Testing phase doesn't have specific mappings
        assert updates == {}
