"""
Implementation Crew for AI Software Factory.

This crew handles the development phase including frontend, backend,
and full-stack implementation.
"""

from crewai import Crew, Task

from backend.agents.roles import (
    get_architect_role,
    get_backend_engineer_role,
    get_frontend_engineer_role,
    get_product_manager_role,
)
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)


def create_implementation_crew() -> Crew:
    """
    Create the implementation crew for development.

    The implementation crew consists of:
    - Architect: Technical oversight and guidance
    - Backend Engineer: Server-side implementation
    - Frontend Engineer: Client-side implementation
    - Product Manager: Requirements validation

    All agents are wired to the enterprise LLM router (Ollama) automatically.

    Returns:
        Crew: Configured implementation crew

    Example:
        >>> from backend.agents.crews import create_implementation_crew
        >>> crew = create_implementation_crew()
        >>> result = crew.kickoff()
    """
    llm = get_llm_router().get_agent_llm(task_type="coding")

    # Create agents
    architect = get_architect_role(llm=llm)
    backend = get_backend_engineer_role(llm=llm)
    frontend = get_frontend_engineer_role(llm=llm)
    pm = get_product_manager_role(llm=llm)

    # Create crew
    crew = Crew(
        agents=[architect, backend, frontend, pm],
        tasks=[],
        verbose=True,
    )

    logger.info("Implementation crew created with Architect, Backend, Frontend, and PM")

    return crew


def create_backend_implementation_task(architecture: str, requirements: str) -> Task:
    """
    Create a task for backend implementation.

    Args:
        architecture: Architecture document
        requirements: Requirements document

    Returns:
        Task: Backend implementation task
    """
    return Task(
        description=f"""
        Implement the backend based on the architecture and requirements:

        REQUIREMENTS:
        {requirements}

        ARCHITECTURE:
        {architecture}

        Your task:
        1. Set up the project structure
        2. Implement data models and database schemas
        3. Implement API endpoints with proper validation
        4. Implement business logic and services
        5. Add authentication and authorization
        6. Write comprehensive tests
        7. Add error handling and logging
        8. Document the API

        Output:
        - Complete backend codebase
        - API documentation
        - Test suite
        - Deployment instructions
        """,
        expected_output="Complete backend implementation with tests and documentation",
    )


def create_frontend_implementation_task(architecture: str, requirements: str) -> Task:
    """
    Create a task for frontend implementation.

    Args:
        architecture: Architecture document
        requirements: Requirements document

    Returns:
        Task: Frontend implementation task
    """
    return Task(
        description=f"""
        Implement the frontend based on the architecture and requirements:

        REQUIREMENTS:
        {requirements}

        ARCHITECTURE:
        {architecture}

        Your task:
        1. Set up the project structure
        2. Implement component architecture
        3. Create reusable UI components
        4. Implement pages and routing
        5. Integrate with backend APIs
        6. Implement state management
        7. Add responsive design
        8. Ensure accessibility (WCAG compliance)
        9. Write component tests
        10. Optimize performance

        Output:
        - Complete frontend codebase
        - Component documentation
        - Test suite
        - Build configuration
        """,
        expected_output="Complete frontend implementation with tests and documentation",
    )
