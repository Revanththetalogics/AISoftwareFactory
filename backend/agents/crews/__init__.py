"""
CrewAI Crew Configurations for AI Software Factory.

This module defines the crews used for different phases of the software
development lifecycle. Each crew is a team of agents working together.
"""

from backend.agents.crews.deployment_crew import create_deployment_crew
from backend.agents.crews.design_crew import create_design_crew
from backend.agents.crews.implementation_crew import create_implementation_crew
from backend.agents.crews.planning_crew import create_planning_crew

__all__ = [
    "create_planning_crew",
    "create_design_crew",
    "create_implementation_crew",
    "create_deployment_crew",
]
