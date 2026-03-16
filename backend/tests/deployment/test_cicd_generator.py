"""
Tests for CI/CD Generator.
"""

import pytest

from backend.deployment.cicd_generator import (
    CICDGenerator,
    PipelineStep,
    PipelineJob,
    CIPlatform,
    TriggerEvent,
)


class TestPipelineStep:
    """Test cases for PipelineStep."""
    
    def test_step_creation(self):
        """Test creating a step."""
        step = PipelineStep(
            name="Build",
            command="npm run build",
        )
        
        assert step.name == "Build"
        assert step.command == "npm run build"


class TestPipelineJob:
    """Test cases for PipelineJob."""
    
    def test_job_creation(self):
        """Test creating job."""
        job = PipelineJob(
            name="build",
            runs_on="ubuntu-latest",
        )
        
        assert job.name == "build"
        assert job.runs_on == "ubuntu-latest"
    
    def test_job_with_steps(self):
        """Test job with steps."""
        steps = [
            PipelineStep(name="Install", command="npm install"),
            PipelineStep(name="Test", command="npm test"),
        ]
        job = PipelineJob(
            name="test",
            steps=steps,
        )
        
        assert len(job.steps) == 2


class TestCICDGenerator:
    """Test cases for CICDGenerator."""
    
    def setup_method(self):
        """Create fresh generator for each test."""
        self.generator = CICDGenerator()
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None
    
    def test_generate_github_actions_python(self):
        """Test generating GitHub Actions for Python."""
        yaml_content = self.generator.generate_github_actions_python(
            project_name="myproject",
            python_versions=["3.10", "3.11"],
        )
        
        assert "name: CI/CD Pipeline" in yaml_content
        assert "on:" in yaml_content
        assert "jobs:" in yaml_content
        assert "pip install" in yaml_content
        assert "pytest" in yaml_content
    
    def test_generate_github_actions_node(self):
        """Test generating GitHub Actions for Node.js."""
        yaml_content = self.generator.generate_github_actions_node(
            project_name="myfrontend",
            node_versions=["18"],
        )
        
        assert "name: CI/CD Pipeline" in yaml_content
        assert "npm ci" in yaml_content or "npm install" in yaml_content
    
    def test_generate_gitlab_ci_python(self):
        """Test generating GitLab CI for Python."""
        yaml_content = self.generator.generate_gitlab_ci_python(
            project_name="myproject",
        )
        
        assert "stages:" in yaml_content
        assert "test:" in yaml_content or "build:" in yaml_content
    
    def test_generate_azure_pipelines(self):
        """Test generating Azure Pipelines."""
        yaml_content = self.generator.generate_azure_pipelines(
            project_name="myproject",
            language="python",
        )
        
        assert "trigger:" in yaml_content or "pr:" in yaml_content
        assert "jobs:" in yaml_content or "steps:" in yaml_content
