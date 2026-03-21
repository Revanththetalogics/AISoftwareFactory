"""
Planning Crew for AI Software Factory.

This crew handles the initial planning phase including requirements gathering,
product definition, and project scoping.
"""

from typing import Any

from crewai import Crew, Task

from backend.agents.roles import get_ceo_role, get_product_manager_role
from backend.core.logging import get_logger

logger = get_logger(__name__)


def create_planning_crew(llm: Any = None) -> Crew:
    """
    Create the planning crew for requirements and product definition.

    The planning crew consists of:
    - CEO: Strategic oversight and decision making
    - Product Manager: Requirements gathering and product definition

    Args:
        llm: Language model to use for all agents

    Returns:
        Crew: Configured planning crew

    Example:
        >>> from backend.agents.crews import create_planning_crew
        >>> crew = create_planning_crew()
        >>> result = crew.kickoff()
    """
    # Create agents
    ceo = get_ceo_role(llm=llm)
    pm = get_product_manager_role(llm=llm)

    # Create crew
    crew = Crew(
        agents=[ceo, pm],
        tasks=[],
        verbose=True,
    )

    logger.info("Planning crew created with CEO and Product Manager")

    return crew


def create_requirements_task(idea_description: str) -> Task:
    """
    Create a task for gathering and documenting requirements.

    Args:
        idea_description: Description of the product idea

    Returns:
        Task: Requirements gathering task
    """
    return Task(
        description=f"""
        Analyze the following product idea and create comprehensive requirements:

        IDEA: {idea_description}

        Your task:
        1. Identify the core problem being solved
        2. Define the target users and their needs
        3. List key features and functionality
        4. Identify constraints and assumptions
        5. Define success criteria

        Output a structured requirements document with:
        - Executive Summary
        - User Personas
        - Functional Requirements
        - Non-functional Requirements
        - Success Metrics
        """,
        expected_output="A comprehensive requirements document in markdown format",
    )


def create_product_strategy_task(requirements: str) -> Task:
    """
    Create a task for defining product strategy.

    Args:
        requirements: Requirements document from previous task

    Returns:
        Task: Product strategy task
    """
    return Task(
        description=f"""
        Based on the following requirements, define the product strategy:

        REQUIREMENTS:
        {requirements}

        Your task:
        1. Define the product vision and mission
        2. Identify competitive advantages
        3. Prioritize features (MVP vs future releases)
        4. Define the go-to-market strategy
        5. Estimate timeline and resources

        Output a product strategy document with clear priorities and roadmap.
        """,
        expected_output="A product strategy document with roadmap and priorities",
    )
