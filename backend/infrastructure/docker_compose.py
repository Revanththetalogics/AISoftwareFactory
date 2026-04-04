"""
Docker Compose generator for Infrastructure module.

This module provides Docker Compose configuration generation
for local development and production deployment.
"""

from typing import Any

import yaml

from backend.core.logging import get_logger

logger = get_logger(__name__)


class DockerComposeGenerator:
    """
    Docker Compose configuration generator.

    Generates docker-compose.yml files for various deployment scenarios.
    """

    def __init__(self, project_name: str = "ai-software-factory"):
        """
        Initialize the generator.

        Args:
            project_name: Project name for container naming
        """
        self._project_name = project_name
        self._logger = get_logger(__name__)

    def generate_development_config(self) -> dict[str, Any]:
        """Generate development Docker Compose configuration."""
        config = {
            "version": "3.8",
            "services": {
                "backend": {
                    "build": {"context": "./backend", "dockerfile": "Dockerfile"},
                    "ports": ["8000:8000"],
                    "volumes": ["./backend:/app", "/app/__pycache__"],
                    "environment": [
                        "ENVIRONMENT=development",
                        "DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_factory",
                        "REDIS_URL=redis://redis:6379",
                    ],
                    "depends_on": ["db", "redis"],
                    "command": "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
                },
                "frontend": {
                    "build": {"context": "./frontend", "dockerfile": "Dockerfile"},
                    "ports": ["3000:3000"],
                    "volumes": ["./frontend:/app", "/app/node_modules"],
                    "environment": ["NEXT_PUBLIC_API_URL=http://localhost:8000"],
                    "command": "npm run dev",
                },
                "db": {
                    "image": "postgres:15-alpine",
                    "environment": {
                        "POSTGRES_USER": "postgres",
                        "POSTGRES_PASSWORD": "postgres",
                        "POSTGRES_DB": "ai_factory",
                    },
                    "ports": ["5432:5432"],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                },
                "redis": {"image": "redis:7-alpine", "ports": ["6379:6379"], "volumes": ["redis_data:/data"]},
            },
            "volumes": {"postgres_data": {}, "redis_data": {}},
        }

        return config

    def generate_production_config(self) -> dict[str, Any]:
        """Generate production Docker Compose configuration."""
        config = {
            "version": "3.8",
            "services": {
                "backend": {
                    "image": "docker.io/revanth2245/aisoftwarefactory-backend:latest",
                    "ports": ["8000:8000"],
                    "environment": ["ENVIRONMENT=production"],
                    "depends_on": ["db", "redis"],
                    "deploy": {"replicas": 2, "resources": {"limits": {"cpus": "1.0", "memory": "1G"}}},
                },
                "frontend": {
                    "image": "docker.io/revanth2245/aisoftwarefactory-frontend:latest",
                    "ports": ["3000:3000"],
                    "environment": ["NODE_ENV=production"],
                    "deploy": {"replicas": 2},
                },
                "db": {
                    "image": "postgres:15-alpine",
                    "environment": {
                        "POSTGRES_USER": "${POSTGRES_USER}",
                        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
                        "POSTGRES_DB": "${POSTGRES_DB}",
                    },
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    "deploy": {"resources": {"limits": {"cpus": "1.0", "memory": "2G"}}},
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "volumes": ["redis_data:/data"],
                    "command": "redis-server --appendonly yes",
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": ["./nginx.conf:/etc/nginx/nginx.conf:ro"],
                    "depends_on": ["backend", "frontend"],
                },
            },
            "volumes": {"postgres_data": {}, "redis_data": {}},
        }

        return config

    def save_config(self, config: dict[str, Any], output_path: str = "docker-compose.yml") -> str:
        """
        Save configuration to file.

        Args:
            config: Docker Compose configuration
            output_path: Output file path

        Returns:
            Path to saved file
        """
        with open(output_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        self._logger.info("Docker Compose config saved", path=output_path)
        return output_path


class DockerComposeManager:
    """
    Docker Compose manager for running and managing containers.

    Provides operations to start, stop, and inspect Docker Compose services.
    """

    def __init__(self, compose_file: str = "docker-compose.yml"):
        """
        Initialize the manager.

        Args:
            compose_file: Path to docker-compose.yml
        """
        self._compose_file = compose_file
        self._logger = get_logger(__name__)

    def up(self, services: list[str] | None = None, detach: bool = True) -> bool:
        """Start Docker Compose services."""
        import subprocess

        cmd = ["docker", "compose", "-f", self._compose_file, "up"]
        if detach:
            cmd.append("-d")
        if services:
            cmd.extend(services)

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def down(self, remove_volumes: bool = False) -> bool:
        """Stop Docker Compose services."""
        import subprocess

        cmd = ["docker", "compose", "-f", self._compose_file, "down"]
        if remove_volumes:
            cmd.append("-v")

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def ps(self) -> str:
        """List running services."""
        import subprocess

        cmd = ["docker", "compose", "-f", self._compose_file, "ps"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def logs(self, service: str | None = None, tail: int = 100) -> str:
        """Get service logs."""
        import subprocess

        cmd = ["docker", "compose", "-f", self._compose_file, "logs", f"--tail={tail}"]
        if service:
            cmd.append(service)

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
