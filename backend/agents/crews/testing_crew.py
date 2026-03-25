"""
Testing Crew for AI Software Factory.

This crew handles the testing phase including test generation,
code review, and quality assurance.
"""

from crewai import Crew, Task

from backend.agents.roles import (
    get_architect_role,
    get_backend_engineer_role,
    get_frontend_engineer_role,
    get_qa_engineer_role,
)
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)


def create_testing_crew() -> Crew:
    """
    Create the testing crew for quality assurance and testing.

    The testing crew consists of:
    - QA Engineer: Test generation and code review
    - Architect: Technical validation
    - Backend Engineer: Backend testing
    - Frontend Engineer: Frontend testing

    All agents are wired to the enterprise LLM router (Ollama) automatically.
    Uses DeepSeek Coder for code review tasks.

    Returns:
        Crew: Configured testing crew

    Example:
        >>> from backend.agents.crews import create_testing_crew
        >>> crew = create_testing_crew()
        >>> result = crew.kickoff()
    """
    # Use code_review task type to get DeepSeek Coder
    llm = get_llm_router().get_agent_llm(task_type="code_review")

    # Create agents
    qa = get_qa_engineer_role(llm=llm)
    architect = get_architect_role(llm=llm)
    backend = get_backend_engineer_role(llm=llm)
    frontend = get_frontend_engineer_role(llm=llm)

    # Create crew
    crew = Crew(
        agents=[qa, architect, backend, frontend],
        tasks=[],
        verbose=True,
    )

    logger.info("Testing crew created with QA, Architect, Backend, and Frontend engineers")

    return crew


def create_test_generation_task(backend_code: str, frontend_code: str, requirements: str) -> Task:
    """
    Create a task for generating comprehensive tests.

    Args:
        backend_code: Backend code to test
        frontend_code: Frontend code to test
        requirements: Requirements to validate against

    Returns:
        Task: Test generation task
    """
    return Task(
        description=f"""
        Generate comprehensive tests for the following code:

        REQUIREMENTS:
        {requirements}

        BACKEND CODE:
        ```python
        {backend_code[:2000]}...
        ```

        FRONTEND CODE:
        ```typescript
        {frontend_code[:2000]}...
        ```

        Your task:
        1. Write unit tests for backend functions
        2. Write integration tests for API endpoints
        3. Write E2E tests for critical user flows
        4. Identify edge cases and boundary conditions
        5. Ensure test coverage is comprehensive
        6. Validate that all requirements are testable

        Output a structured test suite with:
        - Unit Tests (pytest for backend, Jest for frontend)
        - Integration Tests
        - E2E Tests (Playwright)
        - Test Data and Fixtures
        - Coverage Report
        """,
        expected_output="Complete test suite with unit, integration, and E2E tests",
        agent=None,  # Will be assigned by crew
    )


def create_code_review_task(code: str, code_type: str) -> Task:
    """
    Create a task for code review.

    Args:
        code: Code to review
        code_type: Type of code (backend, frontend, etc.)

    Returns:
        Task: Code review task
    """
    return Task(
        description=f"""
        Perform a comprehensive code review of the following {code_type} code:

        ```
        {code[:3000]}...
        ```

        Review for:
        1. Code quality and best practices
        2. Security vulnerabilities
        3. Performance issues
        4. Maintainability concerns
        5. Testability
        6. Documentation completeness
        7. Error handling
        8. Type safety

        Provide:
        - Critical issues (must fix)
        - Warnings (should fix)
        - Suggestions (nice to have)
        - Overall assessment
        """,
        expected_output="Detailed code review report with findings and recommendations",
        agent=None,  # Will be assigned by crew
    )
