"""
Docker Generator for AI Software Factory.

This module provides Docker configuration generation including
Dockerfiles, docker-compose files, and .dockerignore.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ServiceType(StrEnum):
    """Types of services."""
    WEB = "web"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    WORKER = "worker"


@dataclass
class DockerService:
    """
    Docker service configuration.

    Attributes:
        name: Service name
        service_type: Type of service
        image: Docker image
        build_context: Build context path
        dockerfile: Dockerfile path
        ports: Port mappings
        environment: Environment variables
        volumes: Volume mappings
        depends_on: Dependencies
        command: Override command
    """
    name: str
    service_type: ServiceType
    image: str | None = None
    build_context: str | None = None
    dockerfile: str = "Dockerfile"
    ports: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    volumes: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    command: str | None = None

    def to_compose_dict(self) -> dict[str, Any]:
        """Convert to docker-compose service dict."""
        service = {}

        if self.image:
            service["image"] = self.image
        elif self.build_context:
            service["build"] = {
                "context": self.build_context,
                "dockerfile": self.dockerfile,
            }

        if self.ports:
            service["ports"] = self.ports

        if self.environment:
            service["environment"] = self.environment

        if self.volumes:
            service["volumes"] = self.volumes

        if self.depends_on:
            service["depends_on"] = self.depends_on

        if self.command:
            service["command"] = self.command

        return service


class DockerGenerator:
    """
    Docker configuration generator.

    This class provides:
    - Dockerfile generation
    - Docker Compose file generation
    - .dockerignore generation
    - Multi-service orchestration

    Example:
        >>> generator = DockerGenerator()
        >>> dockerfile = generator.generate_dockerfile_python(
        ...     python_version="3.11",
        ...     app_name="myapp"
        ... )
        >>> compose = generator.generate_compose([service1, service2])
    """

    def __init__(self):
        """Initialize the Docker generator."""
        self._logger = get_logger(__name__)

    def generate_dockerfile_python(
        self,
        python_version: str = "3.11",
        app_name: str = "app",
        port: int = 8000,
        use_venv: bool = False,
        extra_packages: list[str] | None = None,
    ) -> str:
        """
        Generate a Dockerfile for Python applications.

        Args:
            python_version: Python version
            app_name: Application name
            port: Exposed port
            use_venv: Whether to use virtual environment
            extra_packages: Additional system packages

        Returns:
            Dockerfile content

        Example:
            >>> dockerfile = generator.generate_dockerfile_python(
            ...     python_version="3.11",
            ...     app_name="myapi",
            ...     port=8000
            ... )
        """
        packages = extra_packages or []

        dockerfile = f'''FROM python:{python_version}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    {(' '.join(packages))} \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3
    CMD curl -f http://localhost:{port}/health || exit 1

# Run application
CMD ["uvicorn", "{app_name}.main:app", "--host", "0.0.0.0", "--port", "{port}"]
'''

        self._logger.info(
            "Dockerfile generated",
            language="python",
            version=python_version,
        )

        return dockerfile

    def generate_dockerfile_node(
        self,
        node_version: str = "18",
        app_name: str = "app",
        port: int = 3000,
        build_command: str = "npm run build",
        start_command: str = "npm start",
    ) -> str:
        """
        Generate a Dockerfile for Node.js applications.

        Args:
            node_version: Node.js version
            app_name: Application name
            port: Exposed port
            build_command: Build command
            start_command: Start command

        Returns:
            Dockerfile content
        """
        dockerfile = f'''# Build stage
FROM node:{node_version}-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN {build_command}

# Production stage
FROM node:{node_version}-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/dist ./dist

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=3s
    CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

CMD [{(', '.join(f'"{cmd}"' for cmd in start_command.split()))}]
'''

        self._logger.info(
            "Dockerfile generated",
            language="node",
            version=node_version,
        )

        return dockerfile

    def generate_compose(
        self,
        services: list[DockerService],
        project_name: str = "myproject",
        version: str = "3.8",
    ) -> str:
        """
        Generate a docker-compose.yml file.

        Args:
            services: List of services
            project_name: Project name
            version: Compose file version

        Returns:
            docker-compose.yml content

        Example:
            >>> web = DockerService(
            ...     name="web",
            ...     service_type=ServiceType.WEB,
            ...     build_context=".",
            ...     ports=["8000:8000"],
            ... )
            >>> compose = generator.generate_compose([web])
        """
        compose = f'''version: '{version}'

services:
'''

        for service in services:
            service_dict = service.to_compose_dict()
            compose += f"  {service.name}:\n"

            # Build or image
            if "build" in service_dict:
                build = service_dict["build"]
                if isinstance(build, dict):
                    compose += "    build:\n"
                    compose += f"      context: {build['context']}\n"
                    compose += f"      dockerfile: {build['dockerfile']}\n"
                else:
                    compose += f"    build: {build}\n"
            elif "image" in service_dict:
                compose += f"    image: {service_dict['image']}\n"

            # Ports
            if "ports" in service_dict:
                compose += "    ports:\n"
                for port in service_dict["ports"]:
                    compose += f"      - \"{port}\"\n"

            # Environment
            if "environment" in service_dict:
                compose += "    environment:\n"
                for key, value in service_dict["environment"].items():
                    compose += f"      {key}: {value}\n"

            # Volumes
            if "volumes" in service_dict:
                compose += "    volumes:\n"
                for vol in service_dict["volumes"]:
                    compose += f"      - {vol}\n"

            # Depends on
            if "depends_on" in service_dict:
                compose += "    depends_on:\n"
                for dep in service_dict["depends_on"]:
                    compose += f"      - {dep}\n"

            # Command
            if "command" in service_dict:
                compose += f"    command: {service_dict['command']}\n"

            compose += "\n"

        # Add volumes section if needed
        volumes = set()
        for service in services:
            for vol in service.volumes:
                if ":" in vol:
                    vol_name = vol.split(":")[0]
                    if not vol_name.startswith(".") and not vol_name.startswith("/"):
                        volumes.add(vol_name)

        if volumes:
            compose += "volumes:\n"
            for vol in volumes:
                compose += f"  {vol}:\n"

        self._logger.info(
            "Docker Compose generated",
            services=len(services),
            project=project_name,
        )

        return compose

    def generate_dockerignore(self, extra_patterns: list[str] | None = None) -> str:
        """
        Generate a .dockerignore file.

        Args:
            extra_patterns: Additional patterns to ignore

        Returns:
            .dockerignore content
        """
        patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "*.so",
            "*.egg",
            "*.egg-info",
            "dist",
            "build",
            ".git",
            ".gitignore",
            ".env",
            ".env.*",
            ".venv",
            "venv",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            ".tox",
            ".idea",
            ".vscode",
            "*.swp",
            "*.swo",
            "*~",
            "node_modules",
            "npm-debug.log",
            "yarn-error.log",
            ".next",
            "out",
        ]

        if extra_patterns:
            patterns.extend(extra_patterns)

        return "\n".join(patterns) + "\n"

    def create_full_stack_compose(
        self,
        project_name: str,
        backend_service: str = "api",
        frontend_service: str = "web",
        database: str = "postgres",
    ) -> str:
        """
        Create a full-stack docker-compose configuration.

        Args:
            project_name: Project name
            backend_service: Backend service name
            frontend_service: Frontend service name
            database: Database type

        Returns:
            docker-compose.yml content
        """
        services = [
            DockerService(
                name=backend_service,
                service_type=ServiceType.API,
                build_context="./backend",
                ports=["8000:8000"],
                environment={
                    "DATABASE_URL": f"postgresql://postgres:postgres@{database}:5432/{project_name}",
                    "REDIS_URL": "redis://redis:6379",
                },
                depends_on=[database, "redis"],
            ),
            DockerService(
                name=frontend_service,
                service_type=ServiceType.WEB,
                build_context="./frontend",
                ports=["3000:3000"],
                environment={
                    "API_URL": "http://api:8000",
                },
                depends_on=[backend_service],
            ),
            DockerService(
                name=database,
                service_type=ServiceType.DATABASE,
                image="postgres:15-alpine",
                ports=["5432:5432"],
                environment={
                    "POSTGRES_DB": project_name,
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_PASSWORD": "postgres",
                },
                volumes=[f"{database}_data:/var/lib/postgresql/data"],
            ),
            DockerService(
                name="redis",
                service_type=ServiceType.CACHE,
                image="redis:7-alpine",
                ports=["6379:6379"],
                volumes=["redis_data:/data"],
            ),
        ]

        return self.generate_compose(services, project_name)
