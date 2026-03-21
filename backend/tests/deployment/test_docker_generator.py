"""
Tests for Docker Generator.
"""


from backend.deployment.docker_generator import (
    DockerGenerator,
    DockerService,
    ServiceType,
)


class TestDockerService:
    """Test cases for DockerService."""

    def test_service_creation(self):
        """Test creating a service."""
        service = DockerService(
            name="web",
            service_type=ServiceType.WEB,
            image="nginx:latest",
            ports=["80:80"],
        )

        assert service.name == "web"
        assert service.service_type == ServiceType.WEB
        assert service.ports == ["80:80"]

    def test_service_to_compose_dict(self):
        """Test converting service to compose dict."""
        service = DockerService(
            name="api",
            service_type=ServiceType.API,
            build_context=".",
            dockerfile="Dockerfile",
            ports=["8000:8000"],
            environment={"DEBUG": "true"},
        )

        data = service.to_compose_dict()

        assert data["build"]["context"] == "."
        assert data["ports"] == ["8000:8000"]


class TestDockerGenerator:
    """Test cases for DockerGenerator."""

    def setup_method(self):
        """Create fresh generator for each test."""
        self.generator = DockerGenerator()

    def test_generator_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None

    def test_generate_dockerfile_python(self):
        """Test generating Python Dockerfile."""
        dockerfile = self.generator.generate_dockerfile_python(
            python_version="3.11",
            app_name="myapi",
            port=8000,
        )

        assert "FROM python:3.11" in dockerfile
        assert "myapi" in dockerfile
        assert "8000" in dockerfile

    def test_generate_dockerfile_node(self):
        """Test generating Node.js Dockerfile."""
        dockerfile = self.generator.generate_dockerfile_node(
            node_version="18",
            app_name="myapp",
            port=3000,
        )

        assert "FROM node:18" in dockerfile
        assert "3000" in dockerfile

    def test_generate_compose(self):
        """Test generating docker-compose."""
        services = [
            DockerService(
                name="api",
                service_type=ServiceType.API,
                image="myapi:latest",
                ports=["8000:8000"],
            ),
        ]

        compose_yaml = self.generator.generate_compose(
            services=services,
            project_name="myproject",
        )

        assert "version:" in compose_yaml
        assert "api:" in compose_yaml

    def test_generate_dockerignore(self):
        """Test generating .dockerignore."""
        content = self.generator.generate_dockerignore()

        assert "__pycache__" in content
        assert ".git" in content

    def test_create_full_stack_compose(self):
        """Test creating full stack compose."""
        compose_yaml = self.generator.create_full_stack_compose(
            project_name="myapp",
            backend_service="api",
            frontend_service="web",
            database="postgres",
        )

        assert "api:" in compose_yaml
        assert "web:" in compose_yaml
        assert "postgres:" in compose_yaml
        assert "redis:" in compose_yaml
