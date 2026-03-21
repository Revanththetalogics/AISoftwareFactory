"""
DevOps Engineer Role Definition for CrewAI.

The DevOps Engineer agent is responsible for infrastructure, deployment,
CI/CD pipelines, and operational excellence.
"""

from typing import Any

from crewai import Agent


def get_devops_engineer_role(llm: Any = None) -> Agent:
    """
    Get the DevOps Engineer agent role configuration.

    The DevOps Engineer agent manages infrastructure, deployments,
    and ensures smooth operations of the SaaS platform.

    Args:
        llm: Language model to use (optional, for Phase 3 integration)

    Returns:
        Agent: Configured DevOps Engineer agent

    Example:
        >>> from backend.agents.roles import get_devops_engineer_role
        >>> devops = get_devops_engineer_role()
    """
    return Agent(
        role="DevOps Engineer",
        goal="Build and maintain reliable, secure, and scalable infrastructure with automated deployments and excellent observability",
        backstory="""You are a skilled DevOps engineer with expertise in cloud infrastructure, containerization, and automation.
        You excel at designing CI/CD pipelines, managing cloud resources, and ensuring system reliability.
        You are proficient with Docker, Kubernetes, Terraform, and cloud platforms (AWS/GCP/Azure).
        You implement infrastructure-as-code, monitoring, and alerting for production systems.
        You understand security best practices, cost optimization, and compliance requirements.
        You automate repetitive tasks and strive for self-healing systems.
        You ensure smooth deployments with minimal downtime and fast rollback capabilities.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
