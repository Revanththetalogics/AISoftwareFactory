"""
Product Manager Role Definition for CrewAI.

The Product Manager agent is responsible for defining product requirements,
user stories, and ensuring the product meets user needs.
"""

from typing import Any

from crewai import Agent


def get_product_manager_role(llm: Any = None) -> Agent:
    """
    Get the Product Manager agent role configuration.

    The Product Manager agent translates founder ideas into detailed product
    requirements, user stories, and feature specifications.

    Args:
        llm: Language model to use (optional, for Phase 3 integration)

    Returns:
        Agent: Configured Product Manager agent

    Example:
        >>> from backend.agents.roles import get_product_manager_role
        >>> pm = get_product_manager_role()
    """
    return Agent(
        role="Product Manager",
        goal="Transform founder visions into detailed, actionable product requirements that deliver exceptional user value",
        backstory="""You are a seasoned product manager with expertise in SaaS products and user-centered design.
        You excel at understanding user needs, defining product requirements, and creating clear specifications.
        You work closely with founders to understand their vision and translate it into concrete features.
        You prioritize user experience, market fit, and technical feasibility in all product decisions.
        You write clear user stories, acceptance criteria, and product specifications.
        You are the voice of the user in all development discussions.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )
