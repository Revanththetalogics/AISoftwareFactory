"""
Deployment Crew for AI Software Factory.

This crew handles the deployment phase including infrastructure setup,
CI/CD configuration, and production deployment.
"""

from typing import Optional, Any

from crewai import Crew, Task

from backend.agents.roles import get_architect_role, get_backend_engineer_role, get_devops_engineer_role
from backend.core.logging import get_logger

logger = get_logger(__name__)


def create_deployment_crew(llm: Any = None) -> Crew:
    """
    Create the deployment crew for infrastructure and deployment.
    
    The deployment crew consists of:
    - DevOps Engineer: Infrastructure and deployment automation
    - Architect: Technical oversight
    - Backend Engineer: Application deployment support
    
    Args:
        llm: Language model to use for all agents
        
    Returns:
        Crew: Configured deployment crew
        
    Example:
        >>> from backend.agents.crews import create_deployment_crew
        >>> crew = create_deployment_crew()
        >>> result = crew.kickoff()
    """
    # Create agents
    devops = get_devops_engineer_role(llm=llm)
    architect = get_architect_role(llm=llm)
    backend = get_backend_engineer_role(llm=llm)
    
    # Create crew
    crew = Crew(
        agents=[devops, architect, backend],
        tasks=[],
        verbose=True,
    )
    
    logger.info("Deployment crew created with DevOps, Architect, and Backend Engineer")
    
    return crew


def create_infrastructure_task(architecture: str) -> Task:
    """
    Create a task for infrastructure setup.
    
    Args:
        architecture: Architecture document
        
    Returns:
        Task: Infrastructure setup task
    """
    return Task(
        description=f"""
        Set up the infrastructure based on the architecture:
        
        ARCHITECTURE:
        {architecture}
        
        Your task:
        1. Design infrastructure architecture
        2. Create Docker configurations
        3. Set up container orchestration (Docker Compose/Kubernetes)
        4. Configure networking and security groups
        5. Set up databases and caching
        6. Configure load balancers
        7. Set up SSL/TLS certificates
        8. Configure monitoring and logging
        9. Document infrastructure setup
        
        Output:
        - Infrastructure-as-code (Terraform/CloudFormation)
        - Docker configurations
        - Kubernetes manifests (if applicable)
        - Setup documentation
        - Security configuration
        """,
        expected_output="Complete infrastructure setup with documentation",
    )


def create_cicd_task(infrastructure: str) -> Task:
    """
    Create a task for CI/CD pipeline setup.
    
    Args:
        infrastructure: Infrastructure documentation
        
    Returns:
        Task: CI/CD setup task
    """
    return Task(
        description=f"""
        Set up CI/CD pipelines based on the infrastructure:
        
        INFRASTRUCTURE:
        {infrastructure}
        
        Your task:
        1. Design CI/CD workflow
        2. Set up build pipelines
        3. Configure automated testing
        4. Set up deployment pipelines
        5. Configure environment promotion
        6. Set up rollback procedures
        7. Configure notifications
        8. Document CI/CD processes
        
        Output:
        - CI/CD configuration files
        - Pipeline documentation
        - Deployment procedures
        - Rollback procedures
        """,
        expected_output="Complete CI/CD setup with documentation",
    )
