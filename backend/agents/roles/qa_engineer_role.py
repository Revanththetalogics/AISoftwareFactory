"""
QA Engineer Role for AI Software Factory.

This role handles testing, quality assurance, and test automation.
"""

from crewai import Agent

from backend.core.logging import get_logger

logger = get_logger(__name__)


def get_qa_engineer_role(llm=None) -> Agent:
    """
    Create the QA Engineer agent role.

    The QA Engineer is responsible for:
    - Writing comprehensive test cases
    - Performing code reviews with quality focus
    - Identifying bugs and edge cases
    - Ensuring test coverage
    - Validating requirements implementation

    Args:
        llm: Language model instance (uses code_review task type for DeepSeek Coder)

    Returns:
        Agent: Configured QA Engineer agent
    """
    return Agent(
        role="QA Engineer",
        goal="Ensure software quality through comprehensive testing and code review",
        backstory="""You are an expert QA Engineer with deep knowledge of software testing
        methodologies, test automation, and code quality. You excel at:
        - Writing unit, integration, and E2E tests
        - Identifying edge cases and potential bugs
        - Reviewing code for quality and best practices
        - Ensuring requirements are properly implemented
        - Validating test coverage

        You are thorough, detail-oriented, and focused on delivering reliable software.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )
