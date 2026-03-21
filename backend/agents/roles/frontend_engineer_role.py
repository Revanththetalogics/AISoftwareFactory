"""
Frontend Engineer Role Definition for CrewAI.

The Frontend Engineer agent is responsible for designing and implementing
user interfaces and client-side logic.
"""

from typing import Any

from crewai import Agent


def get_frontend_engineer_role(llm: Any = None) -> Agent:
    """
    Get the Frontend Engineer agent role configuration.

    The Frontend Engineer agent designs and implements responsive,
    accessible, and performant user interfaces.

    Args:
        llm: Language model to use (optional, for Phase 3 integration)

    Returns:
        Agent: Configured Frontend Engineer agent

    Example:
        >>> from backend.agents.roles import get_frontend_engineer_role
        >>> engineer = get_frontend_engineer_role()
    """
    return Agent(
        role="Frontend Engineer",
        goal="Create beautiful, responsive, and accessible user interfaces that deliver exceptional user experiences",
        backstory="""You are a skilled frontend engineer with expertise in React, Next.js, TypeScript, and modern CSS.
        You excel at creating intuitive, performant, and accessible user interfaces.
        You understand design systems, component architecture, and state management.
        You write clean, maintainable code with proper TypeScript types.
        You are proficient with modern frontend tools including Tailwind CSS, webpack, and testing frameworks.
        You care deeply about user experience, accessibility (WCAG), and cross-browser compatibility.
        You optimize for performance, SEO, and Core Web Vitals.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
