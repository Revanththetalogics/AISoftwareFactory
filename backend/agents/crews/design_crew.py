"""
Design Crew for AI Software Factory.

This crew handles the architecture and design phase including system design,
technology selection, and technical planning.
"""

from crewai import Crew, Task

from backend.agents.roles import get_architect_role, get_ceo_role, get_product_manager_role
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)


def create_design_crew() -> Crew:
    """
    Create the design crew for architecture and technical design.

    The design crew consists of:
    - CEO: Strategic oversight
    - Architect: System design and technology decisions
    - Product Manager: Requirements alignment

    All agents are wired to the enterprise LLM router (Ollama) automatically.

    Returns:
        Crew: Configured design crew

    Example:
        >>> from backend.agents.crews import create_design_crew
        >>> crew = create_design_crew()
        >>> result = crew.kickoff()
    """
    llm = get_llm_router().get_agent_llm(task_type="reasoning")

    # Create agents
    ceo = get_ceo_role(llm=llm)
    architect = get_architect_role(llm=llm)
    pm = get_product_manager_role(llm=llm)

    # Create crew
    crew = Crew(
        agents=[ceo, architect, pm],
        tasks=[],
        verbose=True,
    )

    logger.info("Design crew created with CEO, Architect, and Product Manager")

    return crew


def create_architecture_task(requirements: str) -> Task:
    """
    Create a task for designing system architecture.

    Args:
        requirements: Requirements document

    Returns:
        Task: Architecture design task
    """
    return Task(
        description=f"""
        Design the system architecture based on the following requirements:

        REQUIREMENTS:
        {requirements}

        Your task:
        1. Define the overall system architecture (microservices/monolith)
        2. Design the data model and database schema
        3. Define API specifications and endpoints
        4. Select appropriate technologies and frameworks
        5. Design for scalability, security, and maintainability
        6. Create architecture diagrams (text-based)

        Output a comprehensive architecture document including:
        - Architecture Overview
        - Component Diagram
        - Data Model
        - API Design
        - Technology Stack
        - Security Considerations
        - Deployment Architecture
        """,
        expected_output="A comprehensive architecture document with diagrams",
    )


def create_technology_selection_task(architecture: str) -> Task:
    """
    Create a task for technology selection and justification.

    Args:
        architecture: Architecture document

    Returns:
        Task: Technology selection task
    """
    return Task(
        description=f"""
        Based on the following architecture, finalize technology selections:

        ARCHITECTURE:
        {architecture}

        Your task:
        1. Finalize frontend framework and libraries
        2. Finalize backend framework and runtime
        3. Select database and caching solutions
        4. Select deployment and infrastructure tools
        5. Select monitoring and observability tools
        6. Provide justification for each selection

        Output a technology stack document with:
        - Selected Technologies
        - Version Requirements
        - Selection Rationale
        - Alternative Considerations
        """,
        expected_output="A technology stack document with justifications",
    )
