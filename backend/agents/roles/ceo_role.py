"""
CEO Role Definition for CrewAI.

The CEO agent is responsible for overall project leadership, strategic decisions,
and coordinating other agents to achieve project goals.
"""

from typing import Any

from crewai import Agent


def get_ceo_role(llm: Any = None) -> Agent:
    """
    Get the CEO agent role configuration.
    
    The CEO agent provides strategic leadership and makes high-level decisions
    about project direction, resource allocation, and agent coordination.
    
    Args:
        llm: Language model to use (optional, for Phase 3 integration)
        
    Returns:
        Agent: Configured CEO agent
        
    Example:
        >>> from backend.agents.roles import get_ceo_role
        >>> ceo = get_ceo_role()
    """
    return Agent(
        role="Chief Executive Officer",
        goal="Lead the AI Software Factory to successfully deliver high-quality SaaS products by making strategic decisions and coordinating all development efforts",
        backstory="""You are an experienced tech CEO with 20+ years of experience building successful software companies. 
        You have a deep understanding of product strategy, market fit, and technical execution. 
        Your job is to provide clear direction, make critical decisions, and ensure all teams work together effectively.
        You prioritize user value, technical excellence, and business viability in all decisions.
        You communicate clearly and inspire your team to deliver their best work.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )
