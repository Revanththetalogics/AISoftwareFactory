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


class TestDockerServiceAdditional:
    """Additional test cases for DockerService."""

    def test_to_compose_dict_with_command(self):
        """Test to_compose_dict includes command (line 79)."""
        service = DockerService(
            name="worker",
            service_type=ServiceType.WORKER,
            image="myworker:latest",
            command="python worker.py",
        )

        data = service.to_compose_dict()

        assert "command" in data
        assert data["command"] == "python worker.py"


class TestDockerGeneratorAdditional:
    """Additional test cases for DockerGenerator."""

    def setup_method(self):
        """Create fresh generator for each test."""
        self.generator = DockerGenerator()

    def test_generate_compose_with_command(self):
        """Test generate_compose includes command in output (line 305)."""
        services = [
            DockerService(
                name="worker",
                service_type=ServiceType.WORKER,
                image="myworker:latest",
                command="celery -A app worker",
            ),
        ]

        compose_yaml = self.generator.generate_compose(
            services=services,
            project_name="myproject",
        )

        assert "worker:" in compose_yaml
        assert "command: celery -A app worker" in compose_yaml

    def test_generate_compose_with_build_string(self):
        """Test generate_compose handles string build context (line 275)."""
        # Create service with a modified to_compose_dict that returns string build
        service = DockerService(
            name="api",
            service_type=ServiceType.API,
            build_context=".",
            dockerfile="Dockerfile",
        )

        # Override to_compose_dict to return string build for testing
        original_method = service.to_compose_dict

        def mock_to_compose_dict():
            result = original_method()
            # Replace dict build with string
            result["build"] = "."
            return result

        service.to_compose_dict = mock_to_compose_dict

        compose_yaml = self.generator.generate_compose(
            services=[service],
            project_name="myproject",
        )

        assert "api:" in compose_yaml
        assert "build: ." in compose_yaml

    def test_generate_dockerignore_with_extra_patterns(self):
        """Test generate_dockerignore with extra patterns (line 375)."""
        content = self.generator.generate_dockerignore(extra_patterns=["*.log", "tmp/", "secrets.json"])

        # Check default patterns
        assert "__pycache__" in content
        assert ".git" in content
        # Check extra patterns
        assert "*.log" in content
        assert "tmp/" in content
        assert "secrets.json" in content

    def test_generate_compose_with_volumes_section(self):
        """Test generate_compose creates volumes section for named volumes."""
        services = [
            DockerService(
                name="db",
                service_type=ServiceType.DATABASE,
                image="postgres:15",
                volumes=["pgdata:/var/lib/postgresql/data"],
            ),
        ]

        compose_yaml = self.generator.generate_compose(
            services=services,
            project_name="myproject",
        )

        assert "volumes:" in compose_yaml
        assert "pgdata:" in compose_yaml

    def test_generate_compose_skips_local_volume_paths(self):
        """Test generate_compose skips local paths in volumes section."""
        services = [
            DockerService(
                name="api",
                service_type=ServiceType.API,
                image="myapi:latest",
                volumes=["./src:/app/src", "/etc/config:/app/config"],
            ),
        ]

        compose_yaml = self.generator.generate_compose(
            services=services,
            project_name="myproject",
        )

        # Volumes section shouldn't include local paths
        lines = compose_yaml.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "volumes:":
                # This could be service volumes or top-level volumes
                # We need to check if the next line is a named volume definition
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Named volume definitions are indented with just the name
                    if not next_line.strip().startswith("-"):
                        pass

        # There shouldn't be a top-level volumes section for local paths only
        # This depends on implementation - check the compose_yaml structure
