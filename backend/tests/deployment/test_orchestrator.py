"""
Tests for Deployment Orchestrator.
"""

import pytest
from datetime import datetime

from backend.deployment.orchestrator import (
    DeploymentOrchestrator,
    DeploymentStep,
    DeploymentResult,
    DeploymentStatus,
    DeploymentEnvironment,
)


class TestDeploymentStep:
    """Test cases for DeploymentStep."""
    
    def test_step_creation(self):
        """Test creating a step."""
        step = DeploymentStep(
            name="Build",
            status=DeploymentStatus.PENDING,
        )
        
        assert step.name == "Build"
        assert step.status == DeploymentStatus.PENDING
    
    def test_step_to_dict(self):
        """Test converting step to dict."""
        step = DeploymentStep(
            name="Deploy",
            status=DeploymentStatus.SUCCESS,
            message="Deployed successfully",
        )
        
        data = step.to_dict()
        
        assert data["name"] == "Deploy"
        assert data["status"] == "success"


class TestDeploymentResult:
    """Test cases for DeploymentResult."""
    
    def test_result_creation(self):
        """Test creating result."""
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
        )
        
        assert result.deployment_id == "dep-123"
        assert result.project_name == "myproject"
        assert result.environment == DeploymentEnvironment.PRODUCTION
    
    def test_result_with_steps(self):
        """Test result with steps."""
        steps = [
            DeploymentStep(name="Build", status=DeploymentStatus.SUCCESS),
            DeploymentStep(name="Test", status=DeploymentStatus.SUCCESS),
        ]
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.STAGING,
            steps=steps,
        )
        
        assert len(result.steps) == 2


class TestDeploymentOrchestrator:
    """Test cases for DeploymentOrchestrator."""
    
    def setup_method(self):
        """Create fresh orchestrator for each test."""
        self.orchestrator = DeploymentOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator is not None
    
    def test_get_deployment_nonexistent(self):
        """Test getting nonexistent deployment."""
        deployment = self.orchestrator.get_deployment("nonexistent-id")
        
        assert deployment is None
    
    def test_list_deployments_empty(self):
        """Test listing deployments when empty."""
        deployments = self.orchestrator.list_deployments()
        
        assert len(deployments) == 0
